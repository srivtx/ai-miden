← [Previous: Phase 53: Classical Reinforcement Learning](docs/phase53/SUMMARY.md) | [Next: Phase 55: Distributed Training](docs/phase55/SUMMARY.md) →

---

## Phase 54: Graph Neural Networks

---

### What We Built

A synthetic graph with two communities (8 nodes, 14 edges) where GCN and GAT layers propagate information between neighbors and separate the communities in feature space.

### Key Results

- **Message passing:** Features smoothed toward neighbors
- **GCN layer:** Community A features become [0.67-0.83, 0.59-0.72], Community B becomes [0.00, 0.88-0.92]
- **GAT layer:** Attention weights dynamically balance neighbor influence
- **Classification:** 100% accuracy on held-out test nodes

### Concepts Covered

| Term | File |
|---|---|
| Graph Neural Network | `what_is_graph_neural_network.md` |
| GCN | `what_is_gcn.md` |
| Graph Attention | `what_is_graph_attention.md` |
| Message Passing | `what_is_message_passing.md` |

### Connection to Next Phase

Now that we can learn on graphs, how do we train models that don't fit on a single machine? Phase 55 covers **distributed training**.

### Files

- `docs/phase54/what_is_graph_neural_network.md`
- `docs/phase54/what_is_gcn.md`
- `docs/phase54/what_is_graph_attention.md`
- `docs/phase54/what_is_message_passing.md`
- `docs/phase54/SUMMARY.md`
- `src/phase54/phase54_graph_neural_networks.py`
- `src/phase54/graph_neural_networks.png`

---

← [Previous: Phase 53: Classical Reinforcement Learning](docs/phase53/SUMMARY.md) | [Next: Phase 55: Distributed Training](docs/phase55/SUMMARY.md) →