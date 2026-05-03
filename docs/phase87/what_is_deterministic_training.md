# What is Deterministic Training?

## Why it exists (THE PROBLEM first)

When a bug appears after 40 hours of training, you must reproduce it to fix it. If dropping out a specific neuron or shuffling data in a different order produces a completely different loss curve, debugging becomes impossible. Determinism makes experiments comparable and results trustworthy.

## Definition (very simple)

Deterministic training means that given the same code, data order, hyperparameters, and random seed, the model will initialize with the same weights and follow the exact same optimization trajectory every single time.

## Real-life analogy

A baking recipe with precise oven temperature, ingredient order, and timing should produce the same cake every time. If you change nothing but get a different cake, your kitchen is nondeterministic.

## Tiny numeric example

Setting `np.random.seed(42)` before weight initialization produces weights `[-0.4967, 0.1234, ...]`. If a teammate runs the same script on a different machine with the same seed and gets `[-0.4967, 0.1234, ...]`, determinism is verified.

## Common confusion

- **Determinism does not mean the model is correct.** It only means the result is reproducible, not that the result is good.
- **Determinism is not the same as no randomness.** Random operations still occur, but their sequence is controlled by a seed.
- **Hardware can break determinism.** Some GPU operations are nondeterministic by default (e.g., certain reductions) unless explicitly configured.
- **Data loading order matters.** Even with a fixed seed, shuffling data differently destroys determinism.
- **Determinism can be slower.** Enabling deterministic algorithms sometimes disables faster but nondeterministic GPU kernels.

## Where it is used in our code

In `src/phase87/phase87_checkpointing.py`, we set the NumPy random seed, perform a weight update, save the state, reset the seed, and run the update again. We assert that both resulting weight tensors are identical, proving deterministic recovery.
