# What Is Temporal Attention?

**The Problem:** A 3D U-Net has 3D convolutions, which mix information across space and time within a small receptive field. But motion is *long-range*: a cat at frame 1 is at frame 16 in a different position. The 3D convolution can only "see" a few frames around the current one. To capture long-range temporal dependencies, you need *attention* over the time axis.

**Definition:** *Temporal attention* is a self-attention layer where the query, key, and value come from the same feature map, but the *sequence* dimension is *time* (not space). Each time step attends to all other time steps. This is the key component of modern video diffusion (Sora, Veo, Stable Video Diffusion, etc.).

**How It Works (Step-by-Step):**

1. **Standard self-attention** (in image U-Net):
   - Input: feature map $(B, C, H, W)$.
   - Reshape to $(B, HW, C)$ — flatten spatial dimensions into a sequence.
   - $Q, K, V$ are linear projections.
   - Attention: $\text{softmax}(Q K^T / \sqrt{d_k}) V$. Each "pixel" attends to all other "pixels" in the same image.
   - This is *spatial* self-attention.

2. **Temporal attention** (in video U-Net):
   - Input: feature map $(B, T, C, H, W)$.
   - Reshape to $(B \cdot H \cdot W, T, C)$ — flatten spatial + batch into a sequence, with time as the sequence dimension.
   - $Q, K, V$ are linear projections.
   - Attention: $\text{softmax}(Q K^T / \sqrt{d_k}) V$. Each "spatial location" attends to all other "time steps" at the *same* spatial location.
   - This is *temporal* self-attention.

3. **Combined spatial + temporal attention**:
   - In each transformer block, do spatial self-attention, then temporal self-attention.
   - Sometimes interleaved: spatial-then-temporal, repeated.

4. **Cross-frame conditioning** (in some models):
   - In addition to temporal self-attention, condition each frame on the previous frame.
   - Implemented as: $K, V$ from previous frame; $Q$ from current frame. The current frame "looks at" the previous frame.
   - This is a form of cross-attention.

**Why temporal attention is critical:**

- 3D convolutions have small temporal receptive fields.
- Temporal attention has *global* temporal receptive fields.
- Without it, the model can't capture long-range motion (e.g., a 10-frame walk cycle).
- With it, the model can: a cat at frame 1 is "linked" to a cat at frame 16, and the features are consistent.

**Real-life analogy:** Temporal attention is like an *editor* watching a rough cut of a video. They look at every frame and ensure consistency: "this object was on the left in frame 5 and now it's on the right in frame 10, so there should be smooth motion in between." They attend to *all* frames simultaneously.

**Tiny numeric example:**

For a 16-frame video at 32x32 latent resolution with 320 channels:
- Spatial attention: each pixel attends to 32*32 = 1024 other pixels in the same frame.
- Temporal attention: each pixel attends to 16 time steps (one per frame).
- Combined: each pixel attends to 1024*16 = 16,384 other pixels across all frames.

The cost is high but tractable for 16 frames at 32x32.

**Common confusion:**

- "Temporal attention is the same as cross-attention with a frame." Almost. Cross-attention has $K, V$ from a different source. Temporal self-attention has $K, V, Q$ all from the same video. Cross-frame attention is a special case where $K, V$ are from a specific frame.
- "Temporal attention replaces 3D convolution." No, both are used. 3D convolution captures *local* temporal dependencies (3-5 frames). Temporal attention captures *global* dependencies (any distance).
- "Temporal attention is expensive." $O(T^2)$ per layer. For $T = 16$, this is 256 attention scores. For $T = 100$, it's 10,000. Memory becomes a constraint.
- "Temporal attention requires no special tricks." In practice, several tricks are used: sparse attention (attend only to nearby frames), shifted windows (à la Swin), or factorized attention (time first, then space).
- "Temporal attention is the same as the time embedding." No. The time embedding is a global vector that conditions the U-Net. Temporal attention is a per-spatial-location attention over the time dimension.

**Key properties:**

- **Global temporal receptive field**: each time step sees all others.
- **Quadratic in time**: $O(T^2)$ attention.
- **Combined with spatial attention**: usually interleaved.
- **Critical for temporal coherence**: without it, the model produces flicker.
- **Memory-intensive**: for long videos, requires tricks.

**Tech comparison:**

| Method | Temporal | Local? | Global? | Cost |
|---|---|---|---|---|
| 3D conv | Yes | Yes | No | Linear |
| Temporal attention | Yes | No | Yes | Quadratic |
| Recurrent | Yes | Yes | No | Linear |
| Shifted window | Yes | Yes | Yes (within window) | Linear |
| Sparse attention | Yes | Yes | Yes (sparse) | Sub-quadratic |

**Connection to generative models:** Temporal attention is the *key innovation* of modern video diffusion. It is what makes the difference between "stitching together image samples" and "generating a coherent video." The cost is significant, which is why video generation is slower and more expensive than image generation.
