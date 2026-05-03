# What Is Sparse Autoencoder?

## Problem
Neural network activations are superpositions: many features are represented simultaneously in the same vector, making it hard to isolate what any single neuron means.

## Definition
A Sparse Autoencoder (SAE) is an autoencoder trained to reconstruct network activations with a sparsity penalty on the hidden layer. The hidden units are forced to be mostly zero, causing each unit to represent a single, interpretable feature. By analyzing which SAE features fire on which inputs, researchers can disentangle the model's internal concepts.

## Analogy
A radio signal carries many stations at once. A sparse autoencoder is like a tuner that isolates each station into its own channel, so you can hear them one at a time instead of as a jumbled mix.

## Example
When run on transformer residual stream activations, an SAE might learn features corresponding to "opening parentheses," "French words," or "numbers divisible by 7." Each feature is active on only a small fraction of inputs.

## Common Confusion
Sparse autoencoders are not the same as standard autoencoders used for denoising or compression. The key difference is the strong sparsity penalty, which enforces disentanglement. Also, SAE features are not guaranteed to be interpretable; they are hypotheses that require human validation.

## Code Location
See `src/phase100/phase100_mechinterp.py` for a conceptual discussion in the code comments.
