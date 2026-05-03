## What Is Message Passing?

---

### The Problem

GNNs seem magical — how does information flow through a graph? Is there a general framework that unifies GCN, GAT, GraphSAGE, and all other GNN variants?

---

### Definition

**Message passing** is the general framework underlying all GNNs. It describes how nodes exchange information (messages) along edges and update their states.

**The message passing framework:**
```
For each node i:
  1. MESSAGE: For each neighbor j, compute message m_ji = M(h_i, h_j, e_ij)
  2. AGGREGATE: Combine messages: m_i = AGGREGATE({m_ji for all j in N(i)})
  3. UPDATE: Update node state: h_i' = U(h_i, m_i)
```

Where:
- `M` = message function (how to transform neighbor features)
- `AGGREGATE` = aggregation function (sum, mean, max)
- `U` = update function (how to combine old state with messages)
- `e_ij` = edge features (optional)

**Different GNNs as message passing:**
```
GCN:
  M(h_i, h_j) = (1/√(d_i d_j)) × W × h_j
  AGGREGATE = sum
  U = ReLU

GAT:
  M(h_i, h_j) = α_ij × W × h_j
  AGGREGATE = sum
  U = ReLU

GraphSAGE:
  M(h_i, h_j) = W × h_j
  AGGREGATE = mean or max
  U = concat(h_i, m_i)
```

**Why message passing is powerful:**
- Any GNN can be expressed in this framework
- It is parallelizable (all nodes update simultaneously)
- It is the theoretical foundation of geometric deep learning

---

### Real-Life Analogy

A town hall meeting.
- **Nodes:** Residents
- **Edges:** Friendships
- **Messages:** Each resident tells their friends what they think about a new park
- **Aggregation:** Each resident forms an opinion by averaging what their friends said
- **Update:** Each resident updates their own view based on their friends' input
- **Repeat:** Next week, everyone shares their updated views. Opinions spread.

After several rounds, the town reaches a consensus (or identifies clusters of disagreement). This is exactly how message passing works.

---

### Tiny Numeric Example

**Graph:**
```
A -- B
|    |
C -- D
```

**Round 1:**
```
A tells B and C: "I support the park"
B tells A and D: "I oppose the park"
C tells A and D: "I support the park"
D tells B and C: "I oppose the park"
```

**Aggregation (mean):**
```
A hears: support (from C) + support (self) = 2 support, 0 oppose
B hears: oppose (from D) + oppose (self) = 0 support, 2 oppose
C hears: support (from A) + support (self) = 2 support, 0 oppose
D hears: oppose (from B) + oppose (self) = 0 support, 2 oppose
```

**Round 2:**
```
A tells B: "support" (but B already opposes)
B tells A: "oppose"
```

The graph splits into two clusters: {A, C} support and {B, D} oppose. Message passing reveals the community structure.

---

### Common Confusion

1. **"Message passing is unique to GNNs."** No. Belief propagation in graphical models, PageRank, and even epidemic models use the same concept.

2. **"Message passing must be synchronous."** Usually yes (all nodes update in parallel). Asynchronous versions exist but are harder to parallelize.

3. **"More rounds are always better."** Like GCN layers, too many rounds cause over-smoothing where all nodes become identical.

4. **"Message passing only works for static graphs."** Temporal GNNs extend message passing to time-evolving graphs.

5. **"Message passing is the only way to do graph learning."** It is the dominant paradigm, but spectral methods (using graph Fourier transforms) are an alternative.

---

### Where It Is Used in Our Code

`src/phase54/phase54_graph_neural_networks.py` — We implement the message passing framework explicitly, showing how messages flow from neighbors to nodes and how different aggregation functions change the result.
