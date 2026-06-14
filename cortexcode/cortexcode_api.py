"""
CortexCode API: FastAPI server for interactive code completion testing.

A simple HTTP server that wraps the trained cortexcode_torch.py model and
exposes a /complete endpoint. Designed to run on Colab T4 (free) with
a cloudflared tunnel for public access.

Run locally:
    pip install fastapi uvicorn
    python cortexcode_api.py --model /path/to/cortexcode.pt

Run on Colab:
    !python cortexcode_api.py --model /content/cortexcode.pt
    # In another cell, run cloudflared to tunnel
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as F
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the model
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cortexcode_torch import CortexCodeModel, CodeTokenizer


# =============================================================================
# Pydantic models
# =============================================================================

class CompleteRequest(BaseModel):
    prompt: str
    n_tokens: int = 100
    temperature: float = 0.7
    top_k: int = 50


class CompleteResponse(BaseModel):
    prompt: str
    completion: str
    full: str
    n_tokens: int
    elapsed_ms: float


# =============================================================================
# App state (model + tokenizer)
# =============================================================================

app = FastAPI(title="CortexCode API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals populated at startup
_MODEL = None
_TOKENIZER = None
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_CONFIG = {}


def load_model(model_path: str):
    """Load the trained cortexcode model."""
    global _MODEL, _TOKENIZER, _CONFIG
    print(f"Loading model from {model_path}...")
    ckpt = torch.load(model_path, map_location=_DEVICE, weights_only=False)
    _CONFIG = ckpt["config"]
    tok_data = ckpt["tokenizer"]
    _TOKENIZER = CodeTokenizer()
    _TOKENIZER.token_to_id = tok_data["token_to_id"]
    _TOKENIZER.id_to_token = {int(k): v for k, v in tok_data["id_to_token"].items()}
    _TOKENIZER.next_id = tok_data["next_id"]
    _MODEL = CortexCodeModel(
        vocab_size=len(_TOKENIZER), dim=_CONFIG["dim"], n_layers=_CONFIG["n_layers"],
        n_heads=_CONFIG["n_heads"], ffn_dim=_CONFIG["ffn_dim"], max_seq_len=_CONFIG["max_seq_len"]
    ).to(_DEVICE)
    _MODEL.load_state_dict(ckpt["model_state_dict"])
    _MODEL.eval()
    print(f"Model loaded: {sum(p.numel() for p in _MODEL.parameters()):,} parameters")


# Serve the frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# =============================================================================
# Endpoints
# =============================================================================

@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CortexCode API. POST to /complete with a prompt."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": _MODEL is not None,
        "device": _DEVICE,
        "vocab_size": len(_TOKENIZER) if _TOKENIZER else 0,
        "config": _CONFIG,
    }


@app.post("/complete", response_model=CompleteResponse)
def complete(req: CompleteRequest):
    if _MODEL is None:
        raise HTTPException(503, "Model not loaded. Call /health to check status.")
    t0 = time.time()
    ids = torch.tensor([_TOKENIZER.encode(req.prompt)], device=_DEVICE)
    if ids.shape[1] == 0:
        ids = torch.tensor([[_TOKENIZER.token_to_id.get("<unk>", 1)]], device=_DEVICE)
    out = _MODEL.generate(ids, max_new_tokens=req.n_tokens,
                          temperature=req.temperature, top_k=req.top_k)
    out_list = out[0].cpu().tolist()
    full = _TOKENIZER.decode(out_list)
    new_part = full[len(req.prompt):]
    elapsed = (time.time() - t0) * 1000
    return CompleteResponse(
        prompt=req.prompt,
        completion=new_part,
        full=full,
        n_tokens=req.n_tokens,
        elapsed_ms=elapsed,
    )


@app.post("/reset")
def reset():
    """Reset the conversation (for completeness; the model is stateless)."""
    return {"status": "reset", "note": "CortexCode is stateless; this is a no-op."}


# =============================================================================
# Entry
# =============================================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="/content/cortexcode.pt")
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"ERROR: model file {args.model} not found.")
        print("Run the training step first, or pass --model /path/to/model.pt")
        sys.exit(1)

    load_model(args.model)

    import uvicorn
    print(f"\nCortexCode API running on http://{args.host}:{args.port}")
    print(f"Web UI:  http://{args.host}:{args.port}/")
    print(f"Health:  http://{args.host}:{args.port}/health")
    print(f"\nTo expose publicly, run cloudflared tunnel:")
    print(f"  cloudflared tunnel --url http://localhost:8000\n")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
