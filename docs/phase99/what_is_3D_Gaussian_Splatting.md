# What Is 3D Gaussian Splatting?

## Problem
Traditional 3D scene representations like meshes or voxel grids are hard to optimize and render efficiently from novel viewpoints. Neural radiance fields (NeRF) are slow to render.

## Definition
3D Gaussian Splatting represents a scene as a collection of millions of 3D Gaussians (each with position, covariance, opacity, and color). These Gaussians are rasterized directly to the image plane, enabling real-time rendering and high-quality reconstruction.

## Analogy
Instead of building a solid clay sculpture, imagine a pointillist painting where each dot is a soft, colored puff of smoke. From far away, the puffs blend into a coherent scene. Changing the viewpoint just means looking at the puffs from a different angle.

## Example
A street scene might be represented by 5 million 3D Gaussians. To render a new camera view, each Gaussian is projected to 2D, sorted by depth, and alpha-composited. This runs at 100+ fps on modern GPUs.

## Common Confusion
3D Gaussian Splatting is a rendering and representation technique, not a generative model by itself. It can be combined with diffusion models to generate 3D scenes, but splatting alone does not "create" content from text.

## Code Location
See `src/phase99/phase99_video_3d.py` for a conceptual discussion of 3D representations.
