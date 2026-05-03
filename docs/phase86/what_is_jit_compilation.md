## What Is JIT Compilation?

---

### The Problem

Python is an interpreted language. Every loop, every function call, and every operation has interpreter overhead. For numerical computing with millions of elements, this overhead dominates actual computation. You might spend 90% of the time in Python and 10% in C. JIT compilation solves this by translating the Python function into compiled machine code before execution, removing interpreter overhead entirely and enabling optimizations like fusion that are invisible to the interpreter.

---

### Definition

**JIT** (Just-In-Time) compilation is the process of translating code during execution (rather than beforehand) into optimized machine code. In JAX, `jax.jit` traces a pure function, compiles it via XLA, and caches the compiled version for future calls with the same shapes.

**How it works:**
```
First call with shape (1000000,):
  1. Trace the function: record operations without executing
  2. Send trace to XLA compiler
  3. XLA fuses ops, optimizes layout, generates machine code
  4. Cache compiled executable
  Time: slow (compilation overhead)

Second call with same shape:
  1. Look up cached executable
  2. Run compiled machine code directly
  Time: fast (no Python overhead)
```

**Key properties:**
- **Shape-dependent:** changing input shapes often triggers recompilation.
- **Pure functions required:** side effects and mutation break tracing.
- **Cached:** repeated calls with the same shapes reuse the compiled code.

**Why this matters:**
- A JIT-compiled element-wise pipeline can be 5-10x faster than NumPy because it fuses operations and eliminates intermediate allocations.
- The first call is slow, but training loops call the same function millions of times.

---

### Real-Life Analogy

Imagine giving a speech through a live translator. After every sentence, you pause while the translator converts it into the local language. That is interpreted Python: flexible, but constantly interrupted. JIT compilation is like giving the speech to the translator the night before, receiving a perfectly translated script, and reading from it on stage. The first preparation takes time, but the actual performance is much faster because there are no pauses.

The trade-off is that the translated script is fixed. If you decide to change a joke based on the audience's reaction, you cannot; you are stuck with the pre-translated version. Similarly, JIT-compiled code is optimized for a specific set of input shapes and operations. If your data changes shape or your control flow depends on data values, the JIT must recompile, which costs time. JIT is ideal for stable, repetitive workloads like neural network training, but less helpful for interactive, exploratory data analysis where every command is different.

---

### Tiny Numeric Example

A function that computes `(x + 1) * 2 - 3` on a 1-million-element array:

| Implementation | First Call | Subsequent Calls | Memory Allocations |
|---|---|---|---|
| Pure Python loop | ~2.5 s | ~2.5 s | 3 (for intermediates) |
| NumPy vectorized | ~0.005 s | ~0.005 s | 3 (for intermediates) |
| JAX JIT compiled | ~0.050 s | ~0.001 s | 0 (fused into one kernel) |

The JIT version is 5x faster than NumPy on subsequent calls because XLA fuses all three operations into a single kernel that never allocates intermediate arrays. The first call is slower due to compilation overhead, but in a training loop with millions of iterations, that cost is amortized to near zero.

---

### Common Confusion

1. **"JIT is the same as AOT (Ahead-of-Time) compilation."** No. AOT compiles before the program runs. JIT compiles during execution, often using runtime shape information to specialize the code.

2. **"JIT makes the first call faster."** No. The first call is slower because of compilation time. Subsequent calls with the same shapes are fast.

3. **"JIT works on any Python code."** No. JIT systems like JAX require pure functions with no side effects and usually static array shapes. Code with arbitrary Python control flow may fail to compile.

4. **"JIT eliminates the need for vectorization."** No. JIT optimizes the operations, but you still benefit from writing vectorized code that the compiler can fuse into efficient kernels.

5. **"JIT is unique to JAX."** No. PyTorch has `torch.compile`, Numba has `@jit`, and JavaScript V8 engines have JITs too.

6. **"JIT compiled code uses less memory."** Sometimes. The main benefit is speed, but fusion (enabled by JIT) can reduce intermediate memory allocations.

---

### Where It Is Used in Our Code

`src/phase86/phase86_jax_concepts.py` -- We simulate JIT compilation by comparing three separate NumPy operations (with intermediate memory) against a single fused expression. While NumPy itself does not JIT-compile Python loops, our simulation captures the conceptual benefit of JIT: combining operations into one pass and removing per-operation overhead.
