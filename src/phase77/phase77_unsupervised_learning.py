"""
Phase 77: Unsupervised Learning Concept Demo

Demonstrates K-Means, PCA, t-SNE, and DBSCAN from scratch using only NumPy.
Shows how to discover hidden structure in unlabeled data.

WHY: Supervised learning needs labels, but most real-world data is unlabeled.
These four algorithms are the workhorses of exploratory data analysis.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend so scripts do not hang
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(77)

# ---------------------------------------------------------------------------
# 1. GENERATE SYNTHETIC CLUSTERED DATA
# WHY: We need ground-truth clusters so we can visually verify whether each
# algorithm discovers the structure we planted.
# ---------------------------------------------------------------------------
n_per_cluster = 80
centers = np.array([[-2.0, -2.0], [3.0, 3.0], [6.0, -1.0]])
std = 0.6

X = []
for c in centers:
    X.append(np.random.normal(loc=c, scale=std, size=(n_per_cluster, 2)))
X = np.vstack(X)  # shape (240, 2)
true_labels = np.repeat(np.arange(len(centers)), n_per_cluster)

# Add a few noise points so DBSCAN has something to reject
noise = np.random.uniform(low=-5, high=10, size=(15, 2))
X = np.vstack([X, noise])
true_labels = np.concatenate([true_labels, np.full(15, -1)])

n_points = X.shape[0]

# ---------------------------------------------------------------------------
# 2. K-MEANS FROM SCRATCH
# WHY: K-means is just two steps repeated: assign points to nearest centroid,
# then move centroids to the mean of their assigned points. No magic.
# ---------------------------------------------------------------------------
K = 3
max_iters = 50

# K-means++ initialization (better than random)
# WHY: Random centroids can land close together and produce bad local optima.
# K-means++ spreads them out by choosing each new centroid far from existing ones.
centroids = [X[np.random.randint(n_points)]]
for _ in range(1, K):
    dists = np.array([min([np.linalg.norm(x - c) ** 2 for c in centroids]) for x in X])
    probs = dists / dists.sum()
    next_idx = np.random.choice(n_points, p=probs)
    centroids.append(X[next_idx])
centroids = np.array(centroids)

for iteration in range(max_iters):
    # Assign step: each point gets the index of the closest centroid
    distances = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
    labels_kmeans = np.argmin(distances, axis=1)

    # Update step: move each centroid to the mean of its cluster
    new_centroids = np.array([
        X[labels_kmeans == k].mean(axis=0) if np.any(labels_kmeans == k) else centroids[k]
        for k in range(K)
    ])

    if np.allclose(centroids, new_centroids, atol=1e-6):
        break
    centroids = new_centroids

# ---------------------------------------------------------------------------
# 3. PCA FROM SCRATCH
# WHY: PCA is eigen-decomposition of the covariance matrix. The eigenvectors
# with the largest eigenvalues are the axes that capture the most variance.
# ---------------------------------------------------------------------------
X_centered = X - X.mean(axis=0)

# WHY: Divide by N-1 for sample covariance. Each entry (i,j) tells us how
# feature i and feature j vary together.
Cov = (X_centered.T @ X_centered) / (X_centered.shape[0] - 1)

# WHY: np.linalg.eigh is numerically stable for symmetric matrices.
eigenvalues, eigenvectors = np.linalg.eigh(Cov)

# Sort descending by eigenvalue
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

# Project onto top 2 components (our data is already 2D, but we show the projection anyway)
# WHY: In high-D data you would keep the top-K columns. Here we keep both to visualize.
X_pca = X_centered @ eigenvectors[:, :2]

explained_variance_ratio = eigenvalues / eigenvalues.sum()

# ---------------------------------------------------------------------------
# 4. t-SNE FROM SCRATCH (SIMPLIFIED)
# WHY: t-SNE preserves local neighborhoods by matching probability distributions
# in high-D and low-D space. We implement a simplified version with fixed sigma
# and fewer iterations so the concept is clear without 500 lines of tuning code.
# ---------------------------------------------------------------------------
def compute_pairwise_distances(X_mat):
    """WHY: Efficient squared Euclidean distance matrix without loops."""
    sum_X = np.sum(np.square(X_mat), axis=1)
    D2 = np.add(np.add(-2 * np.dot(X_mat, X_mat.T), sum_X).T, sum_X)
    return np.maximum(D2, 0.0)  # guard against tiny negatives from float error

# High-D similarities using Gaussian kernel with per-point sigma
# WHY: Real t-SNE searches a per-point sigma so each point has the same
# effective number of neighbors (perplexity). We approximate this by setting
# sigma_i to the distance of the k-th nearest neighbor.
D2 = compute_pairwise_distances(X)
D = np.sqrt(D2)
np.fill_diagonal(D, np.inf)  # ignore self-distances
k_neighbors = 10
kth_dist = np.partition(D, k_neighbors, axis=1)[:, k_neighbors]
sigma = kth_dist[:, np.newaxis]
sigma = np.maximum(sigma, 1e-5)  # avoid divide-by-zero

# Gaussian affinities with per-point sigma
P = np.exp(-D2 / (2.0 * sigma ** 2))
np.fill_diagonal(P, 0.0)
P = P / P.sum(axis=1, keepdims=True)
# Symmetrize: WHY: t-SNE uses joint probabilities, not conditional.
P = (P + P.T) / (2.0 * n_points)
P = np.maximum(P, 1e-12)

# Initialize low-D points with PCA projection
# WHY: PCA gives a sensible starting layout so t-SNE does not waste iterations
# escaping a random soup. This is standard in libraries like sklearn.
Y = X_pca.copy()

n_tsne_iters = 500
learning_rate_tsne = 100.0

# Early exaggeration: WHY: multiplying P by a factor (>1) forces tight clusters
# to form early, preventing points from getting stuck in a uniform soup.
early_exaggeration = 4.0
exaggeration_iters = 100

# Momentum helps escape poor local minima
momentum_initial = 0.5
momentum_final = 0.8
momentum_switch = 250

Y_prev = Y.copy()
for t in range(n_tsne_iters):
    # Use exaggerated P during early phase
    P_t = P * early_exaggeration if t < exaggeration_iters else P

    # Low-D pairwise distances
    D2_low = compute_pairwise_distances(Y)
    # Student-t kernel with df=1 (Cauchy) — WHY: heavy tails prevent crowding
    Q = 1.0 / (1.0 + D2_low)
    np.fill_diagonal(Q, 0.0)
    Q = Q / Q.sum()
    Q = np.maximum(Q, 1e-12)

    # Gradient of KL(P || Q)
    # WHY: The gradient pulls points together where P > Q and pushes apart where Q > P.
    PQ_diff = P_t - Q
    grad = np.zeros_like(Y)
    for i in range(n_points):
        # Vectorized gradient for point i
        diff = Y[i] - Y  # (n_points, 2)
        # The t-SNE gradient formula for the t-distribution kernel
        grad[i] = 4.0 * np.sum((PQ_diff[:, i] * Q[:, i] / (1.0 + D2_low[:, i]))[:, np.newaxis] * diff, axis=0)

    # Momentum update
    momentum = momentum_initial if t < momentum_switch else momentum_final
    Y_new = Y - learning_rate_tsne * grad + momentum * (Y - Y_prev)
    Y_prev = Y.copy()
    Y = Y_new

    # Center Y so it does not drift
    Y -= Y.mean(axis=0)

# ---------------------------------------------------------------------------
# 5. DBSCAN FROM SCRATCH (SIMPLIFIED)
# WHY: DBSCAN discovers clusters by linking dense regions. A point is a "core"
# point if it has enough neighbors within distance eps. Clusters grow by
# connecting core points that are neighbors of each other.
# ---------------------------------------------------------------------------
eps = 1.2
min_pts = 5

# Pairwise distances (Euclidean)
dist_matrix = np.sqrt(compute_pairwise_distances(X))

# Core points: count neighbors within eps (including self)
neighbor_counts = (dist_matrix <= eps).sum(axis=1)
core_mask = neighbor_counts >= min_pts

# Expand clusters using BFS from each unvisited core point
labels_dbscan = np.full(n_points, -1)  # -1 = noise/unvisited
cluster_id = 0
visited = np.zeros(n_points, dtype=bool)

for i in range(n_points):
    if not core_mask[i] or visited[i]:
        continue

    # Start a new cluster from core point i
    queue = [i]
    visited[i] = True
    labels_dbscan[i] = cluster_id

    while queue:
        j = queue.pop(0)
        # Find all points within eps of j
        neighbors = np.where(dist_matrix[j] <= eps)[0]
        for nb in neighbors:
            if not visited[nb]:
                visited[nb] = True
                labels_dbscan[nb] = cluster_id
                if core_mask[nb]:
                    queue.append(nb)
    cluster_id += 1

# ---------------------------------------------------------------------------
# 6. VISUALIZATION
# WHY: Pictures are the only way to verify unsupervised learning. Numbers alone
# cannot tell you whether K-means split a cluster or DBSCAN called noise noise.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Phase 77: Unsupervised Learning from Scratch", fontsize=14)

# Helper to scatter with discrete colors
def scatter(ax, data, labels, title, cmap='tab10', show_centroids=None):
    unique = np.unique(labels)
    for u in unique:
        mask = labels == u
        color = 'lightgray' if u == -1 else None
        alpha = 0.3 if u == -1 else 0.8
        label = 'noise' if u == -1 else f'cluster {u}'
        ax.scatter(data[mask, 0], data[mask, 1], label=label, alpha=alpha, s=25, c=color)
    if show_centroids is not None:
        ax.scatter(show_centroids[:, 0], show_centroids[:, 1], c='black', marker='X', s=150, edgecolors='white')
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])

# (0,0) Original data with true labels
scatter(axes[0, 0], X, true_labels, "Original Data (True Clusters)")

# (0,1) K-means result
scatter(axes[0, 1], X, labels_kmeans, "K-Means (K=3)", show_centroids=centroids)

# (0,2) PCA projection (first two PCs)
scatter(axes[0, 2], X_pca, true_labels, f"PCA Projection\n(EVR: [{explained_variance_ratio[0]:.2f}, {explained_variance_ratio[1]:.2f}])")
axes[0, 2].set_xlabel("PC1")
axes[0, 2].set_ylabel("PC2")

# (1,0) t-SNE embedding
scatter(axes[1, 0], Y, true_labels, "t-SNE Embedding (Simplified)")
axes[1, 0].set_xlabel("t-SNE 1")
axes[1, 0].set_ylabel("t-SNE 2")

# (1,1) DBSCAN result
scatter(axes[1, 1], X, labels_dbscan, f"DBSCAN (eps={eps}, min_pts={min_pts})")

# (1,2) Elbow method for K-means
# WHY: Even though we know K=3 for this demo, the elbow method is how you
# choose K in practice when the answer is unknown.
inertias = []
K_range = range(1, 8)
for k in K_range:
    # Quick k-means for inertia only
    init_idx = np.random.choice(n_points, k, replace=False)
    c_temp = X[init_idx].copy()
    for _ in range(20):
        d_temp = np.linalg.norm(X[:, np.newaxis, :] - c_temp[np.newaxis, :, :], axis=2)
        l_temp = np.argmin(d_temp, axis=1)
        c_temp = np.array([X[l_temp == kk].mean(axis=0) if np.any(l_temp == kk) else c_temp[kk] for kk in range(k)])
    inertia = sum(np.sum((X[l_temp == kk] - c_temp[kk]) ** 2) for kk in range(k) if np.any(l_temp == kk))
    inertias.append(inertia)

axes[1, 2].plot(K_range, inertias, marker='o', color='purple')
axes[1, 2].axvline(3, color='red', linestyle='--', alpha=0.5, label='true K=3')
axes[1, 2].set_title("Elbow Method")
axes[1, 2].set_xlabel("K")
axes[1, 2].set_ylabel("Inertia (SSE)")
axes[1, 2].legend()
axes[1, 2].grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_path = "src/phase77/unsupervised_learning.png"
plt.savefig(out_path, dpi=150)
print(f"Saved plot to {out_path}")

# ---------------------------------------------------------------------------
# 7. FINAL REPORT
# WHY: Concrete numbers prove the concepts better than plots alone.
# ---------------------------------------------------------------------------
print("\n--- Phase 77 Results ---")
print(f"Total points: {n_points}")
print(f"K-means converged in {iteration + 1} iterations")
print(f"PCA explained variance ratio: PC1={explained_variance_ratio[0]:.4f}, PC2={explained_variance_ratio[1]:.4f}")
print(f"t-SNE iterations: {n_tsne_iters}")
print(f"DBSCAN found {cluster_id} clusters and {(labels_dbscan == -1).sum()} noise points")
