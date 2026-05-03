#!/usr/bin/env python3
"""
================================================================================
Phase 28: Multimodal AI — Models That See and Read
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 27, we gave the model tools to ACT.
But those tools only processed text.

This phase answers: "Can the model also SEE images,
HEAR audio, and understand multiple types of data?"

We cover five concepts:
  1. Vision Transformer (ViT)    — Transformers for images
  2. CLIP                         — Text + images in one space
  3. Shared Embedding Space       — Aligning modalities
  4. DALL-E / Stable Diffusion    — Images from text
  5. GPT-4o                       — Unified multimodal reasoning

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# PART 1: VISION TRANSFORMER (ViT)
# ==============================================================================
# Instead of sliding filters (CNN), ViT cuts the image into patches,
# flattens each patch into a vector, and feeds them to a Transformer.
# It's BERT for images.
# ==============================================================================

def create_image_patches(image, patch_size):
    """
    Split an image into non-overlapping patches.
    
    PARAMETERS:
        image      = H x W array (grayscale for simplicity)
        patch_size = int, e.g., 2 for 2x2 patches
    
    RETURNS:
        patches = (num_patches, patch_size*patch_size) array
    """
    h, w = image.shape
    num_patches_h = h // patch_size
    num_patches_w = w // patch_size
    num_patches = num_patches_h * num_patches_w

    patches = np.zeros((num_patches, patch_size * patch_size))
    idx = 0
    for i in range(num_patches_h):
        for j in range(num_patches_w):
            patch = image[i*patch_size:(i+1)*patch_size,
                          j*patch_size:(j+1)*patch_size]
            patches[idx] = patch.flatten()
            idx += 1

    return patches


def add_positional_embeddings(patches, d_model):
    """
    Add learnable positional embeddings to each patch.
    
    Without this, the Transformer cannot tell where each patch
    came from in the image. A patch from top-left is different
    from the same patch in bottom-right.
    """
    num_patches = patches.shape[0]
    # Random init for demo; in reality these are learned during training
    np.random.seed(42)
    pos_embed = np.random.randn(num_patches, d_model) * 0.02
    return patches + pos_embed


def softmax(x):
    """Numerically stable softmax."""
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def self_attention(X):
    """Simple single-head self-attention."""
    d = X.shape[1]
    np.random.seed(1)
    W_q = np.random.randn(d, d) * 0.1
    W_k = np.random.randn(d, d) * 0.1
    W_v = np.random.randn(d, d) * 0.1

    Q = X @ W_q
    K = X @ W_k
    V = X @ W_v

    scores = Q @ K.T / np.sqrt(d)
    attn_weights = softmax(scores)
    output = attn_weights @ V
    return output, attn_weights


def demonstrate_vit():
    """Show how ViT processes an image as a sequence of patches."""
    print("=" * 60)
    print("PART 1: VISION TRANSFORMER (ViT)")
    print("=" * 60)
    print()
    print("  Instead of CNN filters, ViT cuts the image into patches.")
    print("  Each patch becomes a 'token,' just like words in BERT.")
    print()

    # Create a simple 8x8 image: a bright square in the center
    image = np.zeros((8, 8))
    image[3:5, 3:5] = 1.0  # 2x2 bright square in center

    print("  Original image (8x8):")
    print("  " + str(image).replace('\n', '\n  '))
    print()

    # Split into 2x2 patches
    patch_size = 2
    patches = create_image_patches(image, patch_size)
    num_patches_h = 8 // patch_size
    num_patches_w = 8 // patch_size

    print(f"  Number of patches: {patches.shape[0]} ({num_patches_h}x{num_patches_w})")
    print(f"  Each patch flattened to: {patches.shape[1]} numbers")
    print()
    print("  Patches (flattened):")
    for i, p in enumerate(patches):
        print(f"    Patch {i}: {p}")
    print()

    # Add positional embeddings
    d_model = 4
    patches_with_pos = add_positional_embeddings(patches, d_model)
    print("  Added positional embeddings (so model knows patch location).")
    print()

    # Add CLS token (like BERT)
    cls_token = np.random.randn(1, d_model) * 0.02
    sequence = np.vstack([cls_token, patches_with_pos])
    print(f"  Sequence length: {sequence.shape[0]} (1 CLS + {patches.shape[0]} patches)")
    print()

    # Self-attention over patches
    output, attn = self_attention(sequence)
    print("  Self-attention computed over all patches.")
    print(f"  Attention shape: {attn.shape}")
    print(f"  CLS token attends most to patch {np.argmax(attn[0, 1:])} (center patch with bright square)")
    print()

    print("  KEY INSIGHT:")
    print("    CNNs use sliding filters. ViT uses patch tokens.")
    print("    The CLS token's final state is used for classification.")
    print("    No convolutions. Pure Transformer.")
    print()

    # Visualize
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(image, cmap='gray', vmin=0, vmax=1)
    axes[0].set_title('Original Image (8x8)', fontweight='bold')
    axes[0].axis('off')

    # Show patches as grid
    patch_grid = np.zeros((num_patches_h, num_patches_w))
    for i in range(num_patches_h):
        for j in range(num_patches_w):
            patch_grid[i, j] = patches[i * num_patches_w + j].mean()
    axes[1].imshow(patch_grid, cmap='gray', vmin=0, vmax=1)
    axes[1].set_title('Patch Averages (2x2 patches)', fontweight='bold')
    axes[1].axis('off')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase28/vit_patches.png', dpi=150)
    print("  Plot saved: src/phase28/vit_patches.png")
    plt.close()
    print()


# ==============================================================================
# PART 2: CLIP — CONTRASTIVE LANGUAGE-IMAGE PRE-TRAINING
# ==============================================================================
# CLIP trains an image encoder and a text encoder together.
# Matching pairs are pulled together. Non-matching pairs are pushed apart.
# ==============================================================================

def clip_contrastive_loss(image_embeds, text_embeds, temperature=0.07):
    """
    Compute CLIP's symmetric contrastive loss.
    
    PARAMETERS:
        image_embeds = (batch_size, d) array, L2-normalized
        text_embeds  = (batch_size, d) array, L2-normalized
        temperature  = scaling factor
    
    RETURNS:
        loss = scalar
    """
    batch_size = image_embeds.shape[0]

    # Cosine similarity matrix
    logits = (image_embeds @ text_embeds.T) / temperature

    # Labels: diagonal elements are the matching pairs
    labels = np.arange(batch_size)

    # Cross-entropy loss in both directions
    # Image -> text
    logits_i2t = logits
    exp_i2t = np.exp(logits_i2t - np.max(logits_i2t, axis=1, keepdims=True))
    probs_i2t = exp_i2t / np.sum(exp_i2t, axis=1, keepdims=True)
    loss_i2t = -np.mean(np.log(probs_i2t[np.arange(batch_size), labels] + 1e-8))

    # Text -> image
    logits_t2i = logits.T
    exp_t2i = np.exp(logits_t2i - np.max(logits_t2i, axis=1, keepdims=True))
    probs_t2i = exp_t2i / np.sum(exp_t2i, axis=1, keepdims=True)
    loss_t2i = -np.mean(np.log(probs_t2i[np.arange(batch_size), labels] + 1e-8))

    return (loss_i2t + loss_t2i) / 2


def normalize(x):
    """L2 normalize rows."""
    return x / (np.linalg.norm(x, axis=1, keepdims=True) + 1e-8)


def demonstrate_clip():
    """Show how CLIP aligns image and text embeddings."""
    print("=" * 60)
    print("PART 2: CLIP — ALIGNING IMAGES AND TEXT")
    print("=" * 60)
    print()
    print("  CLIP learns one vector space for BOTH images and text.")
    print("  A dog photo and the text 'dog' become neighbors.")
    print()

    np.random.seed(42)

    # Simulate 3 image-text pairs
    # In reality, these come from neural network encoders
    # Here we simulate with simple vectors
    d = 8

    # Image embeddings (before training: random)
    image_circle = np.random.randn(d) * 0.5
    image_square = np.random.randn(d) * 0.5
    image_triangle = np.random.randn(d) * 0.5

    # Text embeddings (before training: random)
    text_circle = np.random.randn(d) * 0.5
    text_square = np.random.randn(d) * 0.5
    text_triangle = np.random.randn(d) * 0.5

    image_embeds = normalize(np.array([image_circle, image_square, image_triangle]))
    text_embeds = normalize(np.array([text_circle, text_square, text_triangle]))

    print("  BEFORE TRAINING:")
    print("  Similarity matrix (image rows, text columns):")
    sim_before = image_embeds @ text_embeds.T
    print("  " + str(np.round(sim_before, 3)).replace('\n', '\n  '))
    print("  Diagonal (matching pairs) should be highest, but they are mixed.")
    print()

    # Simulate training by pushing matching pairs together
    # In reality, this is gradient descent on the contrastive loss
    learning_rate = 0.5
    for step in range(100):
        # Simple manual update: push matching pairs closer
        for i in range(3):
            diff = text_embeds[i] - image_embeds[i]
            image_embeds[i] += learning_rate * diff * 0.01
            text_embeds[i] -= learning_rate * diff * 0.01
        image_embeds = normalize(image_embeds)
        text_embeds = normalize(text_embeds)

    print("  AFTER TRAINING (simulated contrastive learning):")
    sim_after = image_embeds @ text_embeds.T
    print("  Similarity matrix:")
    print("  " + str(np.round(sim_after, 3)).replace('\n', '\n  '))
    print("  Diagonal values are now highest! Matching pairs aligned.")
    print()

    # Zero-shot classification
    print("  ZERO-SHOT CLASSIFICATION:")
    print("  New image (simulated as circle-like vector):")
    new_image = normalize(np.array([image_embeds[0] + np.random.randn(d)*0.1]))
    similarities = new_image @ text_embeds.T
    labels = ["circle", "square", "triangle"]
    for label, sim in zip(labels, similarities[0]):
        print(f"    Similarity to '{label}': {sim:.3f}")
    predicted = labels[np.argmax(similarities)]
    print(f"    Predicted label: '{predicted}' (no training on this label!)")
    print()

    print("  KEY INSIGHT:")
    print("    CLIP never saw a labeled dataset of circles/squares/triangles.")
    print("    It learned from image-text pairs on the internet.")
    print("    Now it can classify ANYTHING you can describe in text.")
    print()


# ==============================================================================
# PART 3: SHARED EMBEDDING SPACE
# ==============================================================================
# Visualize how images and text occupy the same coordinates.
# ==============================================================================

def demonstrate_shared_space():
    """Visualize the shared embedding space."""
    print("=" * 60)
    print("PART 3: SHARED EMBEDDING SPACE")
    print("=" * 60)
    print()
    print("  Images and text live in the SAME vector space.")
    print("  We plot them in 2D to see the alignment.")
    print()

    np.random.seed(7)

    # Create embeddings in 2D for visualization
    # Dog cluster
    dog_images = np.random.randn(3, 2) * 0.15 + np.array([1.0, 0.5])
    dog_texts = np.random.randn(3, 2) * 0.15 + np.array([1.1, 0.4])

    # Cat cluster
    cat_images = np.random.randn(3, 2) * 0.15 + np.array([-0.5, 1.0])
    cat_texts = np.random.randn(3, 2) * 0.15 + np.array([-0.4, 0.9])

    # Car cluster
    car_images = np.random.randn(3, 2) * 0.15 + np.array([0.5, -0.8])
    car_texts = np.random.randn(3, 2) * 0.15 + np.array([0.4, -0.7])

    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot dog
    ax.scatter(dog_images[:, 0], dog_images[:, 1], c='blue', s=150, marker='o', label='Dog Images', alpha=0.7)
    ax.scatter(dog_texts[:, 0], dog_texts[:, 1], c='blue', s=150, marker='s', label='Dog Texts', alpha=0.7)

    # Plot cat
    ax.scatter(cat_images[:, 0], cat_images[:, 1], c='red', s=150, marker='o', label='Cat Images', alpha=0.7)
    ax.scatter(cat_texts[:, 0], cat_texts[:, 1], c='red', s=150, marker='s', label='Cat Texts', alpha=0.7)

    # Plot car
    ax.scatter(car_images[:, 0], car_images[:, 1], c='green', s=150, marker='o', label='Car Images', alpha=0.7)
    ax.scatter(car_texts[:, 0], car_texts[:, 1], c='green', s=150, marker='s', label='Car Texts', alpha=0.7)

    # Draw lines between matching image-text pairs
    for img, txt in zip(dog_images, dog_texts):
        ax.plot([img[0], txt[0]], [img[1], txt[1]], 'b--', alpha=0.3)
    for img, txt in zip(cat_images, cat_texts):
        ax.plot([img[0], txt[0]], [img[1], txt[1]], 'r--', alpha=0.3)
    for img, txt in zip(car_images, car_texts):
        ax.plot([img[0], txt[0]], [img[1], txt[1]], 'g--', alpha=0.3)

    ax.set_xlabel('Dimension 1', fontsize=12)
    ax.set_ylabel('Dimension 2', fontsize=12)
    ax.set_title('Shared Embedding Space: Images and Text', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase28/shared_embedding_space.png', dpi=150)
    print("  Plot saved: src/phase28/shared_embedding_space.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    Circles = images, Squares = text.")
    print("    Same color = same concept (dog/cat/car).")
    print("    Dashed lines show matching pairs are close.")
    print("    A new dog image would land near the blue cluster.")
    print("    The nearest text would be 'dog' — zero-shot classification!")
    print()


# ==============================================================================
# PART 4: DIFFUSION (DALL-E / Stable Diffusion concept)
# ==============================================================================
# Start with random noise. Gradually remove noise, guided by text.
# Each step makes the image slightly clearer.
# ==============================================================================

def demonstrate_diffusion():
    """Simulate a tiny diffusion process."""
    print("=" * 60)
    print("PART 4: DIFFUSION — IMAGES FROM TEXT")
    print("=" * 60)
    print()
    print("  Diffusion starts with random noise.")
    print("  Each step removes a little noise, guided by text.")
    print()

    np.random.seed(3)

    # Target: an 8x8 image with a red circle in the center
    # We'll simulate in grayscale for simplicity
    target = np.zeros((8, 8))
    for i in range(8):
        for j in range(8):
            dist = np.sqrt((i - 3.5)**2 + (j - 3.5)**2)
            if dist < 2.5:
                target[i, j] = 1.0 - dist / 2.5

    # Start with pure noise
    noise = np.random.randn(8, 8) * 0.5
    current = noise.copy()

    # Simulate denoising steps
    # In reality, a neural network predicts the noise at each step
    # Here we linearly interpolate toward the target for demonstration
    steps = [0, 3, 6, 9]
    images = [current.copy()]

    for step in range(1, 10):
        # Gradually move from noise toward target
        alpha = step / 10.0
        # Add some randomness to simulate imperfect prediction
        predicted_noise = (1 - alpha) * noise + np.random.randn(8, 8) * 0.05 * (1 - alpha)
        current = target * alpha + predicted_noise
        current = np.clip(current, 0, 1)
        if step in steps[1:]:
            images.append(current.copy())

    images.append(target.copy())

    fig, axes = plt.subplots(1, len(images), figsize=(15, 3))
    titles = ['Step 0\n(Noise)', 'Step 3', 'Step 6', 'Step 9', 'Final\n(Target)']
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img, cmap='gray', vmin=0, vmax=1)
        ax.set_title(title, fontweight='bold')
        ax.axis('off')

    plt.suptitle('Diffusion Process: Noise → Circle', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase28/diffusion_process.png', dpi=150)
    print("  Plot saved: src/phase28/diffusion_process.png")
    plt.close()
    print()

    print("  KEY INSIGHT:")
    print("    Step 0: Pure random noise. No structure.")
    print("    Step 3: A blurry blob emerges.")
    print("    Step 6: Round shape becomes visible.")
    print("    Step 9: Almost there, refining edges.")
    print("    Final: A clear circle.")
    print("    The text embedding GUIDES which shape emerges.")
    print()


# ==============================================================================
# PART 5: UNIFIED MULTIMODAL REASONING (GPT-4o concept)
# ==============================================================================
# Process image patches AND text tokens in the SAME attention layer.
# ==============================================================================

def demonstrate_unified_multimodal():
    """Show image and text tokens processed together."""
    print("=" * 60)
    print("PART 5: UNIFIED MULTIMODAL REASONING")
    print("=" * 60)
    print()
    print("  GPT-4o processes images and text in the SAME model.")
    print("  No separate image captioning step.")
    print()

    # Simulate: 4 text tokens + 4 image patches = 8 tokens total
    d = 6
    np.random.seed(5)

    text_tokens = np.random.randn(4, d) * 0.3
    image_patches = np.random.randn(4, d) * 0.3

    # Mark them differently for visualization
    labels = ['T1', 'T2', 'T3', 'T4', 'I1', 'I2', 'I3', 'I4']
    colors = ['blue'] * 4 + ['red'] * 4

    combined = np.vstack([text_tokens, image_patches])

    # Self-attention over ALL tokens (text + image together)
    output, attn = self_attention(combined)

    print("  Input sequence: 4 text tokens + 4 image patches = 8 tokens")
    print("  All 8 tokens attend to each other in ONE attention layer.")
    print()

    # Show attention from text token T1 to image patches
    print("  Attention weights FROM text token T1:")
    for i, label in enumerate(labels):
        print(f"    To {label}: {attn[0, i]:.3f}")
    print(f"  T1 attends most to image patch: I{np.argmax(attn[0, 4:])}")
    print()

    print("  KEY INSIGHT:")
    print("    In old systems: Image → Caption text → Language model")
    print("    In unified systems: Image patches + Text tokens → ONE model")
    print("    Information flows directly. No translation loss.")
    print("    The model 'sees' the image and 'reads' the text together.")
    print()

    # Visualize attention matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(attn, cmap='hot', interpolation='nearest')
    ax.set_xticks(range(8))
    ax.set_yticks(range(8))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Key Tokens', fontsize=12)
    ax.set_ylabel('Query Tokens', fontsize=12)
    ax.set_title('Cross-Modal Attention: Text ↔ Image', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Attention Weight')
    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase28/cross_modal_attention.png', dpi=150)
    print("  Plot saved: src/phase28/cross_modal_attention.png")
    plt.close()
    print()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 28: MULTIMODAL AI")
    print("=" * 60)
    print()
    print("  Goal: Make the model see images and understand multiple modalities.")
    print()

    # Part 1: ViT
    demonstrate_vit()

    # Part 2: CLIP
    demonstrate_clip()

    # Part 3: Shared Embedding Space
    demonstrate_shared_space()

    # Part 4: Diffusion
    demonstrate_diffusion()

    # Part 5: Unified Multimodal
    demonstrate_unified_multimodal()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - ViT: Image patches as Transformer tokens")
    print("    - CLIP: Contrastive learning aligns images and text")
    print("    - Shared embedding space visualization")
    print("    - Diffusion: Noise gradually becomes an image")
    print("    - Unified attention: Text and image tokens together")
    print()
    print("  KEY INSIGHTS:")
    print("    1. ViT removes CNNs entirely — patches are tokens.")
    print("    2. CLIP learns from internet image-text pairs, not labels.")
    print("    3. Shared space means any modality can query any other.")
    print("    4. Diffusion generates images by reversing noise step-by-step.")
    print("    5. Unified models process everything in one architecture.")
    print()
    print("  NEXT QUESTION:")
    print("    'The model can see and read. Can it CREATE entirely")
    print("     new images from scratch?'")
    print("=" * 60)
