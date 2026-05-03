# Phase 105 Summary: Tiny ML & Edge Deployment

## What We Covered

This phase focused on deploying models to resource-constrained environments:

- **Quantization-Aware Training**: Training models to be robust to low-precision inference by simulating quantization during the forward pass.
- **Knowledge Distillation**: Transferring the behavior of a large teacher model to a small student model using soft targets.
- **Neural Architecture Search for Latency**: Searching for architectures that lie on the Pareto frontier of accuracy vs. inference speed.

## Key Takeaway

Tiny ML is about trade-offs. You cannot simply shrink a model and expect it to work. QAT, distillation, and latency-aware NAS are three tools for compressing models while preserving as much capability as possible. The edge is where AI meets the real world.

## Navigation

- **Previous**: [Phase 104: Architecture Search & Inductive Bias Design](../phase104/SUMMARY.md)
- **Next**: Phase 106 (see curriculum)
