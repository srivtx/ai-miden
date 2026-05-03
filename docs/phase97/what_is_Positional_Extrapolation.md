# What Is Positional Extrapolation?

## Problem
Transformer models are trained on fixed-length sequences. When deployed on longer sequences than seen during training, standard positional encodings fail because the model has never learned representations for those positions.

## Definition
Positional Extrapolation refers to methods that allow a model to generalize to sequence lengths longer than its training distribution. Techniques include ALiBi (Attention with Linear Biases), which adds a learned or fixed bias based on token distance rather than absolute position, and RoPE (Rotary Position Embedding), which encodes relative positions via rotation matrices and can be interpolated or extrapolated.

## Analogy
A speedometer that only goes up to 120 mph is useless on a track where cars hit 200 mph. Extrapolation methods are like replacing the gauge with a logarithmic scale or a digital readout that handles any speed.

## Example
A model trained on 4K tokens with RoPE can be fine-tuned with positional interpolation (scaling position indices) to handle 32K tokens. ALiBi, by design, naturally extrapolates because the bias depends only on relative distance, not absolute position index.

## Common Confusion
Positional extrapolation is not the same as simply "training on longer sequences." It specifically refers to generalizing beyond training length. Some methods require fine-tuning; others (like ALiBi) work out of the box.

## Code Location
See `src/phase97/phase97_long_context.py` for a visualization of sequence scaling.
