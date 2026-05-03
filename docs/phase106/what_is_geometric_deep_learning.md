## What Is Geometric Deep Learning?

---

## The Problem

Standard neural networks treat input features as flat vectors. A CNN assumes a regular grid; an MLP assumes no structure at all. But many scientific datasets live on non-Euclidean domains: 3D molecular graphs, protein surfaces, LiDAR point clouds, and brain connectivity networks. Applying a standard CNN to a point cloud requires voxelization, which destroys fine-grained geometry and rotational invariance. Applying an MLP to a molecular graph treats bonded and distant atoms as equally related. How do you build architectures that respect the inherent geometry of the data?

---

## Definition

**Geometric Deep Learning** is a broad field that extends deep learning beyond grid-structured data (like images) to data with geometric structure. It includes graph neural networks, convolutional networks on meshes, and equivariant networks on point clouds. The key insight is to build architectures that respect the symmetries and invariances of the underlying domain.

**How it works:**
```
Standard approach:   3D point cloud → voxelize into 64x64x64 grid → 3D CNN
                     Problems: rotation-dependent, memory-heavy, resolution-limited

Geometric approach:  3D point cloud → graph where nodes are atoms,
                     edges are bonds or distance cutoffs
                     → message passing using distances and angles
                     → rotation-invariant, continuous, memory-efficient
```

**Key domains:**
- **Graphs:** molecules, social networks, knowledge bases (GNNs)
- **Meshes:** protein surfaces, computer graphics, CAD models (mesh CNNs)
- **Point clouds:** LiDAR, 3D scanning, particle physics (point cloud networks)
- **Manifolds:** brain surfaces, climate data on the sphere (spherical CNNs)

**Why this matters:**
- Standard CNNs fail on molecular data because they are not rotation-invariant
- Geometric networks generalize across orientations and deformations without data augmentation
- They achieve state-of-the-art results on molecular property prediction, protein folding, and materials design

---

## Real-Life Analogy

Imagine trying to recognize a chair. A standard CNN learns that the backrest is at pixel coordinates (50, 100). If you move the chair to the right side of the image, the CNN fails because the backrest is now at (150, 100) and the network has no concept of "part" independent of "position." Geometric Deep Learning is like recognizing the chair by its parts and how they connect: four legs support a seat, a backrest rises from the rear, and armrests may extend from the sides. This description is true regardless of where the chair sits or which way it faces. The network learns topology and geometry, not pixel coordinates.

But the chair analogy understates the scientific stakes. In drug discovery, the "chair" is a protein binding pocket, and the orientation is a 3D rotation in space. A standard approach voxelizes the pocket into a grid and runs a 3D CNN. If the protein is crystallized in a different orientation, the same pocket produces a completely different voxel grid, and the CNN treats it as a different molecule. A geometric network processes the pocket as a graph of atoms connected by distances. Rotate the entire protein, and the distances stay the same. The prediction is invariant.

The trade-off is between generality and specialization. A standard CNN is general: it works on any image, regardless of content. A geometric network is specialized: it knows the data lives in 3D space with distances and angles. This specialization makes it powerful for scientific data but irrelevant for text or tabular data. Geometric Deep Learning is not a replacement for standard deep learning; it is an expansion into domains where geometry is the primary structure.

---

## Tiny Numeric Example

**A protein backbone represented as 10 amino acids in 3D:**

**Standard approach (voxelization):**
```
Resolution:         1 Angstrom per voxel
Grid size:          32x32x32 = 32,768 voxels
Parameters:         3D conv layers with millions of weights
Rotation issue:     Rotating the protein changes which voxels are occupied
                    → different input → different prediction
```

**Geometric approach (distance-based graph):**
```
Nodes:              10 (one per amino acid)
Edges:              pairwise distances < 10 Angstroms
Features:           mean distance, std distance, min distance, max distance
Parameters:         graph message passing with shared weights
Rotation issue:     None — distances are rotation-invariant
```

**Prediction consistency under rotation:**
```
Method              Orientation A    Orientation B    Difference
3D CNN (voxel)      -15.2 kcal/mol   -9.8 kcal/mol    5.4 kcal/mol
Geometric GNN       -15.2 kcal/mol   -15.2 kcal/mol   0.0 kcal/mol
```

**Memory comparison:**
```
3D CNN (32^3 grid):    ~2,000x more memory than 10-node graph
Geometric GNN:          scales with number of atoms, not grid resolution
```

**The shift:** The geometric approach eliminated orientation-dependent prediction errors while using three orders of magnitude less memory than the voxelized alternative.

---

## Common Confusion

1. **"Geometric Deep Learning is just 3D CNNs."** 3D CNNs still operate on grids and are not automatically rotation-invariant. True geometric deep learning respects continuous symmetries rather than discretizing them away.

2. **"Graph Neural Networks are only for social networks."** GNNs are a core tool in geometric deep learning for molecules, proteins, materials, and point clouds. The "graph" is a general structure, not just a social network.

3. **"Geometric networks cannot handle large systems."** Hierarchical message passing, neighbor cutoffs, and sparse operations enable geometric networks to scale to systems with hundreds of thousands of atoms.

4. **"Rotation invariance is the only symmetry that matters."** Translation invariance, permutation invariance (over atom indices), and periodic boundary conditions (for crystals) are equally important and are all handled by specific geometric architectures.

5. **"Geometric Deep Learning requires labeled 3D structures."** Self-supervised pretraining on unlabeled molecular conformations (e.g., denoising, contrastive learning on augmentations) is increasingly common and effective.

6. **"Standard data augmentation achieves the same result."** Augmentation helps but is data-inefficient and never perfect. A geometric network encodes the symmetry by construction, generalizing exactly without seeing every transformation in training.

7. **"Geometric Deep Learning is only for scientific applications."** While most mature in science, it also applies to 3D computer vision (autonomous driving, robotics), graphics, and recommender systems on graphs.

---

## Where It Is Used in Our Code

`src/phase106/phase106_ai_for_science.py` — We demonstrate why rotation-invariant features are necessary for 3D coordinates by comparing a naive coordinate-sum feature against a distance-based feature extractor. We apply random 3D rotations to a synthetic point cloud and plot the stability of each feature type, illustrating the core motivation behind geometric deep learning.
