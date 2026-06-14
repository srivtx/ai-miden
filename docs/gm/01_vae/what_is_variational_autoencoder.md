# What Is a Variational Autoencoder (VAE)?

**The Problem:** A vanilla autoencoder is a great compressor, but it is *not* a generative model. If you sample a random point in the latent space, the decoder produces garbage. The reason: the encoder maps each training image to a *specific* point, but the latent space has no structure — there are huge "gaps" where no training image lives, and the decoder has no idea what to do there. You need a way to *regularize* the latent space so that any point in it decodes to a plausible image. The Variational Autoencoder (VAE) does this with one elegant trick: instead of mapping each image to a point, map it to a *distribution*. Then add a KL term that forces this distribution to be close to a simple prior.

**Definition:** A *Variational Autoencoder* (VAE) is an autoencoder where the encoder outputs the parameters of a distribution (usually a Gaussian), and the loss includes a KL regularization term to keep this distribution close to a prior. Formally:

- **Encoder**: $q_\phi(z | x) = \mathcal{N}(z; \mu_\phi(x), \sigma_\phi(x)^2 I)$ — a Gaussian with mean and variance predicted by the encoder.
- **Decoder**: $p_\theta(x | z)$ — usually a Bernoulli or Gaussian likelihood over pixels.
- **Prior**: $p(z) = \mathcal{N}(0, I)$ — a standard Gaussian.
- **Loss (negative ELBO)**:
  $$\mathcal{L} = -\mathbb{E}_{q_\phi(z | x)}[\log p_\theta(x | z)] + D_{KL}(q_\phi(z | x) \| p(z))$$
  $$= \text{reconstruction loss} + \text{KL regularization}$$

**How It Works (Step-by-Step):**

1. **Encode**: pass $x$ through the encoder. Get $\mu$ and $\log \sigma^2$ (or $\sigma$ directly), each vectors of the latent dimension.
2. **Sample**: draw $z = \mu + \sigma \odot \epsilon$, where $\epsilon \sim \mathcal{N}(0, I)$ and $\odot$ is element-wise multiplication. This is the *reparameterization trick* (Kingma 2013). It allows gradients to flow through the sampling step.
3. **Decode**: pass $z$ through the decoder. Get the reconstruction $\hat{x}$.
4. **Compute losses**:
   - **Reconstruction loss**: $-\log p_\theta(x | z)$. For Bernoulli (binary images), this is binary cross-entropy. For Gaussian (continuous), this is MSE.
   - **KL divergence**: $D_{KL}(q_\phi(z | x) \| p(z))$. For diagonal Gaussian $q$ and standard Gaussian $p$, this has a closed form:
     $$D_{KL} = -\frac{1}{2} \sum_j (1 + \log \sigma_j^2 - \mu_j^2 - \sigma_j^2)$$
5. **Backprop**: total loss = reconstruction + KL. Backprop through both. Update $\phi$ and $\theta$.
6. **Sampling** (after training): sample $z \sim p(z) = \mathcal{N}(0, I)$. Decode: $\hat{x} = p_\theta(\cdot | z)$. The result is a new image.

**The reparameterization trick** is the key innovation. Without it, the sampling step $z \sim q_\phi(z | x)$ is non-differentiable. With it, we write $z$ as a *deterministic* function of $\mu, \sigma$ and a *random* noise $\epsilon$. Gradients flow through $\mu$ and $\sigma$ but not through $\epsilon$. This makes the whole network trainable with backprop.

**The KL term** is what makes the latent space structured. Without it, the encoder would map each image to a tiny point in latent space (the trivial solution that minimizes reconstruction loss). With it, the encoder is forced to map each image to a *distribution* that overlaps with the prior $\mathcal{N}(0, I)$. Different training images have *overlapping* distributions. The latent space becomes a smooth manifold where nearby points decode to similar images.

**Real-life analogy:** A VAE is like a *sketch artist* who is told: "Draw any face, but draw it so that all your drawings could pass for sketches of real faces from the same photo album." The reconstruction loss says "make it look like a real face." The KL term says "stay close to the typical sketches of real faces." The result is a *distribution* over plausible sketches, not a single drawing.

**Tiny numeric example:**

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class VAE(nn.Module):
    def __init__(self, input_dim=784, latent_dim=32, hidden_dim=256):
        super().__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 2 * latent_dim)  # mu and log_var
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Sigmoid()
        )

    def encode(self, x):
        h = self.encoder(x)
        mu, log_var = h.chunk(2, dim=-1)
        return mu, log_var

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        x_hat = self.decode(z)
        return x_hat, mu, log_var

def vae_loss(x, x_hat, mu, log_var):
    # Reconstruction: binary cross-entropy
    recon = F.binary_cross_entropy(x_hat, x, reduction='sum')
    # KL divergence: closed form for diagonal Gaussian
    kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return recon + kl
```

**Common confusion:**

- "The VAE is a generative model." Yes, after training, you can sample by $z \sim \mathcal{N}(0, I)$, then $x = \text{decoder}(z)$. The KL term ensures the latent space is well-structured.
- "The reparameterization trick is just a math trick." Yes, but it is the *key* trick. Without it, you can't backprop through the sampling step, and the network doesn't train.
- "The KL term encourages the latent to be $\mathcal{N}(0, I)$." Yes, but it does so per-image. The encoder maps each image to a Gaussian close to $\mathcal{N}(0, I)$. Different images have different means and variances, but each is close to the prior. The *aggregate* latent space is approximately $\mathcal{N}(0, I)$.
- "VAE samples are blurry." Yes, compared to GANs. The KL term encourages the latent to be a Gaussian, which is "smooth" — the decoder can't represent sharp details as easily. β-VAE (with a stronger KL term) is even blurrier. Diffusion models fix this.
- "VAE requires choosing the latent dimension." Yes, this is a hyperparameter. Too small: blurry. Too large: ignore the latent, overfit. Typical values: 2-256 for images, 32-512 for high-resolution.
- "The prior is always $\mathcal{N}(0, I)$." Usually, yes. But you can use other priors (e.g., mixtures, flows). The math generalizes.
- "VAE and GAN are competitors." Yes, but they are *complementary*. A VAE-GAN combines both: VAE for the latent, GAN for sharper samples. Modern diffusion models also have a VAE component (in Stable Diffusion).

**Key properties:**

- **Variational lower bound**: training maximizes the ELBO, a lower bound on $\log p_\theta(x)$.
- **Reparameterization**: gradients flow through the sampling step.
- **Closed-form KL**: for diagonal Gaussian, the KL is a simple formula. No Monte Carlo needed.
- **Encoder-decoder**: two networks, trained jointly.
- **Smooth latent**: the KL term ensures the latent space is smooth and continuous.
- **Probabilistic**: the encoder outputs a *distribution*, not a point.

**Tech comparison:**

| Method | Latent | Sample quality | Theoretical |
|---|---|---|---|
| Vanilla AE | Point | N/A | None |
| VAE | Distribution | Blurry | ELBO |
| β-VAE | Distribution | Blurrier | β-ELBO |
| VQ-VAE | Discrete | Sharp | None |
| IWAE | Distribution | Slightly sharper | IWAE bound |

**Connection to generative models:** The VAE is the *cleanest* theoretical framework for generative models with latent variables. The score (Part 0.5) is closely related: the gradient of the ELBO with respect to $x$ is an estimate of the score. Diffusion models (Part 2) are *implicit* VAEs — they don't have an explicit encoder, but the math is similar.
