# What Is Gradient Accumulation?

## 1. Why it exists (THE PROBLEM first)

Large batch sizes lead to more stable gradients and better convergence, but they require more GPU memory because the forward and backward passes process more samples at once. If your GPU can only fit batch size 8, but you need the statistical benefit of batch size 32, you have a problem. Gradient accumulation solves this by splitting the large batch into smaller "micro-batches" that fit in memory.

## 2. Definition

**Gradient accumulation** is the technique of running multiple forward/backward passes on small micro-batches, adding (accumulating) the gradients together, and only updating the model weights after the final micro-batch. This simulates training on a larger batch size without requiring the memory for the full batch at once.

## 3. Real-life analogy

Imagine you want to know the average opinion of 32 people, but you can only talk to 8 people at a time. You talk to the first 8 and write down their opinions. Then you talk to the next 8 and add their opinions to your notes. You repeat until all 32 are accounted for, then you compute the final average and make your decision. You never held all 32 conversations simultaneously, but your final decision is based on all 32.

## 4. Tiny numeric example

Effective batch size = 32, micro-batch size = 8, accumulation steps = 4.

Step 1: Forward/backward on samples 0-7. Gradients = g1. Weights NOT updated.
Step 2: Forward/backward on samples 8-15. Gradients = g2. Accumulate: g_total = g1 + g2.
Step 3: Forward/backward on samples 16-23. Gradients = g3. Accumulate: g_total += g3.
Step 4: Forward/backward on samples 24-31. Gradients = g4. Accumulate: g_total += g4.
Optimizer step: weights = weights - lr * (g_total / 4).

The weight update is identical (up to normalization) to processing all 32 at once.

## 5. Common confusion

- **"Gradient accumulation is exactly the same as a real large batch."** Almost, but not perfectly. Layers like batch normalization compute statistics per micro-batch, not the full batch, which changes behavior slightly.
- **"It reduces total compute time."** No. You still run forward/backward on every sample. The total compute is the same; only memory is saved.
- **"It helps reduce activation memory per step."** It reduces memory per micro-batch, but the total number of steps increases proportionally.
- **"You should keep the same learning rate."** Usually you scale the learning rate with the effective batch size, just as you would with a true large batch.
- **"Gradient accumulation is the same as gradient clipping."** No. Clipping limits the magnitude of gradients. Accumulation sums gradients across steps.
- **"It requires multiple GPUs."** No. Gradient accumulation works on a single GPU. It is different from distributed data parallelism.

## 6. Where it is used in our code

In `src/phase84/phase84_memory_engineering.py`, we demonstrate the concept of gradient accumulation by simulating a large effective batch size built from smaller micro-batches. We explain how gradients are summed across steps before the optimizer updates weights.
