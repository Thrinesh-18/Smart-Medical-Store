from typing import Any

from pydantic import BaseModel, Field


class MedicineBase(BaseModel):
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


class MedicineCreate(MedicineBase):
    pass


class Medicine(MedicineBase):
    medicine_id: int


class SearchFilters(BaseModel):
    category: str | None = None
    availability: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    prescription_required: bool | None = None
    dosage_form: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=150)
    top_k: int = Field(default=10, ge=1, le=50)
    use_hybrid: bool = True
    filters: SearchFilters | None = None


class SearchResult(BaseModel):
    medicine_id: int
    medicine_name: str
    generic_name: str
    uses: str
    symptoms: list[str]
    price: float
    stock_status: str
    bm25_score: float
    semantic_score: float
    final_score: float
    why_matched: dict[str, Any]


class SearchResponse(BaseModel):
    normalized_query: str
    corrected_query: str | None = None
    expanded_terms: list[str]
    results: list[SearchResult]
    latency_ms: float


class PopularQueryItem(BaseModel):
    query: str
    count: int


class AnalyticsSnapshot(BaseModel):
    total_queries: int
    failed_queries: int
    average_latency_ms: float
    popular_queries: list[PopularQueryItem]


class EvaluationMetrics(BaseModel):
    precision_at_k: float
    recall_at_k: float
    f1_at_k: float
    map_score: float
    ndcg: float
    mrr: float
