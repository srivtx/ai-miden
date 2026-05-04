## Phase 155 Summary: Real Data Curation Pipeline

This phase introduces a **real data curation pipeline** — the most important system in production AI that nobody talks about.

### Key Takeaways

1. **Data quality dominates model architecture.** A good model on bad data is worse than a bad model on good data.
2. **Deduplication removes 30-60% of web data.** Near-duplicate detection with MinHash+LSH is essential.
3. **Quality filtering is multi-signal.** Length, entropy, language, and trained classifiers all contribute.
4. **Curation is continuous, not one-time.** Production pipelines run 24/7 as new data arrives.

### What We Built

- Loaded 10,000 real Wikipedia articles
- Cleaned HTML, URLs, and encoding issues
- Filtered by length, word count, and entropy
- Deduplicated with MinHash + LSH (128 hashes, 16 bands)
- Exported curated corpus as JSONL with metadata
- Visualized pipeline stages and distributions

### Files

| File | Purpose |
|---|---|
| `docs/phase155/what_is_data_curation_pipeline.md` | The complete curation concept |
| `docs/phase155/what_is_minhash_deduplication.md` | Near-duplicate detection algorithm |
| `src/phase155/phase155_data_curation.py` | Real pipeline on Wikipedia data |

### Connections

- **Phase 63 (Data Curation):** Phase 155 is the production version with real data and real deduplication.
- **Phase 89 (Data Engineering):** This pipeline is what data engineering teams build and maintain.
- **Phase 147 (Synthetic Data):** Curation applies to synthetic data too — generation is only half the pipeline.
- **Phase 121 (Pretraining):** The output of this pipeline is the input to pretraining.

### Next Step

Phase 156: **Real Multi-Tool Agent** — Build a ReAct agent with web search, calculator, code execution, and memory that solves real multi-step problems.
