"""
CortexCode Loop API: the model, the loop, and the server — all in one.

The API no longer just serves a frozen model. It owns a CortexCodeLoop and
exposes it over HTTP. Every /learn, /learn-internet, /watch call updates
the same model that /complete uses. The .pt file on disk is always current.

Endpoints:
    GET  /                  - browser frontend
    GET  /health            - model + loop status
    POST /complete          - generate code completion
    POST /learn             - learn from one text
    POST /learn-internet    - fetch trending Python repos and learn
    POST /watch/start       - start watching a directory
    POST /watch/stop        - stop watching
    GET  /stats             - loss history, surprise log, counters
    POST /save              - explicitly save model to disk (auto on every learn)

Run:
    !python cortexcode_api.py --model /content/cortexcode.pt
"""

import os
import sys
import time
import json
import argparse
import threading
from pathlib import Path
from typing import Optional, List

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import model + loop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cortexcode_torch import CortexCodeModel, CodeTokenizer
from cortexcode_loop import CortexCodeLoop, InternetFetcher, load_loop_model


# =============================================================================
# Request / response models
# =============================================================================

class CompleteRequest(BaseModel):
    prompt: str
    n_tokens: int = 80
    temperature: float = 0.2
    top_k: int = 40


class LearnRequest(BaseModel):
    text: str
    source: str = "api"
    auto_save: bool = True


class LearnInternetRequest(BaseModel):
    n_repos: int = 3
    max_files: int = 20


class WatchRequest(BaseModel):
    directory: str
    interval: float = 1.0


# =============================================================================
# Globals
# =============================================================================

app = FastAPI(title="CortexCode Loop API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

_LOOP: Optional[CortexCodeLoop] = None
_MODEL_PATH: Optional[str] = None
_WATCH_STOP: Optional[threading.Event] = None
_WATCH_THREAD: Optional[threading.Thread] = None
_WATCH_DIR: Optional[str] = None


# =============================================================================
# Init
# =============================================================================

def init_loop(model_path: str, lr: float = 1e-5, threshold: float = 2.0,
              sleep_every: int = 20, sleep_steps: int = 10,
              device: Optional[str] = None):
    """Load a model from disk and wrap it in a CortexCodeLoop."""
    global _LOOP, _MODEL_PATH
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {model_path} on {device}...")
    model, tokenizer, _ = load_loop_model(model_path, device=device)
    _LOOP = CortexCodeLoop(
        model, tokenizer,
        lr=lr, surprise_threshold=threshold,
        sleep_every=sleep_every, sleep_steps=sleep_steps,
        device=device,
    )
    _MODEL_PATH = model_path
    n_params = sum(p.numel() for p in _LOOP.model.parameters())
    print(f"Loop ready: {n_params:,} params, vocab {len(tokenizer)}")
    return _LOOP


# =============================================================================
# Static frontend
# =============================================================================

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# =============================================================================
# Core endpoints
# =============================================================================

@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CortexCode Loop API. See /docs for endpoints."}


@app.get("/health")
def health():
    if _LOOP is None:
        return {"status": "not_initialized"}
    return {
        "status": "ok",
        "model_loaded": True,
        "device": _LOOP.device,
        "vocab_size": len(_LOOP.tokenizer),
        "config": {
            "dim": _LOOP.model.dim,
            "n_layers": _LOOP.model.n_layers,
            "n_heads": _LOOP.model.n_heads,
            "ffn_dim": _LOOP.model.ffn_dim,
            "max_seq_len": _LOOP.model.max_seq_len,
        },
        "loop": _LOOP._summary(),
        "watching": _WATCH_DIR,
    }


@app.post("/complete")
def complete(req: CompleteRequest):
    """Generate code. Uses the model that the loop has been updating."""
    if _LOOP is None:
        raise HTTPException(503, "Model not loaded")
    t0 = time.time()
    unk_id = _LOOP.tokenizer.token_to_id.get("<unk>", 1)
    ids = torch.tensor([_LOOP.tokenizer.encode(req.prompt)], device=_LOOP.device)
    if ids.shape[1] == 0:
        ids = torch.tensor([[unk_id]], device=_LOOP.device)
    out = _LOOP.model.generate(
        ids,
        max_new_tokens=req.n_tokens,
        temperature=max(req.temperature, 0.05),
        top_k=req.top_k,
        ban_tokens={unk_id},
    )
    out_list = out[0].cpu().tolist()
    full = _LOOP.tokenizer.decode(out_list)
    new_part = full[len(req.prompt):]
    elapsed = (time.time() - t0) * 1000
    return {
        "prompt": req.prompt,
        "completion": new_part,
        "full": full,
        "n_tokens": req.n_tokens,
        "elapsed_ms": elapsed,
    }


# =============================================================================
# Loop endpoints
# =============================================================================

@app.post("/learn")
def learn(req: LearnRequest):
    """Feed a text to the loop. It scores by surprise, learns if novel, sleeps if due."""
    if _LOOP is None:
        raise HTTPException(503, "Model not loaded")
    result = _LOOP.on_new_text(req.text, source=req.source)
    if result['action'] == 'learn' and req.auto_save and _MODEL_PATH:
        _LOOP.save(_MODEL_PATH)
    return result


@app.post("/learn-internet")
def learn_internet(req: LearnInternetRequest):
    """Fetch trending Python repos from GitHub and learn from them."""
    if _LOOP is None:
        raise HTTPException(503, "Model not loaded")
    fetcher = InternetFetcher()
    repos = fetcher.fetch_github_trending(req.n_repos)
    if not repos:
        return {"status": "no_repos", "message": "Could not fetch from GitHub"}

    learned = []
    skipped = 0
    for repo in repos:
        count = 0
        for filename, text in fetcher.clone_and_extract(repo['clone_url']):
            if count >= req.max_files:
                break
            r = _LOOP.on_new_text(text, source=f"internet:{repo['name']}/{filename}")
            count += 1
            if r['action'] == 'learn':
                learned.append({"repo": repo['name'], "file": filename, "loss": r['new_loss']})
            else:
                skipped += 1
        if _MODEL_PATH:
            _LOOP.save(_MODEL_PATH)

    return {
        "status": "ok",
        "repos": [{"name": r['name'], "stars": r['stars'], "description": r['description']}
                  for r in repos],
        "learned_count": len(learned),
        "skipped_count": skipped,
        "summary": _LOOP._summary(),
    }


@app.post("/watch/start")
def watch_start(req: WatchRequest):
    """Start a background thread that watches a directory for .py changes."""
    global _WATCH_THREAD, _WATCH_STOP, _WATCH_DIR
    if _LOOP is None:
        raise HTTPException(503, "Model not loaded")
    if _WATCH_THREAD and _WATCH_THREAD.is_alive():
        return {"status": "already_watching", "directory": _WATCH_DIR}

    if not os.path.isdir(req.directory):
        raise HTTPException(400, f"Directory not found: {req.directory}")

    _WATCH_STOP = threading.Event()
    _WATCH_DIR = req.directory

    def watcher():
        directory = Path(req.directory)
        last_mtime = {}
        # Snapshot existing files
        for p in directory.rglob("*.py"):
            if "__pycache__" in str(p) or "/.git/" in str(p):
                continue
            try:
                last_mtime[str(p)] = p.stat().st_mtime
            except OSError:
                pass
        while not _WATCH_STOP.is_set():
            for p in directory.rglob("*.py"):
                if "__pycache__" in str(p) or "/.git/" in str(p) or _WATCH_STOP.is_set():
                    continue
                key = str(p)
                try:
                    mtime = p.stat().st_mtime
                except OSError:
                    continue
                if key in last_mtime and last_mtime[key] != mtime:
                    try:
                        text = p.read_text(errors='ignore')
                        if text:
                            _LOOP.on_new_text(text, source=f"watch:{p.name}")
                            if _MODEL_PATH:
                                _LOOP.save(_MODEL_PATH)
                    except Exception as e:
                        print(f"Watch error on {p}: {e}")
                last_mtime[key] = mtime
            _WATCH_STOP.wait(req.interval)

    _WATCH_THREAD = threading.Thread(target=watcher, daemon=True)
    _WATCH_THREAD.start()
    return {"status": "watching", "directory": req.directory}


@app.post("/watch/stop")
def watch_stop():
    global _WATCH_STOP, _WATCH_DIR
    if _WATCH_STOP:
        _WATCH_STOP.set()
    _WATCH_DIR = None
    return {"status": "stopped"}


@app.get("/stats")
def stats():
    """Detailed loop state: counts, loss history, surprise log."""
    if _LOOP is None:
        raise HTTPException(503, "Model not loaded")
    return {
        **_LOOP._summary(),
        "loss_history": _LOOP.loss_history[-100:],
        "surprise_log": _LOOP.surprise_log[-50:],
        "watching": _WATCH_DIR,
    }


@app.post("/save")
def save():
    """Force-save the model to disk."""
    if _LOOP is None or _MODEL_PATH is None:
        raise HTTPException(503, "Not initialized")
    _LOOP.save(_MODEL_PATH)
    return {"status": "saved", "path": _MODEL_PATH}


# =============================================================================
# Entry
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="/content/cortexcode.pt")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--threshold", type=float, default=2.0)
    parser.add_argument("--sleep-every", type=int, default=20)
    parser.add_argument("--sleep-steps", type=int, default=10)
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"ERROR: model file {args.model} not found.")
        print("Run training first, or pass --model /path/to/model.pt")
        sys.exit(1)

    init_loop(args.model, args.lr, args.threshold,
              args.sleep_every, args.sleep_steps)
    sys.stdout.flush()

    import uvicorn
    print(f"\nCortexCode Loop API on http://{args.host}:{args.port}", flush=True)
    print(f"  GET  /                  browser UI")
    print(f"  POST /complete          generate code")
    print(f"  POST /learn             learn from text")
    print(f"  POST /learn-internet    fetch + learn from GitHub")
    print(f"  POST /watch/start       watch a directory")
    print(f"  POST /watch/stop        stop watching")
    print(f"  GET  /stats             loop statistics")
    print(f"  POST /save              save model to disk")
    print(f"\nDocs: http://{args.host}:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
