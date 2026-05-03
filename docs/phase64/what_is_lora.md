## What Is LoRA?

---

### The Problem

You want to fine-tune a 7-billion-parameter model on your custom dataset. Full fine-tuning requires 28GB of GPU memory just for the gradients, plus the optimizer states. A consumer GPU has 8GB. How do you adapt a giant model to your task without retraining all its parameters?

---

### Definition

**LoRA (Low-Rank Adaptation)** is a parameter-efficient fine-tuning method that freezes the pre-trained model weights and injects trainable low-rank decomposition matrices into each layer. Instead of updating a `d×d` weight matrix, LoRA learns two smaller matrices `B×A` where `B` is `d×r` and `A` is `r×d`, with `r << d`.

**The LoRA formula:**
```
h = W_0 @ x + ΔW @ x
    where ΔW = B @ A

W_0: frozen pre-trained weights (d × d)
B: trainable matrix (d × r)
A: trainable matrix (r × d)
r: rank (typically 4-64)
```

**Key insight:**
- The pre-trained model `W_0` is frozen
- Only `B` and `A` are trained
- Number of trainable parameters: `2 × d × r` instead of `d × d`
- For `d=4096, r=16`: trainable params = 131K instead of 16.8M (128× reduction)

**Why this works:**
- Pre-trained weights already encode rich representations
- Fine-tuning only needs to steer these representations slightly
- Low-rank matrices can capture the necessary steering with few parameters
- The original model can be shared across many tasks, each with its own small LoRA adapter

**Why this matters:**
- Fine-tune a 7B model on a single consumer GPU (8GB)
- Train hundreds of task-specific adapters without storing hundreds of full models
- Switch tasks by swapping small adapter files (MBs, not GBs)
- The base model stays intact; adapters can be merged or removed

---

### Real-Life Analogy

A master chef's kitchen.
- **Full fine-tuning:** You rebuild the entire kitchen for each cuisine. Italian kitchen, Japanese kitchen, Mexican kitchen — each costs $1M and takes months.
- **LoRA:** You keep the master chef's kitchen exactly as is. For Italian cuisine, you add a small spice rack and a pasta attachment. For Japanese cuisine, you add a sushi knife set and a rice cooker. Each attachment costs $100 and takes an hour to install. The core kitchen is untouched.
- **Switching tasks:** To switch from Italian to Japanese, you swap the spice rack for the knife set. The kitchen itself never changes.
- **Sharing:** The master kitchen (base model) is shared across all restaurants. Each restaurant only maintains its own small attachment (LoRA adapter).

---

### Tiny Numeric Example

**Pre-trained weight:** `W_0 = [[1.0, 0.5], [0.5, 1.0]]` (2×2, frozen)

**LoRA with rank r=1:**
```
B = [[b1], [b2]]   (2×1)
A = [[a1, a2]]     (1×2)
ΔW = B @ A = [[b1×a1, b1×a2],
              [b2×a1, b2×a2]]
```

**Input:** `x = [1.0, 0.0]`

**Without LoRA:**
```
h = W_0 @ x = [1.0, 0.5]
```

**With LoRA (initialized B=0, A random):**
```
B = [[0.0], [0.0]]
ΔW = [[0.0, 0.0], [0.0, 0.0]]
h = W_0 @ x + ΔW @ x = [1.0, 0.5] + [0.0, 0.0] = [1.0, 0.5]
```

**After training (B and A learned):**
```
B = [[0.1], [0.2]]
A = [[0.3, 0.4]]
ΔW = [[0.03, 0.04], [0.06, 0.08]]
h = [1.0, 0.5] + [0.03, 0.06] = [1.03, 0.56]
```

The change is small but directional. LoRA steers the output without changing `W_0`.

---

### Common Confusion

1. **"LoRA is just adding layers."** No. It decomposes the weight update into low-rank matrices. The architecture stays the same; only the weight computation changes.

2. **"Lower rank is always better."** Lower rank means fewer parameters but less capacity. For complex tasks, r=64 may be needed. For simple tasks, r=4 may suffice.

3. **"LoRA can only be applied to linear layers."** Originally yes, but variants like LoRA-FA, DoRA, and QLoRA extend it to convolutions, embeddings, and quantized models.

4. **"LoRA and full fine-tuning give the same quality."** Usually close, but full fine-tuning can still win on complex tasks. LoRA is a cost-quality trade-off.

5. **"You need to store W_0 + B + A."** Yes, but `B @ A` is tiny. During inference, you can merge: `W = W_0 + B @ A` and run with no overhead.

---

### Where It Is Used in Our Code

`src/phase64/phase64_sft_lora.py` — We simulate LoRA by freezing a base weight matrix and training two low-rank matrices to minimize loss on a toy task, showing how few parameters are needed to adapt the model.

`src/phase64/phase64_sft_lora_colab.py` — We fine-tune GPT-2/TinyLlama with real LoRA using `peft` and `transformers`, showing the exact command sequence for production fine-tuning.
