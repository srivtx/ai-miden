# Phase 107 Summary: On-Device LLMs

## What We Learned

1. **Memory bandwidth, not compute, is the primary bottleneck for LLM inference.** Flash Attention addresses this by tiling the attention computation and keeping intermediate values in fast SRAM, reducing HBM traffic from quadratic to linear and enabling 2-7x speedups on long sequences.

2. **Speculative decoding accelerates generation without approximating the output distribution.** By drafting tokens with a small model and verifying them in parallel with the large model, it achieves 2-3x wall-clock speedup while producing exactly the same text as the target model alone.

3. **Mobile LLMs are co-designed systems, not just shrunken models.** They combine architectural changes (grouped-query attention, sliding windows), aggressive quantization (INT4 with QAT), and hardware-specific inference engines to fit into phone memory and run in real time.

4. **Quantization error accumulates across layers.** Our NumPy simulation showed that INT4 MSE is higher than INT8, and the gap widens as error propagates through a deep network. This explains why mobile LLMs need quantization-aware training rather than post-training conversion.

5. **The edge is a distinct deployment target with its own constraints and trade-offs.** On-device inference enables privacy, offline operation, and low latency, but sacrifices the peak capability of cloud-scale models. The optimal system is often hybrid, routing tasks between edge and cloud.

6. **Efficiency techniques are composable.** Flash Attention, speculative decoding, and INT4 quantization can be applied simultaneously. A mobile LLM using all three can achieve throughput that would be impossible with any single technique alone.

## Prerequisites

- Phase 29 (Transformers): understanding of self-attention and autoregressive generation
- Phase 70 (Domain Adaptation): understanding of model specialization and distribution shift
- Phase 105 (Tiny ML): understanding of quantization, distillation, and latency-aware design

## Recommended Reading Order

1. `what_is_flash_attention.md` — Understand the memory bottleneck and how to solve it
2. `what_is_speculative_decoding.md` — Learn how to reduce the number of expensive forward passes
3. `what_is_mobile_llm.md` — See how these ideas combine into a deployable on-device system

## Visual Outputs

Running `src/phase107/phase107_on_device.py` produces:
- `quantization_size_tradeoff.png`: Bar chart showing model size for a 1B-parameter LLM at FP32, FP16, INT8, and INT4 precision.
- `quantization_accuracy_tradeoff.png`: Line plot showing how INT8 and INT4 quantization error accumulates across an increasing number of layers.

## Navigation

- **Previous**: [Phase 106: AI for Science](../phase106/SUMMARY.md)
- **Next**: [Phase 108: Multimodal Reasoning](../phase108/SUMMARY.md)
