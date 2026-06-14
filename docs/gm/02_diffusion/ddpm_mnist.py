"""
DDPM on procedural 8x8 digits (NumPy from scratch)
==================================================

A runnable Denoising Diffusion Probabilistic Model (DDPM) on a procedural
MNIST-like dataset. Pure NumPy, no PyTorch, no external data.

Following ai-miden AGENTS.md conventions:
- matplotlib.use('Agg') for headless rendering
- Plots saved to plots/ with descriptive names
- Every line explains WHY, not just WHAT

Run:
    python ddpm_mnist.py

Outputs:
    plots/ddpm_losses.png          - training loss over time
    plots/ddpm_forward.png         - forward process: x_0 -> x_T
    plots/ddpm_samples.png         - generated samples
    plots/ddpm_reverse.gif         - reverse process: x_T -> x_0 (if you add the loop)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# =============================================================================
# Procedural dataset (inlined so this file is self-contained)
# =============================================================================

def make_digit_dataset(n_per_class=200, image_size=8, seed=0):
    """Generate 10 'digit-like' classes procedurally."""
    rng = np.random.RandomState(seed)
    n_classes = 10
    templates = []
    for c in range(n_classes):
        t = np.zeros((image_size, image_size))
        if c == 0:
            cy, cx = image_size // 2, image_size // 2
            for i in range(image_size):
                for j in range(image_size):
                    d = np.sqrt((i - cy)**2 + (j - cx)**2)
                    if 1.5 < d < 2.5:
                        t[i, j] = 1.0
        elif c == 1:
            t[:, 3] = 1.0
        elif c == 2:
            t[3, :] = 1.0
        elif c == 3:
            for i in range(image_size):
                t[i, i] = 1.0
        elif c == 4:
            for i in range(image_size):
                t[i, image_size - 1 - i] = 1.0
        elif c == 5:
            t[:, image_size // 2] = 1.0
            t[image_size // 2, :] = 1.0
        elif c == 6:
            t[2, :] = 1.0
            t[5, :] = 1.0
        elif c == 7:
            t[:, 2] = 1.0
            t[:, 5] = 1.0
        elif c == 8:
            t[1:3, 1:3] = 1.0
            t[1:3, 5:7] = 1.0
            t[5:7, 1:3] = 1.0
            t[5:7, 5:7] = 1.0
        else:
            cy, cx = rng.randint(2, image_size - 2, 2)
            t[cy, cx] = 1.0
            t[cy + 1, cx] = 1.0
            t[cy, cx + 1] = 1.0
            t[cy + 1, cx + 1] = 1.0
        templates.append(t.flatten())

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
    perm = rng.permutation(len(X))
    return X[perm], y[perm]


# =============================================================================
# Noise schedule
# =============================================================================

def make_linear_schedule(T=100, beta_start=1e-4, beta_end=0.02):
    """Linear noise schedule: beta_t increases from beta_start to beta_end."""
    betas = np.linspace(beta_start, beta_end, T, dtype=np.float64)
    alphas = 1.0 - betas
    alpha_bars = np.cumprod(alphas)  # \bar{alpha}_t
    return betas, alphas, alpha_bars


def make_cosine_schedule(T=100, s=0.008):
    """Cosine noise schedule (Nichol & Dhariwal 2021). Better for high-res."""
    steps = T + 1
    x = np.linspace(0, T, steps, dtype=np.float64)
    alpha_bars_full = np.cos(((x / T) + s) / (1 + s) * np.pi / 2) ** 2
    alpha_bars_full = alpha_bars_full / alpha_bars_full[0]
    betas = 1 - alpha_bars_full[1:] / alpha_bars_full[:-1]
    betas = np.clip(betas, 0, 0.999)
    alphas = 1.0 - betas
    alpha_bars = np.cumprod(alphas)
    return betas, alphas, alpha_bars


# =============================================================================
# Forward process (q): given x_0, sample x_t
# =============================================================================

def forward_sample(x0, t, alpha_bars, eps=None):
    """
    Sample x_t from q(x_t | x_0) in one step (closed form).
    x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * eps
    """
    if eps is None:
        eps = np.random.randn(*x0.shape)
    a_bar = alpha_bars[t]
    return np.sqrt(a_bar) * x0 + np.sqrt(1.0 - a_bar) * eps, eps


# =============================================================================
# The U-Net (simplified for NumPy)
# =============================================================================

class TimeEmbedding:
    """Sinusoidal time embedding, like Transformer."""
    def __init__(self, dim=32):
        self.dim = dim

    def __call__(self, t):
        # t is an integer timestep
        half = self.dim // 2
        freqs = np.exp(-np.log(10000.0) * np.arange(half) / half)
        args = t * freqs
        return np.concatenate([np.sin(args), np.cos(args)])


class SimpleUNet:
    """
    A simplified U-Net for 8x8 images.
    In NumPy, we use fully-connected layers with residual connections.
    Time embedding is concatenated to the hidden vector.
    """
    def __init__(self, input_dim=64, hidden_dim=128, time_dim=32, seed=0):
        rng = np.random.RandomState(seed)
        self.time_embed = TimeEmbedding(time_dim)

        # Encoder
        self.W1 = rng.randn(input_dim + time_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = rng.randn(hidden_dim, hidden_dim) * 0.1
        self.b2 = np.zeros(hidden_dim)

        # Decoder
        self.W3 = rng.randn(hidden_dim, hidden_dim) * 0.1
        self.b3 = np.zeros(hidden_dim)
        self.W4 = rng.randn(hidden_dim, input_dim) * 0.1
        self.b4 = np.zeros(input_dim)

        self.params = [self.W1, self.b1, self.W2, self.b2,
                       self.W3, self.b3, self.W4, self.b4]

    def relu(self, x):
        return np.maximum(0, x)

    def relu_grad(self, x):
        return (x > 0).astype(np.float64)

    def forward(self, x, t):
        """Forward pass: predict noise given noisy input x and timestep t."""
        n = x.shape[0]
        # Time embedding
        t_emb = self.time_embed(t)  # (time_dim,)
        t_emb_batch = np.tile(t_emb, (n, 1))  # (n, time_dim)

        # Concatenate input and time
        h = np.concatenate([x, t_emb_batch], axis=1)  # (n, input_dim + time_dim)
        h1 = self.relu(h @ self.W1 + self.b1)
        h2 = self.relu(h1 @ self.W2 + self.b2)
        # Residual
        h3 = self.relu(h2 @ self.W3 + self.b3) + h2
        h4 = h3 @ self.W4 + self.b4  # No activation on output
        return h4

    def backward_and_update(self, x, t, eps_true, lr):
        """One training step. Returns loss."""
        n = x.shape[0]
        t_emb = self.time_embed(t)
        t_emb_batch = np.tile(t_emb, (n, 1))

        # Forward
        h = np.concatenate([x, t_emb_batch], axis=1)
        h1 = self.relu(h @ self.W1 + self.b1)
        h2 = self.relu(h1 @ self.W2 + self.b2)
        h3 = self.relu(h2 @ self.W3 + self.b3) + h2
        eps_pred = h3 @ self.W4 + self.b4

        # Loss: MSE
        loss = np.mean((eps_pred - eps_true) ** 2)

        # Backward
        d_eps = 2 * (eps_pred - eps_true) / n  # (n, input_dim)
        dW4 = h3.T @ d_eps
        db4 = np.mean(d_eps, axis=0)
        d_h3 = d_eps @ self.W4.T

        d_h3_pre = d_h3 * self.relu_grad(h3 - h2)  # subtract residual
        dW3 = h2.T @ d_h3_pre
        db3 = np.mean(d_h3_pre, axis=0)
        d_h2 = d_h3_pre @ self.W3.T + d_h3  # residual

        d_h2_pre = d_h2 * self.relu_grad(h2)
        dW2 = h1.T @ d_h2_pre
        db2 = np.mean(d_h2_pre, axis=0)
        d_h1 = d_h2_pre @ self.W2.T

        d_h1_pre = d_h1 * self.relu_grad(h1)
        dW1 = h.T @ d_h1_pre
        db1 = np.mean(d_h1_pre, axis=0)
        # Don't need to backprop further (h is the input)

        # Update
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        self.W3 -= lr * dW3
        self.b3 -= lr * db3
        self.W4 -= lr * dW4
        self.b4 -= lr * db4

        return loss


# =============================================================================
# Reverse process (sampling): given x_T, generate x_0
# =============================================================================

def ddpm_sample(model, T, alpha_bars, alphas, betas, n_samples=16, input_dim=64):
    """
    The full reverse process. Start with noise, denoise step by step.
    """
    x = np.random.randn(n_samples, input_dim)
    history = [x.copy()]

    for t in reversed(range(T)):
        t_arr = np.array(t)
        eps_pred = model.forward(x, t_arr)
        a_bar_t = alpha_bars[t]
        a_t = alphas[t]
        beta_t = betas[t]

        # Predicted mean
        mean = (x - (1 - a_t) / np.sqrt(1 - a_bar_t) * eps_pred) / np.sqrt(a_t)
        # Add noise (except at t=0)
        if t > 0:
            noise = np.random.randn(*x.shape)
            x = mean + np.sqrt(beta_t) * noise
        else:
            x = mean
        history.append(x.copy())

    return x, history


# =============================================================================
# Training and visualization
# =============================================================================

def train_ddpm(n_epochs=20, batch_size=64, T=100, lr=0.001, seed=42):
    print("=" * 60)
    print("DDPM on procedural 8x8 digits (NumPy)")
    print("=" * 60)

    # Data
    X, y = make_digit_dataset(n_per_class=300, image_size=8, seed=0)
    print(f"Dataset: {X.shape[0]} samples, {X.shape[1]} dims")

    # Schedule
    betas, alphas, alpha_bars = make_linear_schedule(T=T, beta_start=1e-4, beta_end=0.05)
    print(f"Schedule: T={T}, linear, beta in [{betas[0]:.4f}, {betas[-1]:.4f}]")

    # Model
    model = SimpleUNet(input_dim=64, hidden_dim=128, time_dim=32, seed=seed)

    # Training loop
    n_samples = len(X)
    losses = []
    rng = np.random.RandomState(seed)

    for epoch in range(n_epochs):
        perm = rng.permutation(n_samples)
        X_shuf = X[perm]
        epoch_loss = 0
        n_batches = 0

        for i in range(0, n_samples, batch_size):
            x0 = X_shuf[i:i + batch_size]
            # Sample random timesteps
            t_batch = rng.randint(0, T, size=len(x0))
            # Forward process
            x_t = np.zeros_like(x0)
            eps = np.zeros_like(x0)
            for j in range(len(x0)):
                x_t[j], eps[j] = forward_sample(x0[j], t_batch[j], alpha_bars)
            # One training step per element (slow but correct)
            # Group by timestep for vectorization
            for t_val in np.unique(t_batch):
                mask = t_batch == t_val
                loss = model.backward_and_update(x_t[mask], int(t_val), eps[mask], lr)
                epoch_loss += loss * mask.sum()
                n_batches += mask.sum()

        avg_loss = epoch_loss / n_samples
        losses.append(avg_loss)
        if (epoch + 1) % 2 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:3d} | Loss: {avg_loss:.4f}")

    # Save loss plot
    os.makedirs("plots", exist_ok=True)
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.plot(losses, linewidth=2, color="#1f77b4")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE denoising loss")
    ax.set_title("DDPM training loss")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig("plots/ddpm_losses.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_losses.png")

    # Forward process visualization
    fig, axes = plt.subplots(1, 8, figsize=(16, 2))
    sample_idx = 0
    test_x0 = X[sample_idx:sample_idx + 1]
    timesteps_to_show = [0, T // 8, T // 4, T // 2, 3 * T // 4, 7 * T // 8, T - 1, T]
    # The last is wrong (we have 0..T-1). Use T-1
    timesteps_to_show = [0, max(1, T // 8), max(1, T // 4), max(1, T // 2),
                         max(1, 3 * T // 4), max(1, 7 * T // 8), T - 1, T - 1]
    for i, t_show in enumerate(timesteps_to_show[:8]):
        if t_show == 0:
            img = test_x0[0].reshape(8, 8)
        else:
            x_t, _ = forward_sample(test_x0[0], t_show, alpha_bars)
            img = x_t.reshape(8, 8)
        axes[i].imshow(img, cmap="gray")
        axes[i].set_title(f"t={t_show}", fontsize=9)
        axes[i].axis("off")
    fig.suptitle("Forward process: x_0 -> x_T (gradually destroyed)")
    fig.tight_layout()
    fig.savefig("plots/ddpm_forward.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_forward.png")

    # Sample from the model
    print("Sampling new images...")
    samples, history = ddpm_sample(model, T, alpha_bars, alphas, betas, n_samples=16, input_dim=64)
    # Reshape to (n_samples, 8, 8)
    samples = samples.reshape(-1, 8, 8)
    # Clip to [0, 1] for visualization
    samples = np.clip(samples, 0, 1)

    fig, axes = plt.subplots(2, 8, figsize=(16, 4))
    for i in range(16):
        axes[i // 8, i % 8].imshow(samples[i], cmap="gray")
        axes[i // 8, i % 8].axis("off")
    fig.suptitle("DDPM: samples from the model (after reverse process)")
    fig.tight_layout()
    fig.savefig("plots/ddpm_samples.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_samples.png")

    # Reverse process visualization (intermediate steps)
    n_steps_show = 8
    step_indices = np.linspace(0, len(history) - 1, n_steps_show).astype(int)
    fig, axes = plt.subplots(2, 8, figsize=(16, 4))
    for i, step_idx in enumerate(step_indices):
        img = history[step_idx][0].reshape(8, 8)
        img = np.clip(img, 0, 1)
        # top row: high t (more noise), bottom row: low t (cleaner)
        # step_idx=0 is x_T (pure noise), step_idx=T-1 is x_0 (clean)
        # We want to show progression from noise -> clean
        ax = axes[i // 8, i % 8] if i < 8 else axes[1, i - 8]
        ax.imshow(img, cmap="gray")
        t_val = T - 1 - step_idx
        ax.set_title(f"t={t_val}", fontsize=9)
        ax.axis("off")
    fig.suptitle("Reverse process: x_T -> x_0 (gradually denoised)")
    fig.tight_layout()
    fig.savefig("plots/ddpm_reverse.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ddpm_reverse.png")

    return model, losses, samples


if __name__ == "__main__":
    train_ddpm(n_epochs=15, batch_size=64, T=50, lr=0.001, seed=42)
