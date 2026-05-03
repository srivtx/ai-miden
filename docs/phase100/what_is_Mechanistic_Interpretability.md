# What Is Mechanistic Interpretability?

## Problem
Deep neural networks are opaque. We can measure their inputs and outputs, but we do not know which internal components are responsible for specific behaviors, making it hard to trust or fix them.

## Definition
Mechanistic Interpretability is the research program of reverse-engineering neural networks into human-understandable algorithms. It aims to identify "circuits" — subgraphs of weights and activations that implement specific tasks — and to understand how representations are built layer by layer.

## Analogy
A watch tells time, but opening the case reveals gears and springs. Mechanistic interpretability is like horology: understanding how each gear contributes to the final tick, rather than just observing that the watch works.

## Example
Researchers have identified "induction heads" in transformers: attention heads that copy patterns like [A]...[A] -> [B]. These heads are a circuit for in-context learning. By ablating them, the model loses the ability to complete repeated patterns.

## Common Confusion
Mechanistic interpretability is not the same as standard interpretability (e.g., attention heatmaps or saliency maps). Those methods are correlational; mechanistic interpretability seeks causal understanding by intervening on specific components.

## Code Location
See `src/phase100/phase100_mechinterp.py` for a NumPy demonstration of attribution patching.
