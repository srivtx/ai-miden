## What Is Gradient Accumulation?

---

### The Problem

You want to train with a large batch size (e.g., 1024) because large batches give more stable gradients and better convergence. But your GPU can only fit 256 examples in memory at once. How do you simulate a large batch on limited hardware?

---

### Definition

**Gradient accumulation** is the technique of computing gradients on small batches sequentially, adding them up, and only updating model weights after processing enough small batches to equal the desired large batch size.

**How it works:**
```
Desired batch size: 1024
GPU memory limit: 256 per batch
Accumulation steps: 4

Step 1: Process 256 examples → compute gradients → add to accumulator
Step 2: Process 256 examples → compute gradients → add to accumulator
Step 3: Process 256 examples → compute gradients → add to accumulator
Step 4: Process 256 examples → compute gradients → add to accumulator
Update: Divide accumulated gradient by 4, apply to weights
Reset accumulator to zero
```

**Key insight:**
- The averaged gradient over 4 steps of 256 is identical to the gradient of 1 step of 1024
- Each forward/backward pass uses the same model weights (frozen during accumulation)
- Memory usage stays constant (only one small batch at a time)
- Trade-off: 4× more compute time, but same memory as batch size 256

**Why this matters:**
- Training GPT-3 used batch sizes of millions of tokens
- Consumer GPUs (RTX 4090: 24GB) cannot hold large batches
- Gradient accumulation is the standard workaround

---

### Real-Life Analogy

Paying off a large bill in installments.
- **Large batch (ideal):** Pay $1000 all at once. You get the full discount.
- **Limited memory:** Your wallet only holds $250.
- **Gradient accumulation:** Pay $250 today, $250 tomorrow, $250 the next day, $250 the day after. The vendor holds each payment. After 4 days, they average the payments and record one $1000 transaction.
- **Result:** You get the same discount as paying all at once, but you never needed more than $250 in your wallet at any time.

The catch: it takes 4 days instead of 1.

---

### Tiny Numeric Example

**Model:** `y = w × x` (w = 1.0)
**Loss:** MSE
**Desired batch:** 4 examples
**Memory limit:** 2 examples per batch
**Accumulation steps:** 2

**Examples:** [(1, 2), (2, 4), (3, 6), (4, 8)]

**Accumulation step 1 (examples 1-2):**
```
Example 1: pred=1.0, loss=1.0, grad = -2.0
Example 2: pred=2.0, loss=4.0, grad = -4.0
Local gradient: (-2.0 + -4.0) / 2 = -3.0
Accumulator: -3.0 (weights NOT updated)
```

**Accumulation step 2 (examples 3-4):**
```
Example 3: pred=3.0, loss=9.0, grad = -6.0
Example 4: pred=4.0, loss=16.0, grad = -8.0
Local gradient: (-6.0 + -8.0) / 2 = -7.0
Accumulator: -3.0 + -7.0 = -10.0
```

**Update (after 2 steps):**
```
Averaged gradient = -10.0 / 2 = -5.0
w = 1.0 - 0.1 × (-5.0) = 1.5
```

**Full batch of 4 would give:**
```
All grads: -2.0, -4.0, -6.0, -8.0
Mean: -5.0
w = 1.0 - 0.1 × (-5.0) = 1.5
```

**Identical result.** Gradient accumulation is mathematically exact.

---

### Common Confusion

1. **"Gradient accumulation reduces memory by storing fewer gradients."** No. It avoids storing the full batch's activations. Gradients are accumulated and discarded each step.

2. **"You update weights after every mini-batch."** No. Weights are frozen during accumulation. Only the accumulator changes.

3. **"Gradient accumulation speeds up training."** No. It slows down training (more forward/backward passes) but enables larger effective batch sizes.

4. **"Batch normalization works with gradient accumulation."** Tricky. BatchNorm statistics are computed per mini-batch, not the accumulated batch. Solutions: synchronized BatchNorm, LayerNorm, or GroupNorm.

5. **"You need special hardware for gradient accumulation."** No. It is pure software. Every framework supports it with a simple loop.

---

### Where It Is Used in Our Code

`src/phase55/phase55_distributed_training.py` — We demonstrate gradient accumulation by splitting a batch of 16 examples into 4 mini-batches of 4, accumulating gradients, and showing the update matches a full batch of 16.
