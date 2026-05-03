# FRONTIER TRACK: Phase 127 — Vision-Language Fine-tuning Concepts
# LOCAL NumPy concept demonstration
# This script simulates a vision encoder, projection layer, and LLM embedding space.
# WHY: NumPy makes the mechanics of multimodal alignment transparent.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: Reproducibility matters for educational demos.
np.random.seed(127)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
N_CONCEPTS = 5
VISION_DIM = 64
TEXT_DIM = 64
N_TRAIN = 200
N_TEST = 50
LR = 0.05
N_STEPS = 200

# Concepts: cat, dog, car, tree, house
concepts = ['cat', 'dog', 'car', 'tree', 'house']

# ---------------------------------------------------------------------------
# STEP 1: Frozen vision encoder
# WHY: In reality this is a CLIP ViT. We simulate it with a fixed transform.
# We use a shared basis so concepts have structured, generalizable features.
# ---------------------------------------------------------------------------
vision_basis = np.random.randn(N_CONCEPTS, VISION_DIM) * 0.5


def encode_vision(concept_idx):
    """Map a concept index to a vision embedding."""
    # Structured signal: each concept has a distinct basis vector
    signal = vision_basis[concept_idx]
    noise = np.random.randn(VISION_DIM) * 0.05
    return signal + noise


# ---------------------------------------------------------------------------
# STEP 2: Frozen text embeddings
# WHY: In reality this is the LLM token embedding matrix.
# We derive them from the same basis so alignment is learnable.
# ---------------------------------------------------------------------------
text_embeddings = vision_basis[:, :TEXT_DIM] + np.random.randn(N_CONCEPTS, TEXT_DIM) * 0.1
text_embeddings = text_embeddings / np.linalg.norm(text_embeddings, axis=1, keepdims=True)

# ---------------------------------------------------------------------------
# STEP 3: Trainable projection layer
# WHY: This is the ONLY trainable component. It aligns vision to language.
# ---------------------------------------------------------------------------
W_proj = np.random.randn(TEXT_DIM, VISION_DIM) * 0.01
b_proj = np.zeros(TEXT_DIM)


def project(vision_emb):
    return W_proj @ vision_emb + b_proj


def cosine_similarity(a, b):
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)


# ---------------------------------------------------------------------------
# STEP 4: Generate data
# WHY: We train on 4 concepts and test on the 5th to show generalization.
# ---------------------------------------------------------------------------
train_data = []
for _ in range(N_TRAIN):
    c = np.random.randint(0, 4)  # first 4 concepts
    v = encode_vision(c)
    t = text_embeddings[c]
    train_data.append((v, t))

test_data = []
for _ in range(N_TEST):
    c = np.random.randint(0, N_CONCEPTS)  # mix of seen and unseen
    v = encode_vision(c)
    t = text_embeddings[c]
    test_data.append((v, t))

# Separate held-out evaluation
held_out_data = []
for _ in range(N_TEST):
    c = 4  # held-out 'house'
    v = encode_vision(c)
    t = text_embeddings[c]
    held_out_data.append((v, t))

# ---------------------------------------------------------------------------
# STEP 5: Training loop
# WHY: We maximize cosine similarity via gradient descent on the projection.
# ---------------------------------------------------------------------------
losses = []
test_similarities = []
held_out_similarities = []

print("Training projection layer...")
for step in range(N_STEPS):
    total_loss = 0.0
    for v, t in train_data:
        p = project(v)
        sim = cosine_similarity(p, t)
        loss = 1.0 - sim
        total_loss += loss

        # Gradient of (1 - sim) w.r.t. p
        norm_p = np.linalg.norm(p)
        norm_t = np.linalg.norm(t)
        grad_p = -(t / (norm_p * norm_t) - p * (p @ t) / (norm_p**3 * norm_t))

        # Update projection weights
        W_proj -= LR * np.outer(grad_p, v)
        b_proj -= LR * grad_p

    avg_loss = total_loss / len(train_data)
    losses.append(avg_loss)

    test_sims = [cosine_similarity(project(v), t) for v, t in test_data]
    test_similarities.append(np.mean(test_sims))

    held_sims = [cosine_similarity(project(v), t) for v, t in held_out_data]
    held_out_similarities.append(np.mean(held_sims))

    if step % 40 == 0:
        print(f"Step {step}: train_loss={avg_loss:.4f}, test_sim={test_similarities[-1]:.4f}, held_sim={held_out_similarities[-1]:.4f}")

# ---------------------------------------------------------------------------
# STEP 6: Evaluate all concepts
# WHY: Show that the projector maps each concept to its correct text embedding.
# ---------------------------------------------------------------------------
print("\nFinal alignment (cosine similarity):")
for i, name in enumerate(concepts):
    v = encode_vision(i)
    p = project(v)
    sims = [cosine_similarity(p, text_embeddings[j]) for j in range(N_CONCEPTS)]
    best = int(np.argmax(sims))
    print(f"  {name:6s}: best_match={concepts[best]}, sims={['%.2f' % s for s in sims]}")

# ---------------------------------------------------------------------------
# STEP 7: PCA visualization
# WHY: Reduce 64-dim embeddings to 2D so humans can see the alignment.
# ---------------------------------------------------------------------------


def pca_2d(X):
    """Simple PCA to 2 dimensions."""
    X = X - X.mean(axis=0)
    cov = X.T @ X / len(X)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    W = eigvecs[:, idx[:2]]
    return X @ W


vision_points = np.array([encode_vision(i) for i in range(N_CONCEPTS)])
text_points = text_embeddings.copy()
projected_points = np.array([project(encode_vision(i)) for i in range(N_CONCEPTS)])

v_2d = pca_2d(np.vstack([vision_points, text_points, projected_points]))[:N_CONCEPTS]
t_2d = pca_2d(np.vstack([vision_points, text_points, projected_points]))[N_CONCEPTS:2 * N_CONCEPTS]
p_2d = pca_2d(np.vstack([vision_points, text_points, projected_points]))[2 * N_CONCEPTS:]

# ---------------------------------------------------------------------------
# STEP 8: Plotting
# WHY: Curves and scatter plots make the alignment tangible.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].plot(losses, color='steelblue', linewidth=1.5)
axes[0].set_title('Projection Layer Training Loss')
axes[0].set_xlabel('Step')
axes[0].set_ylabel('1 - Cosine Similarity')
axes[0].grid(True, alpha=0.3)

axes[1].plot(test_similarities, color='forestgreen', linewidth=1.5, label='All concepts (mix)')
axes[1].plot(held_out_similarities, color='crimson', linewidth=1.5, label='Held-out "house"')
axes[1].set_title('Concept Alignment Over Training')
axes[1].set_xlabel('Step')
axes[1].set_ylabel('Cosine Similarity')
axes[1].set_ylim(-1, 1)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

ax = axes[2]
ax.scatter(v_2d[:, 0], v_2d[:, 1], color='crimson', s=120, label='Vision encoder', marker='o')
ax.scatter(t_2d[:, 0], t_2d[:, 1], color='steelblue', s=120, label='Text embeddings', marker='s')
ax.scatter(p_2d[:, 0], p_2d[:, 1], color='forestgreen', s=120, label='After projection', marker='^')
for i, name in enumerate(concepts):
    ax.annotate(name, (p_2d[i, 0], p_2d[i, 1]), textcoords="offset points", xytext=(5, 5))
ax.set_title('Vision → Projection → Text (PCA 2D)')
ax.set_xlabel('PC1')
ax.set_ylabel('PC2')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase127/vl_projection_alignment.png', dpi=150)
plt.close()

print("\nPlot saved to src/phase127/vl_projection_alignment.png")

# ---------------------------------------------------------------------------
# FINAL INSIGHT
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHT: The projection layer learns to warp the vision")
print("feature space so that 'cat' images align with 'cat' text")
print("embeddings. The vision encoder and LLM were never updated.")
print("Seen concepts align strongly; the held-out 'house' concept")
print("shows limited generalization, illustrating that projection")
print("quality depends on training diversity.")
print("=" * 60)
