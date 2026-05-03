## What Is Activation Checkpointing?

---

### The Problem

During neural network training, the forward pass computes intermediate values called activations that are required by the backward pass to calculate gradients. For a deep network with large batch sizes, storing every layer's activations consumes gigabytes of GPU memory. Modern GPUs have limited memory (e.g., 24-80 GB). Without a way to reduce activation memory, you cannot train large models or use large batches, even if the model parameters themselves fit easily.

---

### Definition

**Activation checkpointing** (also called gradient checkpointing) is a training technique where only a subset of layer outputs is saved during the forward pass. The discarded activations are recomputed on-the-fly during the backward pass. It trades extra compute for reduced memory usage.

**How it works:**
```
Standard training:
  Forward: save activation after every layer
  Backward: use saved activations to compute gradients
  Memory: O(L) where L is number of layers

Checkpointed training:
  Forward: save activation only every N layers (checkpoints)
  Backward: when a discarded activation is needed, recompute forward from the nearest checkpoint
  Memory: O(sqrt(L)) or O(N) depending on strategy
  Compute: ~1.3-1.5x forward passes
```

**Key strategies:**
- **Full checkpointing:** save nothing during forward; recompute everything during backward. Minimal memory, maximum compute.
- **Selective checkpointing:** save every N layers or only expensive-to-recompute layers.
- **CPU offloading:** move checkpoints to host memory to free GPU memory entirely.

**Why this matters:**
- A 100-layer transformer with batch size 32 and sequence length 2048 can require 40 GB of activation memory.
- Checkpointing can cut that to 10 GB, allowing training on a single consumer GPU.
- The compute overhead is usually modest because forward passes are cheaper than backward passes.

---

### Real-Life Analogy

Imagine filming a complex cooking tutorial with hundreds of steps. Normally you film every single step so you can review any moment later during editing. But your camera only has 10 minutes of storage, and the tutorial takes an hour to cook. Instead, you film only the key milestones -- chopping the vegetables, seasoning the meat, and plating the dish -- and re-do the simple stirring steps when you need to review them during editing. You spend a little more time re-stirring, but you fit the whole tutorial in memory.

The trade-off is time versus storage. If you checkpoint too rarely, you spend so much time recomputing that the recipe takes twice as long. If you checkpoint too often, you run out of storage and gain nothing. The optimal checkpointing strategy depends on the complexity of each step and the cost of recomputing it. In deep learning, layers with expensive operations like attention benefit most from being checkpointed, while cheap element-wise layers can often be recomputed cheaply.

---

### Tiny Numeric Example

A network with 10 layers, batch size 32, hidden size 1024. Each activation tensor is 32 x 1024 floats at 4 bytes per float = 131 KB.

**Without checkpointing:**
| Layer | Saved Activations | Cumulative Memory |
|---|---|---|
| 1 | 131 KB | 131 KB |
| 2 | 131 KB | 262 KB |
| ... | ... | ... |
| 10 | 131 KB | **1.31 MB** |

**With checkpointing every 2 layers:**
| Checkpoint Layer | Saved Activations | Cumulative Memory |
|---|---|---|
| 2 | 131 KB | 131 KB |
| 4 | 131 KB | 262 KB |
| 6 | 131 KB | 393 KB |
| 8 | 131 KB | 524 KB |
| 10 | 131 KB | **655 KB** |

Peak activation memory drops by roughly half. During backward, if layer 7's activation is needed, the system recomputes the forward pass from checkpoint 6 to layer 7, uses the activation, and then discards it. The cost is approximately 1.5x total forward passes, but the memory savings often allow training with larger models or batches that would otherwise be impossible.

---

### Common Confusion

1. **"Checkpointing makes training faster."** No. It makes training slower because you recompute forward passes during backward. The benefit is lower memory usage, not speed.

2. **"Checkpointing reduces model parameter memory."** No. It only reduces activation memory. Model weights and optimizer states still occupy exactly the same space on the GPU.

3. **"Every layer can be checkpointed easily."** Most can, but some layers like batch normalization with running statistics need careful handling because recomputing changes the statistics.

4. **"Checkpointing is the same as model parallelism."** No. Model parallelism splits weights across multiple devices. Checkpointing keeps the full model on one device but saves less activation state.

5. **"You checkpoint during the backward pass."** No. The decision of which activations to keep is made during the forward pass. During backward, you recompute the missing ones from the saved checkpoints.

6. **"Checkpointing changes the final model."** No. The gradients are mathematically identical to standard training. Only the compute schedule and memory footprint change.

---

### Where It Is Used in Our Code

`src/phase84/phase84_memory_engineering.py` -- We simulate a tiny multi-layer network and compare peak activation memory with and without checkpointing. We show that storing every layer's output consumes linearly more memory, while checkpointing every N layers caps the storage at a fraction of the original, illustrating the compute-for-memory trade-off.
