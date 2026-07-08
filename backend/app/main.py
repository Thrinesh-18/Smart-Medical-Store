from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import AnalyticsSnapshot, Medicine, MedicineCreate, SearchRequest, SearchResponse
from app.services.analytics import AnalyticsStore
from app.services.retrieval import RetrievalEngine

app = FastAPI(title="Smart Medical Store IR System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RetrievalEngine()
analytics = AnalyticsStore()
request_windows: dict[str, deque[datetime]] = defaultdict(deque)
RATE_LIMIT = 120


@app.middleware("http")
async def basic_rate_limit(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow()
    window = request_windows[ip]
    while window and window[0] < now - timedelta(minutes=1):
        window.popleft()
    if len(window) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    window.append(now)
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest):
    normalized, corrected, expanded, results, latency_ms = engine.search(
        query=payload.query,
        top_k=payload.top_k,
        filters=payload.filters,
        use_hybrid=payload.use_hybrid,
    )
    analytics.log_query(payload.query, latency_ms, had_results=bool(results))
    return SearchResponse(
        normalized_query=normalized,
        corrected_query=corrected,
        expanded_terms=expanded,
        results=results,
        latency_ms=round(latency_ms, 3),
    )


@app.post("/semantic-search", response_model=SearchResponse)
def semantic_search(payload: SearchRequest):
    payload.use_hybrid = True
    return search(payload)


@app.get("/autocomplete")
def autocomplete(q: str):
    q = q.lower().strip()
    suggestions = sorted({r.medicine_name for r in engine.records if r.medicine_name.lower().startswith(q)})[:10]
    return {"query": q, "suggestions": suggestions}


@app.get("/suggest")
def suggest(q: str):
    corrected = engine.query_processor.spell_correct(q.lower().strip())
    return {"query": q, "suggestion": corrected}


@app.get("/medicine/{medicine_id}", response_model=Medicine)
def get_medicine(medicine_id: int):
    for record in engine.records:
        if record.medicine_id == medicine_id:
            return Medicine(**record.__dict__)
    raise HTTPException(status_code=404, detail="Medicine not found")


@app.post("/add-medicine")
def add_medicine(payload: MedicineCreate):
    next_id = max(r.medicine_id for r in engine.records) + 1
    item = Medicine(medicine_id=next_id, **payload.model_dump())
    path = Path("./data/medicines.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.append(item.model_dump())
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    engine._load()
    return {"message": "Medicine added", "medicine_id": next_id}


@app.put("/update-medicine/{medicine_id}")
def update_medicine(medicine_id: int, payload: MedicineCreate):
    path = Path("./data/medicines.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = False
    for i, item in enumerate(data):
        if item["medicine_id"] == medicine_id:
            data[i] = Medicine(medicine_id=medicine_id, **payload.model_dump()).model_dump()
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Medicine not found")
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    engine._load()
    return {"message": "Medicine updated"}


@app.delete("/delete-medicine/{medicine_id}")
def delete_medicine(medicine_id: int):
    path = Path("./data/medicines.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    filtered = [d for d in data if d["medicine_id"] != medicine_id]
    if len(filtered) == len(data):
        raise HTTPException(status_code=404, detail="Medicine not found")
    path.write_text(json.dumps(filtered, indent=2), encoding="utf-8")
    engine._load()
    return {"message": "Medicine deleted"}


@app.get("/metrics", response_model=AnalyticsSnapshot)
def metrics():
    return analytics.snapshot()


@app.get("/logs")
def logs():
    snap = analytics.snapshot()
    return {"logs": snap["popular_queries"], "failed_queries": snap["failed_queries"]}
