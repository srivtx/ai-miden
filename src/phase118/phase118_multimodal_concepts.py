"""
Phase 118: Native Multimodal Architectures (Early Fusion)
NumPy simulation of image tokenization and early vs late fusion.

We show:
1. A tiny 8x8 image is split into patches and quantized to a discrete codebook.
2. The resulting image tokens are interleaved with text tokens in one sequence.
3. A single self-attention layer processes the mixed sequence (early fusion).
4. We contrast this with late fusion: separate encoders whose outputs are concatenated.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless backend for safe script execution.
import matplotlib.pyplot as plt

np.random.seed(118)

# ------------------------------------------------------------------------------
# 1. Build a tiny synthetic image
# ------------------------------------------------------------------------------
# An 8x8 RGB image with distinct geometric regions so quantization errors are visible.
img = np.zeros((8, 8, 3))
img[:4, :4, 0] = 1.0   # red block top-left
img[4:, 4:, 1] = 1.0   # green block bottom-right
img[:, :, 2] = np.linspace(0, 1, 8).reshape(1, 8)  # blue horizontal gradient

# ------------------------------------------------------------------------------
# 2. Patchify into 2x2 patches -> 16 patches, each 2x2x3 = 12 floats
# ------------------------------------------------------------------------------
patch_size = 2
h, w, c = img.shape
n_patches_h = h // patch_size
n_patches_w = w // patch_size
n_patches = n_patches_h * n_patches_w
patch_dim = patch_size * patch_size * c

patches = []
for i in range(n_patches_h):
    for j in range(n_patches_w):
        patch = img[i*patch_size:(i+1)*patch_size, j*patch_size:(j+1)*patch_size, :]
        patches.append(patch.flatten())
patches = np.stack(patches)  # shape (16, 12)

# ------------------------------------------------------------------------------
# 3. Simulate a learned VQ-VAE codebook
# ------------------------------------------------------------------------------
# In reality the codebook is trained end-to-end; here we pick random patches as centroids.
codebook_size = 8
rng = np.random.default_rng(118)
centroid_idx = rng.choice(n_patches, codebook_size, replace=False)
codebook = patches[centroid_idx].astype(np.float32)  # (8, 12)

def quantize(patches, codebook):
    """Nearest-neighbor assignment in L2 space."""
    # dists[i, j] = distance from patch i to codebook vector j
    dists = np.sum((patches[:, None, :] - codebook[None, :, :]) ** 2, axis=2)
    token_ids = np.argmin(dists, axis=1)
    return token_ids, codebook[token_ids]

token_ids, quantized_patches = quantize(patches, codebook)

# ------------------------------------------------------------------------------
# 4. Reconstruct the image from quantized patches
# ------------------------------------------------------------------------------
recon_patches = quantized_patches.reshape(n_patches_h, n_patches_w, patch_size, patch_size, c)
recon_img = np.zeros_like(img)
for i in range(n_patches_h):
    for j in range(n_patches_w):
        recon_img[i*patch_size:(i+1)*patch_size, j*patch_size:(j+1)*patch_size, :] = recon_patches[i, j]

# ------------------------------------------------------------------------------
# 5. Build an interleaved text + image token sequence
# ------------------------------------------------------------------------------
text_tokens = np.array([101, 234, 56, 89])          # Simulated vocabulary IDs for text.
image_vocab_offset = 1000                           # Image tokens live at a higher index.
image_tokens = token_ids + image_vocab_offset
full_sequence = np.concatenate([text_tokens, image_tokens])
seq_len = len(full_sequence)

# ------------------------------------------------------------------------------
# 6. Early fusion: single self-attention over the mixed sequence
# ------------------------------------------------------------------------------
embed_dim = 16
emb_table = rng.standard_normal((2000, embed_dim), dtype=np.float32) * 0.1
seq_emb = emb_table[full_sequence]  # (seq_len, embed_dim)

# Random projection matrices for one attention head.
W_q = rng.standard_normal((embed_dim, embed_dim), dtype=np.float32) * 0.1
W_k = rng.standard_normal((embed_dim, embed_dim), dtype=np.float32) * 0.1
W_v = rng.standard_normal((embed_dim, embed_dim), dtype=np.float32) * 0.1

Q = seq_emb @ W_q
K = seq_emb @ W_k
V = seq_emb @ W_v

scores = Q @ K.T / np.sqrt(embed_dim)
attn = np.exp(scores - np.max(scores, axis=1, keepdims=True))
attn = attn / np.sum(attn, axis=1, keepdims=True)
out = attn @ V  # (seq_len, embed_dim)

# ------------------------------------------------------------------------------
# 7. Late fusion: separate mean-pooled encoders, then concatenate
# ------------------------------------------------------------------------------
# Vision side: compress all image tokens into one vector.
vision_feature = np.mean(seq_emb[len(text_tokens):], axis=0)  # (embed_dim,)
# Text side: compress all text tokens into one vector.
text_feature = np.mean(seq_emb[:len(text_tokens)], axis=0)    # (embed_dim,)
late_fusion = np.concatenate([text_feature, vision_feature])  # (2*embed_dim,)

# ------------------------------------------------------------------------------
# 8. Visualizations
# ------------------------------------------------------------------------------

# --- Original vs Reconstructed ---
fig, axes = plt.subplots(1, 2, figsize=(8, 4))
axes[0].imshow(np.clip(img, 0, 1))
axes[0].set_title('Original 8x8 Image')
axes[0].axis('off')
axes[1].imshow(np.clip(recon_img, 0, 1))
axes[1].set_title(f'Reconstructed (Codebook size {codebook_size})')
axes[1].axis('off')
fig.tight_layout()
fig.savefig('src/phase118/original_vs_tokenized.png')
print("Saved src/phase118/original_vs_tokenized.png")

# --- Interleaved Token Sequence ---
fig, ax = plt.subplots(figsize=(12, 3))
colors_seq = ['blue'] * len(text_tokens) + ['red'] * len(image_tokens)
ax.bar(range(seq_len), [1]*seq_len, color=colors_seq, width=1.0, edgecolor='black')
ax.set_xlabel('Sequence Position')
ax.set_ylabel('Token Presence')
ax.set_title('Interleaved Sequence: Text Tokens (blue) and Image Tokens (red)')
ax.set_xticks(range(seq_len))
labels = [f'T{t}' for t in text_tokens] + [f'I{i}' for i in token_ids]
ax.set_xticklabels(labels, rotation=90, fontsize=8)
fig.tight_layout()
fig.savefig('src/phase118/token_sequence.png')
print("Saved src/phase118/token_sequence.png")

# --- Attention Heatmap (Early Fusion) ---
fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(attn, cmap='viridis', aspect='auto')
ax.set_xticks(range(seq_len))
ax.set_yticks(range(seq_len))
labels = [f'Text{i}' for i in range(len(text_tokens))] + [f'Img{i}' for i in range(len(image_tokens))]
ax.set_xticklabels(labels, rotation=90, fontsize=8)
ax.set_yticklabels(labels, fontsize=8)
ax.set_title('Early Fusion: Self-Attention Heatmap (Text + Image Tokens)')
fig.colorbar(im, ax=ax)
fig.tight_layout()
fig.savefig('src/phase118/attention_heatmap.png')
print("Saved src/phase118/attention_heatmap.png")

# ------------------------------------------------------------------------------
# 9. Console summary
# ------------------------------------------------------------------------------
print("\n--- Fusion Comparison ---")
print(f"Early fusion output shape: {out.shape} (single stream, {seq_len} tokens)")
print(f"Late fusion output shape: {late_fusion.shape} (two separate streams concatenated)")
print("Early fusion allows every token to attend to every other token in every layer.")
print("Late fusion compresses the image into a summary vector before merging.")
