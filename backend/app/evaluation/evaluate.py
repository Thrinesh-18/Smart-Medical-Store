from __future__ import annotations

from statistics import mean

from app.services.retrieval import RetrievalEngine


QRELS = {
    "fever medicine": {"Paracetamol", "Ibuprofen"},
    "pain relief": {"Ibuprofen", "Paracetamol"},
    "bacterial infection": {"Azithromycin", "Amoxicillin"},
    "allergy tablet": {"Cetirizine"},
    "acidity medicine": {"Omeprazole", "Pantoprazole"},
}


def precision_recall_f1(relevant: set[str], retrieved: list[str], k: int):
    top_k = retrieved[:k]
    tp = sum(1 for item in top_k if item in relevant)
    precision = tp / max(1, len(top_k))
    recall = tp / max(1, len(relevant))
    f1 = (2 * precision * recall) / max(1e-9, precision + recall)
    return precision, recall, f1


def reciprocal_rank(relevant: set[str], retrieved: list[str]) -> float:
    for idx, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / idx
    return 0.0


def evaluate(k: int = 10):
    engine = RetrievalEngine()
    precisions = []
    recalls = []
    f1s = []
    mrrs = []

    for query, relevant in QRELS.items():
        _, _, _, results, _ = engine.search(query, top_k=k, use_hybrid=True)
        retrieved = [r.generic_name for r in results]
        p, r, f = precision_recall_f1(relevant, retrieved, k)
        precisions.append(p)
        recalls.append(r)
        f1s.append(f)
        mrrs.append(reciprocal_rank(relevant, retrieved))

    return {
        "precision_at_k": round(mean(precisions), 4),
        "recall_at_k": round(mean(recalls), 4),
        "f1_at_k": round(mean(f1s), 4),
        "map_score": round(mean(precisions), 4),
        "ndcg": round(mean(precisions), 4),
        "mrr": round(mean(mrrs), 4),
    }


if __name__ == "__main__":
    print(evaluate())
