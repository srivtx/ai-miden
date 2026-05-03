# What Is Data Parallelism?

## 1. Why it exists (THE PROBLEM first)

Training on a single GPU is slow. If you have 4, 8, or 1000 GPUs, you want to use all of them. But simply buying more GPUs does not make training faster unless you can split the work across them. Data parallelism is the simplest way to scale: give every GPU the same model but a different slice of the data.

## 2. Definition

**Data parallelism** is a distributed training strategy where the model is replicated on every GPU (or node), and the training batch is split across them. After each backward pass, gradients are synchronized (typically via all-reduce) so all model copies remain identical.

## 3. Real-life analogy

A teacher gives the same textbook to four students and asks them to summarize it. Each student reads one chapter (a data slice). They then share their notes in a group chat (all-reduce) so everyone has the same complete summary. The textbook (model) is identical for all students; only the reading assignment (data) differs.

## 4. Tiny numeric example

Global batch size = 256, 4 GPUs.

- GPU 0 processes samples 0-63, computes loss, computes gradients g0.
- GPU 1 processes samples 64-127, computes loss, computes gradients g1.
- GPU 2 processes samples 128-191, computes loss, computes gradients g2.
- GPU 3 processes samples 192-255, computes loss, computes gradients g3.

All-reduce averages gradients: g_avg = (g0 + g1 + g2 + g3) / 4.

Each GPU updates its weights using g_avg. All four models stay in sync.

Training throughput is approximately 4x faster (minus communication overhead).

## 5. Common confusion

- **"Data parallelism shards the model."** No. The full model is copied to every GPU. Model sharding is called model parallelism or pipeline parallelism.
- **"You can use different models on each GPU."** No. All copies must be identical, or the all-reduce step makes no sense.
- **"Data parallelism reduces per-GPU memory."** No. Each GPU still holds the full model, full optimizer state, and its slice of activations. It does not help with model size.
- **"Batch normalization works automatically."** No. Batch norm statistics must be synchronized across GPUs, or you must use alternatives like SyncBatchNorm.
- **"Data parallelism is the only form of distributed training."** No. Model parallelism, pipeline parallelism, and tensor parallelism are alternatives for models too large for one GPU.
- **"Global batch size is the per-GPU batch size."** No. Global batch size = per-GPU batch size * number of GPUs.

## 6. Where it is used in our code

In `src/phase85/phase85_multi_node.py`, we simulate four ranks each holding a different local gradient tensor. We perform a ring-allreduce to synchronize them, which is the core communication pattern underlying data parallelism.
