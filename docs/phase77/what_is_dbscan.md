# What is DBSCAN?

## 1. Why it exists (THE PROBLEM first)

K-means forces you to pick K ahead of time and assumes clusters are round and equally sized. In the real world, clusters can be any shape: a spiral galaxy, a crescent moon, or a dense core with sparse satellites. Worse, real data is full of noise — stray points that do not belong anywhere. You need an algorithm that discovers clusters of arbitrary shape, figures out how many there are automatically, and explicitly calls out noise points as outliers.

## 2. Definition (very simple)

**Density-Based Spatial Clustering of Applications with Noise (DBSCAN)** groups together points that are packed closely together, marks points that lie alone in low-density regions as noise, and can find clusters of any shape.

**How it works:**
1. Pick a distance threshold `eps` and a minimum point count `min_pts`.
2. A **core point** has at least `min_pts` neighbors within `eps`.
3. A **border point** is within `eps` of a core point but is not itself a core point.
4. A **noise point** is neither a core point nor a border point.
5. A **cluster** is formed by connecting core points that are within `eps` of each other, plus their border points.

## 3. Real-life analogy

Imagine dropping a handful of raisins and a few grains of salt onto a table.

- **K-means** would say "Divide everything into K piles" and might split a dense raisin cluster in half just because it was far from the others, while forcing isolated salt grains into clusters they do not belong to.
- **DBSCAN** says "If a raisin has enough other raisins nearby, start a pile. Keep adding raisins that touch the pile." Isolated salt grains with no neighbors nearby are labeled as noise and ignored.

DBSCAN naturally discovers that you have one pile of raisins, another pile across the table, and a bunch of scattered salt that is not part of any pile. It never needed you to say "there are 2 piles."

## 4. Tiny numeric example

**Points:** A(0,0), B(0.5,0), C(1,0), D(5,5), E(10,10)

**Parameters:** eps = 0.8, min_pts = 2

**Step 1 — Count neighbors within eps:**
- A: neighbors = {B} (distance 0.5). Count = 1. Not a core point.
- B: neighbors = {A, C} (distances 0.5, 0.5). Count = 2. **Core point.**
- C: neighbors = {B} (distance 0.5). Count = 1. Not a core point.
- D: no neighbors within 0.8. Noise.
- E: no neighbors within 0.8. Noise.

**Step 2 — Expand clusters:**
- B is a core point. A and C are within eps of B, so they join B's cluster as border points.

**Result:**
- Cluster 1: {A, B, C}
- Noise: {D, E}

Notice that DBSCAN discovered exactly one cluster without us specifying K=1. It also correctly rejected D and E as noise.

## 5. Common confusion (5+ bullet points)

- **"DBSCAN always finds the right number of clusters."** No. It finds the right number for your chosen `eps` and `min_pts`. A dense dataset with bad parameters can yield one giant cluster or hundreds of tiny ones.
- **"DBSCAN is better than K-means in every situation."** Not true. DBSCAN is slow on high-dimensional data (distance calculations explode) and fails when clusters have vastly different densities. K-means is faster and more predictable for simple, round clusters.
- **"Border points are always closer to their cluster center than to noise."** Border points are defined by proximity to any core point, not by global distance. A border point might be closer to a noise point than to other members of its cluster.
- **"DBSCAN can cluster any dataset."** The "curse of dimensionality" makes distance meaningless in very high dimensions, so DBSCAN (like all distance-based methods) struggles with text embeddings or image pixels unless preprocessed with PCA first.
- **"A noise point is definitely an outlier."** It is an outlier relative to the chosen `eps` and `min_pts`. If you increase `eps`, yesterday's noise can become today's border point.
- **"DBSCAN produces the same clusters every time."** For a fixed `eps` and `min_pts`, the result is deterministic. But the choice of `eps` is usually a guess, and two reasonable guesses can give very different results.
- **"Core points and border points are equally important."** Only core points can start clusters. If you remove all core points, the cluster collapses. Border points are just passengers.

## 6. Where it is used in our code

`src/phase77/phase77_unsupervised_learning.py` implements a simplified DBSCAN in NumPy. It computes pairwise distances, identifies core points that have at least `min_pts` neighbors within `eps`, and expands clusters by linking reachable core points. The plot shows how DBSCAN discovers the three synthetic clusters of varying density while explicitly marking scattered noise points in gray.
