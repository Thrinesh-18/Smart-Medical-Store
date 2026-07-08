from collections import Counter
from dataclasses import dataclass, field


@dataclass
class AnalyticsStore:
    query_counts: Counter = field(default_factory=Counter)
    failed_queries: int = 0
    latencies: list[float] = field(default_factory=list)

    def log_query(self, query: str, latency_ms: float, had_results: bool) -> None:
        self.query_counts[query] += 1
        self.latencies.append(latency_ms)
        if not had_results:
            self.failed_queries += 1

    def snapshot(self) -> dict:
        avg_latency = sum(self.latencies) / max(1, len(self.latencies))
        return {
            "total_queries": sum(self.query_counts.values()),
            "failed_queries": self.failed_queries,
            "average_latency_ms": round(avg_latency, 3),
            "popular_queries": [{"query": q, "count": c} for q, c in self.query_counts.most_common(10)],
        }
