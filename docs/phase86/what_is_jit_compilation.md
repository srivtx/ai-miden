# What Is JIT Compilation?

## 1. Why it exists (THE PROBLEM first)

Python is an interpreted language. Every loop, every function call, and every operation has interpreter overhead. For numerical computing with millions of elements, this overhead dominates. You might spend 90% of the time in Python and 10% in C. JIT compilation solves this by translating the Python function into compiled machine code before execution, removing interpreter overhead entirely.

## 2. Definition

**JIT** (Just-In-Time) compilation is the process of translating code during execution (rather than beforehand) into optimized machine code. In JAX, `jax.jit` traces a pure function, compiles it via XLA, and caches the compiled version for future calls with the same shapes.

## 3. Real-life analogy

Imagine giving a speech through a live translator. After every sentence, you pause while the translator converts it. That is interpreted Python. JIT compilation is like giving the speech to the translator the night before, receiving a perfectly translated script, and reading from it on stage. The first preparation takes time, but the actual performance is much faster.

## 4. Tiny numeric example

A function that squares every element of a 1-million-element array:

- Pure Python loop: ~2.5 seconds.
- NumPy vectorized: ~0.005 seconds (C-level loop).
- JAX JIT compiled: ~0.001 seconds (fused, no Python overhead, XLA-optimized).

The JIT version is not just in C; it is fused into a single kernel that never allocates intermediate arrays.

## 5. Common confusion

- **"JIT is the same as AOT (Ahead-of-Time) compilation."** No. AOT compiles before the program runs. JIT compiles during execution, often using runtime shape information.
- **"JIT makes the first call faster."** No. The first call is slower because of compilation time. Subsequent calls with the same shapes are fast.
- **"JIT works on any Python code."** No. JIT systems like JAX require pure functions with no side effects and usually static array shapes.
- **"JIT eliminates the need for vectorization."** No. JIT optimizes the operations, but you still benefit from writing vectorized code that the compiler can fuse.
- **"JIT is unique to JAX."** No. PyTorch has `torch.compile`, Numba has `@jit`, and Java/JS engines have JITs too.
- **"JIT compiled code uses less memory."** Sometimes. The main benefit is speed, but fusion (enabled by JIT) can reduce intermediate memory allocations.

## 6. Where it is used in our code

In `src/phase86/phase86_jax_concepts.py`, we simulate JIT compilation by comparing three separate NumPy operations (with intermediate memory) against a single fused expression. While NumPy itself does not JIT-compile Python loops, our simulation captures the conceptual benefit of JIT: combining operations into one pass and removing per-operation overhead.
