"""
VAE on MNIST (NumPy from scratch)
=================================

A runnable Variational Autoencoder trained on a procedural MNIST-like dataset.
Pure NumPy, no PyTorch, no external data download.

The procedural dataset generates digit-like patterns procedurally so we don't
need to download MNIST. It produces 8x8 "digit-like" images with multiple
strokes at class-specific positions.

Following ai-miden AGENTS.md conventions:
- matplotlib.use('Agg') for headless rendering
- Plots saved to plots/ with descriptive names
- Every line explains WHY, not just WHAT

Run:
    python vae_mnist.py
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Data: procedural MNIST-like 8x8 digits
# =============================================================================

def make_digit_dataset(n_per_class=200, image_size=8, seed=0):
    """
    Procedurally generate 10 "digit-like" classes, each defined by a unique
    pattern of strokes at class-specific positions.

    Returns:
        X: (n_samples, 64) array of pixel values in [0, 1]
        y: (n_samples,) integer labels in [0, 9]
    """
    rng = np.random.RandomState(seed)
    n_classes = 10

    # Define a "template" for each class. Each template is a 2D pattern.
    templates = []
    for c in range(n_classes):
        t = np.zeros((image_size, image_size))
        # Different patterns per class
        if c == 0:
            # Ring
            cy, cx = image_size // 2, image_size // 2
            for i in range(image_size):
                for j in range(image_size):
                    d = np.sqrt((i - cy)**2 + (j - cx)**2)
                    if 1.5 < d < 2.5:
                        t[i, j] = 1.0
        elif c == 1:
            # Vertical line
            t[:, 3] = 1.0
        elif c == 2:
            # Horizontal line
            t[3, :] = 1.0
        elif c == 3:
            # Diagonal
            for i in range(image_size):
                t[i, i] = 1.0
        elif c == 4:
            # Anti-diagonal
            for i in range(image_size):
                t[i, image_size - 1 - i] = 1.0
        elif c == 5:
            # Cross
            t[:, image_size // 2] = 1.0
            t[image_size // 2, :] = 1.0
        elif c == 6:
            # Two horizontal lines
            t[2, :] = 1.0
            t[5, :] = 1.0
        elif c == 7:
            # Two vertical lines
            t[:, 2] = 1.0
            t[:, 5] = 1.0
        elif c == 8:
            # 2x2 grid
            t[1:3, 1:3] = 1.0
            t[1:3, 5:7] = 1.0
            t[5:7, 1:3] = 1.0
            t[5:7, 5:7] = 1.0
        else:
            # Random blob
            cy, cx = rng.randint(2, image_size - 2, 2)
            t[cy, cx] = 1.0
            t[cy + 1, cx] = 1.0
            t[cy, cx + 1] = 1.0
            t[cy + 1, cx + 1] = 1.0
        templates.append(t.flatten())

    # Generate noisy versions
    X = []
    y = []
    for c in range(n_classes):
        for _ in range(n_per_class):
            noisy = templates[c] + 0.2 * rng.randn(image_size * image_size)
            noisy = np.clip(noisy, 0, 1)
            X.append(noisy)
            y.append(c)

    X = np.array(X, dtype=np.float64)
    y = np.array(y, dtype=np.int64)
    # Shuffle
    perm = rng.permutation(len(X))
    return X[perm], y[perm]


# =============================================================================
# The VAE
# =============================================================================

class VAE:
    """
    A simple VAE with a 2-layer encoder and 2-layer decoder.
    Latent dimension is 8 (small for visualization).
    """

    def __init__(self, input_dim=64, hidden_dim=64, latent_dim=8, lr=0.01, seed=0):
        rng = np.random.RandomState(seed)
        self.lr = lr
        self.latent_dim = latent_dim

        # Encoder weights: input -> hidden
        self.W_enc1 = rng.randn(input_dim, hidden_dim) * 0.1
        self.b_enc1 = np.zeros(hidden_dim)
        # Encoder: hidden -> mu, log_var
        self.W_mu = rng.randn(hidden_dim, latent_dim) * 0.1
        self.b_mu = np.zeros(latent_dim)
        self.W_logvar = rng.randn(hidden_dim, latent_dim) * 0.1
        self.b_logvar = np.zeros(latent_dim)

        # Decoder weights: latent -> hidden
        self.W_dec1 = rng.randn(latent_dim, hidden_dim) * 0.1
        self.b_dec1 = np.zeros(hidden_dim)
        # Decoder: hidden -> input
        self.W_dec2 = rng.randn(hidden_dim, input_dim) * 0.1
        self.b_dec2 = np.zeros(input_dim)

        # Collect all parameters
        self.params = [self.W_enc1, self.b_enc1, self.W_mu, self.b_mu,
                       self.W_logvar, self.b_logvar,
                       self.W_dec1, self.b_dec1, self.W_dec2, self.b_dec2]

    def relu(self, x):
        return np.maximum(0, x)

    def relu_grad(self, x):
        return (x > 0).astype(np.float64)

    def sigmoid(self, x):
        # Numerically stable
        return np.where(x >= 0, 1 / (1 + np.exp(-x)), np.exp(x) / (1 + np.exp(x)))

    def encode(self, x):
        """Returns mu, log_var."""
        h = self.relu(x @ self.W_enc1 + self.b_enc1)
        mu = h @ self.W_mu + self.b_mu
        log_var = h @ self.W_logvar + self.b_logvar
        return mu, log_var, h

    def reparameterize(self, mu, log_var):
        std = np.exp(0.5 * log_var)
        eps = np.random.randn(*mu.shape)
        return mu + eps * std

    def decode(self, z):
        h = self.relu(z @ self.W_dec1 + self.b_dec1)
        return self.sigmoid(h @ self.W_dec2 + self.b_dec2)

    def forward(self, x):
        mu, log_var, h_enc = self.encode(x)
        z = self.reparameterize(mu, log_var)
        x_hat = self.decode(z)
        return x_hat, mu, log_var, z, h_enc

    def compute_loss(self, x, x_hat, mu, log_var):
        """ELBO loss = -reconstruction - KL (we minimize this)."""
        # Reconstruction: binary cross-entropy
        eps = 1e-8
        recon = -np.sum(x * np.log(x_hat + eps) + (1 - x) * np.log(1 - x_hat + eps))
        # KL: closed form for diagonal Gaussian
        kl = -0.5 * np.sum(1 + log_var - mu ** 2 - np.exp(log_var))
        return recon, kl, recon + kl

    def backward_and_update(self, x, lr):
        """Full backprop pass."""
        x_hat, mu, log_var, z, h_enc = self.forward(x)
        recon, kl, total_loss = self.compute_loss(x, x_hat, mu, log_var)
        n = len(x)

        # Backprop through decoder
        # d_recon / d_x_hat: -x / x_hat + (1 - x) / (1 - x_hat)
        eps = 1e-8
        d_recon_d_xhat = -x / (x_hat + eps) + (1 - x) / (1 - x_hat + eps)
        d_xhat = d_recon_d_xhat  # shape (n, 64)

        # d_xhat / d_dec2 pre-activation
        # x_hat = sigmoid(h_dec2), so d_xhat/d_pre = x_hat * (1 - x_hat)
        h_dec2_pre = None  # we need to recompute
        h = self.relu(z @ self.W_dec1 + self.b_dec1)
        h_dec2_pre = h @ self.W_dec2 + self.b_dec2
        d_pre = d_xhat * (x_hat * (1 - x_hat))  # shape (n, 64)

        dW_dec2 = h.T @ d_pre / n
        db_dec2 = np.mean(d_pre, axis=0)

        d_h = d_pre @ self.W_dec2.T  # shape (n, hidden)
        d_h_pre = d_h * self.relu_grad(h)  # shape (n, hidden)

        dW_dec1 = z.T @ d_h_pre / n
        db_dec1 = np.mean(d_h_pre, axis=0)

        # Backprop through encoder (the mu and log_var paths)
        d_z = d_h_pre @ self.W_dec1.T  # shape (n, latent)

        # d_kl / d_mu = mu
        # d_kl / d_log_var = -0.5 + 0.5 * exp(log_var)
        d_mu_from_kl = mu / n
        d_logvar_from_kl = (-0.5 + 0.5 * np.exp(log_var)) / n

        # From reparameterization: d_z / d_mu = 1, d_z / d_log_var = 0.5 * std * eps
        # We need d_mu_total and d_logvar_total
        d_mu_total = d_z + d_mu_from_kl
        d_logvar_total = d_z * 0.5 * np.exp(0.5 * log_var) * (z - mu) / np.exp(0.5 * log_var) + d_logvar_from_kl
        # Simplify: d_z * 0.5 * eps, where eps = (z - mu) / std
        # Easier: d_logvar_from_z = d_z * d_z/d_logvar
        # z = mu + std * eps, std = exp(0.5 log_var), so dz/d_logvar = 0.5 * std * eps
        d_logvar_from_z = d_z * 0.5 * np.exp(0.5 * log_var) * (z - mu) / np.exp(0.5 * log_var)
        d_logvar_total = d_logvar_from_z + d_logvar_from_kl

        # Backprop through mu and logvar layers
        dW_mu = h_enc.T @ d_mu_total / n
        db_mu = np.mean(d_mu_total, axis=0)

        dW_logvar = h_enc.T @ d_logvar_total / n
        db_logvar = np.mean(d_logvar_total, axis=0)

        # Backprop to encoder hidden
        d_h_enc = d_mu_total @ self.W_mu.T + d_logvar_total @ self.W_logvar.T
        d_h_enc_pre = d_h_enc * self.relu_grad(h_enc)

        dW_enc1 = x.T @ d_h_enc_pre / n
        db_enc1 = np.mean(d_h_enc_pre, axis=0)

        # Update
        self.W_dec2 -= lr * dW_dec2
        self.b_dec2 -= lr * db_dec2
        self.W_dec1 -= lr * dW_dec1
        self.b_dec1 -= lr * db_dec1
        self.W_mu -= lr * dW_mu
        self.b_mu -= lr * db_mu
        self.W_logvar -= lr * dW_logvar
        self.b_logvar -= lr * db_logvar
        self.W_enc1 -= lr * dW_enc1
        self.b_enc1 -= lr * db_enc1

        return recon / n, kl / n, total_loss / n

    def sample(self, n=16):
        """Sample new images from the prior."""
        z = np.random.randn(n, self.latent_dim)
        return self.decode(z)


# =============================================================================
# Training
# =============================================================================

def train_vae(n_epochs=50, batch_size=32, lr=0.01, seed=42):
    print("=" * 60)
    print("VAE on procedural 10-class 8x8 digits (NumPy)")
    print("=" * 60)

    X, y = make_digit_dataset(n_per_class=200, image_size=8, seed=0)
    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} dims, {len(np.unique(y))} classes")

    vae = VAE(input_dim=64, hidden_dim=64, latent_dim=8, lr=lr, seed=seed)

    n_samples = len(X)
    losses = []
    recons = []
    kls = []

    rng = np.random.RandomState(seed)
    for epoch in range(n_epochs):
        # Shuffle
        perm = rng.permutation(n_samples)
        X_shuf = X[perm]

        epoch_recon = 0
        epoch_kl = 0
        n_batches = 0
        for i in range(0, n_samples, batch_size):
            x_batch = X_shuf[i:i + batch_size]
            recon, kl, total = vae.backward_and_update(x_batch, lr)
            epoch_recon += recon
            epoch_kl += kl
            n_batches += 1

        avg_recon = epoch_recon / n_batches
        avg_kl = epoch_kl / n_batches
        recons.append(avg_recon)
        kls.append(avg_kl)
        losses.append(avg_recon + avg_kl)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:3d} | Recon: {avg_recon:.3f} | KL: {avg_kl:.3f} | Total: {avg_recon+avg_kl:.3f}")

    # Save plots
    os.makedirs("plots", exist_ok=True)

    # Loss curves
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.plot(recons, label="Reconstruction", linewidth=2)
    ax.plot(kls, label="KL divergence", linewidth=2)
    ax.plot(losses, label="Total loss", linewidth=2, linestyle="--")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("VAE training curves")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/vae_losses.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_losses.png")

    # Reconstructions
    fig, axes = plt.subplots(2, 10, figsize=(15, 3))
    test_idx = rng.choice(n_samples, 10, replace=False)
    test_x = X[test_idx]
    x_hat, _, _, _, _ = vae.forward(test_x)
    for i in range(10):
        axes[0, i].imshow(test_x[i].reshape(8, 8), cmap="gray")
        axes[0, i].axis("off")
        axes[1, i].imshow(x_hat[i].reshape(8, 8), cmap="gray")
        axes[1, i].axis("off")
    axes[0, 0].set_title("Original", loc="left")
    axes[1, 0].set_title("Reconstruction", loc="left")
    fig.suptitle("VAE: original (top) vs reconstruction (bottom)")
    fig.tight_layout()
    fig.savefig("plots/vae_reconstructions.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_reconstructions.png")

    # Samples from the prior
    samples = vae.sample(n=20)
    fig, axes = plt.subplots(2, 10, figsize=(15, 3))
    for i in range(20):
        axes[i // 10, i % 10].imshow(samples[i].reshape(8, 8), cmap="gray")
        axes[i // 10, i % 10].axis("off")
    fig.suptitle("VAE: samples from the prior p(z) = N(0, I)")
    fig.tight_layout()
    fig.savefig("plots/vae_samples.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/vae_samples.png")

    return vae, losses


if __name__ == "__main__":
    train_vae()
