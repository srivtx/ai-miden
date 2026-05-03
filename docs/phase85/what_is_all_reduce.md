## What Is All-Reduce?

---

### The Problem

In data-parallel training, each GPU processes a different slice of the batch and computes its own local gradients. If each GPU updated its weights using only its own gradients, the model copies would diverge after a single step. You need every GPU to end up with the same gradient values -- the average (or sum) of all local gradients -- so that all model replicas stay synchronized. All-reduce is the collective communication operation that accomplishes this efficiently.

---

### Definition

**All-reduce** is a collective operation where every participating process (rank) starts with a tensor of values and ends with the same tensor containing the sum (or average) of all input tensors across all ranks.

**How it works:**
```
Four GPUs, one scalar gradient each:

Initial:  Rank 0: 2.0, Rank 1: 4.0, Rank 2: 6.0, Rank 3: 8.0

Ring-allreduce (sum):
  Phase 1 - Reduce-scatter: each rank accumulates one chunk
  Phase 2 - All-gather: every rank receives all completed chunks

Final:    Rank 0: 20.0, Rank 1: 20.0, Rank 2: 20.0, Rank 3: 20.0

Average (optional): divide by 4 -> every rank has 5.0
```

**Key algorithms:**
- **Ring-allreduce:** ranks form a ring and pass chunks to their neighbor. Bandwidth-optimal because every link is fully utilized.
- **Tree-allreduce:** organizes ranks into a binary tree. Lower latency for small tensors but more complex.
- **NCCL:** NVIDIA's highly optimized library that implements these algorithms in CUDA.

**Why this matters:**
- For a 1-billion-parameter model, all-reduce must move 4 GB of gradients per step.
- The efficiency of all-reduce often determines whether distributed training scales linearly or hits a wall.

---

### Real-Life Analogy

Four friends split a restaurant bill calculation. Each friend computes the subtotal for their own dishes. Instead of one friend collecting all receipts, adding them up, and shouting the total -- which creates a central bottleneck and noise -- they pass papers around the table. Each person adds their number to the paper they receive. After three passes, everyone has the full total. All-reduce is that passing process.

The trade-off is that passing papers takes time. If the bill is tiny, the overhead of organizing the paper pass is ridiculous; it would be faster for one person to just add four numbers. Similarly, for very small tensors, the latency of setting up all-reduce dominates, and data parallelism becomes inefficient. For large models with billions of parameters, however, the bandwidth-optimal ring algorithm wins because the communication time is dominated by moving bytes, not by setup overhead.

---

### Tiny Numeric Example

Four GPUs compute gradients for a single weight parameter:

| Rank | Local Gradient | After All-Reduce (Sum) | After Average |
|---|---|---|---|
| 0 | 2.0 | 20.0 | 5.0 |
| 1 | 4.0 | 20.0 | 5.0 |
| 2 | 6.0 | 20.0 | 5.0 |
| 3 | 8.0 | 20.0 | 5.0 |

Sum = 2.0 + 4.0 + 6.0 + 8.0 = 20.0.
Average = 20.0 / 4 = 5.0.

All four GPUs now update their local weights using the exact same gradient (5.0), ensuring the model replicas remain identical. If they had used only local gradients, the models would diverge: GPU 0 would step by 2.0, GPU 1 by 4.0, and so on.

---

### Common Confusion

1. **"All-reduce is the same as reduce."** No. Reduce sends the final result to one rank. All-reduce sends the final result to all ranks simultaneously.

2. **"All-reduce is a point-to-point operation."** No. It is a collective operation; every rank must call it at the same time, or the program deadlocks.

3. **"The result is different on each rank."** No. By definition, all ranks receive the identical reduced result.

4. **"Bandwidth doesn't matter for all-reduce."** It matters enormously. For large models with billions of parameters, all-reduce can consume 20-50% of training time on slow networks.

5. **"All-reduce is only for gradients."** It is also used for averaging metrics, distributed embeddings, and any synchronized state across ranks.

6. **"All-reduce and all-gather are the same."** No. All-reduce sums values element-wise. All-gather concatenates tensors so every rank gets the full concatenated result.

---

### Where It Is Used in Our Code

`src/phase85/phase85_multi_node.py` -- We simulate ring-allreduce on a small tensor across four conceptual ranks. We show how the tensor is chunked and how each chunk accumulates contributions from every rank until all ranks hold the final summed tensor.
