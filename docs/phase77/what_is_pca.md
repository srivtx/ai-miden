# What is PCA?

## 1. Why it exists (THE PROBLEM first)

You have a dataset with 500 features, but plotting it is impossible and training models on it is slow. Many of those features are correlated — height and shoe size, income and tax paid — so they carry redundant information. You need a way to compress the data into fewer dimensions while keeping as much useful information as possible, without knowing which features are important ahead of time.

## 2. Definition (very simple)

**Principal Component Analysis (PCA)** is a technique that finds new axes (principal components) along which the data varies the most. It then projects the data onto the top few axes, reducing dimensions while preserving the maximum possible variance.

**How it works:**
1. Center the data (subtract the mean).
2. Compute the covariance matrix (how every feature varies with every other).
3. Find the eigenvectors of that matrix — these are the principal components.
4. Project the data onto the top-K eigenvectors to get a lower-dimensional representation.

## 3. Real-life analogy

Imagine photographing a flock of birds from above. The birds form an oval cloud stretching northeast to southwest. You want to describe each bird's position with just one number instead of two (x and y).

- The **first principal component** is the long axis of the oval — the direction where the birds are most spread out.
- The **second principal component** is the short axis, perpendicular to the first.

If you only keep the first component, you lose a little information (the narrow spread across the short axis), but you capture the vast majority of the pattern with a single coordinate. PCA does exactly this in high-dimensional space.

## 4. Tiny numeric example

**Data:**
| x | y |
|---|---|
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |

**Step 1 — Center:**
Mean x = 2, mean y = 3
Centered: (-1, -1), (0, 0), (1, 1)

**Step 2 — Covariance matrix:**
```
Cov = [ [1.0, 1.0],
        [1.0, 1.0] ]
```

**Step 3 — Eigenvectors:**
- Eigenvalue 2.0 -> eigenvector [1/sqrt(2), 1/sqrt(2)] = [0.707, 0.707]
- Eigenvalue 0.0 -> eigenvector [-0.707, 0.707]

The first eigenvector points along the line y=x, which is exactly where the data lies.

**Step 4 — Project onto first component:**
- Point (-1, -1) . [0.707, 0.707] = -1.414
- Point (0, 0) . [0.707, 0.707] = 0.0
- Point (1, 1) . [0.707, 0.707] = 1.414

We reduced 2D to 1D and kept 100% of the variance because the data was perfectly correlated.

## 5. Common confusion (5+ bullet points)

- **"PCA removes features that are unimportant for prediction."** PCA only cares about variance, not prediction power. A feature with tiny variance might be the best predictor of your target. PCA is unsupervised.
- **"PCA always improves model performance."** Not true. If your model benefits from the original feature space, PCA can hurt performance by discarding nonlinear relationships.
- **"The principal components are the original features."** No. They are linear combinations of all original features. You cannot say "Component 1 is just height"; it is a weighted mix of many features.
- **"PCA is a clustering algorithm."** PCA is dimensionality reduction. It does not group points; it just re-expresses them in fewer dimensions. You can run K-means after PCA, but PCA alone does not cluster.
- **"You should always standardize before PCA."** Almost always yes, especially when features have different scales. If you skip standardization, high-variance features (like salary in dollars) will dominate the components.
- **"PCA preserves distances between all points."** No. PCA preserves variance along the chosen axes, but distances between arbitrary points can shrink or stretch in the reduced space.
- **"Eigenvectors and eigenvalues are only for PCA."** They appear everywhere in linear algebra: physics, graph theory, PageRank, and spectral clustering. PCA is just one application.

## 6. Where it is used in our code

`src/phase77/phase77_unsupervised_learning.py` implements PCA from scratch using NumPy. It centers the synthetic data, computes the covariance matrix, extracts eigenvectors and eigenvalues, and projects the data onto the top two principal components. The resulting 2D scatter plot shows how PCA compresses information while keeping the global structure visible.
