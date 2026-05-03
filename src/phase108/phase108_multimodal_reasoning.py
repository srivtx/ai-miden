"""
Phase 108: Multimodal Reasoning
NumPy simulation of cross-modal attention:
image patch embeddings attend to text token embeddings via attention matrix.
Show how alignment works.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


def softmax(x, axis=-1):
    e = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e / np.sum(e, axis=axis, keepdims=True)


def cross_modal_attention(image_patches, text_tokens, W_q, W_k, W_v):
    """
    image_patches: (num_patches, dim)
    text_tokens: (num_tokens, dim)
    Returns attention weights (text_tokens x image_patches) and attended image features.
    """
    Q = text_tokens @ W_q  # (num_tokens, dim)
    K = image_patches @ W_k  # (num_patches, dim)
    V = image_patches @ W_v  # (num_patches, dim)

    scores = Q @ K.T  # (num_tokens, num_patches)
    attn = softmax(scores, axis=-1)
    output = attn @ V  # (num_tokens, dim)
    return attn, output


def main():
    dim = 64
    num_patches = 16  # 4x4 image grid
    num_tokens = 6    # e.g., [CLS] a dog sits on grass

    # Simulate image patches: some patches contain "dog", some "grass"
    image_patches = np.random.randn(num_patches, dim) * 0.3
    # Patch 3 and 7 have dog-like features
    dog_feature = np.random.randn(dim)
    image_patches[3] += dog_feature * 2.0
    image_patches[7] += dog_feature * 1.5
    # Patch 12 and 13 have grass-like features
    grass_feature = np.random.randn(dim)
    image_patches[12] += grass_feature * 2.0
    image_patches[13] += grass_feature * 1.5

    # Simulate text tokens
    text_tokens = np.random.randn(num_tokens, dim) * 0.3
    # Token 2 is "dog", token 5 is "grass"
    text_tokens[2] += dog_feature * 1.5
    text_tokens[5] += grass_feature * 1.5

    # Random projection matrices (shared dim for simplicity)
    W_q = np.random.randn(dim, dim) * 0.1
    W_k = np.random.randn(dim, dim) * 0.1
    W_v = np.random.randn(dim, dim) * 0.1

    attn, output = cross_modal_attention(image_patches, text_tokens, W_q, W_k, W_v)

    print("Cross-modal attention shape:", attn.shape)
    print("Attention weights for 'dog' token (token 2):")
    print(np.round(attn[2], 3))
    print("Top attended patch for 'dog':", np.argmax(attn[2]))
    print()
    print("Attention weights for 'grass' token (token 5):")
    print(np.round(attn[5], 3))
    print("Top attended patch for 'grass':", np.argmax(attn[5]))
    print()

    # Plot attention heatmap
    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(attn, aspect='auto', cmap='viridis')
    ax.set_xlabel('Image patch index')
    ax.set_ylabel('Text token index')
    ax.set_title('Cross-Modal Attention: Text Tokens -> Image Patches')
    fig.colorbar(im, ax=ax, label='Attention weight')
    # Mark the dog and grass patches
    ax.axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Dog patches')
    ax.axvline(x=7, color='red', linestyle='--', alpha=0.5)
    ax.axvline(x=12, color='green', linestyle='--', alpha=0.5, label='Grass patches')
    ax.axvline(x=13, color='green', linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    fig.tight_layout()
    fig.savefig('src/phase108/cross_modal_attention.png')
    print("Saved plot to src/phase108/cross_modal_attention.png")


if __name__ == '__main__':
    main()
