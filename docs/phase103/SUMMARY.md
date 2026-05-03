# Phase 103 Summary: Multimodal Data Curation

## What We Learned

1. **Web-scale multimodal datasets are inherently noisy.** Raw crawls contain misaligned, spammy, and semantically vacant pairs. Without curation, training on this noise produces models that fail to connect vision and language meaningfully.

2. **CLIP scoring provides a scalable filter.** By projecting images and text into a shared embedding space, we can measure cross-modal alignment using dot-product similarity. This removes the need for manual annotation at billion-pair scale.

3. **Contrastive filtering improves precision dramatically.** Discarding the bottom 30-50% of pairs by similarity score can raise downstream zero-shot accuracy by 10-17 percentage points while shrinking the dataset, making training faster and cheaper.

4. **Temporal alignment extends curation to time-based modalities.** Video-audio and video-text pairs require sub-second synchronization. File-level pairing is insufficient; event-level alignment using forced alignment or dynamic time warping is necessary for clean training signals.

5. **Data curation is a recurring process, not a one-time step.** Thresholds must be recalibrated as data distributions shift, and iterative refinement (filter, retrain, re-filter) produces progressively cleaner datasets and stronger encoders.

6. **The quality of multimodal models is bounded by the quality of their alignment.** No architecture can compensate for training on captions that describe unrelated content. Investment in curation pays off more than equivalent investment in model size.

## Prerequisites

- Phase 68 (Embeddings & Vector Spaces): understanding of dot products and cosine similarity
- Phase 70 (Domain Adaptation): understanding of distribution shift and fine-tuning
- Phase 102 (Synthetic Data Bootstrapping): understanding of data generation and augmentation

## Recommended Reading Order

1. `what_is_clip_scoring.md` — Start here to understand the core scoring mechanism
2. `what_is_contrastive_filtering.md` — Learn how scores are turned into dataset-quality decisions
3. `what_is_temporal_alignment.md` — Extend the concepts to time-based modalities

## Visual Outputs

Running `src/phase103/phase103_multimodal_data.py` produces:
- `phase103_multimodal_data.png`: Three-panel figure showing (1) CLIP score distributions for aligned vs noisy pairs, (2) precision after filtering at the 25th, 50th, and 75th percentiles, and (3) temporal alignment scores across time windows with the true event marked.

## Navigation

- **Previous**: [Phase 102: Synthetic Data Bootstrapping](../phase102/SUMMARY.md)
- **Next**: [Phase 104: Architecture Search & Inductive Bias Design](../phase104/SUMMARY.md)
