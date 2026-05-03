# Phase 102: Synthetic Data Bootstrapping — Summary

This phase covered how models can generate, verify, and curate their own training data to break through the limitations of finite human-labeled datasets.

## What We Learned

- **Not all generated data is useful.** A language model producing synthetic training examples will generate many low-quality or incorrect outputs. Training on unfiltered synthetic data can degrade rather than improve performance.

- **Rejection Sampling is the simplest quality filter.** By generating many candidates and keeping only those that pass a threshold, the training distribution shifts toward higher-quality outputs. The threshold controls the quality-quantity trade-off.

- **Self-improvement creates a feedback loop.** A model generates data, a verifier filters it, and the model trains on the filtered data. Over iterations, capability grows from 35% to 62% in toy simulations, though gains eventually plateau.

- **The verifier is the ceiling.** The quality, reliability, and coverage of the verifier determine the maximum improvement possible. A biased or weak verifier causes model collapse; a perfect verifier enables strong bootstrapping.

- **Verifier-Augmented Generation generalizes the paradigm.** Beyond simple filtering, verifiers can guide decoding, provide rewards for reinforcement learning, and score continuous outputs. Any domain with a checkable quality criterion can benefit.

## Prerequisites

- Understanding of language model sampling and decoding (Phases 22, 24).
- Familiarity with probability distributions and threshold-based filtering.
- Completion of Phase 101 (Advanced Alignment) is helpful but not required.

## Recommended Reading Order

1. `what_is_rejection_sampling.md` — Start with the foundation: how to filter generated data using a quality threshold.
2. `what_is_self_improvement.md` — Extend filtering into an iterative loop where the model bootstraps its own training data.
3. `what_is_verifier_augmented_generation.md` — Generalize to the full paradigm: how verifiers guide generation, decoding, and training beyond simple rejection.

## Visual Outputs

Running `src/phase102/phase102_synthetic_data.py` produces:

- `phase102_synthetic_data.png` — Four-panel histogram showing the effect of rejection sampling at thresholds -0.5, 0.0, 0.5, and 1.0. Each panel compares the full generated distribution (gray) against the accepted distribution (blue), with a dashed red line marking the true target mean.

## Navigation

- **Previous:** Phase 101 — Advanced Alignment
- **Next:** Phase 103 — Multimodal Data Curation
