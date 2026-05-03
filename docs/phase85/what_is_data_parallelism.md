## What Is Data Parallelism?

---

### The Problem

Training on a single GPU is slow. If you have 4, 8, or 1000 GPUs, you want to use all of them. But simply buying more GPUs does not make training faster unless you can split the work across them in a way that keeps every device busy. Data parallelism is the simplest way to scale: give every GPU the same model but a different slice of the data, then synchronize their learning.

---

### Definition

**Data parallelism** is a distributed training strategy where the model is replicated on every GPU (or node), and the training batch is split across them. After each backward pass, gradients are synchronized (typically via all-reduce) so all model copies remain identical.

**How it works:**
```
Global batch size = 256, 4 GPUs

GPU 0: processes samples 0-63, computes loss, computes gradients g0
GPU 1: processes samples 64-127, computes loss, computes gradients g1
GPU 2: processes samples 128-191, computes loss, computes gradients g2
GPU 3: processes samples 192-255, computes loss, computes gradients g3

All-reduce averages gradients: g_avg = (g0 + g1 + g2 + g3) / 4
Each GPU updates its weights using g_avg. All four models stay in sync.
```

**Key properties:**
- **Model replication:** every GPU holds the full model, full optimizer state, and its slice of activations.
- **Communication:** the only cross-GPU traffic is gradient synchronization, which happens once per step.
- **Throughput:** training throughput scales nearly linearly with the number of GPUs, minus communication overhead.

**Why this matters:**
- Data parallelism is the default scaling strategy for models that fit on a single GPU.
- It is simple to implement and requires no changes to model architecture.

---

### Real-Life Analogy

A teacher gives the same textbook to four students and asks them to summarize it. Each student reads one chapter (a data slice). They then share their notes in a group chat (all-reduce) so everyone has the same complete summary. The textbook (model) is identical for all students; only the reading assignment (data) differs. At the end, all four students have learned the same material.

The trade-off is communication cost. If the students spend more time texting notes than reading, adding more students slows everyone down. In deep learning, when models have billions of parameters, the gradient tensors are enormous. All-reducing them across many GPUs can take a significant fraction of each step, especially over slow networks. Data parallelism also does not help if the model itself is too large to fit on one GPU; you need model parallelism or pipeline parallelism instead.

---

### Tiny Numeric Example

Global batch size = 256, 4 GPUs, one weight parameter.

| GPU | Samples | Local Gradient | After All-Reduce (Average) |
|---|---|---|---|
| 0 | 0-63 | 2.0 | 5.0 |
| 1 | 64-127 | 4.0 | 5.0 |
| 2 | 128-191 | 6.0 | 5.0 |
| 3 | 192-255 | 8.0 | 5.0 |

The true gradient over all 256 samples is (2.0 + 4.0 + 6.0 + 8.0) / 4 = 5.0. After all-reduce, every GPU has this exact average and updates its local copy of the weight identically:

```
weight = weight - lr * 5.0
```

Training throughput is approximately 4x faster than a single GPU, minus the time spent in all-reduce communication. For a model with 1 billion parameters, all-reduce must move 4 GB of gradient data per step (1 billion floats * 4 bytes).

---

### Common Confusion

1. **"Data parallelism shards the model."** No. The full model is copied to every GPU. Model sharding is called model parallelism or pipeline parallelism.

2. **"You can use different models on each GPU."** No. All copies must be identical, or the all-reduce step makes no sense and the models would diverge.

3. **"Data parallelism reduces per-GPU memory."** No. Each GPU still holds the full model, full optimizer state, and its slice of activations. It does not help with model size; it helps with training speed.

4. **"Batch normalization works automatically."** No. Batch normalization statistics must be synchronized across GPUs, or you must use alternatives like SyncBatchNorm, because each GPU sees only a micro-batch.

5. **"Data parallelism is the only form of distributed training."** No. Model parallelism, pipeline parallelism, tensor parallelism, and sequence parallelism are alternatives for models too large for one GPU.

6. **"Global batch size is the per-GPU batch size."** No. Global batch size equals per-GPU batch size multiplied by the number of GPUs.

---

### Where It Is Used in Our Code

`src/phase85/phase85_multi_node.py` -- We simulate four ranks each holding a different local gradient tensor. We perform a ring-allreduce to synchronize them, which is the core communication pattern underlying data parallelism.
