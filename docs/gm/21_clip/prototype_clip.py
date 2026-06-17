"""
Minimal CLIP (Contrastive Language-Image Pre-training).

The idea: Train a text encoder and an image encoder so that matching
pairs have high cosine similarity and non-matching pairs have low.

Training: For a batch of N (text, image) pairs:
  1. Encode all N texts -> T (N, d)
  2. Encode all N images -> I (N, d)
  3. Compute similarity matrix: S = T @ I^T / temperature (N, N)
  4. Diagonal (i,i) is the correct pair, off-diagonal are negatives
  5. Cross-entropy loss in BOTH directions (text->image and image->text)

This is the architecture behind Stable Diffusion's text conditioning
and DALL-E's text-to-image. CLIP is trained once on 400M pairs and
then used as the text encoder for generative models.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


def clip_loss(text_features, image_features, temperature=0.07):
    """
    Contrastive loss (InfoNCE) for CLIP training.

    text_features: (N, d) normalized
    image_features: (N, d) normalized

    Returns: scalar loss
    """
    # Cosine similarity matrix (already normalized, so just dot product)
    logits = text_features @ image_features.T / temperature  # (N, N)

    # Labels: diagonal entries are correct pairs
    labels = torch.arange(logits.shape[0], device=logits.device)

    # Loss in both directions (symmetric)
    loss_t2i = F.cross_entropy(logits, labels)  # text -> image
    loss_i2t = F.cross_entropy(logits.T, labels)  # image -> text

    return (loss_t2i + loss_i2t) / 2


class TinyCLIP(nn.Module):
    """Minimal CLIP: two MLP encoders + shared embedding space."""

    def __init__(self, text_dim=64, image_dim=64, embed_dim=32):
        super().__init__()

        # Text encoder: words -> embedding
        self.text_encoder = nn.Sequential(
            nn.Linear(text_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embed_dim),
        )

        # Image encoder: pixels -> embedding
        self.image_encoder = nn.Sequential(
            nn.Linear(image_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embed_dim),
        )

        # Temperature (learnable, in real CLIP it's a scalar parameter)
        self.logit_scale = nn.Parameter(torch.ones([]) * torch.log(torch.tensor(1 / 0.07)))

    def forward(self, text, image):
        # Encode
        t = self.text_encoder(text)
        i = self.image_encoder(image)

        # Normalize (for cosine similarity)
        t = F.normalize(t, dim=-1)
        i = F.normalize(i, dim=-1)

        return t, i

    def encode_text(self, text):
        return F.normalize(self.text_encoder(text), dim=-1)

    def encode_image(self, image):
        return F.normalize(self.image_encoder(image), dim=-1)


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CLIP Demo: contrastive learning")
    print("=" * 60)

    N = 8  # batch size
    model = TinyCLIP(text_dim=64, image_dim=64, embed_dim=32)

    # Toy data: 8 matching text-image pairs
    # In reality, these would be actual embeddings from a real dataset
    torch.manual_seed(42)
    texts = torch.randn(N, 64)  # 8 text embeddings
    images = torch.randn(N, 64)  # 8 matching image embeddings

    # Before training: random similarity
    with torch.no_grad():
        t, i = model(texts, images)
        sim_before = (t @ i.T).detach()
        diag_before = sim_before.diag().mean().item()
        off_before = (sim_before - torch.diag(sim_before.diag())).mean().item()

    print(f"\nBefore training:")
    print(f"  Avg diagonal sim (correct pairs): {diag_before:.4f}")
    print(f"  Avg off-diagonal sim (noise):    {off_before:.4f}")

    # Train for a few iterations
    opt = torch.optim.Adam(model.parameters(), lr=0.01)
    for step in range(500):
        t, i = model(texts, images)
        loss = clip_loss(t, i, temperature=0.07)
        opt.zero_grad()
        loss.backward()
        opt.step()

    # After training
    with torch.no_grad():
        t, i = model(texts, images)
        sim_after = (t @ i.T).detach()
        diag_after = sim_after.diag().mean().item()
        off_after = (sim_after - torch.diag(sim_after.diag())).mean().item()

    print(f"\nAfter training (500 steps):")
    print(f"  Avg diagonal sim (correct pairs): {diag_after:.4f}")
    print(f"  Avg off-diagonal sim (noise):    {off_after:.4f}")
    print(f"  Separation: {(diag_after - off_after):.4f} "
          f"(was {(diag_before - off_before):.4f})")
    print(f"  Final loss: {loss.item():.6f}")

    # How CLIP is used in Stable Diffusion:
    print(f"\n{'=' * 60}")
    print("How CLIP connects text to images in Stable Diffusion:")
    print(f"  1. Pre-train CLIP on 400M (text, image) pairs (OpenAI)")
    print(f"  2. Freeze CLIP text encoder")
    print(f"  3. At inference: text -> CLIP -> embedding")
    print(f"  4. Embedding is fed to diffusion U-Net via cross-attention")
    print(f"  5. U-Net generates image CONDITIONED on text embedding")
    print(f"\nKey insight: CLIP creates a SHARED space where text and image")
    print(f"meaning are aligned. The diffusion model doesn't need to learn")
    print(f"text understanding — CLIP already did that.")
