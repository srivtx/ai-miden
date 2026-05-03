# Phase 86: JAX, XLA & TPU Programming

## What We Learned

Modern ML frameworks are evolving toward functional, compilable designs. This phase covered:

- **Functional Programming for ML:** JAX uses pure functions with no side effects. This enables powerful, composable transformations that are impossible in mutable frameworks.
- **jax.vmap:** Automatic vectorization. Apply a function to a batch without writing a Python loop, pushing iteration into compiled code.
- **jax.grad:** Automatic differentiation of any pure function, not just a model graph. This makes custom loss functions and research code trivial to differentiate.
- **jax.jit:** JIT compilation via XLA that fuses operations and removes Python overhead. The first call compiles; subsequent calls reuse the compiled kernel.
- **XLA:** The optimizing compiler that turns high-level ops into efficient fused kernels for CPU, GPU, and TPU without rewriting code.
- **Imperative vs Functional Mental Models:** PyTorch lets you mutate tensors and debug interactively. JAX requires you to think in terms of functions and transformations, which unlocks automatic optimization but changes how you write code.

## Prerequisites

- Phase 85: NCCL, InfiniBand & Multi-Node Training
- Phase 83: GPU Kernel Optimization (CUDA)
- Phase 82: CPU Optimization and Vectorization

## Recommended Reading Order

1. `what_is_jax.md` -- Understand the functional programming paradigm and core transformations.
2. `what_is_xla.md` -- Learn how the XLA compiler optimizes computation graphs.
3. `what_is_jit_compilation.md` -- See how JIT compilation removes Python overhead and enables fusion.

## Visual Outputs

- `src/phase86/jit_fusion_comparison.png` -- Bar chart comparing execution time of imperative three-pass operations versus a single fused pass.

## Key Terms

- JAX
- XLA
- JIT Compilation

## Code Files

- `src/phase86/phase86_jax_concepts.py` -- NumPy simulation of JIT fusion and vmap concepts. No JAX installation required.

## Connections to Previous Phases

- Phase 85 covered multi-node training. JAX's `pmap` is the natural extension of `vmap` to multiple devices.
- Phase 83 discussed kernel fusion. XLA is the automatic engine that performs fusion without hand-written CUDA.
- Phase 82 optimized CPU code; JIT compilation is the compiler doing similar optimizations automatically.

## Navigation

[Previous: Phase 85: Multi-Node Training](docs/phase85/SUMMARY.md) | [Next: Phase 87: Checkpointing & Fault Tolerance](docs/phase87/SUMMARY.md)
