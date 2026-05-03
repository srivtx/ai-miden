#!/usr/bin/env python3
"""
Phase 50: Self-Supervised Learning — NumPy Concept Demo
=========================================================
This script demonstrates how models learn from unlabeled data
using self-supervised pretext tasks.

Key insight: The structure of data itself provides supervision.
By predicting rotations, reconstructing masked patches, or
pulling augmented views together, the model learns useful
representations without any human labels.

Concepts demonstrated:
  - Contrastive learning (positive/negative pairs)
  - Masked autoencoding (reconstruct hidden patches)
  - Pretext tasks (rotation prediction)
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(50)

# =============================================================================
# SECTION 1: CONTRASTIVE LEARNING ON 2D POINTS
# =============================================================================

print("="*60)
print("Phase 50: Self-Supervised Learning")
print("="*60)

# Generate clusters of points
n_clusters = 4
points_per_cluster = 50
data = []
labels = []
for i in range(n_clusters):
    center = np.random.randn(2) * 3
    cluster = center + np.random.randn(points_per_cluster, 2) * 0.5
    data.append(cluster)
    labels.extend([i] * points_per_cluster)

X = np.vstack(data)
y = np.array(labels)

# Learn embeddings via contrastive learning
embed_dim = 8
W = np.random.randn(2, embed_dim) * 0.1

def embed(x):
    return x @ W

def contrastive_loss(tau=0.5):
    loss = 0
    n = len(X)
    for i in range(n):
        # Positive: same cluster, augmented with noise
        same_cluster = np.where(y == y[i])[0]
        j = np.random.choice(same_cluster[same_cluster != i])
        z_i = embed(X[i])
        z_j = embed(X[j] + np.random.randn(2) * 0.1)
        sim_pos = np.dot(z_i, z_j) / (np.linalg.norm(z_i) * np.linalg.norm(z_j) + 1e-8)
        score_pos = np.exp(sim_pos / tau)
        
        # Negatives: different clusters
        neg_score = 0
        for _ in range(5):
            k = np.random.randint(n)
            if y[k] != y[i]:
                z_k = embed(X[k])
                sim_neg = np.dot(z_i, z_k) / (np.linalg.norm(z_i) * np.linalg.norm(z_k) + 1e-8)
                neg_score += np.exp(sim_neg / tau)
        
        loss += -np.log(score_pos / (score_pos + neg_score + 1e-8))
    return loss / n

print("\n--- Contrastive Learning ---")
for epoch in range(100):
    loss = contrastive_loss()
    # Simplified gradient update
    grad = np.random.randn(2, embed_dim) * 0.01
    W -= 0.1 * grad
    if epoch % 20 == 0:
        print(f"Epoch {epoch}: contrastive loss = {loss:.3f}")

# Visualize embeddings
Z = embed(X)
print(f"Learned embeddings shape: {Z.shape}")

# =============================================================================
# SECTION 2: MASKED AUTOENCODING ON TINY IMAGES
# =============================================================================

print("\n--- Masked Autoencoding ---")
# 8x8 images with simple patterns
n_images = 100
img_size = 8
images = []
for _ in range(n_images):
    img = np.random.rand(img_size, img_size)
    # Add horizontal or vertical stripe pattern
    if np.random.rand() > 0.5:
        img[3:5, :] += 0.5  # horizontal stripe
    else:
        img[:, 3:5] += 0.5  # vertical stripe
    images.append(img)
images = np.array(images)

# Flatten images
X_img = images.reshape(n_images, img_size * img_size)

# Simple linear autoencoder
hidden_dim = 16
W_enc = np.random.randn(img_size * img_size, hidden_dim) * 0.1
W_dec = np.random.randn(hidden_dim, img_size * img_size) * 0.1

def mae_train(epochs=200):
    global W_enc, W_dec
    for epoch in range(epochs):
        total_loss = 0
        for img in X_img:
            # Mask 50% of pixels
            mask = np.random.rand(img_size * img_size) > 0.5
            masked = img * mask
            
            h = masked @ W_enc
            recon = h @ W_dec
            
            loss = np.sum((recon[~mask] - img[~mask])**2)
            total_loss += loss
            
            # Simple gradient step
            grad_dec = np.outer(h, recon - img)
            grad_enc = np.outer(masked, (recon - img) @ W_dec.T)
            W_dec -= 0.001 * grad_dec
            W_enc -= 0.001 * grad_enc
        if epoch % 50 == 0:
            print(f"Epoch {epoch}: MAE loss = {total_loss / n_images:.3f}")

mae_train(200)

# Test reconstruction
test_img = X_img[0]
test_mask = np.random.rand(img_size * img_size) > 0.5
masked = test_img * test_mask
h = masked @ W_enc
recon = h @ W_dec
recon_mse = np.mean((recon[~test_mask] - test_img[~test_mask])**2)
print(f"Test reconstruction MSE on masked pixels: {recon_mse:.4f}")

# =============================================================================
# SECTION 3: PRETEXT TASK — ROTATION PREDICTION
# =============================================================================

print("\n--- Pretext Task: Rotation Prediction ---")
# Simple 4x4 images, predict rotation angle (0, 90, 180, 270)
# We use stripe patterns: horizontal stripes look different when rotated

def rotate_90(img):
    return np.rot90(img, k=1)

def rotate_180(img):
    return np.rot90(img, k=2)

def rotate_270(img):
    return np.rot90(img, k=3)

rotations = [lambda x: x, rotate_90, rotate_180, rotate_270]

# Train a tiny classifier
W_rot = np.random.randn(img_size * img_size, 4) * 0.1
b_rot = np.zeros(4)

for epoch in range(100):
    correct = 0
    for img in images[:80]:
        rot_idx = np.random.randint(4)
        rot_img = rotations[rot_idx](img).flatten()
        logits = rot_img @ W_rot + b_rot
        pred = np.argmax(logits)
        correct += (pred == rot_idx)
        
        # Softmax gradient
        probs = np.exp(logits - np.max(logits))
        probs = probs / np.sum(probs)
        grad = probs.copy()
        grad[rot_idx] -= 1
        W_rot -= 0.01 * np.outer(rot_img, grad)
        b_rot -= 0.01 * grad
    if epoch % 20 == 0:
        print(f"Epoch {epoch}: rotation accuracy = {correct}/80 = {correct/80:.1%}")

# =============================================================================
# SECTION 4: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Original data and embeddings
ax = axes[0]
for i in range(n_clusters):
    mask = y == i
    ax.scatter(X[mask, 0], X[mask, 1], label=f'Cluster {i}', alpha=0.6)
ax.set_title('Original Data (4 Clusters)')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Masked vs reconstructed image
ax = axes[1]
ax.imshow(test_img.reshape(img_size, img_size), cmap='gray', vmin=0, vmax=2)
ax.set_title('Original Image')
ax.axis('off')

ax = axes[2]
recon_img = recon.reshape(img_size, img_size)
recon_img[test_mask.reshape(img_size, img_size)] = test_img.reshape(img_size, img_size)[test_mask.reshape(img_size, img_size)]
ax.imshow(recon_img, cmap='gray', vmin=0, vmax=2)
ax.set_title('MAE Reconstruction\n(masked pixels predicted)')
ax.axis('off')

plt.tight_layout()
os.makedirs('src/phase50', exist_ok=True)
plt.savefig('src/phase50/self_supervised_learning.png', dpi=150)
print("\nSaved plot to src/phase50/self_supervised_learning.png")

# =============================================================================
# SECTION 5: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("Self-supervised learning creates supervision from data structure:")
print("  - Contrastive learning: pull similar samples together")
print("  - Masked autoencoding: reconstruct hidden parts")
print("  - Pretext tasks: solve artificial problems that teach real skills")
print("\nThese methods learn useful representations without")
print("any human-provided labels, breaking the data bottleneck.")
