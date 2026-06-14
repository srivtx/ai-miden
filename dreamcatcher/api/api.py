"""
DreamCatcher API: FastAPI server for machine-scale deployment.
"""

import os
import argparse
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Lazy import the engine
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dreamcatcher_pro import DreamCatcher

app = FastAPI(title="DreamCatcher API", version="2.0")

# CORS for the web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the static UI
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Engine (initialized at startup)
_engine: Optional[DreamCatcher] = None


def get_engine() -> DreamCatcher:
    global _engine
    if _engine is None:
        _engine = DreamCatcher()
    return _engine


# ---------- API models ----------

class AddRequest(BaseModel):
    content: str
    source: Optional[str] = "text"
    url: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 5


# ---------- Endpoints ----------

@app.get("/")
def root():
    """Serve the web UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DreamCatcher API. Visit /docs for OpenAPI."}


@app.get("/api/status")
def status():
    return get_engine().status()


@app.post("/api/add")
def add(req: AddRequest):
    content = req.content
    if req.url:
        content = f"[{req.url}] {content}"
    cid = get_engine().add(content, source=req.source)
    return {"id": cid}


@app.post("/api/sleep")
def sleep(days: int = 1):
    return get_engine().sleep(days=days)


@app.post("/api/search")
def search(req: SearchRequest):
    return get_engine().search(req.query, k=req.k)


@app.get("/api/surprise")
def surprise():
    s = get_engine().surprise()
    if s is None:
        raise HTTPException(404, "No items yet.")
    return s


@app.post("/api/prune")
def prune(days_threshold: int = 90):
    return get_engine().prune(days_threshold=days_threshold)


def run_server(engine=None, host="0.0.0.0", port=8000):
    global _engine
    if engine is not None:
        _engine = engine
    print(f"DreamCatcher API running on http://{host}:{port}")
    print(f"Web UI: http://{host}:{port}/")
    print(f"API docs: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)
