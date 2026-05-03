← [Previous: Phase 30: Generative Models — GANs](docs/phase30/SUMMARY.md) | [Next: Phase 32: Foundation Models & The Future](docs/phase32/SUMMARY.md) →

---

## Phase 31 Summary: Generative Models — Diffusion

**The Question:** "GANs are hard to train and sometimes collapse. Is there a more stable way to generate images?"

---

### What We Learned

1. **Forward Diffusion**
   - Fixed process that gradually adds Gaussian noise to an image
   - After T steps, the image becomes pure static
   - Closed-form formula allows jumping directly from clean to any timestep
   - No neural network involved — purely mathematical

2. **Reverse Diffusion**
   - Learned process that starts from noise and iteratively denoises
   - Neural network predicts the noise that was added
   - Subtract predicted noise to take one step toward the clean image
   - Stochastic — each run produces slightly different outputs

3. **U-Net Architecture**
   - Encoder compresses image, decoder expands it back
   - Skip connections preserve fine details across scales
   - Bottleneck captures global structure
   - Essential for processing images at multiple resolutions

4. **Timestep Conditioning**
   - Tells the network which noise level it is processing
   - Implemented via sinusoidal embeddings injected into layers
   - Early timesteps = conservative denoising
   - Late timesteps = aggressive reconstruction

---

### Results

- Forward diffusion turned a clean 1D signal into pure noise in 100 steps
- Reverse diffusion recovered the signal by predicting and subtracting noise
- U-Net with skip connections preserved local details better than plain autoencoder
- Timestep conditioning allowed the network to adapt its strategy per step
- Generated novel patterns by starting from pure noise and denoising

---

### Phase 31 Files

| File | Purpose |
|---|---|
| `docs/phase31/what_is_forward_diffusion.md` | Gradually adding noise to images |
| `docs/phase31/what_is_reverse_diffusion.md` | Learning to denoise step by step |
| `docs/phase31/what_is_unet.md` | Hourglass architecture with skip connections |
| `docs/phase31/what_is_timestep_conditioning.md` | Telling the network the noise level |
| `src/phase31/phase31_diffusion.py` | Toy 1D diffusion demonstration |
| `src/phase31/phase31_diffusion_colab.py` | Real DDPM on MNIST (Colab T4) |

---

### Connects To

- **Phase 30:** GANs — Adversarial training is unstable. Diffusion replaces competition with gradual refinement.
- **Phase 32:** Foundation Models — We can generate images. How does this fit into the future of AI?

---

← [Previous: Phase 30: Generative Models — GANs](docs/phase30/SUMMARY.md) | [Next: Phase 32: Foundation Models & The Future](docs/phase32/SUMMARY.md) →