## What Is GCN?

---

### The Problem

You have a graph where each node has features. You want to classify nodes based on both their own features and their neighbors' features. How do you aggregate neighbor information in a way that preserves graph structure and handles varying node degrees?

---

### Definition

**GCN (Graph Convolutional Network)** is a GNN that updates each node's representation by averaging its neighbors' features, normalized by node degree.

**The GCN update rule:**
```
h_i^(l+1) = σ(Σ_j (1/√(d_i × d_j)) × W^(l) × h_j^(l))
```

Where:
- `h_i^(l)` = feature vector of node i at layer l
- `d_i` = degree of node i (number of neighbors)
- `W^(l)` = learnable weight matrix at layer l
- `σ` = activation function (e.g., ReLU)
- The sum is over all neighbors j of node i (including i itself)

**Why normalization matters:**
- Without normalization, high-degree nodes (like celebrities in a social network) dominate
- `1/√(d_i × d_j)` balances the influence so all nodes contribute fairly
- This is called "symmetric normalization"

**GCN as a Laplacian smoothing operator:**
- Each layer averages node features with neighbors
- After K layers, features are smoothed over K-hop neighborhoods
- This is why GCNs work: connected nodes tend to have similar labels

---

### Real-Life Analogy

Averaging exam scores within study groups.
- **Without normalization:** A study group of 20 students dominates the average. Their average becomes everyone's score, even if other groups have only 3 students.
- **With GCN normalization:** Each group's contribution is divided by the square root of its size. Large groups still matter, but small groups are not drowned out.
- **Self-connection:** Each student also includes their own score in the average (not just their group).

The result is a fairer, more balanced representation that respects both individual merit and peer influence.

---

### Tiny Numeric Example

**Graph:**
```
Node A: degree 2, feature = [2.0]
Node B: degree 2, feature = [4.0]
Node C: degree 1, feature = [6.0]

Edges: A-B, B-C (line graph)
```

**GCN Layer 1 (W = [0.5], no activation):**

**Node A update:**
```
Neighbors: A (self), B
Contribution from A: (1/√(2×2)) × 0.5 × 2.0 = 0.5 × 0.5 × 2.0 = 0.5
Contribution from B: (1/√(2×2)) × 0.5 × 4.0 = 0.5 × 0.5 × 4.0 = 1.0
New h_A = 0.5 + 1.0 = 1.5
```

**Node B update:**
```
Neighbors: A, B (self), C
Contribution from A: (1/√(2×2)) × 0.5 × 2.0 = 0.5
Contribution from B: (1/√(2×2)) × 0.5 × 4.0 = 1.0
Contribution from C: (1/√(2×1)) × 0.5 × 6.0 = 0.707 × 3.0 = 2.12
New h_B = 0.5 + 1.0 + 2.12 = 3.62
```

**Node C update:**
```
Neighbors: B, C (self)
Contribution from B: (1/√(1×2)) × 0.5 × 4.0 = 0.707 × 2.0 = 1.41
Contribution from C: (1/√(1×1)) × 0.5 × 6.0 = 3.0
New h_C = 1.41 + 3.0 = 4.41
```

**Result:**
```
Before: A=2.0, B=4.0, C=6.0
After:  A=1.5, B=3.62, C=4.41
```

Features moved toward neighbors — A and C pulled B toward the middle.

---

### Common Confusion

1. **"GCN is just averaging neighbors."** It is averaging with degree normalization and a learned weight matrix. The weight matrix is crucial.

2. **"GCN works for directed graphs."** The standard GCN formula assumes undirected graphs. Directed variants exist but are more complex.

3. **"More GCN layers are always better."** Too many layers cause over-smoothing — all node features converge to the same value.

4. **"GCN handles edge features."** Standard GCN does not. Variants like GAT and R-GCN do.

5. **"GCN is the best GNN."** It is simple and effective, but GAT (attention), GraphSAGE (sampling), and GIN (expressiveness) often outperform it on specific tasks.

---

### Where It Is Used in Our Code

`src/phase54/phase54_graph_neural_networks.py` — We implement a 2-layer GCN on a synthetic graph, showing how node features propagate and converge based on graph topology.
