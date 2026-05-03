# What is K-Means Clustering?

## 1. Why it exists (THE PROBLEM first)

You have a dataset with thousands of customer transactions, but no labels telling you which customers belong to which segment. You need to discover natural groupings so you can target marketing, detect fraud, or recommend products. Without labels, supervised learning cannot help. You need an algorithm that finds structure on its own.

## 2. Definition (very simple)

**K-means clustering** is an algorithm that partitions data into K groups by repeatedly assigning each point to the nearest group center (centroid) and then moving each centroid to the average of its assigned points. It stops when the centroids stop moving.

**The two steps:**
1. **Assign:** Each point joins the cluster whose centroid is closest.
2. **Update:** Each centroid moves to the mean of all points in its cluster.

Repeat until stable.

## 3. Real-life analogy

Imagine a teacher who walks into a dark gymnasium where students are standing randomly. The teacher needs to divide them into K teams but cannot see well.

- The teacher randomly places K cones on the floor (initial centroids).
- Every student walks to the nearest cone (assignment).
- The teacher moves each cone to the center of the students gathered around it (update).
- Students walk to the new nearest cone again.

After a few rounds, the cones stop moving. Each cone now sits in the true center of a natural group of students. The teams have been discovered without anyone telling the teacher who should be on which team.

## 4. Tiny numeric example

**Data points:** A(1, 1), B(2, 1), C(5, 5), D(6, 5)

**Goal:** K = 2 clusters

**Initial centroids:** C1 = (1, 2), C2 = (6, 4)

**Step 1 — Assign:**
- Distance A to C1 = sqrt((1-1)^2 + (1-2)^2) = 1.0
- Distance A to C2 = sqrt((1-6)^2 + (1-4)^2) = 5.8
- A is closer to C1. By the same logic, B goes to C1; C and D go to C2.

Cluster 1: {A, B}, Cluster 2: {C, D}

**Step 2 — Update:**
- New C1 = ((1+2)/2, (1+1)/2) = (1.5, 1.0)
- New C2 = ((5+6)/2, (5+5)/2) = (5.5, 5.0)

**Next assign:** A and B are still closer to C1; C and D are still closer to C2.
Centroids do not move again. Convergence reached.

Final clusters: {A, B} and {C, D}.

## 5. Common confusion (5+ bullet points)

- **"K-means finds the globally best clusters."** No. K-means only finds a local optimum. Random initialization can yield completely different clusters, which is why K-means++ and multiple restarts are standard.
- **"The elbow method always gives a clear K."** The elbow is often a smooth curve with no obvious bend. It is a heuristic, not a theorem.
- **"K-means can find clusters of any shape."** No. K-means assumes spherical, equally-sized clusters because it uses Euclidean distance to a single center. It fails on crescents, rings, or stretched ellipses.
- **"K-means is deterministic."** Without fixed initialization, it is random. Two runs can produce different assignments, so always set a random seed or use K-means++.
- **"You must scale your data before K-means."** Not always, but usually yes. If one feature is in dollars (0-100,000) and another is in ratings (0-5), distance is dominated by dollars. Standardizing features prevents this bias.
- **"K-means handles outliers well."** Outliers drag centroids toward them. A single extreme point can warp an entire cluster. DBSCAN or K-medoids are more robust.
- **"K-means can be used for classification directly."** K-means is unsupervised. The cluster labels (0, 1, 2) have no semantic meaning and may not align with true class labels.

## 6. Where it is used in our code

`src/phase77/phase77_unsupervised_learning.py` implements K-means from scratch using only NumPy. It generates 2D data with three true clusters, initializes three centroids, and alternates assignment and update steps until convergence. The final cluster assignments and centroids are plotted so you can see the algorithm discover structure without any labels.
