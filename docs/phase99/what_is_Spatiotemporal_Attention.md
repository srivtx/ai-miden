# What Is Spatiotemporal Attention?

## Problem
Video data has three dimensions: height, width, and time. Treating time as just another spatial dimension ignores motion and temporal causality. Treating every frame independently ignores spatial relationships.

## Definition
Spatiotemporal Attention is an attention mechanism that operates jointly over space and time. It can be implemented as factorized attention (spatial attention within frames, then temporal attention across frames), or as full 3D attention over a video tube. It allows the model to track objects and motions coherently.

## Analogy
Watching a movie by looking at each frame as a separate photograph misses the plot. Spatiotemporal attention is like watching the movie: you understand both what is in each shot and how the story progresses from shot to shot.

## Example
In a video generation model, a spatiotemporal transformer might first attend to all spatial positions in the current frame to understand the scene layout, then attend to the same spatial position across past frames to understand motion.

## Common Confusion
Spatiotemporal attention is not just "attention with extra tokens." The positional encoding and masking must respect causality in time (future frames should not influence past frames in a predictor). Confusing spatial and temporal axes breaks temporal coherence.

## Code Location
See `src/phase99/phase99_video_3d.py` for a toy spatiotemporal convolution demonstration.
