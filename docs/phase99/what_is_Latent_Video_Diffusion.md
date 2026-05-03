# What Is Latent Video Diffusion?

## Problem
Diffusing raw video pixels is computationally prohibitive. A 10-second 256x256 video at 30 fps has 76,800 frames; operating in pixel space requires enormous memory and compute.

## Definition
Latent Video Diffusion first compresses video into a lower-dimensional latent space using a 3D autoencoder (or a 2D spatial + 1D temporal encoder). The diffusion model then learns to denoise in this compact latent space, dramatically reducing compute while preserving temporal coherence.

## Analogy
Instead of painting every grain of sand on a beach, an artist sketches the scene on a small canvas and then scales it up. The diffusion process happens on the sketch, not on the full beach.

## Example
Stable Video Diffusion uses a video variational autoencoder to compress 256x256x4-frame clips into a 32x32x4 latent tensor. The U-Net diffusion model operates on this latent tensor, and a decoder maps back to pixels.

## Common Confusion
Latent video diffusion is not the same as "frame-by-frame image diffusion." The latent space must encode temporal information, and the diffusion model must include temporal layers (3D convolutions, temporal attention) or the output will flicker.

## Code Location
See `src/phase99/phase99_video_3d.py` for a toy diffusion process on a 1D+time signal.
