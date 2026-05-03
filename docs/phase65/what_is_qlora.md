## What Is QLoRA?

---

### The Problem

LoRA reduced trainable parameters, but the base model still sits in GPU memory at full precision (16-bit or 32-bit). A 7B parameter model needs 14GB in FP16 and 28GB in FP32. Add optimizer states, activations, and LoRA weights, and even a 24GB GPU chokes. You cannot fine-tune Llama-2-7B on a single consumer GPU if the base model alone consumes all the memory. How do you fit a 7B model into 8GB VRAM while still fine-tuning it?

---

### Definition

**QLoRA (Quantized Low-Rank Adaptation)** is a memory-efficient fine-tuning method that stores the frozen base model in 4-bit precision while keeping the LoRA adapter weights in full (16-bit) precision. During the forward pass, 4-bit weights are dequantized on-the-fly to 16-bit for computation; during the backward pass, only the LoRA adapters receive gradients.

**The QLoRA stack:**
```
1. 4-bit Normal Float Quantization (NF4) — compress base weights
2. Double Quantization — quantize the quantization constants themselves
3. Paged Optimizers — offload optimizer states to CPU RAM when GPU overflows
4. LoRA adapters — trainable low-rank matrices in FP16/BF16
```

**Key insight:**
- The base model weights are frozen AND compressed to 4 bits
- Only LoRA adapters (tiny) stay in full precision
- 4-bit weights are dequantized to 16-bit at computation time
- A 7B model fits in ~4GB instead of 14GB

**Why this matters:**
- Fine-tune a 7B model on a single 8GB consumer GPU
- Fine-tune a 70B model on a single 48GB GPU
- The base model stays compressed; adapters remain small and portable

---

### Real-Life Analogy

A traveling library with a master librarian.
- **Full fine-tuning:** You carry every book in hardcover first edition (heavy, expensive, one suitcase per book). You can only carry five books.
- **LoRA only:** You still carry hardcover books, but you only write annotations on sticky notes instead of rewriting pages. Still heavy.
- **QLoRA:** You carry every book as a digital e-reader file (compressed, tiny). The e-reader decompresses pages on-the-fly when you read them. You still write your annotations on sticky notes (LoRA adapters) in full ink. You carry 1,000 books in your pocket and annotate freely.
- **Paged optimizers:** When your desk gets too crowded with sticky notes, the assistant moves older notes to a filing cabinet (CPU RAM) and brings them back only when needed.

---

### Tiny Numeric Example

**Pre-trained weight block (simplified 4×1):**
```
W = [0.35, -0.82, 1.15, -0.21]
```

**Step 1: Find min/max and quantize to 4-bit (16 levels, 0-15):**
```
min = -0.82, max = 1.15, scale = (1.15 - (-0.82)) / 15 = 0.131

quantized = round((W - min) / scale)
          = [8, 0, 15, 4]   (4-bit integers)
```

**Step 2: Store in 4 bits per value:**
```
32-bit storage: 4 values × 32 bits = 128 bits
4-bit storage:  4 values × 4 bits  = 16 bits  (8× reduction)
```

**Step 3: Dequantize for computation:**
```
W_deq = quantized × scale + min
      = [0.348, -0.82, 1.115, -0.296]
```

**Step 4: Apply LoRA on dequantized weights:**
```
h = W_deq @ x + B @ A @ x
```

**Precision loss:**
```
Original:  [0.35,   -0.82,   1.15,   -0.21]
Dequant:   [0.348,  -0.82,   1.115,  -0.296]
Error:     [0.002,   0.0,    0.035,  -0.086]
```

The error is small relative to the weight magnitude, and the LoRA adapter learns to compensate.

---

### Common Confusion

1. **"QLoRA quantizes the LoRA weights too."** No. Only the frozen base model is quantized to 4-bit. The LoRA adapters (B and A) remain in full BF16/FP16 precision so gradients can flow properly.

2. **"4-bit means the model runs in 4-bit arithmetic."** No. The weights are stored in 4-bit but dequantized to 16-bit during the forward and backward passes. The matmuls still happen in 16-bit or 32-bit.

3. **"QLoRA destroys model quality."** Not in practice. NF4 is designed to minimize error for normally distributed weights. The rank of the LoRA adapter can be increased slightly to compensate for any quantization noise.

4. **"Double quantization means quantizing twice."** Almost, but not redundantly. It means quantizing the quantization constants (the scale factors) themselves, saving even more memory for large blocks.

5. **"Paged optimizers are only for QLoRA."** No. Paged optimizers (using CPU RAM as swap) can be used with any training setup, but QLoRA makes them essential because the model is so compressed that optimizer states become the memory bottleneck.

6. **"QLoRA is slower than LoRA."** Yes, slightly. Dequantization adds overhead. Expect 10-30% slowdown versus FP16 LoRA, but you can run it on hardware that could not even fit FP16 LoRA.

7. **"You can merge QLoRA adapters like normal LoRA."** You can, but you must first dequantize the base model to full precision, then add the LoRA update, then optionally re-quantize. The merged result is no longer 4-bit.

---

### Where It Is Used in Our Code

`src/phase65/phase65_qlora.py` — We simulate 4-bit quantization on a toy weight matrix, dequantize it, and train LoRA adapters on top, showing that fine-tuning still converges despite quantization error.

`src/phase65/phase65_qlora_colab.py` — We run a real QLoRA pipeline with `transformers`, `peft`, `bitsandbytes`, and `trl`, loading a model in 4-bit NF4 and fine-tuning with `SFTTrainer` on a consumer GPU.
