# What Is JAX?

## 1. Why it exists (THE PROBLEM first)

Traditional ML frameworks like PyTorch and TensorFlow 1.x mix mutable state, in-place operations, and side effects. This makes it hard for compilers to optimize across operations, automatically parallelize code, or transform functions (e.g., take a gradient of any function). JAX was built to solve this by embracing pure functional programming: no mutation, no side effects, and composable transformations.

## 2. Definition

**JAX** is a high-performance numerical computing library that combines NumPy-like syntax with functional transformations: automatic differentiation (`grad`), vectorization (`vmap`), compilation (`jit`), and parallelization (`pmap`). It uses XLA to compile and run code on CPUs, GPUs, and TPUs.

## 3. Real-life analogy

PyTorch is like improvisational jazz: you play a note, listen, adjust, and play the next note (imperative, mutable). JAX is like writing a full orchestral score: every note is written down in advance, so the conductor can rearrange sections, photocopy parts for every musician, and optimize the whole performance (functional, traceable, compilable).

## 4. Tiny numeric example

```python
import jax.numpy as jnp
from jax import grad, vmap, jit

def f(x):
    return x ** 2

# Automatic differentiation
df = grad(f)
print(df(3.0))  # 6.0

# Vectorization (no Python loop)
inputs = jnp.array([1.0, 2.0, 3.0])
print(vmap(f)(inputs))  # [1.0, 4.0, 9.0]

# JIT compilation
fast_f = jit(f)
print(fast_f(3.0))  # 9.0
```

Three powerful transformations applied to a pure Python function with NumPy-like code.

## 5. Common confusion

- **"JAX is a deep learning framework."** Not exactly. It has no built-in `nn.Module` or training loop. It is a numerical computing library that you can build frameworks on top of (e.g., Flax, Haiku).
- **"JAX allows in-place mutation."** No. JAX arrays are immutable. Operations like `x[0] = 5` are forbidden. You must create a new array.
- **"JAX is just faster NumPy."** On CPU without JIT, it is often similar to NumPy. The speedups come from JIT compilation, GPU/TPU execution, and operator fusion via XLA.
- **"Randomness works the same as NumPy."** No. JAX uses explicit, stateless random keys. You split keys rather than mutating a global random state.
- **"JAX replaces PyTorch for everything."** No. PyTorch's eager mode and mutable tensors are easier for debugging and dynamic architectures. JAX excels at research, compilation, and scaling.
- **"You need a TPU to use JAX."** No. JAX runs on CPU and GPU too. TPUs are just particularly well-supported because JAX and XLA were developed together at Google.

## 6. Where it is used in our code

In `src/phase86/phase86_jax_concepts.py`, we simulate JAX's core ideas without installing JAX. We demonstrate functional transformations by writing pure functions and showing how `vmap` (vectorized map) and `jit` (fusion/compilation) would transform them. This captures the mental model shift from imperative PyTorch to functional JAX.
