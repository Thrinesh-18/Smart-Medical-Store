# Presentation Deck Content

## Slide 1 - Title
Smart Medical Store Information Retrieval System  
Hybrid BM25 + Semantic Search for Pharmacy Intelligence

## Slide 2 - Problem
- Misspelled medicine names
- Brand vs generic confusion
- Symptom-only user queries
- Need for explainable and fast ranking

## Slide 3 - Objectives
- Build production IR pipeline
- Combine lexical and semantic retrieval
- Add explainability and analytics
- Deliver API + UI + deployment readiness

## Slide 4 - Architecture
- UI -> FastAPI -> Query processing -> BM25 + FAISS -> Hybrid rank -> Explanation

## Slide 5 - Dataset
- 600 realistic medicine records
- JSON/CSV/SQLite support
- Fields include symptoms, aliases, stock, prescription, pricing

## Slide 6 - NLP Pipeline
- Normalization, tokenization, stopword removal
- Lemmatization + stemming
- RapidFuzz spell correction
- Synonym and symptom expansion

## Slide 7 - Retrieval Algorithms
- BM25 scoring for lexical relevance
- MiniLM embeddings for semantic relevance
- Weighted hybrid final score

## Slide 8 - Explainability
- Matched keywords
- Semantic similarity score
- Alias and symptom overlap
- Retrieval source labels

## Slide 9 - API + UI
- Search, semantic-search, autocomplete, suggest
- CRUD medicine operations
- Analytics dashboard in React

## Slide 10 - Evaluation
- Precision, Recall, F1
- MAP, NDCG, MRR
- Latency and throughput testing

## Slide 11 - Deployment
- Docker Compose
- Render / Railway / HF Spaces / EC2 paths

## Slide 12 - Demo Flow
1. Typo query (`paracetmol`)
2. Symptom query (`tablet for headache`)
3. Filtered query (availability/category)
4. Analytics panel and explanation cards

## Speaker Notes
- Emphasize why hybrid retrieval beats single-method retrieval.
- Explain practical pharmacy use-cases and user trust via explainability.
