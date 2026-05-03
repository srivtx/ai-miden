## What Is Adapter Merging?

---

### The Problem

You have deployed a LoRA adapter alongside your base model. At every forward pass, the model computes `W' = W + BA`. This adds a small matrix multiplication — not huge, but not zero either. If you are serving millions of requests per day, that overhead adds up. Can you eliminate the adapter cost at inference time?

---

### Definition

**Adapter merging** (or **adapter fusion**) combines the LoRA update into the base weights before inference:
```
W_merged = W + BA
```

After merging:
- The model has the exact same architecture as the base model
- No extra matrix multiplications at inference
- Zero latency overhead
- The adapter can no longer be "removed" without keeping a backup of W

**Multi-adapter merging:**
If you have multiple adapters for different tasks, you can merge them all into one set of weights, or keep the base model and swap merged weights per task.

**Task arithmetic:**
Some research shows you can add or subtract adapter updates:
```
W_chat = W + B_chat·A_chat
W_coding = W + B_coding·A_coding
W_chat_coding = W + B_chat·A_chat + B_coding·A_coding
```
This sometimes creates a blended behavior without retraining.

---

### Real-Life Analogy

A restaurant with a standard menu (base model) and daily specials written on a chalkboard (LoRA adapter). During service, chefs constantly glance at the chalkboard to modify standard dishes. This works but adds friction.

**Merging:** The owner prints a new permanent menu that includes the most popular daily specials. The chalkboard is erased. Service is faster because chefs do not need to cross-reference. But if customers want the old standard dish, it is gone unless the owner kept a copy of the old menu.

---

### Tiny Numeric Example

**Base weights:**
```
W = [[2.0, 1.0],
     [0.5, 1.5]]
```

**LoRA adapter (r=1):**
```
B = [[0.3],
     [0.1]]

A = [[0.2, 0.4]]

BA = [[0.06, 0.12],
      [0.02, 0.04]]
```

**Before merging (inference with adapter):**
```
forward(x):
  y1 = W · x        # base computation
  y2 = B · (A · x)  # adapter computation
  return y1 + y2    # two matrix multiplications
```

**After merging:**
```
W_merged = [[2.06, 1.12],
            [0.52, 1.54]]

forward(x):
  return W_merged · x  # single matrix multiplication
```

**Computational cost:**
- Before: d×d + 2×d×r operations
- After: d×d operations
- For r << d, the savings are small per layer but add up across all layers and millions of requests.

---

### Common Confusion

1. **"Merging loses the base model."** Only if you overwrite W in-place. In practice, you save `W_merged` as a separate checkpoint. The original base model and adapter remain available if needed.

2. **"Merging multiple adapters is the same as training one multi-task adapter."** Not exactly. Adding adapter updates (`W + BA1 + BA2`) can work, but the updates may interfere (one adapter's change might undo another's). Task arithmetic is an active research area.

3. **"Merging is mandatory for deployment."** No. Many production systems keep adapters separate to enable runtime task switching. Merging is an optimization for latency-critical deployments with a fixed task.

4. **"Merged weights are larger than base + adapter."** No. Merged weights are exactly the same size as the base model. The adapter is "absorbed" into the weights.

5. **"You can un-merge after merging."** Only if you saved W and the adapter separately. If you only kept W_merged, you cannot recover the original base model behavior without retraining or reloading from checkpoints.

---

### Where It Is Used in Our Code

`src/phase35/phase35_lora.py` — Demonstrates merging the trained adapter into the base weights. The script compares inference with separate W and BA versus merged W_merged, showing identical outputs.
