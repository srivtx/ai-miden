## What Is LoRA?

---

### The Problem

You want to fine-tune a 70 billion parameter model to write in your company's style. Full fine-tuning requires 280 GB just for the weights, plus another 560 GB for Adam optimizer states. That is nearly a terabyte of GPU memory — completely inaccessible. Even a 7B model needs 84 GB total. How do you adapt a giant model without updating (or even storing gradients for) all its parameters?

---

### Definition

**LoRA (Low-Rank Adaptation)** freezes the pre-trained model weights and injects small, trainable **rank-decomposition matrices** into selected layers.

Instead of updating a weight matrix `W` directly, LoRA learns:
```
W' = W + B·A
```

Where:
- `W` is the frozen pre-trained matrix (size d×d)
- `B` is a d×r matrix
- `A` is an r×d matrix
- `r << d` (the "rank," typically 8, 16, 32, or 64)

**Example for a 4096×4096 matrix:**
- Full fine-tuning: 16.7 million trainable parameters
- LoRA with r=16: 2 × 4096 × 16 = 131,072 parameters (0.8% of full!)

**Why low-rank works:** Pre-trained weights have a low "intrinsic dimension." The meaningful changes needed for adaptation live in a low-dimensional subspace. LoRA finds that subspace instead of searching the entire parameter space.

---

### Real-Life Analogy

A massive symphony orchestra has been playing classical music for years. Now they need to learn jazz. Instead of retraining every musician from scratch (full fine-tuning), the conductor hands out small "style cards" to each section:
- Strings: "Swing the eighth notes"
- Brass: "Add growl on long notes"
- Rhythm: "Walk the bass line"

These cards are tiny — a few pages versus reprinting the entire orchestral library. The core skills (reading music, playing in tune, ensemble balance) remain unchanged. Only the style adapter is new. And if the orchestra wants to switch to rock tomorrow, they just swap the cards.

---

### Tiny Numeric Example

**Base weight matrix:** `W = [[2.0, 1.0], [0.5, 1.5]]` (frozen)

**LoRA rank r = 1:**
```
B = [[0.3],     (2×1)
     [0.1]]

A = [[0.2, 0.4]]   (1×2)
```

**Compute BA:**
```
BA = B · A = [[0.3],    · [[0.2, 0.4]]
              [0.1]]

   = [[0.3×0.2, 0.3×0.4],
       [0.1×0.2, 0.1×0.4]]

   = [[0.06, 0.12],
       [0.02, 0.04]]
```

**Updated weights:**
```
W' = W + BA
   = [[2.0, 1.0],    + [[0.06, 0.12],
       [0.5, 1.5]]       [0.02, 0.04]]

   = [[2.06, 1.12],
       [0.52, 1.54]]
```

**Parameter count:**
- Full W: 4 parameters (all trainable)
- LoRA: B has 2, A has 2 → 4 parameters total
- With r=1 and d=2, LoRA has the same count. But with d=1000 and r=8, LoRA uses only 2 × 1000 × 8 = 16,000 parameters versus 1,000,000 for full W.

---

### Common Confusion

1. **"LoRA reduces inference memory."** Not by default. At inference, you still load the base model plus the adapters. However, you can **merge** the adapter into the base weights (`W_merged = W + BA`) for zero inference overhead. QLoRA reduces training memory, not inference memory.

2. **"Higher rank is always better."** Often r=64 matches or exceeds r=256. Low rank acts as regularization — it prevents overfitting by constraining the search space. The sweet spot is usually r=8 to r=64.

3. **"LoRA is only for language models."** No. LoRA works for any model with linear layers: diffusion models (custom Stable Diffusion styles), vision transformers (domain adaptation), speech models, and more.

4. **"LoRA can change the model's core knowledge."** Not easily. LoRA adapts style, format, and shallow behaviors. If you need to teach the model completely new facts or change its reasoning deeply, full fine-tuning may still be necessary.

5. **"You must apply LoRA to every layer."** No. Applying LoRA only to the Query and Value projection matrices in attention often gives 90% of the quality with 50% of the adapter parameters. This is the most common configuration.

---

### Where It Is Used in Our Code

`src/phase35/phase35_lora.py` — Demonstrates a frozen base linear model and a tiny LoRA adapter (rank=2) that adapts it to new data. Compares trainable parameter counts and shows merging at inference.
