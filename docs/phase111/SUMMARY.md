# Phase 111 Summary: FP8 and Low-Precision Training

## What We Learned

1. **FP8 is not one format but two:** E4M3 trades range for precision and is used for weights; E5M2 trades precision for range and is used for gradients. Using the wrong format causes either underflow or overflow.
2. **Mixed precision training keeps a high-precision master copy while computing in low precision.** FP32 master weights and optimizer state stabilize training, while FP8 tensor cores deliver 2x throughput.
3. **Delayed scaling avoids synchronization stalls by using the previous step's max-abs to set the current step's scale.** It accepts one step of potential clipping to keep the pipeline full.
4. **Quantization-aware training inserts fake quantization into the forward pass.** The straight-through estimator allows gradients to flow through rounding, and LSQ learns the optimal step size per tensor.
5. **Training in FP8 is harder than inference in FP8.** Gradients are noisier, outliers are destructive, and scaling must be managed per-tensor or per-block. Frontier labs invest engineering effort specifically in making FP8 training stable at trillion-parameter scale.

## Prerequisites

- Phase 45: Quantization (uniform vs non-uniform, INT8/INT4 basics)
- Phase 83: CUDA and GPU Architecture (tensor cores, memory hierarchy)
- Phase 84: Memory Bandwidth and Activation Checkpointing (why bandwidth is the bottleneck)

## Recommended Reading Order

1. `what_is_fp8_format.md` — E4M3 vs E5M2, bit layouts, dynamic range
2. `what_is_mixed_precision_training.md` — Transformer Engine recipe, delayed scaling, master weights
3. `what_is_quantization_aware_training.md` — QAT vs PTQ, STE, LSQ
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase111/fp8_dynamic_range.png` — Representable values for FP32, BF16, E4M3, E5M2, and INT8 across magnitude ranges.
- `src/phase111/fp8_quantization_error.png` — Quantization error histograms showing how scaling reduces clipping and underflow.
- `src/phase111/fp8_delayed_scaling.png` — Max-abs tracking and scale adaptation across simulated training steps.
- `src/phase111/fp8_loss_curves.png` — Loss curves comparing FP32, simulated FP8 with scaling, and simulated FP8 without scaling.

## Navigation

- **Previous:** [Phase 110: Test-Time Compute Scaling](../phase110/SUMMARY.md)
- **Next:** [Phase 112: Multi-Token Prediction](../phase112/SUMMARY.md)
