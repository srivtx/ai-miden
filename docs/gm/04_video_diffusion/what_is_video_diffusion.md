# What Is Video Diffusion?

**The Problem:** Image diffusion (Parts 2, 3) generates one frame at a time. For video, you need to generate $T$ frames that are *temporally coherent* — frame 2 must be a natural continuation of frame 1, with the same objects, the same lighting, and smooth motion. Independent image generation produces *flicker* — the cat moves discontinuously from frame to frame. Video diffusion fixes this by extending the architecture and training procedure to handle time.

**Definition:** *Video diffusion* is diffusion applied to a 4D tensor $(T, C, H, W)$ (time, channels, height, width) instead of a 3D tensor $(C, H, W)$. The U-Net has *temporal* layers (in addition to spatial layers) that mix information across frames. The training loss is the same as DDPM, just on videos instead of images.

**How It Works (Step-by-Step):**

1. **Architecture choice**: a 3D U-Net (or inflated 2D U-Net with temporal attention). Key components:
   - **Spatial convolutions**: process each frame independently (like image U-Net).
   - **Temporal convolutions or attention**: mix information across frames.
   - **Cross-attention** (for text): same as in latent diffusion.

2. **Forward process** (destruction):
   - Take a video $(x_0^1, x_0^2, \ldots, x_0^T)$ of $T$ frames.
   - Add Gaussian noise to each frame independently, all using the same noise schedule.
   - $x_t^i = \sqrt{\bar\alpha_t} x_0^i + \sqrt{1 - \bar\alpha_t} \epsilon^i$ for each frame $i$.
   - The "video at step $t$" is $(x_t^1, x_t^2, \ldots, x_t^T)$.

3. **Reverse process** (generation):
   - Start with noise video $(x_T^1, \ldots, x_T^T)$.
   - At each step, the U-Net predicts the noise for *all* frames jointly, using temporal attention to ensure consistency.
   - Denoise one step. Repeat for $T$ steps.

4. **Temporal attention** (the key innovation):
   - Standard self-attention: $Q, K, V$ are all projections of the same feature map, and the attention is over the spatial dimensions.
   - Temporal attention: $Q, K, V$ are projections of the same feature map, but the attention is over the *time* dimension.
   - Each time step attends to all other time steps in the video.
   - This is what makes the video coherent.

5. **Latent video**:
   - Compress each frame with a pretrained VAE.
   - Operate in latent space $(T, h, w, c)$.
   - Decompress at the end.

**Real-life analogy:** Video diffusion is like *animating a flipbook*. Each frame is a drawing. The artist must make each frame consistent with the last (same character, smooth motion). Temporal attention is like the artist looking at the previous frame while drawing the next one. Latent video is like working from a sketchbook first, then filling in detail.

**Tiny numeric example:**

A 16-frame video at 256x256x3:
- VAE compresses to (16, 32, 32, 4) = 65,536 values per time step.
- U-Net operates on this 4D tensor.
- Each forward pass costs ~16x more than an image U-Net.
- Sampling 1000 steps: 16x more expensive than Stable Diffusion.

**Common confusion:**

- "Video diffusion is a different model." No, the math is the same. The architecture has extra dimensions.
- "Temporal attention is the same as spatial attention." Almost. The difference: spatial attention lets a pixel attend to other pixels in the *same* frame. Temporal attention lets a frame attend to other frames (same location, different time).
- "Latent video compression includes time." Usually not. The VAE compresses space, not time. The temporal axis is preserved. This is because temporal compression would lose frame-level details.
- "Video diffusion is just image diffusion run multiple times." No, that produces flicker. The temporal layers are essential.
- "Video diffusion requires paired (text, video) data." Usually yes. The text is the prompt; the video is the target.
- "Video diffusion is slow." Yes, 16x-100x slower than image diffusion. The frontier is making it faster (e.g., distillation, consistency models, frame interpolation).

**Key properties:**

- **3D architecture**: time + space.
- **Temporal attention**: the key innovation.
- **Same loss as image DDPM**: just on videos.
- **Latent space**: VAE compresses space, time preserved.
- **Coherent motion**: through temporal attention.
- **Slow**: 16x-100x slower than image diffusion.

**Tech comparison:**

| Model | Latent? | Frames | Temporal | Open? |
|---|---|---|---|---|
| Make-A-Video | Yes | 16 | Attention | No |
| Imagen Video | Yes | 16+ | 3D U-Net | No |
| Sora | Yes | 100s | 3D U-Net | No (technical report) |
| Veo | Yes | 100s | 3D U-Net | No |
| Stable Video Diffusion | Yes | 14-25 | Inflation | Yes |
| Wan | Yes | 16-81 | 3D U-Net | Yes |
| CogVideoX | Yes | 49 | 3D U-Net | Yes |

**Connection to generative models:** Video diffusion is the *current* frontier. The math is the same as image diffusion; the engineering is what makes it hard. Major open challenges: data, compute, temporal coherence at long horizons, and physical consistency (objects should not spontaneously change color, etc.).
