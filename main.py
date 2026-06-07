"""
Vizuara Agent — FastAPI entry point.
Endpoints: POST /chat, GET /metrics, GET /health
"""

import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from router.main_router import process

app = FastAPI(title="Vizuara Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_PATH = Path("logs/query_log.jsonl")


class ChatRequest(BaseModel):
    query: str
    user_id: str = "anonymous"
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    response: str
    intent: str
    intent_confidence: float
    confidence_score: float
    confidence_level: str
    disclaimer: str
    latency_ms: int
    tokens_used: int


@app.get("/health")
def health():
    return {"status": "ok", "agent": "Vizuara"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = process(
        user_query=req.query,
        user_id=req.user_id,
        conversation_history=req.conversation_history or [],
    )
    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        intent_confidence=result["intent_confidence"],
        confidence_score=result["confidence"]["score"],
        confidence_level=result["confidence"]["level"],
        disclaimer=result["confidence"]["disclaimer"],
        latency_ms=result["latency_ms"],
        tokens_used=result["tokens_used"],
    )


@app.get("/metrics")
def metrics():
    if not LOG_PATH.exists():
        return {"total_queries": 0}

    logs = []
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not logs:
        return {"total_queries": 0}

    total = len(logs)
    avg_confidence = round(sum(r.get("confidence_score", 0) for r in logs) / total, 3)
    avg_latency    = round(sum(r.get("latency_ms", 0) for r in logs) / total, 1)
    avg_tokens     = round(sum(r.get("tokens_used", 0) for r in logs) / total, 1)

    intent_counts: dict[str, int] = {}
    level_counts:  dict[str, int] = {}
    for r in logs:
        i = r.get("intent", "UNKNOWN")
        l = r.get("confidence_level", "UNKNOWN")
        intent_counts[i] = intent_counts.get(i, 0) + 1
        level_counts[l]  = level_counts.get(l, 0) + 1

    return {
        "total_queries":    total,
        "avg_confidence":   avg_confidence,
        "avg_latency_ms":   avg_latency,
        "avg_tokens":       avg_tokens,
        "intent_breakdown": intent_counts,
        "confidence_breakdown": level_counts,
        "recent_queries":   logs[-5:],
    }
