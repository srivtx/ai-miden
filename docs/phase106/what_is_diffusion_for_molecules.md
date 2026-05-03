# What is Diffusion for Molecules?

## 1. Problem Statement

Designing new molecules (e.g., drugs) with specific properties is a vast combinatorial search problem. Traditional methods rely on expert knowledge and expensive simulation. Generative models offer a way to sample novel, realistic molecules from a learned distribution, but must respect physical constraints like bond lengths and valency.

## 2. Definition

**Diffusion models for molecules** apply the diffusion framework to 3D molecular structures. They learn to reverse a noising process that gradually corrupts atomic coordinates (and optionally atom types). By conditioning on target properties (e.g., binding affinity), they can generate molecules optimized for a specific task. The model is typically built with equivariant layers so that generated structures are physically plausible regardless of orientation.

## 3. Analogy

Imagine sculpting a statue by starting with a block of marble and gradually chipping away noise to reveal the form. Diffusion for molecules is the reverse: start with random atomic soup and progressively denoise it into a stable molecular structure, guided by a learned "sculptor's eye."

## 4. Example

A diffusion model trained on protein-ligand complexes generates candidate drug molecules inside a protein binding pocket. At each denoising step, the model updates atom positions using an equivariant network conditioned on the protein structure, ensuring chemically valid binding poses.

## 5. Common Confusion

Diffusion for molecules is NOT just running a standard image diffusion model on voxel grids. True molecular diffusion operates on continuous 3D coordinates and discrete atom types, uses equivariant architectures, and enforces physical constraints like translation invariance.

## 6. Code Location

See `src/phase106/phase106_ai_for_science.py` for a NumPy demo focusing on rotation-invariant features needed for molecular data.
