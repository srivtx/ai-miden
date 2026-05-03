## What Is Selectivity?

---

### The Problem

In a standard State Space Model, the transition matrices A, B, and C are fixed. This means every input token updates the state in exactly the same way. But in language, some tokens matter enormously ("not," "don't," a named entity) and others are filler ("the," "um," "very"). How do you make the model pay attention to what matters and ignore what does not?

---

### Definition

**Selectivity** is Mamba's breakthrough idea: make the SSM parameters **input-dependent**. Instead of fixed B and C matrices, each token computes its own B_t and C_t:

```
B_t = Linear_B(x_t)     (how much this input affects the state)
C_t = Linear_C(x_t)     (how much the state contributes to output)
Δ_t = Softplus(Linear_Δ(x_t) + bias)   (how fast the state updates)
```

Now the model can:
- **Amplify** important tokens (large B_t)
- **Suppress** irrelevant tokens (small B_t)
- **Control** how quickly it forgets old information (via Δ_t)

This is analogous to attention weights in a Transformer, but computed in O(1) per token instead of O(N) per token.

---

### Real-Life Analogy

A smart security guard at a building entrance. A standard SSM is like a guard who asks everyone the same questions and writes the same amount of detail for every visitor. A selective SSM is like a guard who sizes people up:
- Delivery driver with a package: quick glance, minimal notes (small B)
- VIP with a reservation: full screening, detailed log (large B)
- Person in a maintenance uniform: check credentials thoroughly (large B)
- Random pedestrian: ignore completely (B ≈ 0)

The guard's notebook (the state) only contains information worth remembering.

---

### Tiny Numeric Example

**State dimension:** 2
**Input:** scalar x_t

**Fixed (non-selective) SSM:**
```
B = [0.5, 0.5]  (always the same)
```

**Selective SSM:**
```
B_t = [sigmoid(0.3·x_t + 0.1), sigmoid(-0.2·x_t + 0.4)]
```

**Input sequence:** x = [10.0, 0.1, 10.0, 0.1]

**Non-selective B values:**
```
t=0: B_0 = [0.5, 0.5]
t=1: B_1 = [0.5, 0.5]
t=2: B_2 = [0.5, 0.5]
t=3: B_3 = [0.5, 0.5]
```

**Selective B values:**
```
t=0: B_0 = [sigmoid(3.1), sigmoid(-1.6)] = [0.957, 0.168]
t=1: B_1 = [sigmoid(0.13), sigmoid(0.38)] = [0.532, 0.594]
t=2: B_2 = [sigmoid(3.1), sigmoid(-1.6)] = [0.957, 0.168]
t=3: B_3 = [sigmoid(0.13), sigmoid(0.38)] = [0.532, 0.594]
```

**What happens:**
- For large inputs (10.0), the selective model uses B_0 ≈ [0.96, 0.17], strongly updating the first state dimension.
- For small inputs (0.1), the selective model uses B_1 ≈ [0.53, 0.59], making a moderate update.
- The non-selective model treats both identically.

Over many steps, the selective model learns to "filter" its inputs, while the non-selective model is forced to process everything equally.

---

### Common Confusion

1. **"Selectivity is the same as attention."** The effect is similar (focus on important tokens), but the mechanism is completely different. Attention computes pairwise comparisons: O(N²). Selectivity computes per-token gating: O(N). You get content-aware focusing without the quadratic cost.

2. **"Selective parameters B_t and C_t are learned directly."** No. The model learns fixed weight matrices `Linear_B` and `Linear_C`. At each timestep, the input token is projected through these matrices to produce B_t and C_t. The weights are shared across all timesteps.

3. **"Selectivity makes training slower."** It does remove some of the optimizations available to non-selective SSMs (like the convolution trick). But Mamba uses a hardware-aware parallel scan to recover efficient training. Mamba-2 is even faster.

4. **"Selectivity alone is enough for any task."** Not quite. While selectivity helps, SSMs still struggle with tasks that require precise copying of specific tokens from far away. This is why hybrid models combine SSMs with local attention.

5. **"All tokens should have high B_t for important things."** The model learns this automatically. During training, if a token is predictive of the target, gradients will push B_t higher for that token. If a token is noise, gradients will push B_t toward zero.

---

### Where It Is Used in Our Code

`src/phase34/phase34_mamba.py` — The `SelectiveSSM` class computes B_t and C_t as linear projections of the input. You can see how B_t values are larger for "important" impulses and smaller for noise in the generated plots.
