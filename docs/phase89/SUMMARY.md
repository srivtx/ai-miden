# Phase 89: Data Engineering at Scale (Web pipelines)

## What we covered

- **Deduplication:** Removing exact and near-duplicate documents using techniques like MinHash.
- **Data Filtering:** Selecting high-quality examples based on length, language, and heuristics.
- **Perplexity Filtering:** Using a reference model to score and remove linguistically anomalous text.

## Why this matters

Data quality dominates model quality. A mediocre architecture trained on clean, diverse data often beats a state-of-the-art architecture trained on noisy duplicates. At web scale, automation is the only way to curate training data in time and budget.

## Key takeaways

1. MinHash makes near-deduplication feasible on billions of documents.
2. Filtering is domain-specific: rules that work for English may fail for code or other languages.
3. Perplexity is expensive but powerful for catching subtle garbage that heuristics miss.

## Navigation

- [Previous Phase](../phase88/SUMMARY.md)
- [Next Phase](../phase90/SUMMARY.md)
