## What Is QLoRA?

---

### The Problem

LoRA reduces the number of trainable parameters, but you still need to load the full base model into GPU memory. A 65B parameter model in FP16 needs 130 GB of VRAM just to exist. Even with LoRA, you cannot fine-tune it on a single consumer GPU. How do you shrink the base model itself without destroying its capabilities?

---

### Definition

**QLoRA (Quantized LoRA)** combines two ideas:
1. **4-bit quantization of the base model:** Store weights in 4-bit NormalFloat (NF4) format instead of 16-bit or 32-bit.
2. **LoRA adapters in higher precision:** Keep the tiny adapter matrices in 16-bit or 32-bit for stable training.

**Additional innovations:**
- **Double quantization:** Quantize the quantization constants themselves to save even more memory.
- **Paged optimizers:** Offload optimizer states to CPU RAM when GPU memory is full, then page them back in as needed.

**Result:** Fine-tune a 65B parameter model on a single 48 GB GPU.

---

### Real-Life Analogy

An architect working with blueprints of a skyscraper.
- **Full fine-tuning:** The architect keeps the full-resolution blueprint (huge drafting table, expensive). Every edit requires moving massive sheets of paper.
- **LoRA:** The architect keeps the full blueprint but only edits sticky notes placed on top.
- **QLoRA:** The architect stores a compressed, thumbnail version of the blueprint (tiny file). They only expand the small region they are currently editing to full resolution. The sticky notes (LoRA adapters) are written at full resolution.

The thumbnail is lossy but good enough for reference. The edits are precise because they happen at full resolution.

---

### Tiny Numeric Example

**Model:** 1 billion parameters

**Memory requirements for fine-tuning:**

| Component | FP32 | FP16 | 4-bit (QLoRA) |
|---|---|---|---|
| Base model weights | 4 GB | 2 GB | 0.5 GB |
| Gradients | 4 GB | 2 GB | 0 GB (frozen) |
| Adam optimizer states | 8 GB | 8 GB | ~0.5 GB (paged) |
| LoRA adapters | — | 0.01 GB | 0.01 GB |
| **Total** | **16 GB** | **12 GB** | **~1 GB** |

**Key insight:** QLoRA does not quantize the gradients or optimizer states for the adapter — only the frozen base weights. The adapter trains in full precision, so learning is stable.

---

### Common Confusion

1. **"QLoRA quantizes everything to 4 bits."** No. Only the frozen base model weights are 4-bit. The LoRA adapters train in 16-bit or 32-bit. The activations and gradients for the adapter are also in higher precision.

2. **"4-bit quantization destroys model quality."** Surprisingly, no. NF4 quantization is designed specifically for neural network weight distributions. The information loss is minimal for inference, and the adapter can compensate for any slight degradation during training.

3. **"QLoRA is slower than regular LoRA."** Yes, slightly. Dequantizing 4-bit weights to 16-bit for computation adds overhead. But the slowdown is typically 10-30% — a small price for fitting a 65B model on one GPU.

4. **"QLoRA works for any model size."** Theoretically yes, but practically the paging overhead becomes severe for models >100B on single GPUs. For very large models, you still need multi-GPU setups or model parallelism.

5. **"QLoRA and LoRA are completely different methods."** No. QLoRA = LoRA + 4-bit quantization + double quantization + paging. The core adaptation mechanism (BA matrices) is identical.

---

### Where It Is Used in Our Code

`src/phase35/phase35_lora_colab.py` — Demonstrates QLoRA-style training: a quantized base model with high-precision LoRA adapters. Shows memory savings and stable convergence.
