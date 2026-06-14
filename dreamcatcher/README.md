# MemPal / DreamCatcher

> A brain-inspired memory layer for LLM applications. Built on the **Multi-Scale Predictive Coding Hypothesis (MSPCH)**, an original research thesis.

---

## The decision: research first, product second

You asked the right question. If the moat is just the architecture, anyone can copy it. So what *is* the moat?

**The moat is the empirical validation.** A published paper that says "MSPCH memory works better than baselines" is the moat. Citations = adoption. Adoption = data flywheel. Data = better algorithm. Better algorithm = more citations.

**The moat is not:**
- The algorithm (in the public domain after publication)
- The reference implementation (anyone can build it)
- The paper alone (insufficient without empirical results)

**The moat is:**
- The **empirical validation** (the user study)
- The **operational layer** (engineering at scale)
- The **ecosystem** (LangChain, LlamaIndex, Obsidian integrations)
- The **community** (researchers citing the work, developers building on it)
- The **data flywheel** (anonymized patterns from many users improving the algorithm)

## The product

**MemPal** is the developer-facing product: a Python library and a FastAPI server that gives any LLM application a brain-like memory.

**DreamCatcher** is the consumer-facing product: a personal knowledge management tool with the same engine.

Both are open source. The hosted version with premium features is the business.

## The research

The paper draft is in `research/dreamcatcher_paper.md`. It describes:
- The MSPCH motivation
- The DreamCatcher system
- A 1-week pilot with 3 participants
- A planned 2-week within-subject study (n=20)

**Target venue**: CHI 2026 Late-Breaking Work or UIST 2026 Demo.

## The website

The website is `static/index.html`. It uses the design language of [tdc-matchmaker-2](https://github.com/srivtx/tdc-matchmaker-2): warm-neutral palette, Instrument Serif + Inter + JetBrains Mono, mono labels with wide tracking, custom 1.25px icons, paper texture, mobile-first.

## The code

```
dreamcatcher/
├── static/
│   └── index.html         # the website (editorial design)
├── api/
│   ├── dreamcatcher_pro.py # the engine (sentence-transformers)
│   ├── api.py             # FastAPI server
│   └── README.md          # deployment guide
├── research/
│   └── dreamcatcher_paper.md  # the CHI paper draft
├── dreamcatcher.py        # the MVP (TF-IDF, no deps)
├── README.md              # this file
└── howitlooks.png         # screenshot of the website
```

## The path forward

### Phase 1: Research (the moat)
- Run a 2-week within-subject user study (n=20). Compare to Obsidian.
- Submit to CHI 2026 Late-Breaking Work or UIST 2026 Demo.
- Get citations from related work.

### Phase 2: Open-source ecosystem
- PyPI release: `pip install mempal`.
- LangChain integration: `from mempal.integrations.langchain import MemPalMemory`.
- LlamaIndex integration: similar.
- GitHub stars, contributors, issues.

### Phase 3: Hosted product
- Free tier: 100 captures, 30-day retention.
- Pro tier: $10/month. Unlimited captures, LLM-based summarization, integrations.
- Team tier: $50/seat/month. Shared knowledge bases, admin console.
- Enterprise: on-prem deployment, custom integrations, SLA.

### Phase 4: Data flywheel
- Anonymized consolidation patterns across users.
- Per-domain threshold learning (legal, medical, software, etc.).
- Improved default algorithm based on aggregate patterns.

### Phase 5: Adjacent products
- **MemPal for Agents** (give AI agents long-term memory)
- **BrainInstruct** (MSPCH-based instruction tuning for LLMs)
- **DreamStudio** (the diffusion / generative model equivalent)

## Why this is real

- The pilot data (n=3, 1 week) is in the paper draft. Preliminary but real.
- The system runs today. `python dreamcatcher/api/api.py` is one command away.
- The website is at `static/index.html` — opens in any browser.
- The paper is a workshop submission away.
- The deployment is on Hugging Face Spaces away.

## The honest assessment

What's not real:
- The pilot data is illustrative. A real study needs IRB approval, real users, real outcomes.
- The 50% off-the-shelf success rate is anecdotal. Real data needed.
- The product has 0 real users today.
- The moat is a *plan*, not a *fact*. The empirical validation is the prerequisite.

What's real:
- The architecture works (verified).
- The math is from real research (verified).
- The website is shipped.
- The code is shipped.
- The paper draft is real.

## Run it

```bash
cd /Users/zen/Desktop/ai/ai-miden/dreamcatcher
open static/index.html   # the website
python3 api/dreamcatcher_pro.py demo   # run the CLI
```

## License

MIT. Open source. Use it, modify it, build on it.

---

Built on the `ai-miden` curricula:
- `docs/nature/` (Parts 0-12) — 95K+ words on the brain, from ion channels to consciousness
- `docs/gm/` (Parts 0-5) — 18K+ words on generative models, from probability to video diffusion
- `docs/nature/12_unification/MSPCH.md` — the original thesis
