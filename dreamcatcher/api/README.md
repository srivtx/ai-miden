# DreamCatcher Pro

> The production version. Same five MSPCH principles, but with real embeddings, a web API, and a deployable UI.

---

## What this is

A **personal knowledge management system** built on the Multi-Scale Predictive Coding Hypothesis (MSPCH) developed in `docs/nature/12_unification/`. The MVP version is `dreamcatcher.py` (TF-IDF). This is the **Pro version**: sentence-transformers embeddings, FastAPI backend, web UI, ready to deploy.

## The science (in one paragraph)

The brain solves "too much information, can't find it" with **multi-system memory + sleep consolidation**. The hippocampus captures everything one-shot. The cortex stores integrated knowledge. Sleep replay transfers hippocampal traces to cortical knowledge, dedupes, links, consolidates. Neuromodulators (DA, ACh) gate what gets encoded. Synaptic homeostasis prunes what's unused. **DreamCatcher does the same thing**, with SQLite + sentence-transformers + a FastAPI server.

## What's different from the MVP

| Feature | MVP (`dreamcatcher.py`) | Pro (`api/dreamcatcher_pro.py`) |
|---|---|---|
| Embeddings | TF-IDF (no deps) | sentence-transformers (semantic) |
| Embedding quality | Keyword overlap | True semantic similarity |
| Synonyms | Misses | Captures ("ML" = "machine learning") |
| API | None | FastAPI with 6 endpoints |
| Web UI | None | Static HTML/JS in `static/` |
| Deployment | Local script | Hugging Face Spaces, Render, etc. |
| Use case | Demo | Real product |

## Quick start

### Local

```bash
# Install deps
pip install fastapi uvicorn sentence-transformers numpy matplotlib

# Run the API server
python dreamcatcher/api/api.py
# or
cd dreamcatcher/api && python api.py

# Visit
open http://localhost:8000
```

The web UI is at `/`. The OpenAPI docs are at `/docs`.

### CLI (same as MVP)

```bash
python dreamcatcher/api/dreamcatcher_pro.py add "Just read about MSPCH..."
python dreamcatcher/api/dreamcatcher_pro.py sleep
python dreamcatcher/api/dreamcatcher_pro.py search "diffusion"
python dreamcatcher/api/dreamcatcher_pro.py surprise
python dreamcatcher/api/dreamcatcher_pro.py status
```

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Web UI (HTML) |
| `/api/add` | POST | Add a capture |
| `/api/sleep` | POST | Run consolidation |
| `/api/search` | POST | Semantic search |
| `/api/surprise` | GET | Surface novel item |
| `/api/prune` | POST | Prune unused |
| `/api/status` | GET | System status |
| `/docs` | GET | OpenAPI documentation |

Example with curl:

```bash
curl -X POST http://localhost:8000/api/add \
  -H "Content-Type: application/json" \
  -d '{"content": "MSPCH is the multi-scale predictive coding hypothesis."}'

curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "diffusion", "k": 5}'
```

## Deploy to Hugging Face Spaces (free, public)

This is the fastest way to get this in front of real users.

1. Create a Space: https://huggingface.co/new-space
2. Select "Docker" as the SDK.
3. Push the code:
   ```bash
   git remote add space https://huggingface.co/spaces/YOUR_NAME/dreamcatcher
   git push space main
   ```
4. Add `requirements.txt` with the deps.
5. Hugging Face handles the build, hosting, and HTTPS.

The Space will be live at `https://huggingface.co/spaces/YOUR_NAME/dreamcatcher` within 5 minutes.

## Deploy to Render / Railway / Fly.io

Standard Python web service. `uvicorn api:app --host 0.0.0.0 --port 8000`. The DB is on-disk; for production, use a persistent volume or a managed Postgres.

## Roadmap (the path from 0 to 1M users)

| Stage | What | Effort | Revenue model |
|---|---|---|---|
| 1 | MVP at TF-IDF | 1 day | None (research) |
| 2 | Pro with sBERT + API | 2 days | None (OSS) |
| 3 | Deploy to HF Spaces | 1 hour | Free tier |
| 4 | LLM-based cluster summarization | 1 day | Pro $10/mo |
| 5 | Browser extension (capture from anywhere) | 3 days | Pro $10/mo |
| 6 | Mobile quick-capture | 1 week | Pro $10/mo |
| 7 | Multi-user (B2B teams) | 2 weeks | Team $50/seat/mo |
| 8 | Privacy-preserving federation | 1 month | Enterprise |

## The paper this enables

**Title**: "DreamCatcher: a brain-inspired personal knowledge management system with automatic consolidation"

**Contributions**:
1. The first open-source system implementing the full MSPCH memory architecture for personal knowledge.
2. Empirical evidence (via a within-subject user study, n=20) that automatic consolidation improves retrieval, reduces duplication, and surfaces forgotten material compared to existing tools (Obsidian, Notion).
3. A reference implementation that other researchers can build on.

**Venue**: CHI 2026, UIST 2026, IUI 2026. Or a system paper at NeurIPS / ICML.

## The research contribution

The system embodies a *specific* claim: **multi-system memory + automatic consolidation is the right architecture for personal knowledge management**. This is testable. If true, the field of personal knowledge management shifts toward brain-inspired designs. If false, we learn something about what the brain does that we don't.

## The product contribution

Most tools stop at "store and search." DreamCatcher adds "consolidate" — the missing step. The user doesn't have to manually link notes. The system does it for them, every night, like sleep.

## Files

- `api/dreamcatcher_pro.py` — the engine (sentence-transformers)
- `api/api.py` — FastAPI server
- `static/index.html` — web UI
- `../dreamcatcher.py` — the MVP (TF-IDF, no deps)
- `../README.md` — the MVP docs

## License

Open source. Use it, modify it, build on it.
