## What Is a Parallel Scan?

---

### The Problem

A selective SSM computes: `h_t = A_t·h_{t-1} + B_t·x_t`. Each state depends on the previous state. This looks sequential: you cannot compute h_3 until you have h_2. But GPUs are massively parallel. If we process one timestep at a time, we waste the GPU's power. How do you parallelize a sequential recurrence?

---

### Definition

A **parallel scan** (also called prefix sum or associative scan) is an algorithm that computes a sequence of dependent operations in parallel by exploiting the **associative property**.

For a simple recurrence like:
```
h_t = a_t · h_{t-1} + b_t
```

We can rewrite it as an **associative operator** on pairs `(a, b)`:
```
(a2, b2) ⊗ (a1, b1) = (a2·a1, a2·b1 + b2)
```

This operator is associative: `(c ⊗ b) ⊗ a = c ⊗ (b ⊗ a)`. Because it is associative, we can apply it in any order — including a tree-like parallel reduction.

**The algorithm:**
1. **Up-sweep (reduce):** Build a binary tree of partial results, bottom-up.
2. **Down-sweep (scan):** Distribute the accumulated results back down the tree.

This computes ALL h_t values in O(log N) parallel steps instead of O(N) sequential steps.

---

### Real-Life Analogy

A team of accountants computing the running total of daily sales for a year.

**Sequential approach:** One accountant adds January 1 + January 2 + January 3 ... all the way to December 31. Takes 365 steps.

**Parallel scan approach:**
- Accountant A adds Jan 1-15. Accountant B adds Jan 16-31. They do this simultaneously.
- Then accountant C adds A's total to B's total for the month.
- Meanwhile, other accountants do the same for February, March, etc.
- Finally, a tree of accountants combines monthly totals into running year-to-date totals.

The total work is the same (all numbers are still added), but the elapsed time drops from 365 steps to about log₂(365) ≈ 9 steps because many additions happen simultaneously.

---

### Tiny Numeric Example

**Recurrence:** h_t = a_t · h_{t-1} + b_t, with h_0 = 0

**Inputs:**
```
a = [2, 3, 4]
b = [1, 2, 3]
```

**Sequential computation:**
```
h_1 = 2·0 + 1 = 1
h_2 = 3·1 + 2 = 5
h_3 = 4·5 + 3 = 23
```

**Parallel scan (associative operator):**

First, convert each step to a pair (a_t, b_t):
```
Step 1: (2, 1)
Step 2: (3, 2)
Step 3: (4, 3)
```

**Up-sweep (tree reduction):**
```
Level 0 (pairs): (2,1), (3,2), (4,3)
Level 1 (combine adjacent):
  (3,2) ⊗ (2,1) = (3·2, 3·1 + 2) = (6, 5)
  (4,3) is alone at this level

Level 2 (combine):
  (4,3) ⊗ (6,5) = (4·6, 4·5 + 3) = (24, 23)
```

**Down-sweep (distribute prefixes):**
```
Prefix after step 1: (2, 1)  → h_1 = 1
Prefix after step 2: (6, 5)  → h_2 = 5
Prefix after step 3: (24, 23) → h_3 = 23
```

Same result, but the tree structure allows parallel computation.

---

### Common Confusion

1. **"Parallel scan is just batching."** No. Batching processes independent examples in parallel. A scan processes a single example's sequence in parallel by restructuring the computation.

2. **"Parallel scan changes the result."** No. The associative property guarantees the result is identical to sequential computation (up to floating-point rounding).

3. **"Parallel scan is only for SSMs."** No. It is a general algorithm used everywhere: prefix sums, cumulative products, dynamic programming on trees, and more. It is a fundamental parallel primitive.

4. **"Parallel scan is slower on short sequences."** Yes. For very short sequences (N < 100), the overhead of setting up the parallel tree can exceed the benefit. Mamba typically uses the scan for training on long sequences and falls back to simple recurrence for inference.

5. **"You need special hardware for parallel scan."** GPUs work well because the tree structure maps naturally to their thread hierarchy. But the algorithm works on any parallel architecture, including CPU vector instructions.

---

### Where It Is Used in Our Code

`src/phase34/phase34_mamba.py` — We do not implement the full parallel scan (that requires GPU kernels), but we demonstrate the recurrence and visualize how the state evolves. The Colab version uses PyTorch's scan primitives for true parallel training.
