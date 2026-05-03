# Phase 89: Data Engineering at Scale (Web Pipelines)

## What We Learned

1. **Data quality dominates model quality.** A mediocre architecture trained on clean, diverse data often beats a state-of-the-art architecture trained on noisy duplicates. Filtering and deduplication are not optional preprocessing steps; they are core determinants of model capability.
2. **MinHash makes near-deduplication feasible at billion-document scale.** By estimating Jaccard similarity through MinHash signatures, pipelines can remove near-duplicates without comparing every pair, reducing both compute waste and memorization risk.
3. **Heuristic filtering removes obvious junk before expensive scoring.** Rules based on length, punctuation ratio, and language detection are cheap and catch the majority of low-quality documents, leaving perplexity filtering for subtler anomalies.
4. **Perplexity filtering catches linguistically anomalous text.** A reference language model's surprise score identifies grammatically correct but semantically empty documents that pass surface heuristics.
5. **Filtering rules are domain-specific.** A threshold that works for English prose may destroy valid code or Chinese text. Pipelines must be tuned per domain and monitored as data distributions shift.
6. **The pipeline mindset is sequential and composable.** Deduplication, heuristic filtering, and perplexity scoring form a chain where each stage refines the output of the previous one, much like a compiler optimization pipeline.

## Prerequisites

- Understanding of hash functions and probability (for MinHash intuition)
- Familiarity with n-grams and text tokenization
- Basic knowledge of language model inference and perplexity
- Experience with NumPy array operations

## Recommended Reading Order

1. `what_is_deduplication.md` — Start with removing redundancy, the highest-impact preprocessing step
2. `what_is_data_filtering.md` — Learn heuristic quality filtering that runs before expensive scoring
3. `what_is_perplexity_filtering.md` — Finish with the nuanced, model-based filter for subtle garbage

## Visual Outputs

- `src/phase89/minhash_similarity.png` — Heatmap showing estimated Jaccard similarity between three toy documents using MinHash signatures.

## Navigation

- [Previous Phase](../phase88/SUMMARY.md)
- [Next Phase](../phase90/SUMMARY.md)
