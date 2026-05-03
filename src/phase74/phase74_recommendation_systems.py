"""
================================================================================
Phase 74: Recommendation Systems — NumPy Concept Demo
================================================================================

This script is for a COMPLETE BEGINNER.

Recommendation systems answer: "What should I show this user next?"

We cover three approaches:
  1. Popularity Baseline    — Show everyone the same top items
  2. Collaborative Filtering — Find similar users and copy their taste
  3. Matrix Factorization    — Learn hidden "taste" dimensions from data

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


# ==============================================================================
# PART 1: BUILD A SYNTHETIC SPARSE RATING MATRIX
# ==============================================================================
# In the real world, rating matrices are enormous and mostly empty.
# Here we use a tiny 5-user x 6-item matrix so you can see every number.
# Zero means "unrated / missing."
# ==============================================================================

ratings = np.array([
    [5, 3, 0, 1, 0, 2],   # User 0: loves item 0, hates item 3
    [4, 0, 0, 2, 3, 0],   # User 1: similar to User 0 on items 0 and 3
    [1, 1, 0, 5, 4, 5],   # User 2: opposite taste — loves what User 0 hates
    [0, 0, 2, 4, 5, 0],   # User 3: niche taste, items 2-4
    [2, 4, 5, 0, 0, 1],   # User 4: overlaps with User 3 on items 2, likes item 1
], dtype=np.float32)

n_users, n_items = ratings.shape
TARGET_USER = 0

print("=" * 60)
print("PHASE 74: RECOMMENDATION SYSTEMS")
print("=" * 60)
print()
print("Original Rating Matrix (0 = missing):")
print(ratings)
print()


# ==============================================================================
# PART 2: POPULARITY BASELINE
# ==============================================================================
# The simplest possible recommendation: "show whatever is most popular."
# This ignores the user completely. It is our floor — anything smarter
# should beat this.
# ==============================================================================

def popularity_baseline(ratings):
    """
    Compute mean rating for each item, ignoring zeros (missing).
    Returns a score vector of length n_items.
    """
    # Mask out missing ratings so they do not drag the mean down
    masked = np.where(ratings > 0, ratings, np.nan)
    return np.nanmean(masked, axis=0)

pop_scores = popularity_baseline(ratings)
print("Popularity Baseline (mean rating per item):")
print(np.round(pop_scores, 2))
print()


# ==============================================================================
# PART 3: USER-BASED COLLABORATIVE FILTERING
# ==============================================================================
# Idea: Users who agreed in the past will agree in the future.
# Step 1: Measure similarity between TARGET_USER and every other user
#         using ONLY the items they both rated.
# Step 2: Predict missing ratings as a weighted average of similar users.
# ==============================================================================

def cosine_similarity(u, v):
    """
    Cosine similarity between two rating vectors,
    computed only over items BOTH users rated.
    """
    mask = (u > 0) & (v > 0)
    if mask.sum() == 0:
        return 0.0
    u_m = u[mask]
    v_m = v[mask]
    return np.dot(u_m, v_m) / (np.linalg.norm(u_m) * np.linalg.norm(v_m) + 1e-9)


def collaborative_filtering(ratings, target_user):
    """
    Predict every missing rating for target_user by asking neighbors.
    """
    preds = np.zeros(ratings.shape[1])
    for item in range(n_items):
        if ratings[target_user, item] > 0:
            continue  # Already rated — no need to predict

        numerator = 0.0
        denominator = 0.0
        for other in range(n_users):
            if other == target_user:
                continue
            if ratings[other, item] > 0:
                sim = cosine_similarity(ratings[target_user], ratings[other])
                numerator += sim * ratings[other, item]
                denominator += abs(sim)

        preds[item] = numerator / (denominator + 1e-9)
    return preds

cf_preds = collaborative_filtering(ratings, TARGET_USER)
print("User-Based Collaborative Filtering predictions for User 0:")
print(np.round(cf_preds, 2))
print()


# ==============================================================================
# PART 4: MATRIX FACTORIZATION (SVD-STYLE)
# ==============================================================================
# Problem: The rating matrix is sparse and high-dimensional.
# Solution: Factor it into two low-rank matrices.
#   U  = user latent vectors   (n_users x k)
#   Vt = item latent vectors   (k x n_items)
# Reconstruct:  R_hat = U @ S @ Vt  (plus means to undo centering)
#
# WHY center by user mean? Some users are generous (rate everything 5),
# others are harsh (rate everything 2). Centering removes this bias
# so the latent factors capture *taste*, not *mood*.
# ==============================================================================

def matrix_factorization_svd(ratings, k=2):
    """
    Fill missing with global mean, center by user mean, run SVD, reconstruct.
    Returns full predicted matrix.
    """
    global_mean = ratings[ratings > 0].mean()
    filled = ratings.copy()
    filled[filled == 0] = global_mean

    # Center each user's ratings around their own average
    user_means = np.array([filled[u][ratings[u] > 0].mean() for u in range(n_users)])
    centered = filled - user_means[:, None]

    # SVD: centered = U @ diag(S) @ Vt
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)

    # Keep only the top k latent factors
    U_k = U[:, :k]
    S_k = np.diag(S[:k])
    Vt_k = Vt[:k, :]

    # Reconstruct and add user means back
    reconstructed = (U_k @ S_k @ Vt_k) + user_means[:, None]
    return reconstructed, U_k, S_k, Vt_k

mf_preds_full, U_k, S_k, Vt_k = matrix_factorization_svd(ratings, k=2)
mf_preds = mf_preds_full[TARGET_USER]

print("Matrix Factorization predictions for User 0:")
print(np.round(mf_preds, 2))
print()


# ==============================================================================
# PART 5: COMPARISON TABLE
# ==============================================================================
# We look only at items User 0 has NOT rated and see what each method
# would recommend. The differences reveal the mechanics of each approach.
# ==============================================================================

unrated = np.where(ratings[TARGET_USER] == 0)[0]
print("Comparison for UNSEEN items (User 0):")
print("Item | Popularity | CF Score | MF Score")
print("-" * 40)
for i in unrated:
    print(f"  {i}  |   {pop_scores[i]:6.2f}   |  {cf_preds[i]:6.2f}  |  {mf_preds[i]:6.2f}")
print()


# ==============================================================================
# PART 6: VISUALIZATION
# ==============================================================================
# We draw three panels:
#   1. The raw rating matrix heatmap
#   2. Users and items plotted in the 2D latent space
#   3. Recommendation scores for User 0 across all three methods
# ==============================================================================

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# --- Panel 1: Rating Matrix ---
im = axes[0].imshow(ratings, cmap='YlGnBu', aspect='auto', vmin=0, vmax=5)
axes[0].set_title('Original Rating Matrix\n(0 = missing)', fontweight='bold')
axes[0].set_xlabel('Item')
axes[0].set_ylabel('User')
for i in range(n_users):
    for j in range(n_items):
        text = int(ratings[i, j]) if ratings[i, j] > 0 else '-'
        axes[0].text(j, i, text, ha='center', va='center', color='black')
fig.colorbar(im, ax=axes[0])

# --- Panel 2: Latent Space ---
# Project users and items into the same 2D space for intuition.
# user_latent = U_k @ sqrt(S_k)
# item_latent = sqrt(S_k) @ Vt_k
user_latent = U_k @ np.sqrt(S_k)
item_latent = np.sqrt(S_k) @ Vt_k

axes[1].scatter(user_latent[:, 0], user_latent[:, 1],
                c='blue', s=120, label='Users', marker='o', edgecolors='k')
for i in range(n_users):
    axes[1].annotate(f'U{i}', (user_latent[i, 0], user_latent[i, 1]),
                     textcoords="offset points", xytext=(6, 4), fontsize=9)

axes[1].scatter(item_latent[0, :], item_latent[1, :],
                c='red', s=120, label='Items', marker='s', edgecolors='k')
for j in range(n_items):
    axes[1].annotate(f'I{j}', (item_latent[0, j], item_latent[1, j]),
                     textcoords="offset points", xytext=(6, 4), fontsize=9)

axes[1].set_title('Latent Space (k=2)', fontweight='bold')
axes[1].set_xlabel('Latent Dimension 1')
axes[1].set_ylabel('Latent Dimension 2')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# --- Panel 3: Recommendation Scores for User 0 ---
x = np.arange(n_items)
width = 0.25

# For MF, mask already-rated items so they do not clutter the chart
mf_plot = mf_preds.copy()
mf_plot[ratings[TARGET_USER] > 0] = 0  # zero out for visual clarity

axes[2].bar(x - width, pop_scores, width, label='Popularity', color='gray', alpha=0.7)
axes[2].bar(x, cf_preds, width, label='Collaborative Filtering', color='orange', alpha=0.7)
axes[2].bar(x + width, mf_plot, width, label='Matrix Factorization', color='green', alpha=0.7)
axes[2].set_title(f'Recommendation Scores for User {TARGET_USER}', fontweight='bold')
axes[2].set_xlabel('Item')
axes[2].set_ylabel('Predicted Score')
axes[2].set_xticks(x)
axes[2].set_xticklabels([f'Item {i}' for i in x])
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase74/recommendation_systems.png', dpi=150)
print("Plot saved: src/phase74/recommendation_systems.png")
print()


# ==============================================================================
# SUMMARY
# ==============================================================================
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print()
print("  WHAT WE BUILT:")
print("    - Popularity baseline (simple average, no personalization)")
print("    - User-based collaborative filtering (cosine similarity + weighted average)")
print("    - Matrix factorization via SVD (latent taste vectors)")
print()
print("  KEY INSIGHTS:")
print("    1. Popularity ignores the user. It is the floor, not the ceiling.")
print("    2. CF finds similar users but struggles when overlap is sparse.")
print("    3. MF generalizes by learning hidden dimensions (latent factors).")
print("    4. In the latent space, similar users and items cluster together.")
print()
print("  NEXT QUESTION:")
print("    'These methods work on paper, but how do they scale to millions")
print("     of users and items in production?'")
print("=" * 60)
