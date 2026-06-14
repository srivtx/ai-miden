"""
VAE on MNIST (PyTorch + CUDA)
==============================

The PyTorch version of the VAE prototype. Same architecture as
vae_mnist.py, but using PyTorch for autograd and GPU acceleration.

Uses the real MNIST dataset. Run in Colab with a T4 GPU.

Run:
    !python vae_mnist_colab.py

Outputs:
    plots/vae_pytorch_losses.png
    plots/vae_pytorch_reconstructions.png
    plots/vae_pytorch_samples.png

The code follows the ai-miden AGENTS.md conventions.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Optional: torch is required
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    print("PyTorch not available. In Colab: !pip install torch")
    sys.exit(1)


# Optional: torchvision for MNIST
try:
    from torchvision import datasets, transforms
    TORCHVISION_AVAILABLE = True
except ImportError:
    TORCHVISION_AVAILABLE = False
    print("torchvision not available. Using procedural dataset instead.")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vae_mnist import make_digit_dataset


# =============================================================================
# VAE architecture
# =============================================================================

class VAE(nn.Module):
    def __init__(self, input_dim=784, hidden_dim=400, latent_dim=20):
        super().__init__()
        self.latent_dim = latent_dim

        # Encoder
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

        # Decoder
        self.fc3 = nn.Linear(latent_dim, hidden_dim)
        self.fc4 = nn.Linear(hidden_dim, input_dim)

    def encode(self, x):
        h = F.relu(self.fc1(x))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, log_var):
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h = F.relu(self.fc3(z))
        return torch.sigmoid(self.fc4(h))

    def forward(self, x):
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        return self.decode(z), mu, log_var


def vae_loss(x, x_hat, mu, log_var):
    """ELBO loss: -reconstruction - KL (we minimize this)."""
    recon = F.binary_cross_entropy(x_hat, x, reduction='sum')
    kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return recon, kl, recon + kl


# =============================================================================
# Training
# =============================================================================

def train_vae_pytorch(n_epochs=20, batch_size=128, lr=1e-3, latent_dim=20):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Data
    if TORCHVISION_AVAILABLE:
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.view(-1))  # flatten
        ])
        train_dataset = datasets.MNIST(
            root="./data", train=True, download=True, transform=transform
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        input_dim = 784
    else:
        X, y = make_digit_dataset(n_per_class=500, image_size=8, seed=0)
        X = torch.tensor(X, dtype=torch.float32)
        train_dataset = torch.utils.data.TensorDataset(X)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        input_dim = 64

    # Model
    model = VAE(input_dim=input_dim, hidden_dim=400, latent_dim=latent_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    losses = []
    recons = []
    kls = []

    for epoch in range(n_epochs):
        epoch_recon = 0
        epoch_kl = 0
        n = 0
        for batch in train_loader:
            if TORCHVISION_AVAILABLE:
                x, _ = batch
            else:
                (x,) = batch
            x = x.to(device)
            optimizer.zero_grad()
            x_hat, mu, log_var = model(x)
            recon, kl, total = vae_loss(x, x_hat, mu, log_var)
            total.backward()
            optimizer.step()
            epoch_recon += recon.item()
            epoch_kl += kl.item()
            n += len(x)

        avg_recon = epoch_recon / n
        avg_kl = epoch_kl / n
        recons.append(avg_recon)
        kls.append(avg_kl)
        losses.append(avg_recon + avg_kl)
        print(f"Epoch {epoch+1:3d} | Recon: {avg_recon:.3f} | KL: {avg_kl:.3f} | Total: {avg_recon+avg_kl:.3f}")

    # Save plots
    os.makedirs("plots", exist_ok=True)

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.plot(recons, label="Reconstruction", linewidth=2)
    ax.plot(kls, label="KL divergence", linewidth=2)
    ax.plot(losses, label="Total loss", linewidth=2, linestyle="--")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("VAE training (PyTorch)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/vae_pytorch_losses.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_pytorch_losses.png")

    # Reconstructions
    if TORCHVISION_AVAILABLE:
        test_x = next(iter(train_loader))[0][:10].to(device)
        img_size = 28
    else:
        X, _ = make_digit_dataset(n_per_class=10, image_size=8, seed=99)
        test_x = torch.tensor(X[:10], dtype=torch.float32).to(device)
        img_size = 8
    with torch.no_grad():
        x_hat, _, _ = model(test_x)
    fig, axes = plt.subplots(2, 10, figsize=(15, 3))
    for i in range(10):
        axes[0, i].imshow(test_x[i].cpu().view(img_size, img_size), cmap="gray")
        axes[0, i].axis("off")
        axes[1, i].imshow(x_hat[i].cpu().view(img_size, img_size), cmap="gray")
        axes[1, i].axis("off")
    fig.suptitle("VAE: original (top) vs reconstruction (bottom)")
    fig.tight_layout()
    fig.savefig("plots/vae_pytorch_reconstructions.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_pytorch_reconstructions.png")

    # Samples
    with torch.no_grad():
        z = torch.randn(20, latent_dim).to(device)
        samples = model.decode(z)
    fig, axes = plt.subplots(2, 10, figsize=(15, 3))
    for i in range(20):
        axes[i // 10, i % 10].imshow(samples[i].cpu().view(img_size, img_size), cmap="gray")
        axes[i // 10, i % 10].axis("off")
    fig.suptitle("VAE: samples from the prior (PyTorch)")
    fig.tight_layout()
    fig.savefig("plots/vae_pytorch_samples.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_pytorch_samples.png")

    return model, losses


if __name__ == "__main__":
    train_vae_pytorch(n_epochs=10, batch_size=128, lr=1e-3, latent_dim=20)
