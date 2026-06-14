"""
Latent Diffusion Model — Architecture Skeleton
================================================

A runnable NumPy implementation of the Latent Diffusion architecture.
This is a *skeleton* that demonstrates the components: VAE encoder/decoder
+ U-Net with cross-attention. It runs but is too small to be useful for
real images. The point is to show the architecture.

For the production version, see the PyTorch implementation in
prototype_colab.py and the actual Stable Diffusion 3 codebase.

Run:
    python latent_diffusion.py

Outputs:
    plots/ldm_architecture.png  - architecture diagram
    plots/ldm_pipeline.png      - the data flow

Following ai-miden AGENTS.md conventions.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# =============================================================================
# The architecture components (skeletons)
# =============================================================================

class VAEEncoder:
    """A tiny VAE encoder: image -> latent distribution."""
    def __init__(self, img_h=8, img_w=8, latent_dim=8, hidden=32, seed=0):
        rng = np.random.RandomState(seed)
        self.img_h = img_h
        self.img_w = img_w
        self.latent_dim = latent_dim
        # A simple "conv-like" layer: flatten -> linear -> split into mu, logvar
        self.W1 = rng.randn(img_h * img_w, hidden) * 0.1
        self.b1 = np.zeros(hidden)
        self.W_mu = rng.randn(hidden, latent_dim) * 0.1
        self.b_mu = np.zeros(latent_dim)
        self.W_logvar = rng.randn(hidden, latent_dim) * 0.1
        self.b_logvar = np.zeros(latent_dim)

    def __call__(self, x):
        h = np.maximum(0, x @ self.W1 + self.b1)
        mu = h @ self.W_mu + self.b_mu
        logvar = h @ self.W_logvar + self.b_logvar
        return mu, logvar


class VAEDecoder:
    """A tiny VAE decoder: latent -> image."""
    def __init__(self, latent_dim=8, img_h=8, img_w=8, hidden=32, seed=0):
        rng = np.random.RandomState(seed)
        self.img_h = img_h
        self.img_w = img_w
        self.W1 = rng.randn(latent_dim, hidden) * 0.1
        self.b1 = np.zeros(hidden)
        self.W2 = rng.randn(hidden, img_h * img_w) * 0.1
        self.b2 = np.zeros(img_h * img_w)

    def __call__(self, z):
        h = np.maximum(0, z @ self.W1 + self.b1)
        out = 1 / (1 + np.exp(-(h @ self.W2 + self.b2)))  # sigmoid
        return out


class TextEncoder:
    """A simple text encoder: token IDs -> embeddings."""
    def __init__(self, vocab_size=100, embed_dim=32, max_len=16, seed=0):
        rng = np.random.RandomState(seed)
        self.embed = rng.randn(vocab_size, embed_dim) * 0.1
        self.max_len = max_len
        self.embed_dim = embed_dim

    def __call__(self, tokens):
        # tokens: (batch, max_len) integer IDs
        return self.embed[tokens]


class CrossAttention:
    """A single-head cross-attention layer: Q from image, K/V from text."""
    def __init__(self, dim=32, text_dim=32, seed=0):
        rng = np.random.RandomState(seed)
        self.W_q = rng.randn(dim, dim) * 0.1
        self.W_k = rng.randn(text_dim, dim) * 0.1
        self.W_v = rng.randn(text_dim, dim) * 0.1
        self.scale = 1.0 / np.sqrt(dim)

    def __call__(self, x, text_emb):
        # x: (batch, n_patches, dim), text_emb: (batch, max_len, text_dim)
        Q = x @ self.W_q
        K = text_emb @ self.W_k
        V = text_emb @ self.W_v
        # Attention: (batch, n_patches, max_len)
        attn = self.scale * (Q @ K.transpose(0, 2, 1))
        attn = attn - attn.max(axis=-1, keepdims=True)
        attn = np.exp(attn)
        attn = attn / attn.sum(axis=-1, keepdims=True)
        # Output: (batch, n_patches, dim)
        return attn @ V


class UNetWithCrossAttention:
    """A tiny U-Net with cross-attention for text conditioning."""
    def __init__(self, latent_dim=8, hidden=32, text_dim=32, time_dim=16, seed=0):
        rng = np.random.RandomState(seed)
        # Time embedding (sinusoidal, simplified)
        self.time_dim = time_dim
        # Encoder
        self.W_enc1 = rng.randn(latent_dim, hidden) * 0.1
        self.W_enc2 = rng.randn(hidden, hidden * 2) * 0.1
        # Bottleneck with cross-attention
        self.cross_attn = CrossAttention(dim=hidden * 2, text_dim=text_dim, seed=seed)
        self.W_bot = rng.randn(hidden * 2, hidden * 2) * 0.1
        # Decoder: concat of bottleneck (hidden*2) + h1 (hidden) = hidden*3
        self.W_dec1 = rng.randn(hidden * 3, hidden) * 0.1
        self.W_dec2 = rng.randn(hidden, latent_dim) * 0.1

    def time_embed(self, t):
        half = self.time_dim // 2
        freqs = np.exp(-np.log(10000.0) * np.arange(half) / half)
        return np.concatenate([np.sin(t * freqs), np.cos(t * freqs)])

    def __call__(self, z, t, text_emb):
        # z: (batch, latent_dim)
        # text_emb: (batch, max_len, text_dim)
        t_emb = self.time_embed(np.array(t))  # (time_dim,)
        # Project t into z's space (skip for simplicity)

        # Encoder
        h1 = np.maximum(0, z @ self.W_enc1)  # (batch, hidden)
        h2 = np.maximum(0, h1 @ self.W_enc2)  # (batch, hidden*2)
        # Add a "patch" dimension for cross-attention
        h2_patched = h2[:, None, :]  # (batch, 1, hidden*2)
        # Cross-attention with text
        attended = self.cross_attn(h2_patched, text_emb)  # (batch, 1, hidden*2)
        attended = attended.squeeze(1)  # (batch, hidden*2)
        # Bottleneck
        b = np.maximum(0, attended @ self.W_bot)  # (batch, hidden*2)
        # Decoder with skip connection: concat(b, h1) -> (batch, hidden*2 + hidden)
        d = np.maximum(0, np.concatenate([b, h1], axis=1) @ self.W_dec1)  # (batch, hidden)
        out = d @ self.W_dec2  # (batch, latent_dim)
        return out


# =============================================================================
# The full pipeline
# =============================================================================

def latent_diffusion_pipeline(
    text_prompt_tokens,  # (batch, max_len)
    T=50,                # diffusion steps
    latent_dim=8,
    img_h=8, img_w=8,
    seed=0,
):
    """
    The full Stable Diffusion pipeline, simplified.
    Returns the generated image.
    """
    rng = np.random.RandomState(seed)
    encoder = VAEEncoder(img_h=img_h, img_w=img_w, latent_dim=latent_dim, seed=seed)
    decoder = VAEDecoder(latent_dim=latent_dim, img_h=img_h, img_w=img_w, seed=seed)
    text_enc = TextEncoder(seed=seed)
    unet = UNetWithCrossAttention(latent_dim=latent_dim, seed=seed)

    # Step 1: encode text
    text_emb = text_enc(text_prompt_tokens)  # (batch, max_len, embed_dim)

    # Step 2: sample z_T ~ N(0, I)
    batch = text_prompt_tokens.shape[0]
    z = rng.randn(batch, latent_dim)

    # Step 3: simple linear schedule
    betas = np.linspace(1e-4, 0.05, T)
    alphas = 1.0 - betas
    alpha_bars = np.cumprod(alphas)

    # Step 4: reverse process
    for t in reversed(range(T)):
        # Predict noise (with cross-attention to text)
        eps_pred = unet(z, t, text_emb)
        a_bar = alpha_bars[t]
        a = alphas[t]
        beta = betas[t]
        mean = (z - (1 - a) / np.sqrt(1 - a_bar) * eps_pred) / np.sqrt(a)
        if t > 0:
            z = mean + np.sqrt(beta) * rng.randn(*z.shape)
        else:
            z = mean

    # Step 5: decode
    image = decoder(z)
    return image.reshape(batch, img_h, img_w)


# =============================================================================
# Visualization: architecture diagram
# =============================================================================

def draw_architecture():
    """Draw the Latent Diffusion architecture."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Boxes
    boxes = [
        (1, 4, 1.5, 1, "Text prompt", "#FFD700"),
        (4, 4, 1.5, 1, "Text encoder", "#FFA500"),
        (1, 1, 1.5, 1, "Image x", "#FF6347"),
        (4, 1, 1.5, 1, "VAE encoder", "#FF6347"),
        (7, 2.5, 2, 1.5, "U-Net (with\ncross-attention)", "#1f77b4"),
        (10.5, 1, 1.5, 1, "VAE decoder", "#90EE90"),
        (12.5, 1, 1.3, 1, "Image x'", "#90EE90"),
        (7, 5, 1.5, 0.6, "noise z_T", "#cccccc"),
    ]
    for x, y, w, h, label, color in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.05",
            edgecolor='black', facecolor=color, linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha='center', va='center', fontsize=10, weight='bold')

    # Arrows
    arrows = [
        ((2.5, 4.5), (4, 4.5)),     # text -> text encoder
        ((5.5, 4), (8, 3.4)),        # text_emb -> U-Net (cross-attention)
        ((2.5, 1.5), (4, 1.5)),     # image -> VAE enc
        ((5.5, 1.5), (7, 2.8)),     # latent -> U-Net
        ((7, 5.3), (8, 3.5)),        # z_T -> U-Net
        ((9, 3.25), (10.5, 1.5)),   # z_0 -> VAE dec
        ((12, 1.5), (12.5, 1.5)),   # VAE dec -> image
    ]
    for (x0, y0), (x1, y1) in arrows:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))

    ax.set_title("Latent Diffusion Model (Stable Diffusion) — architecture",
                 fontsize=14, weight='bold')
    fig.tight_layout()
    os.makedirs("plots", exist_ok=True)
    fig.savefig("plots/ldm_architecture.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ldm_architecture.png")


def draw_pipeline():
    """Draw the data flow through the pipeline."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")

    steps = [
        (0.5, "Text\nprompt"),
        (2.5, "Text\nembeddings"),
        (4.5, "Random\nlatent z_T"),
        (6.5, "Denoised\nlatent z_0"),
        (8.5, "Decoded\nimage"),
        (10.5, "Final\nimage"),
    ]
    for i, (x, label) in enumerate(steps):
        color = ["#FFD700", "#FFA500", "#cccccc", "#1f77b4", "#90EE90", "#FF6347"][i]
        rect = mpatches.FancyBboxPatch(
            (x - 0.5, 1.5), 1.2, 1, boxstyle="round,pad=0.05",
            edgecolor='black', facecolor=color, linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(x + 0.1, 2, label, ha='center', va='center', fontsize=10, weight='bold')
    for i in range(5):
        ax.annotate("", xy=(steps[i + 1][0] - 0.5, 2), xytext=(steps[i][0] + 0.7, 2),
                    arrowprops=dict(arrowstyle="->", lw=1.5, color="black"))
    ax.set_title("Latent Diffusion: end-to-end pipeline", fontsize=14, weight='bold')
    fig.tight_layout()
    fig.savefig("plots/ldm_pipeline.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ldm_pipeline.png")


# =============================================================================
# Run
# =============================================================================

def main():
    print("=" * 60)
    print("Latent Diffusion Model — Architecture Skeleton (NumPy)")
    print("=" * 60)

    # Draw the architecture diagrams
    draw_architecture()
    draw_pipeline()

    # Run a forward pass
    print("Running forward pass with random text prompt...")
    batch = 2
    max_len = 16
    text_prompt_tokens = np.random.randint(0, 100, size=(batch, max_len))
    images = latent_diffusion_pipeline(text_prompt_tokens, T=20, latent_dim=8)
    print(f"Generated images shape: {images.shape}")
    print(f"Pixel range: [{images.min():.3f}, {images.max():.3f}]")

    # Plot
    fig, axes = plt.subplots(1, batch, figsize=(4, 2))
    if batch == 1:
        axes = [axes]
    for i in range(batch):
        axes[i].imshow(images[i], cmap="gray")
        axes[i].axis("off")
    fig.suptitle("Latent Diffusion: skeleton output (untrained)")
    fig.tight_layout()
    fig.savefig("plots/ldm_skeleton_samples.png", dpi=120)
    plt.close(fig)
    print("Saved: plots/ldm_skeleton_samples.png")

    print()
    print("Note: this is an UN-TRAINED architecture skeleton.")
    print("Real Stable Diffusion uses billions of images and weeks of GPU time.")
    print("See the PyTorch version in ddpm_mnist_colab.py for a real training run.")


if __name__ == "__main__":
    main()
