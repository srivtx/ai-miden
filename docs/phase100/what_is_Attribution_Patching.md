# What Is Attribution Patching?

## Problem
When you intervene on a model (e.g., swap an activation from a corrupted run into a clean run), the output changes. But which layers actually caused that change? Naive ablation destroys too much information.

## Definition
Attribution Patching is a technique that attributes the effect of an intervention to specific layers or components by computing how much each layer's activation contributes to the final output difference. It uses gradients to approximate the causal impact without running the model separately for every component.

## Analogy
If replacing one musician in an orchestra changes the concert's mood, attribution patching is like asking each musician how much their part influenced the overall change, rather than removing them one by one and replaying the whole symphony.

## Example
Suppose a model correctly solves a math problem in a "clean" run but fails when a token is corrupted. By patching the corrupted activation at layer 5 with the clean activation, the model recovers. Attribution patching reveals that layers 4-6 are most responsible for the recovery, while later layers merely propagate the signal.

## Common Confusion
Attribution patching approximates causal effects using gradients; it is not always exact. It can be confused with activation patching (the actual intervention), which is the forward pass with swapped activations. Attribution patching is the *measurement* of where the intervention mattered.

## Code Location
See `src/phase100/phase100_mechinterp.py` for a NumPy demo comparing clean, corrupted, and patched forward passes.
