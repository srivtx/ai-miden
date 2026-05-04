#!/usr/bin/env python3
"""
Phase 149: Multimodal RAG Concepts — NumPy Simulation
=======================================================
This script demonstrates three core ideas of multimodal RAG using only NumPy:

  1. Unified embedding space: text and image vectors live in the same space.
  2. Cross-modal retrieval: a text query retrieves image vectors and vice versa.
  3. Multimodal reasoning: weighted fusion of conflicting evidence beats
     naive averaging.

We simulate 8 concepts (cat, dog, car, tree, house, phone, boat, bird).
For each concept we create:
  - one text vector (e.g., "a domestic cat")
  - one image vector (e.g., photo of a cat)
  - one audio vector (e.g., "meow")

All vectors share a 16-dimensional space. The text, image, and audio vectors
for the same concept are perturbed around a shared centroid. This simulates
the alignment property of real multimodal encoders like CLIP.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(149)

# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================
# WHY 8 concepts? Enough to show statistical trends, few enough to trace
# every retrieval by hand. WHY 16 dimensions? Richer than 2D (avoids
# collisions) but small enough to visualize after PCA.

CONCEPTS = [
    'cat', 'dog', 'car', 'tree',
    'house', 'phone', 'boat', 'bird'
]
N_CONCEPTS = len(CONCEPTS)
DIM = 16
N_PER_CONCEPT = 3   # text, image, audio
NOISE_SCALE = 0.08  # how far modality vectors drift from the centroid

# =============================================================================
# SECTION 2: BUILD UNIFIED EMBEDDING SPACE
# =============================================================================
# WHY shared centroids? In real multimodal encoders, CLIP's text encoder
# and image encoder are trained so that "cat" in text and a photo of a cat
# land near each other. We simulate that by creating well-separated concept
# centroids and perturbing them with modality-specific noise.

# Concept centroids: random orthonormal vectors in 16D space.
# WHY orthonormal? Two orthogonal unit vectors have dot product zero.
# Adding small noise preserves near-zero dot products for different concepts
# while keeping high dot products for the same concept.
R = np.random.randn(DIM, DIM)
Q, _ = np.linalg.qr(R)
centroids = Q[:N_CONCEPTS].copy()  # first N_CONCEPTS rows are orthonormal

# Generate modality vectors around centroids.
text_embeddings = []
image_embeddings = []
audio_embeddings = []
labels = []   # which concept each vector belongs to
modalities = []  # 0=text, 1=image, 2=audio

for i, concept in enumerate(CONCEPTS):
    c = centroids[i]
    # Text vector: centroid + small noise
    # WHY no re-normalization? Re-normalizing after adding noise projects
    # the vector back onto the unit sphere, which mixes noise into all
    # dimensions and destroys the orthogonality between concepts. Keeping
    # the raw centroid+noise preserves the separation structure.
    t = c + np.random.randn(DIM) * NOISE_SCALE
    text_embeddings.append(t)
    labels.append(i)
    modalities.append(0)

    # Image vector: centroid + different small noise
    img = c + np.random.randn(DIM) * NOISE_SCALE
    image_embeddings.append(img)
    labels.append(i)
    modalities.append(1)

    # Audio vector: centroid + different small noise
    aud = c + np.random.randn(DIM) * NOISE_SCALE
    audio_embeddings.append(aud)
    labels.append(i)
    modalities.append(2)

text_embeddings = np.array(text_embeddings)
image_embeddings = np.array(image_embeddings)
audio_embeddings = np.array(audio_embeddings)
labels = np.array(labels)
modalities = np.array(modalities)

# Unified index: stack all embeddings.
all_embeddings = np.vstack([text_embeddings, image_embeddings, audio_embeddings])
all_labels = np.tile(np.arange(N_CONCEPTS), 3)  # text(0-7), image(0-7), audio(0-7)
all_modalities = np.hstack([
    np.zeros(N_CONCEPTS), np.ones(N_CONCEPTS), np.full(N_CONCEPTS, 2)
])

print("="*70)
print("PHASE 149: MULTIMODAL RAG CONCEPTS")
print("="*70)
print(f"Concepts: {CONCEPTS}")
print(f"Embeddings per concept: {N_PER_CONCEPT} (text, image, audio)")
print(f"Vector dimension: {DIM}")
print(f"Total vectors in index: {len(all_embeddings)}")

# =============================================================================
# SECTION 3: CROSS-MODAL RETRIEVAL
# =============================================================================
# WHY cosine similarity? In high-dimensional normalized spaces, cosine
# similarity directly measures angular alignment, which is what aligned
# multimodal encoders optimize for.

def cosine_similarity(a, b):
    # WHY divide by norms? The embeddings are not pre-normalized (we removed
    # re-normalization to preserve orthogonal structure). True cosine similarity
    # requires dividing by the product of L2 norms.
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10)

def retrieve(query_vec, exclude_modality=None, k=3):
    """Return top-k indices and labels, optionally excluding one modality."""
    sims = np.array([cosine_similarity(query_vec, vec) for vec in all_embeddings])
    if exclude_modality is not None:
        mask = all_modalities != exclude_modality
        sims = sims[mask]
        idxs = np.arange(len(all_embeddings))[mask]
    else:
        idxs = np.arange(len(all_embeddings))
    top_k = np.argsort(sims)[-k:][::-1]
    return idxs[top_k], sims[top_k], all_labels[idxs][top_k]

# Test: text query -> retrieve images and audio.
print("\n--- Cross-Modal Retrieval: Text Query -> Images ---")
text_to_image_recalls = []
for i in range(N_CONCEPTS):
    query = text_embeddings[i]
    top_idx, top_sim, top_labels = retrieve(query, exclude_modality=0, k=3)
    # The ground-truth image for this concept should be in top-3.
    recall = int(i in top_labels)
    text_to_image_recalls.append(recall)
    print(f"  Query: '{CONCEPTS[i]}' (text) -> Retrieved: "
          f"{[CONCEPTS[l] for l in top_labels]} (sim: {top_sim[0]:.3f})")

print(f"\nText->Image Recall@3: {np.mean(text_to_image_recalls):.2%}")

# Test: image query -> retrieve text and audio.
print("\n--- Cross-Modal Retrieval: Image Query -> Text ---")
image_to_text_recalls = []
for i in range(N_CONCEPTS):
    query = image_embeddings[i]
    top_idx, top_sim, top_labels = retrieve(query, exclude_modality=1, k=3)
    recall = int(i in top_labels)
    image_to_text_recalls.append(recall)
    print(f"  Query: '{CONCEPTS[i]}' (image) -> Retrieved: "
          f"{[CONCEPTS[l] for l in top_labels]} (sim: {top_sim[0]:.3f})")

print(f"\nImage->Text Recall@3: {np.mean(image_to_text_recalls):.2%}")

# =============================================================================
# SECTION 4: ALIGNMENT VS. NO-ALIGNMENT ABLATION
# =============================================================================
# WHY this ablation? The single most important lesson of cross-modal retrieval
# is that alignment matters more than encoder quality. We prove it by
# randomly rotating the image vectors (breaking alignment) and watching
# retrieval collapse.

# Unaligned image embeddings: completely random vectors.
# WHY random instead of rotated? A random rotation of an already-noisy
# vector can still preserve some similarity by chance. Completely random
# vectors guarantee zero alignment, making the baseline comparison stark.
image_embeddings_unaligned = np.random.randn(N_CONCEPTS, DIM)

# For the ablation, we compare text only against unaligned images.
# WHY exclude audio? Audio embeddings are still aligned in this simulation.
# Including them would inflate unaligned recall through the audio channel,
# which misrepresents the effect of breaking image-text alignment.
unaligned_index = np.vstack([text_embeddings, image_embeddings_unaligned])
unaligned_labels = np.hstack([np.arange(N_CONCEPTS), np.arange(N_CONCEPTS)])

def retrieve_unaligned(query_vec, k=3):
    # Only retrieve from the image half of unaligned_index.
    image_half = unaligned_index[N_CONCEPTS:]
    sims = np.array([cosine_similarity(query_vec, vec) for vec in image_half])
    top_k = np.argsort(sims)[-k:][::-1]
    return top_k, sims[top_k], unaligned_labels[N_CONCEPTS:][top_k]

unaligned_recalls = []
for i in range(N_CONCEPTS):
    query = text_embeddings[i]
    _, _, top_labels = retrieve_unaligned(query, k=3)
    unaligned_recalls.append(int(i in top_labels))

print(f"\n--- Alignment Ablation ---")
print(f"Aligned Text->Image Recall@3:    {np.mean(text_to_image_recalls):.2%}")
print(f"Unaligned Text->Image Recall@3:  {np.mean(unaligned_recalls):.2%}")
print(f"Random baseline (1/8 chance):    {1/8:.2%}")

# =============================================================================
# SECTION 5: MULTIMODAL REASONING — CONFLICT RESOLUTION
# =============================================================================
# WHY simulate conflict? In real applications, different modalities can
# disagree. A text report may say 'mild' while an image shows 'severe'.
# Naive averaging of classifier outputs fails. Weighted fusion by modality
# reliability succeeds.

# Simulate a 3-class diagnosis task: classes 0, 1, 2.
N_SAMPLES = 100
n_classes = 3

# Ground-truth labels.
gt = np.random.randint(0, n_classes, size=N_SAMPLES)

# Each modality produces a softmax-like probability vector.
# Reliability: text=0.5 (noisy), image=0.8 (sharp), audio=0.6 (moderate).
reliabilities = {'text': 0.5, 'image': 0.8, 'audio': 0.6}

def generate_modality_probs(gt_labels, reliability, n_classes):
    """
    Generate probability vectors where the correct class gets boosted
    proportional to reliability. Higher reliability = sharper peak.
    """
    probs = np.random.dirichlet(np.ones(n_classes), size=len(gt_labels))
    for i, true_class in enumerate(gt_labels):
        # Boost true class; reliability controls how much.
        probs[i, true_class] += reliability * 0.7
        probs[i] /= probs[i].sum()
    return probs

text_probs = generate_modality_probs(gt, reliabilities['text'], n_classes)
image_probs = generate_modality_probs(gt, reliabilities['image'], n_classes)
audio_probs = generate_modality_probs(gt, reliabilities['audio'], n_classes)

# Naive uniform averaging.
uniform_avg = (text_probs + image_probs + audio_probs) / 3.0
uniform_preds = np.argmax(uniform_avg, axis=1)
uniform_acc = np.mean(uniform_preds == gt)

# Reliability-weighted fusion.
weights = np.array([reliabilities['text'], reliabilities['image'], reliabilities['audio']])
weights = weights / weights.sum()
weighted_avg = (weights[0] * text_probs +
                weights[1] * image_probs +
                weights[2] * audio_probs)
weighted_preds = np.argmax(weighted_avg, axis=1)
weighted_acc = np.mean(weighted_preds == gt)

# Best single modality.
best_single_acc = max(
    np.mean(np.argmax(text_probs, axis=1) == gt),
    np.mean(np.argmax(image_probs, axis=1) == gt),
    np.mean(np.argmax(audio_probs, axis=1) == gt),
)

print(f"\n--- Multimodal Reasoning (Conflict Resolution) ---")
print(f"Best single-modality accuracy:   {best_single_acc:.2%}")
print(f"Naive uniform fusion accuracy:   {uniform_acc:.2%}")
print(f"Reliability-weighted accuracy:   {weighted_acc:.2%}")
print(f"Image-only accuracy (reliable):  {np.mean(np.argmax(image_probs, axis=1) == gt):.2%}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================
# We project the 16D embeddings to 2D with PCA so the spatial clustering
# is visible. Then we plot four subplots:
#   1. Unified space: text, image, audio clusters
#   2. Cross-modal retrieval arrows (text -> image)
#   3. Alignment ablation (unaligned images scattered)
#   4. Multimodal reasoning accuracy comparison

# PCA to 2D.
def pca_2d(X):
    Xc = X - X.mean(axis=0)
    cov = Xc.T @ Xc / len(Xc)
    eigvals, eigvecs = np.linalg.eigh(cov)
    # Sort descending.
    idx = np.argsort(eigvals)[::-1]
    W = eigvecs[:, idx[:2]]
    return Xc @ W

all_2d = pca_2d(all_embeddings)
text_2d = all_2d[:N_CONCEPTS]
img_2d = all_2d[N_CONCEPTS:2*N_CONCEPTS]
aud_2d = all_2d[2*N_CONCEPTS:]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# --- Plot 1: Unified embedding space ---
ax = axes[0, 0]
for i, concept in enumerate(CONCEPTS):
    ax.scatter(*text_2d[i], color='blue', s=120, alpha=0.8, edgecolors='black')
    ax.scatter(*img_2d[i], color='red', s=120, alpha=0.8, edgecolors='black')
    ax.scatter(*aud_2d[i], color='green', s=120, alpha=0.8, edgecolors='black')
    # Label once per concept near the text point.
    ax.annotate(concept, (text_2d[i, 0], text_2d[i, 1]),
                textcoords="offset points", xytext=(5, 5), fontsize=9)
# Add a single legend entry per modality.
ax.scatter([], [], color='blue', label='Text', s=80)
ax.scatter([], [], color='red', label='Image', s=80)
ax.scatter([], [], color='green', label='Audio', s=80)
ax.set_title('Unified Embedding Space (PCA 2D)')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 2: Cross-modal retrieval arrows ---
# For each concept, draw an arrow from text to the retrieved image.
ax = axes[0, 1]
ax.scatter(text_2d[:, 0], text_2d[:, 1], color='blue', s=100, label='Text', zorder=3)
ax.scatter(img_2d[:, 0], img_2d[:, 1], color='red', s=100, label='Image', zorder=3)
for i in range(N_CONCEPTS):
    top_idx, _, _ = retrieve(text_embeddings[i], exclude_modality=0, k=1)
    # top_idx is in the full index; map to image index.
    retrieved_img_idx = top_idx[0] - N_CONCEPTS
    if 0 <= retrieved_img_idx < N_CONCEPTS:
        ax.annotate('', xy=img_2d[retrieved_img_idx], xytext=text_2d[i],
                    arrowprops=dict(arrowstyle='->', color='purple', lw=1.5, alpha=0.6))
ax.set_title('Text Query -> Retrieved Image')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 3: Unaligned image ablation ---
ax = axes[1, 0]
unaligned_img_2d = pca_2d(np.vstack([text_embeddings, image_embeddings_unaligned]))[N_CONCEPTS:]
ax.scatter(text_2d[:, 0], text_2d[:, 1], color='blue', s=100, label='Text', zorder=3)
ax.scatter(unaligned_img_2d[:, 0], unaligned_img_2d[:, 1], color='red', s=100,
           label='Image (unaligned)', zorder=3, marker='x')
for i in range(N_CONCEPTS):
    ax.annotate(CONCEPTS[i], (text_2d[i, 0], text_2d[i, 1]),
                textcoords="offset points", xytext=(5, 5), fontsize=9)
ax.set_title('Alignment Broken: Images Scattered Randomly')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 4: Reasoning accuracy bar chart ---
ax = axes[1, 1]
methods = ['Best Single\nModality', 'Naive Uniform\nFusion', 'Reliability-\nWeighted Fusion']
accuracies = [best_single_acc, uniform_acc, weighted_acc]
colors = ['#e74c3c', '#f39c12', '#27ae60']
bars = ax.bar(methods, accuracies, color=colors, edgecolor='black')
ax.set_ylim(0, 1.0)
ax.set_ylabel('Accuracy')
ax.set_title('Multimodal Reasoning: Weighted Fusion Wins')
for bar, val in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{val:.2%}', ha='center', va='bottom', fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
os.makedirs('src/phase149', exist_ok=True)
plt.savefig('src/phase149/multimodal_rag_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase149/multimodal_rag_concepts.png")
plt.close()

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Cross-modal retrieval (aligned):")
print(f"  Text -> Image Recall@3: {np.mean(text_to_image_recalls):.2%}")
print(f"  Image -> Text Recall@3: {np.mean(image_to_text_recalls):.2%}")
print(f"Cross-modal retrieval (unaligned):")
print(f"  Text -> Image Recall@3: {np.mean(unaligned_recalls):.2%}")
print(f"Multimodal reasoning (100 simulated diagnoses):")
print(f"  Best single modality:  {best_single_acc:.2%}")
print(f"  Naive uniform fusion:  {uniform_acc:.2%}")
print(f"  Reliability-weighted:  {weighted_acc:.2%}")
print("\nKey lessons:")
print("  1. Aligned embeddings enable cross-modal retrieval.")
print("  2. Breaking alignment (random rotation) collapses retrieval to baseline.")
print("  3. Alignment quality matters more than individual encoder quality.")
print("  4. Multimodal reasoning requires weighted fusion, not naive averaging.")
print("  5. The most reliable modality should dominate when sources conflict.")
print("="*70)
