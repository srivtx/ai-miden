## Phase 45: Quantization & GGUF

---

### What We Built

A demonstration of how neural networks can be compressed from FP32 to INT8 and INT4 with minimal accuracy loss. We implemented uniform quantization, per-channel scaling, GPTQ-style error compensation, and AWQ-style activation-aware weight protection.

### Key Results

- **FP32:** 95.5% accuracy, 4.5 KB
- **INT8 uniform:** 95.5% accuracy, 0.6 KB (8× smaller)
- **INT4 uniform:** 94.5% accuracy, 0.3 KB (16× smaller)
- **Per-channel INT8:** 95.5% accuracy (better outlier handling)
- **AWQ-style INT4:** 95.5% accuracy (protects top 10% most important weights)

### Concepts Covered

| Term | File |
|---|---|
| Quantization | `what_is_quantization.md` |
| GPTQ | `what_is_gptq.md` |
| AWQ | `what_is_awq.md` |
| GGUF | `what_is_gguf.md` |

### How It Works

1. Weights cluster around zero in a bell curve
2. Map the weight range to 256 (INT8) or 16 (INT4) bins using scale and zero-point
3. Per-channel scaling handles outliers per output channel
4. GPTQ compensates quantization error across remaining unquantized weights
5. AWQ protects weights with high (weight × activation) importance

### Connection to Previous Phases

- **Phase 25 (Inference Optimization):** Quantization was mentioned but never built from scratch
- **Phase 39 (Distillation):** Distillation makes models smaller by architecture; quantization makes them smaller by precision
- **Phase 43 (Model Merging):** Merged models can be quantized just like any other model

### Connection to Next Phase

Now that we can make models tiny, can we understand what they are actually doing inside? In Phase 46, we explore **mechanistic interpretability** — techniques to understand what individual neurons and circuits compute.

### Files

- `docs/phase45/what_is_quantization.md`
- `docs/phase45/what_is_gptq.md`
- `docs/phase45/what_is_awq.md`
- `docs/phase45/what_is_gguf.md`
- `docs/phase45/SUMMARY.md`
- `src/phase45/phase45_quantization.py`
- `src/phase45/phase45_quantization_colab.py`
- `src/phase45/quantization.png`
