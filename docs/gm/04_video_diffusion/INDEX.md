# Part 4: Video Diffusion

> Adding a time axis to image diffusion. The key challenge: temporal coherence. Frame 2 must look like a continuation of frame 1, not a random sample from the image distribution. This requires 3D U-Nets, temporal attention, and careful architecture choices. This is the architecture behind Sora, Veo, Wan, and most modern text-to-video models.

---

## The files in this part

| File | One-line summary |
|---|---|
| `what_is_video_diffusion.md` | The extension from image to video. 3D U-Nets, temporal attention, latent video. |
| `what_is_temporal_attention.md` | How attention over the time axis gives temporal coherence. |

## The challenge: temporal coherence

Image diffusion generates each frame independently. This is fine for a single image but produces *flicker* in video — frame 2's cat is in a different pose, lighting, and position from frame 1's cat. The viewer's eye picks up the inconsistency immediately.

Video diffusion solves this by:
1. **Treating video as a 3D tensor** (time, height, width) instead of 2D (height, width).
2. **Adding temporal attention** to the U-Net so that features at time t can "see" features at t-1 and t+1.
3. **Joint training** on (frame, prev_frame) pairs so the model learns motion priors.

## The architectures

### 3D U-Net

The standard image U-Net is 2D (spatial only). For video, we have two options:
- **Inflated 2D U-Net**: take a 2D U-Net and inflate the convolutions to 3D (add a time axis). Cheap but limited.
- **Native 3D U-Net**: 3D convolutions throughout. More expressive, more expensive.

Most modern video diffusion uses inflated 2D U-Nets with explicit temporal attention layers.

### Temporal attention

The 2D U-Net has spatial self-attention. Add a parallel *temporal* self-attention: query, key, value all from the same frame, but the sequence dimension is *time* (not space). Each time step attends to all other time steps. This captures long-range temporal dependencies.

### Latent video

Following latent diffusion (Part 3):
- VAE compresses each frame to a latent.
- The U-Net operates on (time, h, w, c) latents.
- Compression factor: often (1, 8, 8) — no temporal compression, but 8x spatial.

This is the architecture of Stable Video Diffusion, Sora (according to the technical report), and Wan.

## The training data

Video models are data-hungry:
- 100M-1B video clips, each 1-30 seconds.
- Each clip has a caption (auto-generated or human-annotated).
- Total: 100M-10B (clip, caption) pairs.
- Storage: 100s of petabytes.

This is one reason why open-source video diffusion has lagged behind closed-source. Sora, Veo, and similar are trained on the largest video corpora ever assembled.

## The sampling

Once trained, sampling is the same as for image diffusion:
- Sample $z_T \sim \mathcal{N}(0, I)$ in latent space.
- Run reverse process for $T$ steps.
- Decode: $z_0 \to x_0$ is a video, frame by frame.

But there are extra tricks:
- **Frame interpolation**: at each denoising step, interpolate between adjacent frames. Improves smoothness.
- **Optical flow conditioning**: use optical flow to ensure motion is consistent across frames.
- **3D position encoding**: extend 2D positional encoding to 3D (time + space).

## Where this leads

After Part 4, you understand the *concepts* behind video diffusion. To build a real video model, you would need:
- A 3D U-Net implementation (e.g., in PyTorch).
- A pretrained image VAE (from Stable Diffusion).
- A pretrained text encoder (CLIP or T5).
- 100M+ video clips and 1000s of GPU-hours.
- A noise schedule tuned for video (often longer $T$).

The math is the same as image diffusion. The engineering is the hard part.
