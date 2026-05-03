# Phase 117 Summary: Data Mixing Laws and Curriculum Learning

## What We Learned

1. **Data mixing laws determine the optimal domain ratio for pretraining.** Uniform mixing is rarely optimal; hard or information-dense domains usually need higher weight than their raw volume suggests.
2. **DoReMi and similar approaches use a small proxy model to discover mixing weights** based on per-domain validation loss, avoiding the cost of training a full model multiple times.
3. **Curriculum learning trains on easy data first and gradually increases difficulty.** This stabilizes early gradients and often leads to better final performance than random mixing.
4. **Capability gap diagnosis decomposes model performance into fine-grained skills** and traces weaknesses back to missing data sources, enabling targeted collection instead of blind scaling.
5. **These three ideas form a unified data strategy:** diagnose gaps, set mixing weights, and schedule difficulty to maximize training efficiency.

## Prerequisites

- Phase 50: Evaluating Language Models (perplexity, downstream accuracy)
- Phase 95: Chain-of-Thought Prompting (reasoning as a skill to diagnose)
- Phase 105: Scaling Laws (Chinchilla total-token budget)

## Recommended Reading Order

1. `what_is_data_mixing_law.md` — Why uniform mixing fails and how to optimize domain ratios
2. `what_is_curriculum_learning.md` — Training schedules that progress from easy to hard
3. `what_is_capability_gap_diagnosis.md` — Identifying missing skills and tracing them to data sources
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase117/mixing_comparison.png` — Loss curves for uniform, optimal, and curriculum strategies across three simulated domains.
- `src/phase117/mixing_weights.png` — Evolution of domain weights over training steps.
- `src/phase117/capability_gaps.png` — Final per-domain loss comparison showing gaps and how targeted reweighting closes them.

## Navigation

- **Previous:** Phase 116 (see curriculum)
- **Next:** [Phase 118: Native Multimodal Architectures (Early Fusion)](../phase118/SUMMARY.md)
