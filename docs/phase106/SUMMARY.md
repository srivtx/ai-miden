# Phase 106 Summary: AI for Science

## What We Learned

This phase introduced how AI is applied to scientific domains, particularly molecular and protein data. The key challenge is that scientific data lives in 3D space with rich geometric structure, which standard architectures do not respect.

## Key Takeaways

1. **Geometric Deep Learning** extends deep learning beyond grids to graphs, point clouds, and manifolds.
2. **Equivariant Networks** ensure that rotating or translating the input produces a correspondingly transformed output, rather than arbitrary changes.
3. **Diffusion for Molecules** uses equivariant diffusion models to generate novel 3D molecular structures for drug design and protein folding.

## Why It Matters

Standard CNNs and MLPs fail on molecular data because they are not rotation-invariant. Building AI that respects physical symmetries is essential for scientific discovery in chemistry, biology, and materials science.

## Navigation

- **Previous:** Phase 105 (see curriculum)
- **Next:** [Phase 107: On-Device LLMs](../phase107/SUMMARY.md)
