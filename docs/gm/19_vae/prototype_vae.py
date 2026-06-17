"""
Minimal VAE for latent diffusion.

The idea: Instead of running diffusion on 3 x 128 x 128 = 49,152 pixels,
compress the image into a 4 x 16 x 16 = 1,024 dimensional latent code.
Run diffusion on the LATENT (48x smaller), then decode the latent to
get the final image.

  pixel -> Encoder -> z (mean, logvar) -> sample z_0 -> Decoder -> pixel_hat
                                                             ^
  diffusion runs here (on z, not on pixels)                  |

Training: VAE loss = reconstruction_loss + KL_penalty
  - Reconstruction: how well can we recover the image from z?
  - KL penalty:      keep z close to N(0, 1) so we can sample from it

After VAE is trained, it's FROZEN. Diffusion trains on z, not on pixels.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class TinyVAE(nn.Module):
    """Minimal VAE for 64x64 RGB images -> 16x16x4 latent."""

    def __init__(self, latent_dim=4):
        super().__init__()
        self.latent_dim = latent_dim

        # Encoder: 3x64x64 -> 4x16x16 (down 4x)
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 4, stride=2, padding=1),  # 32x32
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, stride=2, padding=1),  # 16x16
            nn.ReLU(),
        )
        self.fc_mu = nn.Conv2d(64, latent_dim, 3, padding=1)
        self.fc_logvar = nn.Conv2d(64, latent_dim, 3, padding=1)

        # Decoder: 4x16x16 -> 3x64x64 (up 4x)
        self.decoder = nn.Sequential(
            nn.Conv2d(latent_dim, 64, 3, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),  # 32x32
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 4, stride=2, padding=1),  # 64x64
            nn.Sigmoid(),  # output in [0, 1]
        )

    def encode(self, x):
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        """Sample z = mu + sigma * epsilon, where epsilon ~ N(0,1)."""
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        return mu  # at inference, just use the mean

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_hat = self.decode(z)
        return x_hat, mu, logvar

    def vae_loss(self, x, x_hat, mu, logvar, beta=1.0):
        """
        VAE loss = reconstruction + β * KL divergence.

        Reconstruction: MSE between input and output
        KL: D_KL(q(z|x) || p(z)) where p(z) = N(0, 1)

        For a Gaussian VAE:
          D_KL = 0.5 * sum(1 + logvar - mu^2 - exp(logvar))

        β controls the trade-off: β>1 = better disentanglement, β<1 = better reconstruction.
        """
        recon = F.mse_loss(x_hat, x, reduction="mean")

        # KL divergence for Gaussian: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        kl = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        kl = kl / x.size(0)  # normalize by batch

        return recon + beta * kl, recon, kl


# =============================================================================
# Demo: toy 64x64 images
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VAE Demo: image -> latent -> reconstruction")
    print("=" * 60)

    # Toy data: 64x64 RGB images
    B = 4
    x = torch.rand(B, 3, 64, 64)  # 4 random images

    vae = TinyVAE(latent_dim=4)

    # Forward pass
    x_hat, mu, logvar = vae(x)
    loss, recon_loss, kl_loss = vae.vae_loss(x, x_hat, mu, logvar)

    print(f"\n  Input shape:       {x.shape} ({x.numel()} elements)")
    print(f"  Latent shape:      {mu.shape} ({mu.numel()} elements)")

    # Compression ratio
    input_pixels = x.numel() / B
    latent_pixels = mu.numel() / B
    ratio = input_pixels / latent_pixels
    print(f"\n  Compression: {input_pixels:.0f} pixels -> {latent_pixels:.0f} latent ({ratio:.0f}x)")
    print(f"  Reconstruction loss: {recon_loss.item():.6f}")
    print(f"  KL loss:             {kl_loss.item():.6f}")
    print(f"  Total loss:          {loss.item():.6f}")

    # Show that we can generate from latent space
    print(f"\n{'=' * 60}")
    print("Generation from random noise: z ~ N(0, 1) -> image")
    z_rand = torch.randn(1, 4, 16, 16)
    gen = vae.decode(z_rand)
    print(f"  Random latent: {z_rand.shape} -> output: {gen.shape}")
    print(f"  Output range: [{gen.min().item():.3f}, {gen.max().item():.3f}]")

    # This is what the diffusion model would do:
    # 1. Start from random noise z_T ~ N(0, 1) in latent space
    # 2. Run diffusion/flow matching reverse process
    # 3. Get z_0 (clean latent)
    # 4. Decode: pixel = vae.decode(z_0)

    print(f"\nKey insight: Diffusion in latent space instead of pixel space")
    print(f"gives {ratio:.0f}x compression for equal compute budget.")
    print(f"The VAE is trained once and frozen. Diffusion never sees pixels.")
