from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import get_settings
from app.schemas import SearchFilters, SearchResult
from app.services.preprocessing import QueryProcessor


@dataclass
class MedicineRecord:
    medicine_id: int
    medicine_name: str
    generic_name: str
    composition: str
    symptoms: list[str]
    uses: str
    dosage_form: str
    category: str
    prescription_required: bool
    manufacturer: str
    side_effects: list[str]
    price: float
    stock_status: str
    keywords: list[str]
    aliases: list[str]

    def lexical_text(self) -> str:
        return " ".join(
            [
                self.medicine_name,
                self.generic_name,
                self.composition,
                self.uses,
                " ".join(self.symptoms),
                " ".join(self.keywords),
                " ".join(self.aliases),
                self.category,
            ]
        )


class RetrievalEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.records: list[MedicineRecord] = []
        self.documents: list[str] = []
        self.bm25: BM25Okapi | None = None
        self.tfidf = TfidfVectorizer()
        self.tfidf_matrix = None
        self.embedder = SentenceTransformer(self.settings.embedding_model_name)
        self.faiss_index = None
        self.query_processor: QueryProcessor | None = None
        self._load()

    def _load(self) -> None:
        data_path = Path(self.settings.data_json_path)
        with data_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        self.records = [MedicineRecord(**item) for item in payload]
        self.documents = [r.lexical_text().lower() for r in self.records]
        tokenized = [doc.split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
        self.tfidf_matrix = self.tfidf.fit_transform(self.documents)

        embeddings = self.embedder.encode(self.documents, convert_to_numpy=True, normalize_embeddings=True)
        dim = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dim)
        self.faiss_index.add(embeddings.astype("float32"))

        vocab = list({r.medicine_name.lower() for r in self.records} | {r.generic_name.lower() for r in self.records})
        alias_map = {}
        for r in self.records:
            for alias in r.aliases:
                alias_map[alias.lower()] = r.generic_name
        symptom_map = {sym: [] for r in self.records for sym in r.symptoms}
        for r in self.records:
            for sym in r.symptoms:
                symptom_map[sym].append(r.generic_name)
        self.query_processor = QueryProcessor(vocab, alias_map, symptom_map)

    @staticmethod
    def _matches_filters(record: MedicineRecord, filters: SearchFilters | None) -> bool:
        if not filters:
            return True
        if filters.category and record.category.lower() != filters.category.lower():
            return False
        if filters.availability and record.stock_status.lower() != filters.availability.lower():
            return False
        if filters.prescription_required is not None and record.prescription_required != filters.prescription_required:
            return False
        if filters.dosage_form and record.dosage_form.lower() != filters.dosage_form.lower():
            return False
        if filters.min_price is not None and record.price < filters.min_price:
            return False
        if filters.max_price is not None and record.price > filters.max_price:
            return False
        return True

    def search(self, query: str, top_k: int, filters: SearchFilters | None = None, use_hybrid: bool = True):
        start = time.perf_counter()
        assert self.query_processor is not None and self.bm25 is not None
        normalized = self.query_processor.normalize_text(query)
        corrected = self.query_processor.spell_correct(normalized)
        processed_query = corrected or normalized
        expanded_terms = self.query_processor.expand_query(processed_query)

        bm25_scores = np.array(self.bm25.get_scores(expanded_terms if expanded_terms else processed_query.split()))
        query_emb = self.embedder.encode([processed_query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        semantic_scores, _ = self.faiss_index.search(query_emb, len(self.records))
        semantic_scores = semantic_scores.flatten()

        alpha = self.settings.bm25_weight
        beta = self.settings.semantic_weight
        bm25_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-9)
        semantic_norm = (semantic_scores - semantic_scores.min()) / (semantic_scores.max() - semantic_scores.min() + 1e-9)
        final = alpha * bm25_norm + beta * semantic_norm if use_hybrid else bm25_norm

        ranked_indices = np.argsort(final)[::-1]
        results: list[SearchResult] = []
        for idx in ranked_indices:
            record = self.records[int(idx)]
            if not self._matches_filters(record, filters):
                continue
            lexical_hits = [term for term in expanded_terms if term in record.lexical_text().lower()]
            result = SearchResult(
                medicine_id=record.medicine_id,
                medicine_name=record.medicine_name,
                generic_name=record.generic_name,
                uses=record.uses,
                symptoms=record.symptoms,
                price=record.price,
                stock_status=record.stock_status,
                bm25_score=float(bm25_norm[idx]),
                semantic_score=float(semantic_norm[idx]),
                final_score=float(final[idx]),
                why_matched={
                    "matching_keywords": lexical_hits[:10],
                    "retrieval_source": "hybrid" if use_hybrid else "lexical",
                    "alias_match": processed_query in [a.lower() for a in record.aliases],
                    "symptom_overlap": list(set(expanded_terms).intersection(set(record.symptoms))),
                },
            )
            results.append(result)
            if len(results) == top_k:
                break

        latency_ms = (time.perf_counter() - start) * 1000
        return normalized, corrected, expanded_terms, results, latency_ms
