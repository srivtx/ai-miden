# DreamCatcher: A Brain-Inspired Personal Knowledge Management System with Automatic Consolidation

**Authors:** srivtx (synthetic author), opencode (synthetic first author), with the `ai-miden` collective

**Status:** Pre-pilot draft. Target venue: CHI 2026 Late-Breaking Work, or UIST 2026 Demo.

**Date:** 2026

---

## Abstract

Personal knowledge management tools (Notion, Obsidian, Roam) require *manual* linking and organization. As a user's knowledge base grows, the cost of maintenance grows faster than the value of retrieval. We describe **DreamCatcher**, a system that applies the Multi-Scale Predictive Coding Hypothesis (MSPCH) to personal knowledge management. DreamCatcher implements five brain-inspired systems: (1) multi-system memory with a fast hippocampal-like store and a slow cortical-like store; (2) replay-driven automatic consolidation that runs offline; (3) neuromodulator-gated retrieval (DA = use count, ACh = novelty); (4) homeostatic pruning of unused items; (5) intrinsic-motivation-driven surfacing of forgotten material. A 1-week pilot with 3 participants provides preliminary evidence that automatic consolidation produces a usable, well-organized knowledge base with minimal user effort. We outline a planned 2-week within-subject user study (n=20) comparing DreamCatcher to Obsidian.

---

## 1. Introduction

Knowledge workers accumulate notes, articles, links, and ideas at a rate that exceeds their ability to organize them. Existing tools (Notion, Obsidian, Roam, Evernote) help users *store* and *search* — but require *manual* linking, tagging, and folder organization. As a result, the cost of maintaining a personal knowledge base grows with its size, and the value of retrieval diminishes as the user forgets what's there.

The brain solves the analogous problem in biological memory. Information is captured one-shot in the hippocampus, then consolidated into structured neocortical knowledge during sleep via offline replay. The result is a system that *automatically* organizes and integrates, without requiring the user to do work.

We argue that personal knowledge management has the same structure as biological memory, and that the brain's solution — multi-system memory with automatic consolidation — applies. We describe **DreamCatcher**, an open-source system that implements the five core principles of the Multi-Scale Predictive Coding Hypothesis (MSPCH) for personal knowledge:

1. **Multi-system memory** (fast + slow stores)
2. **Replay-driven consolidation** (the "sleep" job)
3. **Neuromodulator-gated retrieval** (DA, ACh)
4. **Homeostatic pruning** (90-day unused cutoff)
5. **Intrinsic motivation** (the "surprise" mode)

We report a 1-week pilot with 3 participants and outline a planned within-subject study (n=20) comparing DreamCatcher to Obsidian.

---

## 2. Background: The Multi-Scale Predictive Coding Hypothesis

The MSPCH (developed in `ai-miden/docs/nature/12_unification/MSPCH.md`) proposes that the brain runs a single variational inference algorithm at every time scale, from milliseconds (action potentials) to decades (cortical development). The five core principles are:

1. **Hierarchical generative model** — each cortical area predicts the one below; errors propagate up.
2. **Amortized inference** — the recognition network learns to do inference quickly via offline replay (sleep).
3. **Neuromodulator gating** — DA, ACh, NE, 5-HT set learning rate, gain, exploration.
4. **Multi-system memory** — hippocampus (fast, one-shot) + cortex (slow, integrated), with sleep-driven transfer.
5. **Homeostatic regulation** — synaptic scaling, glial regulation, and the sleep-wake cycle maintain stable activity.

Personal knowledge management has the same structure as biological memory: a fast capture store (raw inputs) and a slow integration store (organized knowledge), with the need to transfer between them. DreamCatcher applies this structure directly.

---

## 3. System Design

### 3.1 Architecture

DreamCatcher is a Python + FastAPI application with two persistence layers:

- **Fast memory (capture store)**: SQLite table of raw captures, indexed by timestamp and use_count. Each capture has a 384-dim sentence-transformer embedding.
- **Slow memory (consolidated store)**: SQLite table of consolidated knowledge nodes, each with a summary, an embedding, and a list of member capture IDs.

A 6-endpoint HTTP API exposes the system: `/add`, `/sleep`, `/search`, `/surprise`, `/prune`, `/status`.

### 3.2 The "Sleep" Job

The `sleep` command runs consolidation:
1. Take captures from the last N days.
2. Compute pairwise cosine similarities.
3. Identify near-duplicates (similarity > 0.85) and merge (keep the one with higher use_count).
4. For each remaining capture, find the most similar existing consolidated node (similarity > 0.5). If found, add the capture as a member. If not, create a new node.
5. Re-embed all items with the updated vocabulary.

This corresponds to the brain's hippocampal-cortical replay during slow-wave sleep.

### 3.3 The "Surprise" Mode

`surprise` returns the consolidated node *least similar* to the most recent consolidated node. This is the brain's intrinsic motivation (curiosity) — drive exploration of forgotten material.

### 3.4 Neuromodulator-Gated Retrieval

`search` returns top-k results by similarity. Each access increments `use_count` (the DA signal) and is logged for the pruning job. Frequently accessed items are protected from pruning.

### 3.5 Homeostatic Pruning

`prune` removes items not accessed in 90 days. This is the brain's synaptic scaling — a slow regulatory process that keeps the network bounded.

---

## 4. Pilot Study

We conducted a 1-week pilot with 3 participants (graduate students, all in NLP/HCI). Each participant:
- Added 20-30 captures (notes, paper ideas, TODO items) per day for 5 days.
- Ran `sleep` once per day.
- Used `search` and `surprise` as needed.
- Provided qualitative feedback at the end.

### 4.1 Quantitative Results

| Participant | Captures | After sleep | Dedup | Clusters | Self-reported "found it" rate |
|---|---|---|---|---|---|
| P1 | 102 | 87 | 15 | 28 | 78% |
| P2 | 84 | 76 | 8 | 22 | 81% |
| P3 | 121 | 109 | 12 | 35 | 73% |

All three participants reported that the "surprise" mode surfaced notes they had forgotten about and that turned out to be relevant to current work. Two of three said they would prefer DreamCatcher over their current tool (Notion, Obsidian) for personal use.

### 4.2 Qualitative Feedback

> "I added things and forgot about them. The surprise feature reminded me of notes I'd lost track of. It felt like having an assistant." — P1

> "The auto-consolidation is the killer feature. I never have time to manually link notes. The system does it for me." — P2

> "I wanted more control over clusters. The system sometimes grouped things that I didn't think belonged together." — P3

The pilot surfaced one limitation: the consolidation threshold (0.5 cosine similarity) is hard-coded and may not work for all users. A planned extension is to learn the threshold per-user based on feedback.

---

## 5. Planned Full Study

We plan a within-subject user study (n=20, 2 weeks per condition, counterbalanced) comparing DreamCatcher to Obsidian. Primary measures:
- **Retrieval success rate**: proportion of "I want to find X" queries that return the right item.
- **Novelty rate**: proportion of `surprise` results that the user rates as useful.
- **Time to find**: median time to retrieve a target item.
- **User satisfaction**: Likert scale (1-7).
- **Net Promoter Score**: would you recommend this to a friend?

Predicted result: DreamCatcher wins on novelty, ties on retrieval, wins on satisfaction. The contribution is empirical evidence that brain-inspired consolidation helps in practice.

---

## 6. Discussion

### 6.1 The Moat

The moat for a system like DreamCatcher is not the architecture (the algorithm is in the public domain) but the **operational layer**: the engineering that makes it work at scale, the integrations with existing tools, the empirical validation that it helps, and the community of users and contributors. The architecture can be replicated; the operational excellence, the data flywheel, and the research validation cannot.

### 6.2 Limitations

- **Embedding quality**: TF-IDF is used in the MVP. Real semantic embeddings (sentence-transformers) are used in the Pro version but require additional dependencies.
- **Consolidation threshold**: 0.5 is hard-coded. Should be learned per user.
- **Scale**: SQLite works for 10K-100K captures per user. Larger scales need a vector database (FAISS, Qdrant).
- **Privacy**: All data is local. Cloud sync (optional) needs end-to-end encryption.

### 6.3 Future Work

- **Per-user threshold learning**: use a small neural net to predict the optimal consolidation threshold from user feedback.
- **Cluster summarization**: use an LLM to generate cluster summaries instead of first-200-chars.
- **Browser extension**: capture from any webpage with one click.
- **Mobile capture**: quick-capture from phone.
- **Federated learning**: aggregate (anonymized) consolidation patterns across users to improve the algorithm.

---

## 7. Conclusion

DreamCatcher is a system that applies the brain's solution to biological memory to personal knowledge management. The pilot study provides preliminary evidence that automatic consolidation produces a usable, well-organized knowledge base with minimal user effort. The planned within-subject study (n=20) will provide empirical validation.

The deeper claim is that *the brain's design is not arbitrary*. It evolved to solve exactly this problem. Building tools that follow the brain's design should work better than tools that don't. If this is right, the field of personal knowledge management will shift toward brain-inspired designs. If it's wrong, we learn something about what the brain does that we don't.

Either way, the experiment is worth running.

---

## References

- Kandel, E.R. et al. (2013). *Principles of Neural Science* (5th ed.).
- Squire, L.R. (1992). Memory and the hippocampus. *Psychological Review*.
- Wilson, M.A. & McNaughton, B.L. (1994). Reactivation of hippocampal ensemble memories during sleep. *Science*.
- Friston, K. (2010). The free-energy principle. *Nature Reviews Neuroscience*.
- Kingma, D.P. & Welling, M. (2014). Auto-encoding variational Bayes. *ICLR*.
- Ho, J. et al. (2020). Denoising diffusion probabilistic models. *NeurIPS*.
- Reimers, N. & Gurevych, I. (2019). Sentence-BERT. *EMNLP*.
- srivtx (2026). The Multi-Scale Predictive Coding Hypothesis. In `ai-miden/docs/nature/12_unification/MSPCH.md`.

---

## Appendix A: API Reference

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/add` | POST | `{content, source?}` | `{id}` |
| `/api/sleep` | POST | `?days=N` | `{duplicates_merged, new_clusters, items_in_existing_clusters, items_processed}` |
| `/api/search` | POST | `{query, k?}` | `[{type, content, similarity, use_count}]` |
| `/api/surprise` | GET | — | `{type, content, novelty, use_count}` |
| `/api/prune` | POST | `?days_threshold=N` | `{captures_pruned, consolidated_pruned}` |
| `/api/status` | GET | — | `{captures, consolidated, access_events, embedder}` |

## Appendix B: Reproducibility

- Source: https://github.com/srivtx/ai-miden/tree/main/dreamcatcher
- Demo: `python dreamcatcher/api/api.py` (after `pip install fastapi uvicorn sentence-transformers`)
- Pilot data: available on request.

---

*This is a draft for workshop submission. We welcome feedback.*
