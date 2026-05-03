# What are Equivariant Networks?

## 1. Problem Statement

If you rotate a molecule, its physical properties do not change. But if a neural network processes the raw (x, y, z) coordinates, the output changes arbitrarily under rotation because standard layers are not designed to handle transformed inputs consistently. We need networks whose outputs transform predictably when the input transforms.

## 2. Definition

An **equivariant function** f satisfies f(T(x)) = T(f(x)) for some transformation group T (e.g., rotations). An **invariant function** satisfies f(T(x)) = f(x). **E(n)-equivariant networks** are architectures where each layer respects the Euclidean symmetries (rotations, translations, reflections) of n-dimensional space. If you rotate the input point cloud, the output feature vectors rotate the same way.

## 3. Analogy

Think of a weather vane. When the wind rotates, the vane rotates with it—that is equivariance. A compass reading "North" no matter which way you hold it—that is invariance. Equivariant networks are like the weather vane: they track the transformation rather than discarding it.

## 4. Example

E(n) Equivariant Graph Neural Networks (EGNNs) update node features using relative distances between points. The message passing depends only on pairwise distances and directions, so rotating all points by the same matrix simply rotates the learned directional features by the same matrix.

## 5. Common Confusion

Equivariance is NOT the same as invariance. Invariance means the output does not change at all. Equivariance means the output changes in the same structured way as the input. Both are useful: invariant outputs for predictions (e.g., energy), equivariant outputs for tasks requiring directional information (e.g., forces).

## 6. Code Location

See `src/phase106/phase106_ai_for_science.py` for a NumPy demo with a simple distance-based equivariant feature extractor.
