# Phase 105 Summary: Tiny ML & Edge Deployment

## What We Learned

1. **Model compression requires multiple complementary techniques.** No single method — quantization, distillation, or NAS — is sufficient alone. Real-world Tiny ML pipelines combine all three: a latency-aware search discovers efficient architectures, knowledge distillation preserves accuracy during shrinking, and quantization-aware training hardens the result for low-precision inference.

2. **Knowledge distillation transfers more than accuracy; it transfers structure.** Training a student on soft targets teaches the relative relationships between classes, not just the correct answer. Our NumPy simulation showed that soft-label distillation closed 55% of the accuracy gap between a large teacher and a tiny student on synthetic data.

3. **Quantization-aware training is essential for aggressive compression.** Post-training quantization to INT4 can destroy accuracy, but QAT learns weights that tolerate coarse grids. Our simulation showed INT4 error dropping by nearly 70% when the model is trained with quantization in the loop.

4. **Latency is not the same as FLOPs.** Hardware-aware NAS optimizes for real-world inference time on target chips, not theoretical operation counts. Memory bandwidth, kernel fusion, and operator scheduling matter as much as arithmetic.

5. **The edge is where AI meets the real world.** On-device inference enables privacy (data never leaves the phone), offline operation, and real-time responsiveness. These constraints make Tiny ML one of the hardest and most impactful frontiers in AI engineering.

6. **Trade-offs are unavoidable.** Every compression decision sacrifices something: accuracy, latency, memory, or energy. The art of Tiny ML is choosing the right point on the Pareto frontier for the specific product and user context.

## Prerequisites

- Phase 15 (Convolutional Neural Networks): understanding of spatial features and parameter counts
- Phase 70 (Domain Adaptation): understanding of distribution shift and model specialization
- Phase 104 (Architecture Search): understanding of inductive bias and automated design

## Recommended Reading Order

1. `what_is_knowledge_distillation.md` — Understand how to transfer capability from large to small models
2. `what_is_quantization_aware_training.md` — Learn how to prepare models for low-precision hardware
3. `what_is_neural_architecture_search_for_latency.md` — See how to search for architectures optimized for real-world constraints

## Visual Outputs

Running `src/phase105/phase105_tiny_ml.py` produces:
- `phase105_tiny_ml.png`: Two-panel figure showing (1) training loss curves for hard-label vs soft-label (distillation) training, and (2) validation accuracy comparison between the two student training regimes alongside teacher baselines.

## Navigation

- **Previous**: [Phase 104: Architecture Search & Inductive Bias Design](../phase104/SUMMARY.md)
- **Next**: [Phase 106: AI for Science](../phase106/SUMMARY.md)
