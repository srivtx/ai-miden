# Phase 106 Summary: AI for Science

## What We Learned

1. **Scientific data lives in continuous geometric spaces, not flat grids.** Molecules, proteins, and point clouds have structure defined by distances, angles, and connectivity. Standard CNNs and MLPs ignore this structure, leading to poor generalization under rotation and deformation.

2. **Geometric Deep Learning extends deep learning to non-Euclidean domains.** By building architectures that respect the symmetries of the underlying data — graphs, meshes, manifolds, and point clouds — we achieve better sample efficiency and physically consistent predictions.

3. **Equivariance is distinct from invariance, and both are essential.** Invariant outputs (e.g., energy) do not change under rotation. Equivariant outputs (e.g., force vectors) transform consistently with the input. The right choice depends on the prediction target.

4. **Molecular diffusion models generate novel structures by reversing noise in 3D coordinate space.** Unlike image diffusion on voxels, molecular diffusion uses continuous coordinates and equivariant architectures to ensure physically valid outputs, enabling applications in drug discovery and materials design.

5. **Naive coordinate-based features fail under symmetry transformations.** Our NumPy demonstration showed that a simple sum of coordinates oscillates wildly when the input is rotated, while distance-based features remain constant. This empirical result motivates the entire field of geometric deep learning.

6. **Physical correctness is not an afterthought; it must be architecturally enforced.** You cannot train a standard MLP on enough rotated examples to learn exact rotational symmetry. The symmetry must be baked into the network's operations.

## Prerequisites

- Phase 15 (Convolutional Neural Networks): understanding of spatial inductive bias and weight sharing
- Phase 29 (Transformers): understanding of attention and message passing
- Phase 70 (Domain Adaptation): understanding of specialized domains and distribution shift

## Recommended Reading Order

1. `what_is_geometric_deep_learning.md` — Start with the broad motivation for handling non-grid data
2. `what_is_equivariant_networks.md` — Learn the specific symmetry constraints that make geometric learning work
3. `what_is_diffusion_for_molecules.md` — See how these ideas combine into a generative framework for molecular design

## Visual Outputs

Running `src/phase106/phase106_ai_for_science.py` produces:
- `rotation_invariant_demo.png`: A plot comparing a naive coordinate-sum feature (red, oscillating) against a rotation-invariant mean-distance feature (blue, flat) as a 3D point cloud is rotated through 360 degrees.

## Navigation

- **Previous**: [Phase 105: Tiny ML & Edge Deployment](../phase105/SUMMARY.md)
- **Next**: [Phase 107: On-Device LLMs](../phase107/SUMMARY.md)
