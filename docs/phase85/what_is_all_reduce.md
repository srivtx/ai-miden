# What Is All-Reduce?

## 1. Why it exists (THE PROBLEM first)

In data-parallel training, each GPU processes a different slice of the batch and computes its own local gradients. If each GPU updated its weights using only its own gradients, the model copies would diverge. You need every GPU to end up with the same gradient values—the average (or sum) of all local gradients. All-reduce is the collective communication operation that accomplishes this efficiently.

## 2. Definition

**All-reduce** is a collective operation where every participating process (rank) starts with a tensor of values and ends with the same tensor containing the sum (or average) of all input tensors across all ranks.

## 3. Real-life analogy

Four friends split a restaurant bill calculation. Each friend computes the subtotal for their own dishes. Instead of one friend collecting all receipts, adding them up, and shouting the total (which creates a bottleneck), they pass papers around the table. Each person adds their number to the paper they receive. After three passes, everyone has the full total. All-reduce is that passing process.

## 4. Tiny numeric example

Four GPUs compute gradients for a single weight:

- Rank 0 gradient: 2.0
- Rank 1 gradient: 4.0
- Rank 2 gradient: 6.0
- Rank 3 gradient: 8.0

After all-reduce(sum), every rank has: 2.0 + 4.0 + 6.0 + 8.0 = 20.0.

After dividing by 4 (average), every rank has: 5.0.

All four GPUs now update their local weights using the exact same gradient.

## 5. Common confusion

- **"All-reduce is the same as reduce."** No. Reduce sends the final result to one rank. All-reduce sends the final result to **all** ranks.
- **"All-reduce is a point-to-point operation."** No. It is a collective operation; every rank must call it simultaneously.
- **"The result is different on each rank."** No. By definition, all ranks receive the identical reduced result.
- **"Bandwidth doesn't matter for all-reduce."** It matters enormously. For large models with billions of parameters, all-reduce can consume a significant fraction of training time.
- **"All-reduce is only for gradients."** It is also used for averaging metrics, distributed embeddings, and any synchronized state.
- **"All-reduce and all-gather are the same."** No. All-reduce sums values. All-gather concatenates tensors so every rank gets the full concatenated result.

## 6. Where it is used in our code

In `src/phase85/phase85_multi_node.py`, we simulate ring-allreduce on a small tensor across four conceptual ranks. We show how the tensor is chunked and how each chunk accumulates contributions from every rank until all ranks hold the final summed tensor.
