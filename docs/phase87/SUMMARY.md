# Phase 87: Checkpointing, Fault Tolerance & Determinism

## What we covered

- **Checkpointing:** Saving model weights, optimizer state, and RNG state so training can survive crashes.
- **Deterministic Training:** Fixing random seeds and using deterministic algorithms so experiments are reproducible.
- **Fault Tolerance:** Designing systems to recover automatically from hardware or software failures.

## Why this matters

Training large models is expensive. A single crash without checkpoints can destroy days of progress. Without determinism, you cannot trust that a bug fix or hyperparameter change caused the observed effect. Fault tolerance turns fragile long-running jobs into robust pipelines.

## Key takeaways

1. Save checkpoints more frequently than you can afford to re-train.
2. Determinism requires controlling seeds, data order, and nondeterministic GPU ops.
3. Fault tolerance = detection + checkpointing + automatic restart.

## Navigation

- [Previous Phase](../phase86/SUMMARY.md)
- [Next Phase](../phase88/SUMMARY.md)
