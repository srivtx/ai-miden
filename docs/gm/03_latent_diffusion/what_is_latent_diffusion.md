# What Is Latent Diffusion (Stable Diffusion)?

**The Problem:** Vanilla DDPM (Part 2) runs the forward and reverse processes in *pixel space*. For a 256x256 image, that's 196,608 values per step. A diffusion model needs ~1000 steps to sample. So generating one image requires ~200 million U-Net operations. This is slow and expensive. The *latent diffusion* idea (Rombach et al. 2022) is to compress the image first, run diffusion in the compressed space, and decode back. Compression is 8x in each spatial dimension, so a 256x256 image becomes a 32x32x4 latent. The U-Net is 48x cheaper per step. The quality is preserved because the VAE encoder/decoder preserve the perceptually important information.

**Definition:** *Latent Diffusion Models* (LDMs), aka *Stable Diffusion*, are generative models that perform diffusion in a *learned latent space* instead of pixel space. They have three components:
1. **A pretrained VAE encoder** $E$: maps an image $x$ to a latent $z = E(x)$.
2. **A U-Net** $\epsilon_\theta$: a diffusion model in latent space, conditioned on text.
3. **A pretrained VAE decoder** $D$: maps a latent back to an image $\hat{x} = D(z)$.

The training loss is the same as DDPM, but on latents:
$$\mathcal{L} = \mathbb{E}_{x, t, \epsilon} \left[ \| \epsilon - \epsilon_\theta(z_t, t, c) \|^2 \right]$$
where $z_t = \sqrt{\bar\alpha_t} z_0 + \sqrt{1 - \bar\alpha_t} \epsilon$ and $c$ is the text conditioning.

**How It Works (Step-by-Step):**

1. **VAE training** (separate, before diffusion):
   - Train a VAE on images.
   - Encoder: image (256x256x3) -> latent (32x32x4).
   - Decoder: latent (32x32x4) -> image (256x256x3).
   - Loss: pixel MSE + perceptual loss + adversarial loss + KL.

2. **Text encoder** (separate, frozen):
   - Use a pretrained text model (CLIP, T5).
   - Text -> sequence of embeddings (e.g., 77 x 768).
   - Frozen during diffusion training.

3. **U-Net training** (the main training):
   - For each training step:
     a. Take a batch of images.
     b. Encode them to latents: $z_0 = E(x)$.
     c. Encode the captions: $c = \text{TextEncoder}(\text{caption})$.
     d. Sample $t \sim \text{Uniform}(1, T)$, $\epsilon \sim \mathcal{N}(0, I)$.
     e. Compute $z_t = \sqrt{\bar\alpha_t} z_0 + \sqrt{1 - \bar\alpha_t} \epsilon$.
     f. Predict $\hat\epsilon = \epsilon_\theta(z_t, t, c)$.
     g. Loss: $\| \hat\epsilon - \epsilon \|^2$.
     h. Backprop, update U-Net only.
   - The VAE and text encoder are frozen.

4. **Sampling** (text-to-image):
   - Encode the text prompt: $c = \text{TextEncoder}(\text{prompt})$.
   - Also encode a *null* prompt: $c_\emptyset$ (for classifier-free guidance).
   - Sample $z_T \sim \mathcal{N}(0, I)$.
   - For $t = T, T-1, \ldots, 1$:
     - Predict $\hat\epsilon_\emptyset = \epsilon_\theta(z_t, t, c_\emptyset)$ (unconditional).
     - Predict $\hat\epsilon_c = \epsilon_\theta(z_t, t, c)$ (conditional).
     - Combine: $\hat\epsilon = \hat\epsilon_\emptyset + w (\hat\epsilon_c - \hat\epsilon_\emptyset)$.
     - Denoise one step.
   - Decode: $\hat{x} = D(z_0)$.

**Key architectural choices:**

- **Spatial compression**: 8x (in each dimension). So 256x256 -> 32x32. Higher compression (e.g., 16x) is faster but loses detail.
- **Latent channels**: 4 (typical). Higher = more information, slower.
- **U-Net channels**: 320 to 1280 depending on layer.
- **Cross-attention**: at multiple resolutions (8x8, 16x16, 32x32) for text conditioning.
- **Time embedding**: sinusoidal, added to feature maps at every layer.

**Classifier-free guidance (Ho & Salimans 2022):**

The original way to condition was *classifier guidance* (Dhariwal & Nichol 2021): train a separate classifier on noisy images, use its gradients to push samples toward the desired class. This requires an extra network and is awkward.

Classifier-free guidance is simpler: train the model to be *both* conditional and unconditional. During training, drop the conditioning 10% of the time. During sampling, combine the two predictions.

The combination $\hat\epsilon = \hat\epsilon_\emptyset + w (\hat\epsilon_c - \hat\epsilon_\emptyset)$ is the key. The term $(\hat\epsilon_c - \hat\epsilon_\emptyset)$ is the *direction* toward the conditioning. Multiplying by $w$ and adding to $\hat\epsilon_\emptyset$ amplifies this direction.

Higher $w$ = more adherence to the prompt, but lower diversity. $w = 7.5$ is a common default.

**Real-life analogy:** Latent diffusion is like an *architect's workflow*. The architect draws a quick sketch (latent) and the draftsman adds detail (decoder). The draftsman is fixed (pretrained VAE); the architect learns to draw (U-Net). The customer describes what they want (text prompt), and the architect adjusts the sketch accordingly. Classifier-free guidance is like "make it more like what the customer said" — a parameter that amplifies the prompt's influence.

**Tiny numeric example:**

For a 256x256 image:
- VAE compresses to 32x32x4 = 4096 values.
- U-Net operates on 32x32x4 features with 320-1280 channels.
- 1000 steps * U-Net cost = total sample time.
- Decode: 32x32x4 -> 256x256x3.

Compare to pixel DDPM:
- U-Net on 256x256x3 = 196,608 values.
- 1000 steps.
- ~48x more expensive per step.

**Common confusion:**

- "Latent diffusion is a different model." No, it's *the same* DDPM loss and math, just in a different space.
- "The VAE is trained with the U-Net." No, the VAE is trained *separately* and frozen.
- "The text encoder is trained with the U-Net." No, it's also frozen (CLIP, T5, etc. are pretrained).
- "Latent diffusion is unconditional." No, the *original* LDM paper had unconditional and class-conditional variants. Stable Diffusion adds text conditioning via cross-attention.
- "Latent diffusion is faster than pixel DDPM." Yes, by ~48x in wall-clock time for the same image size.
- "Latent diffusion produces better images than pixel DDPM." Usually yes, because the VAE removes high-frequency noise that DDPM struggles to model.
- "Classifier-free guidance is always good." Not always. High $w$ produces "memorized" images (low diversity, low realism). $w = 5-7$ is typical.

**Key properties:**

- **3 components**: VAE encoder, U-Net, VAE decoder.
- **VAE trained separately** (perceptual + adversarial loss).
- **U-Net trained on latents**, not pixels.
- **Text conditioning** via cross-attention.
- **Classifier-free guidance** for prompt adherence.
- **48x faster** than pixel DDPM at the same resolution.
- **SOTA quality** on text-to-image benchmarks (COCO, FID, etc.).

**Tech comparison:**

| Model | Latent? | Text? | Speed | Quality |
|---|---|---|---|---|
| Pixel DDPM | No | No (originally) | Slow | Good |
| Classifier-guided | No | No (extra classifier) | Slow | Good |
| Latent diffusion (LDM) | Yes | Optional | Fast | Good |
| Stable Diffusion 1 | Yes | Yes | Fast | High |
| SDXL | Yes | Yes | Fast | Very high |
| SD3 / FLUX | Yes | Yes (T5 + CLIP) | Fast | Very high |

**Connection to generative models:** Latent diffusion is the *current* state of the art for text-to-image. Stable Diffusion 1, 2, 3, SDXL, FLUX, and most open-source text-to-image models use this architecture. The same idea extends to text-to-video (Part 4) and text-to-audio (MusicGen, AudioLDM, etc.).
