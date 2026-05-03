# What Is Activation Checkpointing?

## 1. Why it exists (THE PROBLEM first)

During neural network training, the forward pass computes intermediate values (activations) that are required by the backward pass to calculate gradients. For a deep network with large batch sizes, storing every layer's activations consumes gigabytes of GPU memory. Modern GPUs have limited memory (e.g., 24-80 GB). Without a way to reduce activation memory, you cannot train large models or use large batches, even if the model parameters themselves fit easily.

## 2. Definition

**Activation checkpointing** (also called gradient checkpointing) is a training technique where only a subset of layer outputs is saved during the forward pass. The discarded activations are recomputed on-the-fly during the backward pass. It trades extra compute for reduced memory usage.

## 3. Real-life analogy

Imagine filming a complex cooking tutorial. Normally you film every single step so you can review any moment later. But your camera only has 10 minutes of storage. Instead, you film only the key milestones (chopping, seasoning, plating) and re-do the simple stirring steps when you need to review them. You spend a little more time re-stirring, but you fit the whole tutorial in memory.

## 4. Tiny numeric example

A network with 10 layers, batch size 32, hidden size 1024.

- Each activation tensor: 32 x 1024 floats x 4 bytes = 131 KB.
- Without checkpointing: store all 10 activations = 1.31 MB.

With checkpointing every 2 layers:
- Save activations at layers 2, 4, 6, 8, 10 = 5 tensors.
- During backward, recompute layers between checkpoints from the nearest saved activation.
- Peak activation memory: ~0.65 MB (half).

The cost: the forward pass conceptually runs 1.5x because portions are recomputed during backward.

## 5. Common confusion

- **"Checkpointing makes training faster."** No. It makes training slower because you recompute forward passes during backward. The benefit is lower memory.
- **"Checkpointing reduces model parameter memory."** No. It only reduces activation memory. Model weights and optimizer states still occupy the same space.
- **"Every layer can be checkpointed easily."** Most can, but some layers (like batch normalization with running statistics) need careful handling.
- **"Checkpointing is the same as model parallelism."** No. Model parallelism splits weights across devices. Checkpointing keeps the full model on one device but saves less activation state.
- **"You checkpoint during the backward pass."** No. The decision of which activations to keep is made during the forward pass. During backward, you recompute the missing ones.
- **"Checkpointing changes the final model."** No. The gradients are mathematically identical. Only the compute schedule changes.

## 6. Where it is used in our code

In `src/phase84/phase84_memory_engineering.py`, we simulate a tiny multi-layer network and compare peak activation memory with and without checkpointing. We show that storing every layer's output consumes linearly more memory, while checkpointing every N layers caps the storage.
