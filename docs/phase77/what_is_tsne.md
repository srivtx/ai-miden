# What is t-SNE?

## 1. Why it exists (THE PROBLEM first)

PCA is great for compression, but it only captures linear relationships and global variance. When you project high-dimensional data down to 2D for visualization, PCA often smashes clusters together because it tries to preserve the largest spread, not the local neighborhoods. You need a method that keeps nearby points close and far-away points far apart, so that visual clusters in 2D actually correspond to real clusters in the original space.

## 2. Definition (very simple)

**t-Distributed Stochastic Neighbor Embedding (t-SNE)** is a dimensionality reduction technique that converts high-dimensional distances between points into probabilities of being neighbors, then finds a low-dimensional arrangement where those neighbor probabilities match as closely as possible.

**Key idea:**
- In high-D: compute similarity between points using a Gaussian kernel.
- In low-D: compute similarity using a Student-t kernel (heavier tails).
- Move low-D points around to minimize the KL divergence between the two similarity distributions.

## 3. Real-life analogy

Imagine a city with skyscrapers. From a helicopter, you want to draw a flat map that preserves which buildings are close to each other on the ground, even though the real city is 3D.

- PCA would preserve the overall east-west and north-south spread, possibly placing two buildings on opposite sides of the map just because one is much taller.
- t-SNE asks: "Who are each building's immediate neighbors?" It then draws the flat map so that those neighbor relationships are preserved, even if the global distances get distorted. Two buildings on the same block stay close; buildings in different boroughs can be pushed far apart or placed arbitrarily, as long as their local neighborhoods match.

## 4. Tiny numeric example

**High-D points:** A(0, 0), B(0, 1), C(10, 10)

**Step 1 — Compute pairwise similarities with Gaussian:**
- Distance AB = 1.0. Similarity P(A,B) is high.
- Distance AC = 14.1. Similarity P(A,C) is near zero.
- Distance BC = 13.5. Similarity P(B,C) is near zero.

So in high-D, A and B are neighbors; C is an outlier.

**Step 2 — Random low-D initialization:**
A'=(0.5, 0.2), B'=(0.1, 0.8), C'=(5.0, 5.0)

**Step 3 — Compute low-D similarities with Student-t:**
Because of the heavy-tailed t-distribution, moderate distances in low-D still get some probability mass. The KL divergence penalizes heavily if A and B are far apart in low-D (they were neighbors in high-D), but cares less if C is placed arbitrarily because C had no strong relationships.

**Step 4 — Gradient descent nudges A' and B' closer together.**
After a few iterations, A' and B' cluster, while C' sits alone. The local neighborhood is preserved.

## 5. Common confusion (5+ bullet points)

- **"t-SNE preserves global structure."** No. t-SNE explicitly prioritizes local neighborhoods over global distances. The distance between two clusters in a t-SNE plot has no guaranteed meaning.
- **"Cluster size in t-SNE means something."** It does not. Because of the Student-t kernel, t-SNE tends to expand dense clusters and compress sparse ones. A big blob is not necessarily more points than a small blob.
- **"Running t-SNE longer always gives a better plot."** After convergence, running longer just adds noise. The plot drifts randomly because the objective has many equivalent minima related by rotation and translation.
- **"t-SNE is deterministic."** It is highly stochastic. Different random seeds produce different layouts. Always run it multiple times and look for consistent patterns.
- **"Perplexity is just a guess."** Perplexity is roughly the effective number of nearest neighbors each point considers. Typical values are 5-50. Too low = tiny clusters; too high = everything merges into one blob.
- **"You can use t-SNE as a preprocessing step for classification."** Bad idea. t-SNE is nonlinear, non-parametric, and stochastic. It does not produce a reusable mapping. Use PCA or an autoencoder for preprocessing.
- **"t-SNE and PCA are interchangeable."** PCA is linear, deterministic, and preserves global variance. t-SNE is nonlinear, stochastic, and preserves local neighborhoods. Use PCA for compression; use t-SNE for visualization.

## 6. Where it is used in our code

`src/phase77/phase77_unsupervised_learning.py` includes a simplified t-SNE implementation in NumPy. It computes high-dimensional neighbor probabilities with a Gaussian kernel, initializes random 2D positions, and performs gradient descent to match those neighbor relationships in 2D. The resulting plot shows how t-SNE separates the three synthetic clusters more cleanly than PCA, at the cost of global distance distortion.
