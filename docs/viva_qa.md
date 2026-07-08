# Viva Questions and Answers

## Basic
1. **What is Information Retrieval?**  
IR is the process of finding relevant items from a large collection for a given query.
2. **Why BM25?**  
BM25 provides robust lexical ranking by balancing term frequency and document length normalization.

## Intermediate
3. **Why use both stemming and lemmatization?**  
Lemmatization preserves linguistic correctness; stemming improves matching robustness under morphological variation.
4. **What is query expansion?**  
Adding related terms (synonyms, aliases, symptom mappings) to improve recall.

## Advanced Semantic Retrieval
5. **Why sentence transformers for medicine search?**  
They encode semantic meaning, enabling retrieval even when exact keywords differ.
6. **Why FAISS?**  
Efficient similarity search over dense vectors with scalable indexing strategies.
7. **How is hybrid retrieval computed?**  
Weighted fusion: `alpha * normalized_bm25 + beta * normalized_semantic`.

## System Design
8. **How does explainability help?**  
It improves trust and debugging by exposing lexical matches, semantic score, and overlap signals.
9. **How do you evaluate IR quality?**  
Using Precision/Recall/F1 for set overlap and MAP/NDCG/MRR for ranking quality.
10. **How is production readiness addressed?**  
Modular architecture, tests, rate limiting, environment configs, Docker, and deployment guides.
