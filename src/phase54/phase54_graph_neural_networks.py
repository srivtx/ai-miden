#!/usr/bin/env python3
"""
Phase 54: Graph Neural Networks — NumPy Concept Demo
======================================================
This script demonstrates how neural networks handle graph-structured data.

Key insight: Images are grids, text is sequences, but graphs have arbitrary
connections. GNNs learn by passing messages between connected nodes.

Concepts demonstrated:
  - Message passing framework
  - GCN (Graph Convolutional Network) with degree normalization
  - GAT (Graph Attention Network) with learned attention weights
  - Node classification on a synthetic community graph
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(54)

# =============================================================================
# SECTION 1: BUILD A SYNTHETIC GRAPH WITH COMMUNITY STRUCTURE
# =============================================================================
# 8 nodes, 2 communities:
#   Community A: nodes 0, 1, 2, 3 (well-connected among themselves)
#   Community B: nodes 4, 5, 6, 7 (well-connected among themselves)
#   Sparse edges between communities

n_nodes = 8
n_features = 2

# Node features: Community A centers around [1, 0], Community B around [0, 1]
features = np.array([
    [1.0, 0.1],   # node 0 (A)
    [0.9, 0.2],   # node 1 (A)
    [1.1, 0.0],   # node 2 (A)
    [0.8, 0.3],   # node 3 (A)
    [0.1, 0.9],   # node 4 (B)
    [0.2, 1.0],   # node 5 (B)
    [0.0, 0.8],   # node 6 (B)
    [0.3, 0.7],   # node 7 (B)
])

# Labels: 0 = Community A, 1 = Community B
labels = np.array([0, 0, 0, 0, 1, 1, 1, 1])

# Adjacency list (undirected edges)
edges = [
    (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3),  # Community A dense
    (4, 5), (4, 6), (4, 7), (5, 6), (5, 7), (6, 7),  # Community B dense
    (0, 4), (3, 7),  # Sparse cross-community bridges
]

# Build adjacency matrix with self-loops
A = np.eye(n_nodes)
for i, j in edges:
    A[i, j] = 1
    A[j, i] = 1

print("="*60)
print("Phase 54: Graph Neural Networks")
print("="*60)
print(f"\nGraph: {n_nodes} nodes, {len(edges)} edges")
print(f"Communities: A=[0,1,2,3], B=[4,5,6,7]")
print(f"Features shape: {features.shape}")

# =============================================================================
# SECTION 2: MESSAGE PASSING (Mean Aggregation)
# =============================================================================

print("\n--- Message Passing (Mean Aggregation) ---")

# Degree matrix (for normalization)
degrees = A.sum(axis=1)
D_inv = np.diag(1.0 / degrees)

# One round of mean message passing: h' = D^-1 @ A @ h
messages = A @ features  # sum of neighbor features
features_mp = D_inv @ messages  # normalize by degree

print("Features after 1 round of message passing:")
for i in range(n_nodes):
    print(f"  Node {i}: [{features_mp[i, 0]:.2f}, {features_mp[i, 1]:.2f}]  (label={labels[i]})")

# =============================================================================
# SECTION 3: GCN LAYER (Symmetric Normalization)
# =============================================================================
# GCN: h' = D^-0.5 @ A @ D^-0.5 @ h @ W

print("\n--- GCN Layer (Symmetric Normalization) ---")

D_sqrt_inv = np.diag(1.0 / np.sqrt(degrees))
A_gcn = D_sqrt_inv @ A @ D_sqrt_inv  # normalized adjacency

# Simple weight matrix: rotate and scale
W_gcn = np.array([[1.0, 0.5],
                  [-0.5, 1.0]])

features_gcn = A_gcn @ features @ W_gcn
# ReLU activation
features_gcn = np.maximum(features_gcn, 0)

print("Features after GCN layer:")
for i in range(n_nodes):
    print(f"  Node {i}: [{features_gcn[i, 0]:.2f}, {features_gcn[i, 1]:.2f}]  (label={labels[i]})")

# =============================================================================
# SECTION 4: GRAPH ATTENTION (GAT)
# =============================================================================
# Single-head attention: learn attention scores between neighbors

print("\n--- Graph Attention Network (GAT) ---")

# Weight matrix for feature transformation
W_gat = np.array([[0.8, 0.2],
                  [0.2, 0.8]])

# Attention vector
a_gat = np.array([0.5, 0.5])

features_gat = np.zeros((n_nodes, 2))

for i in range(n_nodes):
    # Transform node features
    h_i = W_gat @ features[i]
    
    # Find neighbors (including self)
    neighbors = np.where(A[i] > 0)[0]
    
    # Compute attention scores
    scores = []
    for j in neighbors:
        h_j = W_gat @ features[j]
        # Concatenate and compute score
        concat = np.concatenate([h_i, h_j])
        score = np.tanh(np.dot(a_gat, concat[:2]) + np.dot(a_gat, concat[2:]))
        scores.append(score)
    
    scores = np.array(scores)
    # Softmax normalization
    attn_weights = np.exp(scores) / np.sum(np.exp(scores))
    
    # Aggregate weighted messages
    h_new = np.zeros(2)
    for idx, j in enumerate(neighbors):
        h_j = W_gat @ features[j]
        h_new += attn_weights[idx] * h_j
    
    features_gat[i] = np.maximum(h_new, 0)  # ReLU
    
    if i in [0, 4]:  # Print attention for one node from each community
        print(f"  Node {i} attention weights:")
        for idx, j in enumerate(neighbors):
            print(f"    → Node {j}: {attn_weights[idx]:.3f}")

print("\nFeatures after GAT layer:")
for i in range(n_nodes):
    print(f"  Node {i}: [{features_gat[i, 0]:.2f}, {features_gat[i, 1]:.2f}]  (label={labels[i]})")

# =============================================================================
# SECTION 5: NODE CLASSIFICATION (Simple Linear Classifier on GNN Features)
# =============================================================================

print("\n--- Node Classification ---")

# Use GCN features for classification
# Train a simple logistic regression on 6 nodes, test on 2
train_mask = np.array([True, True, True, False, True, True, True, False])
test_mask = ~train_mask

X_train = features_gcn[train_mask]
y_train = labels[train_mask]

# Train: find best separating hyperplane via least squares
X_aug = np.column_stack([X_train, np.ones(X_train.shape[0])])
w = np.linalg.lstsq(X_aug, y_train, rcond=None)[0]

# Predict
X_test = features_gcn[test_mask]
X_test_aug = np.column_stack([X_test, np.ones(X_test.shape[0])])
preds = (X_test_aug @ w > 0.5).astype(int)
acc = np.mean(preds == labels[test_mask])

print(f"Train nodes: {np.where(train_mask)[0]}")
print(f"Test nodes: {np.where(test_mask)[0]}")
print(f"Predictions: {preds}")
print(f"True labels: {labels[test_mask]}")
print(f"Accuracy: {acc*100:.0f}%")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Original features
def plot_features(ax, feats, title, show_edges=True):
    colors = ['#e74c3c' if l == 0 else '#3498db' for l in labels]
    ax.scatter(feats[:, 0], feats[:, 1], c=colors, s=200, edgecolors='black', zorder=3)
    for i in range(n_nodes):
        ax.annotate(str(i), (feats[i, 0], feats[i, 1]), ha='center', va='center', fontsize=9, fontweight='bold')
    if show_edges:
        for i, j in edges:
            ax.plot([feats[i, 0], feats[j, 0]], [feats[i, 1], feats[j, 1]], 'k-', alpha=0.2, linewidth=1)
    ax.set_title(title)
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.grid(True, alpha=0.3)

plot_features(axes[0, 0], features, 'Original Features', show_edges=True)
plot_features(axes[0, 1], features_mp, 'After Message Passing', show_edges=False)
plot_features(axes[1, 0], features_gcn, 'After GCN Layer', show_edges=False)
plot_features(axes[1, 1], features_gat, 'After GAT Layer', show_edges=False)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#e74c3c', edgecolor='black', label='Community A'),
                   Patch(facecolor='#3498db', edgecolor='black', label='Community B')]
fig.legend(handles=legend_elements, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 0.98))

plt.tight_layout(rect=[0, 0, 1, 0.96])
os.makedirs('src/phase54', exist_ok=True)
plt.savefig('src/phase54/graph_neural_networks.png', dpi=150)
print("\nSaved plot to src/phase54/graph_neural_networks.png")

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Node classification accuracy: {acc*100:.0f}%")
print("\nGraph Neural Networks extend deep learning to arbitrary graphs:")
print("  - Message passing: nodes exchange information with neighbors")
print("  - GCN: normalized aggregation stabilizes learning")
print("  - GAT: attention learns which neighbors matter most")
print("  - After propagation, nodes in the same community cluster together")
print("\nApplications: molecules, social networks, knowledge graphs, traffic")
