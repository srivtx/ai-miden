"""
Phase 77: Unsupervised Learning Colab Real-Workflow Script

Upload this to Google Colab with a T4 GPU (CPU is also fine).
WHY: Local NumPy demos show the math, but real workflows use sklearn on
real datasets. This script bridges the gap with heavy comments explaining WHY.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
import numpy as np

np.random.seed(77)

# ---------------------------------------------------------------------------
# 1. LOAD REAL DATASET
# WHY: We use sklearn's digits dataset (8x8 images, 64 features, 10 classes).
# It is built-in (no download needed) and behaves like a tiny MNIST.
# In production you would swap this for fetch_openml('mnist_784').
# ---------------------------------------------------------------------------
data = load_digits()
X = data.data          # shape (1797, 64)
y = data.target        # true labels 0-9 (only for evaluation, NOT given to algorithms)
images = data.images   # shape (1797, 8, 8) for optional image display

print(f"Dataset shape: {X.shape}")
print(f"Classes: {np.unique(y)}")

# ---------------------------------------------------------------------------
# 2. STANDARDIZE FEATURES
# WHY: PCA and distance-based methods (K-means, DBSCAN, t-SNE) are sensitive
# to scale. A feature in 0-255 (pixel intensity) dominates a feature in 0-1.
# StandardScaler makes every feature mean=0, std=1 so they contribute equally.
# ---------------------------------------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------------------------------------------------------------------------
# 3. PCA — DIMENSIONALITY REDUCTION
# WHY: 64 dimensions is hard to visualize. PCA finds the axes that capture
# the most variance and projects the data down to 2D for plotting.
# We also inspect the explained variance ratio to see how much information
# we keep versus how much we discard.
# ---------------------------------------------------------------------------
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

print("\n--- PCA ---")
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total variance kept: {pca.explained_variance_ratio_.sum():.4f}")

# ---------------------------------------------------------------------------
# 4. K-MEANS CLUSTERING
# WHY: We know there are 10 digits, but in unsupervised learning we pretend
# we do not know the labels. We set K=10 and see if the algorithm discovers
# 10 coherent groups that roughly align with the true digits.
# ---------------------------------------------------------------------------
kmeans = KMeans(n_clusters=10, random_state=77, n_init=10)
kmeans_labels = kmeans.fit_predict(X_scaled)

print("\n--- K-Means ---")
print(f"Inertia (SSE): {kmeans.inertia_:.2f}")

# ---------------------------------------------------------------------------
# 5. t-SNE EMBEDDING
# WHY: PCA is linear and may smash clusters together. t-SNE is nonlinear and
# optimized to keep neighbors nearby. We run it on the FULL 64-D data so it
# has the richest possible distance information.
# ---------------------------------------------------------------------------
# WHY: perplexity ~ effective number of neighbors. 30 is a safe default.
# learning_rate='auto' uses a heuristic that usually converges well.
tsne = TSNE(n_components=2, perplexity=30, learning_rate='auto', init='pca', random_state=77)
X_tsne = tsne.fit_transform(X_scaled)

print("\n--- t-SNE ---")
print(f"KL divergence after optimization: {tsne.kl_divergence_:.4f}")

# ---------------------------------------------------------------------------
# 6. DBSCAN CLUSTERING
# WHY: DBSCAN does not need K. It discovers clusters by density and marks
# noise explicitly. On high-D data it is tricky, so we first reduce to 50D
# with PCA (a common preprocessing step) to make distances meaningful again.
# ---------------------------------------------------------------------------
X_pca_50 = PCA(n_components=50).fit_transform(X_scaled)
# WHY: eps=5 and min_samples=10 are dataset-specific guesses found by trial.
dbscan = DBSCAN(eps=5, min_samples=10)
dbscan_labels = dbscan.fit_predict(X_pca_50)

n_dbscan_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
n_noise = list(dbscan_labels).count(-1)

print("\n--- DBSCAN ---")
print(f"Clusters found: {n_dbscan_clusters}")
print(f"Noise points: {n_noise} ({100 * n_noise / len(dbscan_labels):.1f}%)")

# ---------------------------------------------------------------------------
# 7. VISUALIZE CLUSTERS IN 2D
# WHY: Humans cannot see 64D. Every algorithm is plotted in 2D so we can
# compare whether the discovered groups align with the true digit labels.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("Phase 77: Unsupervised Learning on Digits Dataset", fontsize=14)

def plot_scatter(ax, coords, labels, title, cmap='tab10'):
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap=cmap, s=15, alpha=0.7)
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    return scatter

# True labels (cheating — only for reference)
plot_scatter(axes[0, 0], X_pca, y, "PCA (True Labels)")
plot_scatter(axes[0, 1], X_tsne, y, "t-SNE (True Labels)")

# K-Means clusters (unsupervised)
plot_scatter(axes[0, 2], X_pca, kmeans_labels, "PCA + K-Means (K=10)")
plot_scatter(axes[1, 0], X_tsne, kmeans_labels, "t-SNE + K-Means (K=10)")

# DBSCAN clusters (unsupervised)
plot_scatter(axes[1, 1], X_pca, dbscan_labels, f"PCA + DBSCAN\n({n_dbscan_clusters} clusters, {n_noise} noise)")
plot_scatter(axes[1, 2], X_tsne, dbscan_labels, f"t-SNE + DBSCAN\n({n_dbscan_clusters} clusters, {n_noise} noise)")

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_path = "src/phase77/unsupervised_learning_colab.png"
plt.savefig(out_path, dpi=150)
print(f"\nSaved plot to {out_path}")

# ---------------------------------------------------------------------------
# 8. EXPLAINED VARIANCE RATIO BAR CHART
# WHY: The first two components only keep ~20% of variance. We need to see
# how many components are required to capture 80% or 95% — this informs
# whether PCA is a viable preprocessing step for downstream models.
# ---------------------------------------------------------------------------
pca_full = PCA().fit(X_scaled)
cumsum = np.cumsum(pca_full.explained_variance_ratio_)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(np.arange(1, len(cumsum) + 1), cumsum, marker='o', color='blue')
ax.axhline(0.80, color='red', linestyle='--', label='80% variance')
ax.axhline(0.95, color='green', linestyle='--', label='95% variance')
ax.set_xlabel('Number of Components')
ax.set_ylabel('Cumulative Explained Variance')
ax.set_title('PCA Explained Variance on Digits Dataset')
ax.legend()
ax.grid(True, alpha=0.3)

out_path2 = "src/phase77/pca_explained_variance.png"
plt.tight_layout()
plt.savefig(out_path2, dpi=150)
print(f"Saved explained-variance plot to {out_path2}")

# ---------------------------------------------------------------------------
# 9. QUANTITATIVE SUMMARY
# WHY: Adjusted Rand Index (ARI) measures clustering quality against true
# labels without requiring label names to match (unsupervised labels are
# arbitrarily permuted). ARI=1 is perfect; ARI=0 is random.
# ---------------------------------------------------------------------------
from sklearn.metrics import adjusted_rand_score

ari_kmeans = adjusted_rand_score(y, kmeans_labels)
ari_dbscan = adjusted_rand_score(y, dbscan_labels) if n_dbscan_clusters > 0 else float('nan')

print("\n--- Adjusted Rand Index (vs true labels) ---")
print(f"K-Means ARI: {ari_kmeans:.3f}")
print(f"DBSCAN ARI:  {ari_dbscan:.3f}")
print("\nNote: ARI compares cluster shapes, not label names.")
