import json
import os
import re
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient, TEXT

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000)
db = client.threat_lab
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
STATUSES = ["Anticipated", "Active", "Evolving", "Resolved"]


def seed():
    records = json.loads(Path("data/threats.json").read_text())
    for record in records:
        db.threats.replace_one({"_id": record["_id"]}, record, upsert=True)
    db.threats.create_index([("summary", TEXT), ("package", TEXT), ("title", TEXT)])
    db.threats.create_index("status")
    return db.threats.count_documents({})


@asynccontextmanager
async def lifespan(app):
    seed()
    yield
    client.close()


app = FastAPI(title="Linux Threat Intelligence Assistant", lifespan=lifespan)


@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/api/health")
def health():
    state = {"database": "unavailable", "model": "unavailable", "model_tag": MODEL}
    try:
        client.admin.command("ping")
        state["database"] = "available"
    except Exception:
        pass
    try:
        response = httpx.get(OLLAMA + "/api/tags", timeout=3)
        response.raise_for_status()
        state["model"] = "available" if MODEL in [m["name"] for m in response.json()["models"]] else "not downloaded"
    except Exception:
        pass
    return state


@app.get("/api/threats")
def threats(q: str = "", status: str = ""):
    query = {}
    if status:
        if status not in STATUSES:
            raise HTTPException(422, "Unknown lifecycle status")
        query["status"] = status
    if q.strip():
        query["$text"] = {"$search": q[:500]}
    return list(db.threats.find(query).sort("_id", 1).limit(50))


@app.get("/api/threats/{record_id}")
def detail(record_id: str):
    record = db.threats.find_one({"_id": record_id})
    if not record:
        raise HTTPException(404, "Record not found")
    return record


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=64)


def retrieve(message, exchanges):
    lower = message.lower()
    if re.search(r"\b(first|that one|it)\b", lower) and exchanges:
        ids = exchanges[-1].get("record_ids", [])
        return [detail(ids[0])] if ids else []
    status = next((s for s in STATUSES if re.search(r"\b" + s.lower() + r"\b", lower)), "")
    if status and any(w in lower for w in ("linux", "threat", "dataset")):
        return threats(status=status)[:3]
    return threats(q=message, status=status)[:3]


@app.post("/api/chat")
def chat(request: ChatRequest):
    cid = request.conversation_id or str(uuid.uuid4())
    conversation = db.conversations.find_one({"_id": cid}) or {}
    exchanges = conversation.get("exchanges", [])[-5:]
    records = retrieve(request.message, exchanges)
    sources = [{"id": r["_id"], "url": r["source"], "title": r["title"]} for r in records]
    answer = "The records in this dataset provide insufficient evidence to answer that question."
    generated = False
    if records:
        from app.rag import generate_and_store
        try:
            result = generate_and_store(db, cid, request.message, records)
            return {"conversation_id": cid, "answer": result["answer"], "retrieved_sources": sources,
                    "model_generated": True, "history_exchanges_used": result["history_exchanges_used"]}
        except Exception:
            raise HTTPException(503, "Model unavailable, timed out, or returned unsupported citations. Search remains available.")
    db.conversations.update_one({"_id": cid}, {"$push": {"exchanges": {"$each": [{"question": request.message, "answer": answer, "record_ids": [r["_id"] for r in records]}], "$slice": -5}}}, upsert=True)
    return {"conversation_id": cid, "answer": answer, "retrieved_sources": sources, "model_generated": generated}
