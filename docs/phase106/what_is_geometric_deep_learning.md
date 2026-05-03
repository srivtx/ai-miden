# What is Geometric Deep Learning?

## 1. Problem Statement

Traditional neural networks treat input features as flat vectors. But many scientific datasets live on non-Euclidean domains: 3D molecular graphs, meshes, point clouds, and manifolds. Applying a standard CNN or MLP to these structures ignores their geometry, leading to poor generalization when the object rotates, translates, or deforms.

## 2. Definition

**Geometric Deep Learning** is a broad field that extends deep learning beyond grid-structured data (like images) to data with geometric structure. It includes graph neural networks, convolutional networks on meshes, and equivariant networks on point clouds. The key insight is to build architectures that respect the symmetries and invariances of the underlying domain.

## 3. Analogy

Imagine trying to recognize a chair. A standard CNN learns that the backrest is at pixel coordinates (50, 100). If you move the chair, the CNN fails. Geometric Deep Learning is like recognizing the chair by its parts and how they connect—regardless of where it sits or which way it faces.

## 4. Example

A 3D point cloud of a protein backbone. Standard approach: voxelize into a 3D grid and run a 3D CNN. Geometric approach: treat each amino acid as a point with 3D coordinates and learn features using distances and angles, which remain valid even if the entire protein rotates.

## 5. Common Confusion

Geometric Deep Learning is NOT just 3D CNNs. 3D CNNs still operate on grids and are not automatically rotation-invariant. True geometric deep learning respects the continuous symmetries of the data (e.g., rotation, translation) rather than discretizing them away.

## 6. Code Location

See `src/phase106/phase106_ai_for_science.py` for a NumPy demo showing why rotation-invariant features are necessary for 3D coordinates and how distance-based features solve this.
