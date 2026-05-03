← [Previous: Phase 28: Multimodal AI](docs/phase28/SUMMARY.md) | [Next: Phase 30: Generative Models — GANs](docs/phase30/SUMMARY.md) →

---

## Phase 29 Summary: Generative Models — VAEs

**The Question:** "My model classifies and generates text. Can it create entirely new images?"

---

### What We Learned

1. **Autoencoder**
   - Encoder compresses input into a latent code
   - Decoder reconstructs input from the code
   - Trained to minimize reconstruction error (MSE)
   - Cannot generate new data — latent space is unstructured

2. **Latent Space**
   - The compressed bottleneck representation
   - In a good space, similar inputs cluster together
   - Moving smoothly between points produces smooth transitions
   - Plain autoencoders have messy, non-interpolatable spaces

3. **VAE (Variational Autoencoder)**
   - Encoder outputs a distribution (mu, log_var) instead of a point
   - Decoder samples from that distribution
   - KL divergence term forces distributions toward N(0,1)
   - Latent space becomes smooth and generative

4. **Reparameterization Trick**
   - z = mu + sigma * epsilon, where epsilon ~ N(0,1)
   - Moves randomness outside the gradient path
   - Makes sampling differentiable so backpropagation works
   - Essential breakthrough for training VAEs with gradient descent

5. **KL Divergence**
   - Penalizes encoder distributions for deviating from N(0,1)
   - Prevents the encoder from collapsing to a plain autoencoder
   - Trades off against reconstruction quality
   - Computed analytically for Gaussian latents

---

### Results

- Autoencoder compressed 8-pixel patterns into 2 numbers with <1% error
- VAE latent space showed clear clustering of similar patterns
- Interpolation between two latent codes produced smooth morphing
- Random samples from N(0,1) decoded into plausible new patterns
- KL divergence successfully prevented posterior collapse

---

### Phase 29 Files

| File | Purpose |
|---|---|
| `docs/phase29/what_is_autoencoder.md` | Compression and reconstruction |
| `docs/phase29/what_is_latent_space.md` | The structured bottleneck representation |
| `docs/phase29/what_is_vae.md` | Generative autoencoder with probabilistic latents |
| `docs/phase29/what_is_reparameterization_trick.md` | Differentiable sampling |
| `docs/phase29/what_is_kl_divergence.md` | Regularizing the latent distribution |
| `src/phase29/phase29_vae.py` | Demonstrations of all five concepts |

---

### Connects To

- **Phase 28:** Multimodal AI — We can see and understand images. Now we learn to CREATE them.
- **Phase 30:** GANs — VAE images are blurry. How do we make them sharp?

---

← [Previous: Phase 28: Multimodal AI](docs/phase28/SUMMARY.md) | [Next: Phase 30: Generative Models — GANs](docs/phase30/SUMMARY.md) →