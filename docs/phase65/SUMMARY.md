## Phase 65: QLoRA & Memory-Efficient Training

---

### What We Built

A NumPy simulation of 4-bit quantization, dequantization, and LoRA fine-tuning on quantized weights. We compared memory usage (32-bit vs. 4-bit), measured quantization error, and showed that LoRA converges nearly as well on a quantized base as on a full-precision base. We also wrote a Colab script for real QLoRA fine-tuning with `transformers`, `peft`, `bitsandbytes`, and `trl`.

### Key Results

- **Memory reduction:** 6.4× (32-bit → 4-bit with block-wise scaling)
- **Quantization MSE:** 0.000677
- **LoRA params:** 128 (vs. 1,024 full fine-tuning, 8× reduction)
- **LoRA on 4-bit loss:** 0.0024
- **LoRA on FP32 loss:** 0.0004
- **Quality gap:** 0.0020 (quantization error is small for this task)

### Concepts Covered

| Term | File |
|---|---|
| QLoRA | `what_is_qlora.md` |
| BitsAndBytes | `what_is_bitsandbytes.md` |
| Gradient Checkpointing | `what_is_gradient_checkpointing.md` |
| 4-bit Quantization (NF4) | `what_is_4bit_quantization.md` |

### Connection to Next Phase

QLoRA compresses the base model and trains tiny adapters. Phase 66 covers **inference optimization and model serving** — how to deploy these compressed and adapted models efficiently in production, including merging adapters, quantization-aware inference, and batching strategies.

### Files

- `docs/phase65/what_is_qlora.md`
- `docs/phase65/what_is_bitsandbytes.md`
- `docs/phase65/what_is_gradient_checkpointing.md`
- `docs/phase65/what_is_4bit_quantization.md`
- `docs/phase65/SUMMARY.md`
- `src/phase65/phase65_qlora.py`
- `src/phase65/phase65_qlora_colab.py`
- `src/phase65/qlora.png`
