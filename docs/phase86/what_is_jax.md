## What Is JAX?

---

### The Problem

Traditional ML frameworks like PyTorch and TensorFlow 1.x mix mutable state, in-place operations, and side effects. This makes it hard for compilers to optimize across operations, automatically parallelize code, or transform functions. For example, taking the gradient of an arbitrary Python function requires building a static computation graph and tracking every mutation. JAX was built to solve this by embracing pure functional programming: no mutation, no side effects, and composable transformations that work on any pure function.

---

### Definition

**JAX** is a high-performance numerical computing library that combines NumPy-like syntax with functional transformations: automatic differentiation (`grad`), vectorization (`vmap`), compilation (`jit`), and parallelization (`pmap`). It uses XLA to compile and run code on CPUs, GPUs, and TPUs.

**How it works:**
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

**Key transformations:**
- **`grad`:** computes the derivative of any pure function automatically.
- **`vmap`:** automatically vectorizes a function over a batch dimension without explicit loops.
- **`jit`:** compiles a function via XLA, fusing operations and removing Python overhead.
- **`pmap`:** parallelizes a function across multiple devices.

**Why this matters:**
- You can write research code in pure Python and get GPU/TPU performance without hand-written CUDA.
- Functional purity enables aggressive compiler optimizations that are impossible in mutable frameworks.

---

### Real-Life Analogy

PyTorch is like improvisational jazz: you play a note, listen, adjust, and play the next note. It is imperative, mutable, and interactive. You can change your mind mid-solo, which is wonderful for experimentation and debugging. JAX is like writing a full orchestral score: every note is written down in advance, so the conductor can rearrange sections, photocopy parts for every musician, and optimize the whole performance. It is functional, traceable, and compilable.

The trade-off is flexibility versus optimizability. In jazz, you can react to the room; in an orchestra, you cannot change the key signature after the curtain rises. JAX arrays are immutable, so you cannot do `x[0] = 5`; you must create a new array. This feels restrictive when you are prototyping, but it is exactly what allows XLA to fuse operations, eliminate dead code, and parallelize across hundreds of TPU cores. PyTorch's eager mode and mutable tensors are easier for debugging and dynamic architectures. JAX excels at research, compilation, and scaling.

---

### Tiny Numeric Example

Consider a pure function and three JAX transformations:

```python
def f(x):
    return x ** 2 + 3 * x + 1
```

**Automatic differentiation:**
| Input | f(x) | grad(f)(x) |
|---|---|---|
| 1.0 | 5.0 | 5.0 |
| 2.0 | 11.0 | 7.0 |
| 3.0 | 19.0 | 9.0 |

The gradient is exact, not a finite-difference approximation.

**Vectorization with `vmap`:**
| Batch Input | Manual Loop [f(x) for x in batch] | vmap(f)(batch) |
|---|---|---|
| [1.0, 2.0, 3.0] | [5.0, 11.0, 19.0] | [5.0, 11.0, 19.0] |

`vmap` produces the same result but pushes the loop into compiled C++/CUDA, removing Python iteration overhead.

**JIT compilation:**
A 5-million-element element-wise pipeline:
| Mode | Time |
|---|---|
| Pure Python loop | ~2.5 s |
| NumPy vectorized | ~0.005 s |
| JAX JIT compiled | ~0.001 s |

The JIT version fuses the entire pipeline into a single kernel with no intermediate allocations.

---

### Common Confusion

1. **"JAX is a deep learning framework."** Not exactly. It has no built-in `nn.Module` or training loop. It is a numerical computing library that you can build frameworks on top of (e.g., Flax, Haiku, Equinox).

2. **"JAX allows in-place mutation."** No. JAX arrays are immutable. Operations like `x[0] = 5` are forbidden. You must create a new array with the updated value.

3. **"JAX is just faster NumPy."** On CPU without JIT, it is often similar to NumPy. The speedups come from JIT compilation, GPU/TPU execution, and operator fusion via XLA.

4. **"Randomness works the same as NumPy."** No. JAX uses explicit, stateless random keys. You split keys rather than mutating a global random state, which is essential for reproducibility in parallel code.

5. **"JAX replaces PyTorch for everything."** No. PyTorch's eager mode and mutable tensors are easier for debugging and dynamic architectures. JAX excels at research, compilation, and scaling.

6. **"You need a TPU to use JAX."** No. JAX runs on CPU and GPU too. TPUs are particularly well-supported because JAX and XLA were developed together at Google.

---

### Where It Is Used in Our Code

`src/phase86/phase86_jax_concepts.py` -- We simulate JAX's core ideas without installing JAX. We demonstrate functional transformations by writing pure functions and showing how `vmap` (vectorized map) and `jit` (fusion and compilation) would transform them. This captures the mental model shift from imperative PyTorch to functional JAX.
