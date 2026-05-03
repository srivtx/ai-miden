← [Previous: Phase 76: Fairness & Bias](docs/phase76/SUMMARY.md) | [Next: Phase 78: Object Detection & Segmentation](docs/phase78/SUMMARY.md) →

---

# Phase 77 Summary: Unsupervised Learning

## What You Learned

This phase covered how to discover hidden structure in data that has no labels.
You learned four foundational algorithms that every data scientist uses before
building supervised models.

### Key Terms

| Term | One-Sentence Meaning |
|---|---|
| **K-Means** | Repeatedly assign points to the nearest centroid, then move centroids to the cluster mean. |
| **Elbow Method** | Plot inertia versus K and look for a bend to guess the number of clusters. |
| **PCA** | Find the axes of maximum variance and project data onto them to reduce dimensions. |
| **Eigenvector** | A direction that only gets stretched (not rotated) when a matrix transforms it. |
| **t-SNE** | Match neighbor probabilities between high-D and low-D space to produce visualizable clusters. |
| **DBSCAN** | Grow clusters from dense core points; mark isolated points as noise. |

## How It Connects

- **Phase 72 (Real Agents)** used tools and reasoning with structured data.
- **Phase 77** steps back to explore raw, unlabeled data before applying any model.
- **Phase 79 (Causal Inference)** will ask "why" the clusters exist, not just "what" they are.

## The Math in Plain English

**K-Means:** Pick K centers. Everyone joins the closest center. Move each center
to the average of its members. Repeat until nobody changes teams.

**PCA:** Center the data. Find the directions where the cloud is stretched the
most. Those directions are the eigenvectors of the covariance matrix. Keep the
top few and throw away the rest.

**t-SNE:** In high-D, measure "who is close to whom." In low-D, arrange points
so the same "who is close to whom" relationships hold. Distort global distances
freely; protect local neighborhoods at all costs.

**DBSCAN:** A point is a "core" point if it has enough neighbors nearby. Start
a cluster at any core point and add every reachable core point and its neighbors.
Points with no dense neighbors are noise.

## Code You Built

| File | What It Does |
|---|---|
| `src/phase77/phase77_unsupervised_learning.py` | NumPy from-scratch implementations of K-means, PCA, t-SNE, and DBSCAN on synthetic data. |
| `src/phase77/phase77_unsupervised_learning_colab.py` | Real sklearn workflow on the digits dataset with PCA variance analysis and cluster visualization. |

## The Big Idea

Supervised learning is powerful, but labels are expensive and often impossible
to get. Unsupervised learning lets the data speak for itself: find groups,
compress dimensions, visualize structure, and spot outliers. These four
algorithms — K-means, PCA, t-SNE, and DBSCAN — are the lens through which
every data scientist first looks at a new dataset.

---

← [Previous: Phase 76: Fairness & Bias](docs/phase76/SUMMARY.md) | [Next: Phase 78: Object Detection & Segmentation](docs/phase78/SUMMARY.md) →
