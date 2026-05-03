# Phase 112 Summary: Multi-Token Prediction

## What We Learned

1. **Multi-token prediction produces N future-token predictions from a single forward pass.** Each prediction head is a lightweight linear projection, and the loss is the average cross-entropy over all N predictions.
2. **MTP does not hurt model quality.** DeepSeek-V3 and Meta demonstrated that N=4 MTP reaches the same or better perplexity as standard next-token prediction, because natural language tokens are conditionally correlated and the shared backbone is strong.
3. **Parallel decoding turns MTP heads into draft models at inference time.** Acceptance/rejection sampling with tree attention verifies multiple draft tokens in one base-model pass, yielding up to 2x inference speedup.
4. **Training efficiency improves because label density increases.** The backbone transformer is amortized across four prediction tasks, so the model learns roughly 2x more per wall-clock hour. The speedup is sublinear due to head overheads and diminishing gradient quality at large N.
5. **MTP is a training-time technique, distinct from speculative decoding.** Speculative decoding is an inference optimization; MTP is a training objective. They complement each other but are not the same.

## Prerequisites

- Phase 20: Sampling and Temperature (autoregressive generation basics)
- Phase 36: Speculative Decoding (draft/verify inference paradigm)
- Phase 38: Compute-Optimal Training (Chinchilla scaling laws)

## Recommended Reading Order

1. `what_is_multi_token_prediction.md` — The MTP objective, information theory, and difference from speculative decoding
2. `what_is_parallel_decoding.md` — Acceptance/rejection, Medusa heads, tree attention
3. `what_is_training_efficiency.md` — Labels per FLOP, wall-clock speedup, diminishing returns
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase112/mtp_loss_comparison.png` — Training loss curves for MTP vs standard next-token prediction, plotted against steps and wall-clock time.
- `src/phase112/mtp_gradient_norms.png` — Gradient norm distributions showing richer gradients from MTP.
- `src/phase112/mtp_perplexity_comparison.png` — Validation perplexity over training for both methods.
- `src/phase112/mtp_token_distribution.png` — Probability distribution of predicted tokens at multiple offsets.

## Navigation

- **Previous:** [Phase 111: FP8 and Low-Precision Training](../phase111/SUMMARY.md)
- **Next:** Phase 113 (see curriculum)
