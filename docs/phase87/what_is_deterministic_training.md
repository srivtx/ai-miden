## What Is Deterministic Training?

---

### The Problem

When a bug appears after 40 hours of training, you must reproduce it to fix it. If dropping out a specific neuron or shuffling data in a different order produces a completely different loss curve, debugging becomes impossible. You cannot tell whether a hyperparameter change improved the model or just changed the random seed. Determinism makes experiments comparable, results trustworthy, and bugs reproducible.

---

### Definition

**Deterministic training** means that given the same code, data order, hyperparameters, and random seed, the model will initialize with the same weights and follow the exact same optimization trajectory every single time.

**How it works:**
```
Step 1: Set random seed (e.g., np.random.seed(42))
Step 2: Initialize weights -> deterministic array W0
Step 3: Set data shuffling seed -> deterministic batch order
Step 4: Train for N steps
Step 5: Save checkpoint

On rerun:
  Load checkpoint, reset seed, run same N steps
  Assert: new weights == old weights (bitwise identical)
```

**Key requirements:**
- **Fixed seeds:** for weight initialization, data shuffling, and dropout.
- **Deterministic algorithms:** some GPU operations have nondeterministic fast paths that must be disabled.
- **Identical data loading:** same shard order, same preprocessing, same worker count.

**Why this matters:**
- A/B testing hyperparameters requires that only the hyperparameter changes, not randomness.
- Debugging distributed training requires identical behavior across ranks.
- Regulatory and scientific applications demand reproducible results.

---

### Real-Life Analogy

A baking recipe with precise oven temperature, ingredient order, and timing should produce the same cake every time. If you change nothing but get a different cake -- one is fluffy, one is dense -- your kitchen is nondeterministic. Maybe the oven has hot spots, or the flour measuring cup is different. You cannot improve the recipe because you do not know which variable caused the difference.

The trade-off is that forcing determinism can be slower. Some GPU algorithms have a fast path that uses slightly different summation orders depending on thread scheduling, which is nondeterministic. Enabling deterministic mode often disables these fast paths, using slower but reproducible kernels. For debugging and publication, this slowdown is acceptable. For production training at massive scale, teams sometimes accept nondeterminism to maximize throughput, relying on statistical averaging across multiple seeds instead.

---

### Tiny Numeric Example

Setting `np.random.seed(42)` before weight initialization:

| Run | Seed | First Weight | Second Weight | Trajectory Match |
|---|---|---|---|---|
| 1 | 42 | -0.4967 | 0.1234 | -- |
| 2 | 42 | -0.4967 | 0.1234 | Identical |
| 3 | 43 | 0.2341 | -0.8765 | Diverged |

After 100 steps with seed 42:
| Metric | Run 1 | Run 2 | Match |
|---|---|---|---|
| Loss | 1.2345 | 1.2345 | Yes |
| Weight sum | 42.7182 | 42.7182 | Yes |

If a teammate runs the same script on a different machine with the same seed and gets exactly the same weights and loss, determinism is verified. Any deviation indicates an uncontrolled source of randomness.

---

### Common Confusion

1. **"Determinism means the model is correct."** No. It only means the result is reproducible, not that the result is good. A deterministic bad model will reliably produce bad results.

2. **"Determinism is the same as no randomness."** No. Random operations still occur, but their sequence is controlled by a seed. The randomness is pseudo-random and repeatable.

3. **"Hardware can break determinism."** Yes. Some GPU operations are nondeterministic by default (e.g., certain reductions and convolutions) unless explicitly configured with deterministic flags.

4. **"Data loading order matters."** Yes. Even with a fixed seed, shuffling data differently or using a different number of workers destroys determinism.

5. **"Determinism can be slower."** Yes. Enabling deterministic algorithms sometimes disables faster but nondeterministic GPU kernels, reducing throughput by 10-20%.

---

### Where It Is Used in Our Code

`src/phase87/phase87_checkpointing.py` -- We set the NumPy random seed, perform a weight update, save the state, reset the seed, and run the update again. We assert that both resulting weight tensors are identical, proving deterministic recovery.
