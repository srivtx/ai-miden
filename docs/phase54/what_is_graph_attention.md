## What Is Graph Attention?

---

### The Problem

In GCN, all neighbors contribute equally to a node's update. But in reality, some neighbors are more important than others. In a social network, a close friend's opinion matters more than a distant acquaintance's. In a molecule, a bonded oxygen matters more than a distant hydrogen. How do you learn which neighbors to pay attention to?

---

### Definition

**GAT (Graph Attention Network)** is a GNN that uses attention mechanisms to learn the importance of each neighbor when aggregating messages.

**The GAT update rule:**
```
For node i and neighbor j:
  e_ij = LeakyReLU(a^T × [W×h_i || W×h_j])
  α_ij = softmax_j(e_ij) = exp(e_ij) / Σ_k exp(e_ik)
  h_i' = σ(Σ_j α_ij × W × h_j)
```

Where:
- `e_ij` = attention score (how much node i should attend to node j)
- `a` = learnable attention vector
- `α_ij` = normalized attention weight (sum over neighbors = 1)
- `W` = learnable weight matrix
- `||` = concatenation

**Multi-head attention:**
- Run K independent attention mechanisms in parallel
- Concatenate or average their outputs
- This is identical to Transformer multi-head attention, but on graph edges

**Why GAT is powerful:**
- Different neighbors get different weights
- The weights are interpretable (you can see which neighbors matter)
- Works for both transductive and inductive tasks

---

### Real-Life Analogy

A committee meeting.
- **GCN:** Everyone on the committee votes equally. The janitor's vote counts the same as the CEO's.
- **GAT:** The chairperson learns to weight each member's input. The CFO's financial opinion gets high weight. The intern's opinion gets low weight. The weights are learned from past decisions.
- **Multi-head:** Three subcommittees each vote independently, then their recommendations are combined.

GAT is the chairperson who learns who to listen to.

---

### Tiny Numeric Example

**Node A with neighbors B and C:**
```
h_A = [1.0, 0.0]
h_B = [0.0, 1.0]
h_C = [2.0, 0.0]
W = identity matrix (for simplicity)
a = [0.5, 0.5]  (attention vector)
```

**Attention scores:**
```
e_AB = LeakyReLU([0.5, 0.5] · [1.0, 0.0, 0.0, 1.0])
     = LeakyReLU(0.5×1.0 + 0.5×0.0 + 0.5×0.0 + 0.5×1.0)
     = LeakyReLU(1.0) = 1.0

e_AC = LeakyReLU([0.5, 0.5] · [1.0, 0.0, 2.0, 0.0])
     = LeakyReLU(0.5 + 0 + 1.0 + 0)
     = LeakyReLU(1.5) = 1.5
```

**Attention weights:**
```
α_AB = exp(1.0) / (exp(1.0) + exp(1.5)) = 2.72 / (2.72 + 4.48) = 0.38
α_AC = exp(1.5) / (exp(1.0) + exp(1.5)) = 4.48 / (2.72 + 4.48) = 0.62
```

**Node A update:**
```
h_A' = 0.38 × [0.0, 1.0] + 0.62 × [2.0, 0.0]
     = [0.0, 0.38] + [1.24, 0.0]
     = [1.24, 0.38]
```

Node A pays more attention to C (weight 0.62) than B (weight 0.38).

---

### Common Confusion

1. **"GAT is just GCN with weights."** The weights are learned per-edge per-layer dynamically, not fixed like GCN's degree normalization.

2. **"Attention weights are static."** No. They change for every layer and depend on the current node features.

3. **"GAT is slower than GCN."** Yes, computing attention adds overhead. But the improved accuracy often justifies it.

4. **"GAT only works for node classification."** It works for link prediction, graph classification, and any graph task.

5. **"Multi-head attention is always better."** Usually yes, but it increases parameters and compute. 4-8 heads is typical.

---

### Where It Is Used in Our Code

`src/phase54/phase54_graph_neural_networks.py` — We implement a single-head GAT layer, showing how attention weights dynamically focus on the most relevant neighbors.
