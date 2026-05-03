# Phase 102 Summary: Synthetic Data Bootstrapping

## What We Covered

This phase covered how models can generate and curate their own training data:

- **Rejection Sampling**: Generating many candidates and keeping only those that pass a quality threshold.
- **Self-Improvement**: Using the model's own outputs, verified by an external checker, to iteratively improve performance.
- **Verifier-Augmented Generation**: Training or sampling with a verifier model that scores candidate outputs for correctness or quality.

## Key Takeaway

Synthetic data bootstrapping is powerful but brittle. The quality of the verifier or filter determines the ceiling. Without it, models can amplify their own errors. The shift from weak to strong supervision depends on having a reliable signal to filter on.

## Navigation

- **Previous**: [Phase 101: Advanced Alignment](../phase101/SUMMARY.md)
- **Next**: [Phase 103: Multimodal Data Curation](../phase103/SUMMARY.md)
