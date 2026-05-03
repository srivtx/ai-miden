## What Is Spatiotemporal Attention?

---

### The Problem

A video is not a stack of independent photographs. A cat jumping across a room appears in different pixel positions in consecutive frames, and the motion itself carries meaning. If a model treats each frame as an isolated image, it misses the jump. If it treats time as just another spatial axis, it violates causality — frame 10 should not influence frame 5 in a predictive model. How do you build an attention mechanism that respects both spatial relationships within a frame and temporal continuity across frames?

---

### Definition

**Spatiotemporal Attention** is an attention mechanism that operates jointly over space (height and width) and time (frames) in video data. It can be implemented as factorized attention (spatial attention within frames followed by temporal attention across frames) or as full 3D attention over a space-time volume. The goal is to let the model track objects and motions coherently while respecting temporal causality.

**How it works:**
```
Input: video tensor of shape (T, H, W, C)

Factorized spatiotemporal attention:
  Step 1 — Spatial attention:
    For each frame t, compute self-attention over all (H, W) positions.
    Captures: "What is in this frame?" (objects, background, layout)

  Step 2 — Temporal attention:
    For each spatial position (h, w), compute attention over all T frames.
    Captures: "How does this pixel change over time?" (motion, deformation)

  Result: each output token attends to relevant space-time neighbors.

Causal masking in temporal attention:
  Frame t can only attend to frames 0 ... t-1 (for prediction)
  Frame t can attend to all frames (for encoding)
```

**Key properties:**
- Factorization reduces complexity from O((T*H*W)^2) to O(T*(H*W)^2 + H*W*T^2).
- Positional encodings must include both spatial (x, y) and temporal (t) coordinates.
- Causal masking is essential for autoregressive video generation.

**Why this matters:**
- Full 3D attention over a 5-second 256x256 video at 30 fps would attend across 9.8 million tokens — intractable.
- Factorized spatiotemporal attention makes video transformers feasible.
- It is the backbone of latent video diffusion models and video understanding architectures.

---

### Real-Life Analogy

Imagine watching a tennis match. Your eyes do not treat every millisecond as an unrelated image. Instead, you perform two coupled operations. First, within each glance, you spatially attend: you track the ball, the players' positions, the court lines. You understand the layout of the scene. Second, across glances, you temporally attend: you notice that the ball moved from the server's racket to the opponent's backhand, and you predict where it will bounce next. Your understanding of the match depends on neither operation alone. Spatiotemporal attention is that dual-focus visual system: spatial attention answers "what," and temporal attention answers "what happens next."

The trade-off is between factorization and expressiveness. Factorized attention is efficient but assumes that spatial and temporal relationships are separable, which is not always true. A spinning ball deforms as it moves; its spatial appearance and temporal trajectory are coupled. Full 3D attention could capture this coupling but is computationally prohibitive for long videos. Modern architectures strike a balance by using factorized attention in early layers and limited 3D attention in deeper layers, or by using local space-time windows rather than global attention. There is no free lunch: every choice sacrifices some expressive power for tractability.

---

### Tiny Numeric Example

**Complexity of full 3D attention versus factorized:**
```
Video dimensions: 16 frames, 32x32 spatial resolution
Total tokens: 16 * 32 * 32 = 16,384

Full 3D attention:
  Attention matrix size: 16,384 x 16,384 = 268,435,456 entries
  Operations per layer: ~268 million

Factorized spatiotemporal attention:
  Spatial attention per frame: (32*32) x (32*32) = 1,024 x 1,024 = 1,048,576
  Over 16 frames: 16 * 1,048,576 = 16,777,216
  Temporal attention per pixel: 16 x 16 = 256
  Over 1,024 pixels: 1,024 * 256 = 262,144
  Total operations per layer: ~17 million

Speedup: 268M / 17M = 15.8x
```

**Memory usage comparison:**
```
Method                 | Attention Memory | Relative
-----------------------|------------------|----------
Full 3D attention      | 1,024 MB         | 16x
Factorized (spatial)   | 64 MB            | 1x
Factorized (temporal)  | 1 MB             | 0.02x
Factorized (total)     | 65 MB            | 1.01x
```

**The shift:** Factorization makes video transformers tractable. The 15.8x speedup means a model that would need a supercomputer can run on a single GPU, albeit with a slightly less expressive attention field.

---

### Common Confusion

1. **"Spatiotemporal attention is just attention with more tokens."** It is not merely scaling. The positional encodings, masking rules, and factorization strategy are specifically designed for the space-time structure of video. Treating time as an arbitrary token dimension breaks temporal coherence.

2. **"Factorized attention is always worse than full 3D attention."** Not necessarily. For many real-world videos, spatial and temporal correlations are approximately separable. Factorized attention can generalize better because it imposes a useful inductive bias.

3. **"Causal masking means the model cannot see the future."** Only in autoregressive generation. In video understanding tasks (classification, captioning), bidirectional temporal attention is standard and perfectly valid.

4. **"Spatiotemporal attention only applies to transformers."** The concept predates transformers. 3D convolutions are a form of spatiotemporal attention with fixed, local receptive fields. The attention mechanism generalizes this to dynamic, global receptive fields.

5. **"You need the same resolution in space and time."** No. Modern models often use patchified spatial tokens (e.g., 2x2 pixel patches) while keeping full temporal resolution, or they compress time with strided convolutions before applying attention.

6. **"Spatiotemporal attention solves the flickering problem."** It helps, but it does not guarantee temporal consistency. Additional mechanisms like temporal super-resolution, frame conditioning, and optical-flow losses are often needed.

7. **"It is only used for video generation."** It is also used for video understanding (action recognition, video question answering), motion forecasting, and even some audio-visual tasks where spectrograms have a time-frequency structure analogous to space-time.

---

### Where It Is Used in Our Code

`src/phase99/phase99_video_3d.py` — We simulate a 1D spatial signal evolving over time and apply a 2D convolution kernel over the space-time grid to produce a spatiotemporal feature map. We compare the shape and complexity of the input signal versus the feature map, and we illustrate how operating jointly over space and time extracts motion patterns that frame-independent processing would miss.
