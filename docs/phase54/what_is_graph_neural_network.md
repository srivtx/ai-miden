## What Is a Graph Neural Network?

---

### The Problem

Images are grids. Text is sequences. But what about social networks, molecules, traffic systems, or knowledge graphs? These are graphs — nodes connected by edges. Standard neural networks cannot handle graphs because nodes have varying numbers of neighbors and no fixed ordering. How do you apply deep learning to graph-structured data?

---

### Definition

A **Graph Neural Network (GNN)** is a neural network that operates on graph data by passing messages between connected nodes and updating each node's representation based on its neighbors.

**Key idea:**
```
For each node:
  1. Collect messages from neighboring nodes
  2. Aggregate messages (sum, mean, max)
  3. Update own representation using aggregated messages
  4. Repeat for multiple layers
```

**Why this works:**
- Each layer propagates information one hop through the graph
- After K layers, each node knows about nodes K hops away
- The network learns representations that encode both node features and graph structure

**Applications:**
- **Molecules:** Predict toxicity from atomic bonds
- **Social networks:** Recommend friends, detect communities
- **Knowledge graphs:** Answer questions by traversing relationships
- **Traffic:** Predict congestion from road network topology

---

### Real-Life Analogy

Gossip spreading through a social network.
- **Layer 0:** Each person knows only their own secret.
- **Layer 1:** Each person tells their secret to their friends. Now everyone knows their friends' secrets.
- **Layer 2:** Friends tell their friends. Now everyone knows their friends-of-friends' secrets.
- **After K layers:** Each person has a composite understanding of everyone within K degrees of separation.

A GNN is like this gossip process, but each person computes a weighted summary of what they hear and updates their "understanding" accordingly.

---

### Tiny Numeric Example

**Graph with 3 nodes:**
```
Node A: feature = [1.0, 0.0], neighbors = [B, C]
Node B: feature = [0.0, 1.0], neighbors = [A]
Node C: feature = [1.0, 1.0], neighbors = [A]
```

**GNN Layer 1 (mean aggregation):**
```
Message to A from B: [0.0, 1.0]
Message to A from C: [1.0, 1.0]
Aggregated at A: mean([0.0, 1.0], [1.0, 1.0]) = [0.5, 1.0]

A's new feature: update([1.0, 0.0], [0.5, 1.0])
                = [1.0, 0.0] + [0.5, 1.0] = [1.5, 1.0]
```

**After 2 layers:**
```
B receives A's updated feature [1.5, 1.0]
B's new feature incorporates information from A, which itself incorporated information from C
```

Node B now indirectly knows about Node C, even though they are not directly connected.

---

### Common Confusion

1. **"GNNs are just CNNs on graphs."** Related but different. CNNs use fixed-size kernels on grids. GNNs use variable-size neighborhoods on graphs.

2. **"GNNs need the entire graph in memory."** For large graphs, sampling techniques (GraphSAGE, Cluster-GCN) train on subgraphs.

3. **"All nodes are treated equally."** No. Attention mechanisms (GAT) learn which neighbors are most important.

4. **"GNNs only work for small graphs."** Modern GNNs handle billion-node graphs (e.g., Pinterest's recommendation graph).

5. **"GNNs replace graph algorithms."** They complement them. PageRank, shortest path, and community detection still matter.

---

### Where It Is Used in Our Code

`src/phase54/phase54_graph_neural_networks.py` — We implement a simple GNN that classifies nodes in a synthetic graph by propagating messages between neighbors and aggregating them.
