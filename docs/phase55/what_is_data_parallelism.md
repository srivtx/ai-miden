## What Is Data Parallelism?

---

### The Problem

You have a huge dataset and a powerful GPU, but the GPU is sitting idle most of the time waiting for the next batch to load. Or worse, your batch is so large it does not fit in one GPU's memory. How do you train faster by using multiple GPUs at once?

---

### Definition

**Data parallelism** is the technique of splitting a training batch across multiple devices (GPUs), computing gradients independently on each device, then combining them to update a single shared model.

**How it works:**
```
1. Split batch of 1024 examples across 4 GPUs → 256 per GPU
2. Each GPU computes forward + backward pass on its 256 examples
3. Each GPU has its own gradient vector
4. All GPUs average their gradients (all-reduce)
5. Every GPU updates its copy of the model with the same averaged gradient
```

**Key insight:**
- 4 GPUs processing 256 examples each is mathematically equivalent to 1 GPU processing 1024 examples
- The only overhead is synchronizing gradients at the end of each step
- Linear speedup is possible if communication is fast

**Why this matters:**
- GPT-4 was trained on thousands of GPUs in parallel
- Without data parallelism, training would take years instead of months
- It is the simplest and most common form of distributed training

---

### Real-Life Analogy

A group of 4 students solving a math worksheet together.
- **Batch:** The worksheet has 40 problems
- **Data parallelism:** Each student solves 10 problems independently
- **Forward pass:** Student solves their 10 problems
- **Backward pass:** Student identifies which concepts they got wrong
- **All-reduce:** Students share their mistakes and agree on a single list of concepts everyone needs to review
- **Update:** All four students study the same concepts from the shared list
- **Result:** The worksheet is finished 4× faster, and everyone learns the same lessons

---

### Tiny Numeric Example

**Model:** `y = w × x` (single parameter w = 2.0)
**Loss:** MSE
**Batch:** 4 examples: [(x=1, y=2), (x=2, y=4), (x=3, y=6), (x=4, y=8)]
**2 GPUs:**

**GPU 1 gets first 2 examples:**
```
Example 1: pred = 2.0 × 1 = 2.0, loss = 0, grad = 0
Example 2: pred = 2.0 × 2 = 4.0, loss = 0, grad = 0
Local gradient on GPU 1: [0.0]
```

**GPU 2 gets last 2 examples:**
```
Example 3: pred = 2.0 × 3 = 6.0, loss = 0, grad = 0
Example 4: pred = 2.0 × 4 = 8.0, loss = 0, grad = 0
Local gradient on GPU 2: [0.0]
```

**All-reduce (average):**
```
Global gradient = (0.0 + 0.0) / 2 = 0.0
```

**Both GPUs update w:**
```
w = 2.0 - 0.1 × 0.0 = 2.0 (already optimal)
```

Now suppose w = 1.0 (wrong):

**GPU 1:**
```
Example 1: pred=1.0, loss=1.0, grad = -2.0
Example 2: pred=2.0, loss=4.0, grad = -4.0
Local gradient: (-2.0 + -4.0) / 2 = -3.0
```

**GPU 2:**
```
Example 3: pred=3.0, loss=9.0, grad = -6.0
Example 4: pred=4.0, loss=16.0, grad = -8.0
Local gradient: (-6.0 + -8.0) / 2 = -7.0
```

**All-reduce:**
```
Global gradient = (-3.0 + -7.0) / 2 = -5.0
```

**Single GPU with all 4 examples would also get -5.0.** Data parallelism is mathematically identical.

---

### Common Confusion

1. **"Data parallelism makes the batch size bigger."** No. The effective batch size is the same. The difference is that multiple GPUs process subsets simultaneously.

2. **"Each GPU trains a different model."** No. They train copies of the same model and synchronize gradients so all copies stay identical.

3. **"Data parallelism is only for GPUs."** It works on any device — CPUs, TPUs, even multiple machines in a cluster.

4. **"You get perfect linear speedup."** Rarely. Communication overhead (all-reduce) and data loading bottlenecks reduce speedup. 4 GPUs might give 3.5× speedup, not 4×.

5. **"Data parallelism solves the out-of-memory problem."** Partially. Each GPU still holds a full copy of the model. If the model itself is too large, you need model parallelism instead.

---

### Where It Is Used in Our Code

`src/phase55/phase55_distributed_training.py` — We simulate 4 workers processing data shards, computing local gradients, and performing all-reduce to synchronize. We show that distributed training matches single-GPU results.
