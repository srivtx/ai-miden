## What Is Gradient Checkpointing?

---

### The Problem

During backpropagation, PyTorch needs to store intermediate activations (the outputs of each layer) to compute gradients. For a transformer with 32 layers and a batch size of 4, these activations can consume 20-40GB of GPU memory. You run out of VRAM before you even reach the optimizer states. You cannot increase batch size, sequence length, or model depth because the activations eat all the memory.

---

### Definition

**Gradient Checkpointing** is a memory optimization technique that trades compute for memory. Instead of storing all intermediate activations during the forward pass, it stores only a subset of "checkpoint" activations. During the backward pass, it recomputes the missing activations on-the-fly by re-running the forward computation of the segments between checkpoints.

**The trade-off:**
```
Standard training:
  Forward:  compute layer 1 → store a1 → compute layer 2 → store a2 → ... → store aN
  Backward: use aN → grad → use aN-1 → grad → ... → use a1 → grad
  Memory:   O(N) activations stored

Gradient checkpointing:
  Forward:  compute layer 1 → store a1 (checkpoint) → compute layer 2 → drop a2
            → ... → compute layer N → store aN (checkpoint)
  Backward: recompute layers k+1..N from checkpoint k → use aN → grad
            → recompute layers k+1..N-1 → use aN-1 → grad → ...
  Memory:   O(√N) or O(1) checkpoints stored (depends on strategy)
  Compute:  ~1.33× forward passes (one real, one recomputed)
```

**Key insight:**
- Memory for activations drops by 50-90%
- Forward pass time increases by ~20-30%
- Total training time increases by ~20-30%
- Enables training with 2-3× larger models or batch sizes

**Why this matters:**
- Train a 7B model on a 16GB GPU instead of 24GB
- Use batch size 4 instead of 1
- Process longer sequences without OOM

---

### Real-Life Analogy

Baking a multi-layer wedding cake.
- **Standard training:** You bake each layer, set it aside on the counter (store activation), frost it later. You need a huge kitchen with counters for all 32 layers. If your kitchen is small, you cannot bake a big cake.
- **Gradient checkpointing:** You bake a layer, take a quick photo of it (checkpoint), then throw the actual layer away to free counter space. When it is time to frost, you look at the photo, rebake just that layer from the recipe (recompute), frost it, and throw it away again. You rebake each layer multiple times, but you only need counter space for 2-3 layers at once.
- **Trade-off:** You use more oven time (compute) but need a much smaller kitchen (memory).

---

### Tiny Numeric Example

**A 3-layer network:**
```
x → [Layer 1] → a1 → [Layer 2] → a2 → [Layer 3] → a3 → loss
```

**Standard backprop memory (per sample):**
```
Store: a1 (100 floats), a2 (100 floats), a3 (100 floats)
Total: 300 floats × 4 bytes = 1,200 bytes
```

**With gradient checkpointing (checkpoint after Layer 1 only):**
```
Forward:  compute a1 → STORE a1 → compute a2 → DROP a2 → compute a3 → DROP a3
Backward:
  Step 1: Recompute a2, a3 from a1 and weights
          a1 → [Layer 2] → a2 → [Layer 3] → a3 → grad_w3, grad_w2
  Step 2: Use stored a1 → grad_w1
Memory: 100 floats (a1 only) × 4 bytes = 400 bytes  (3× reduction)
Extra compute: One extra forward pass of Layers 2-3
```

**For a 32-layer transformer:**
```
Standard:     store all 32 layer outputs  → 32 units of memory
Checkpoint every 4 layers: store 8 outputs  → 8 units of memory  (4× reduction)
Checkpoint every layer:    store 1 output   → 1 unit of memory   (32× reduction, max recompute)
```

---

### Common Confusion

1. **"Gradient checkpointing reduces model size."** No. It reduces activation memory, not parameter memory. The model weights still take the same space.

2. **"It makes training faster."** No. It makes training slower by ~20-30% because of recomputation. It lets you train larger models or use larger batches that would otherwise be impossible.

3. **"You only recompute the forward pass once."** No. During the backward pass, each checkpointed segment is recomputed as many times as needed to propagate gradients through it.

4. **"Gradient checkpointing is the same as gradient accumulation."** No. Gradient accumulation splits a large batch into micro-batches and averages gradients. Gradient checkpointing saves activation memory by recomputation. They are orthogonal and often used together.

5. **"It works automatically for any model."** In PyTorch, you must wrap segments with `torch.utils.checkpoint.checkpoint`. In HuggingFace Transformers, you call `model.gradient_checkpointing_enable()`. Custom architectures need manual annotation of checkpoint boundaries.

6. **"You should checkpoint every single layer."** Not always. The optimal checkpoint frequency balances memory savings against recompute cost. For transformers, checkpointing every transformer block is common.

7. **"Gradient checkpointing affects model convergence."** No. The gradients computed with checkpointing are mathematically identical to standard training (up to floating-point non-associativity). It is purely a systems optimization.

---

### Where It Is Used in Our Code

`src/phase65/phase65_qlora_colab.py` — We enable gradient checkpointing via `model.gradient_checkpointing_enable()` before training. This is critical because QLoRA already compresses model weights; without checkpointing, activations become the next memory bottleneck that causes OOM.
