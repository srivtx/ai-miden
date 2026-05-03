# Phase 86: JAX, XLA & TPU Programming

## What We Learned

Modern ML frameworks are evolving toward functional, compilable designs. This phase covered:

- **Functional Programming for ML:** JAX uses pure functions with no side effects. This enables powerful, composable transformations.
- **jax.vmap:** Automatic vectorization. Apply a function to a batch without writing a loop.
- **jax.grad:** Automatic differentiation of any pure function, not just a model graph.
- **jax.jit:** JIT compilation via XLA that fuses operations and removes Python overhead.
- **XLA:** The optimizing compiler that turns high-level ops into efficient fused kernels for CPU, GPU, and TPU.
- **Imperative vs Functional Mental Models:** PyTorch lets you mutate tensors and debug interactively. JAX requires you to think in terms of functions and transformations, which unlocks automatic optimization but changes how you write code.

## Key Terms

- JAX
- XLA
- JIT Compilation

## Code Files

- `src/phase86/phase86_jax_concepts.py` — NumPy simulation of JIT fusion and vmap concepts. No JAX installation required.

## Connections to Previous Phases

- Phase 85 covered multi-node training. JAX's `pmap` is the natural extension of `vmap` to multiple devices.
- Phase 83 discussed kernel fusion. XLA is the automatic engine that performs fusion without hand-written CUDA.
- Phase 82 optimized CPU code; JIT compilation is the compiler doing similar optimizations automatically.

## Navigation

← Previous: Phase 85 | Next: Phase 87 →
