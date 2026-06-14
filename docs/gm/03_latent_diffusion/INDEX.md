# Part 3: Latent Diffusion (Stable Diffusion)

> Vanilla DDPM works in pixel space, which is slow for high-resolution images. Latent diffusion (Rombach et al. 2022, the Stable Diffusion paper) compresses images to a smaller latent space with a VAE, runs diffusion in that space, and decodes back. This makes generation 10-100x faster, while preserving quality. It is the architecture of Stable Diffusion 1, 2, 3, SDXL, and most modern text-to-image models.

---

## The files in this part

| File | One-line summary |
|---|---|
| `what_is_latent_diffusion.md` | The full Stable Diffusion architecture: VAE encoder + U-Net + VAE decoder + text encoder. |
| `latent_diffusion.py` | The architecture skeleton, with a runnable U-Net that takes both image latents and text embeddings. |

## Why latent diffusion

Vanilla DDPM at 256x256 requires 50,000+ U-Net operations to sample one image. The bottleneck is the U-Net: it must process 256x256x3 = 196,608 values per step. The fix: don't run diffusion on pixels. Run it on a *compressed* representation.

The pipeline:
1. **VAE encoder**: image (256x256x3) -> latent (32x32x4). 48x compression.
2. **U-Net**: diffusion on the latent (32x32x4). 48x fewer values per step.
3. **VAE decoder**: latent (32x32x4) -> image (256x256x3).

The VAE encoder/decoder are trained *separately* and frozen during diffusion training. The U-Net is trained on the latents, with text conditioning via cross-attention.

## Reading order

1. **`what_is_latent_diffusion.md`**. The full architecture, step-by-step.

## The components in detail

### VAE encoder/decoder

- A standard VAE (Part 1) with a *large* encoder/decoder (often based on the VQ-VAE or VQGAN architecture).
- Trained on perceptual loss + adversarial loss + KL regularization.
- Compression factor: 8x in each spatial dimension. So 256x256 -> 32x32.
- Latent channels: 4 (typical).
- The encoder is *frozen* during diffusion training. The decoder is also frozen.

### U-Net (the diffusion model)

- Operates on 32x32x4 latents.
- Has cross-attention layers for text conditioning.
- Time embedding (sinusoidal) for the diffusion step.
- Outputs a *noise prediction* of the same shape as the input (32x32x4).

### Text encoder

- A pretrained text model (CLIP, T5, etc.) that turns text into a sequence of embeddings.
- The embeddings are fed into the U-Net's cross-attention layers.
- The text encoder is *frozen* during diffusion training.

### Classifier-free guidance

- During training, the text conditioning is *dropped* (replaced with a null token) 10% of the time. This lets the model do unconditional generation.
- During sampling, two predictions are made: one with the text, one without. The final prediction is:
  $$\hat\epsilon = \hat\epsilon_{\text{uncond}} + w (\hat\epsilon_{\text{cond}} - \hat\epsilon_{\text{uncond}})$$
  where $w$ is the *guidance scale* (typically 5-15).
- Higher $w$ → more adherence to the prompt, but less diversity.

## Real-life analogy

Latent diffusion is like *sketching in a low-dimensional style*. The VAE is like translating the world into a simpler language (sketches). The U-Net is the artist who learns to draw new sketches from noise. The text encoder is the customer's description. The VAE decoder is the printer that turns the sketch back into a high-fidelity image.

## Where this leads

After Part 3, you understand the Stable Diffusion architecture. The same framework extends to:
- Higher resolutions (SDXL, SD3, FLUX)
- Different modalities (audio, video — see Part 4)
- Conditioning (ControlNet, IP-Adapter, LoRA)
- Distillation (consistency models, few-step samplers)
