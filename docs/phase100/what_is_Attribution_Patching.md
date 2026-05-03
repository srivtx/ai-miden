## What Is Attribution Patching?

---

### The Problem

You have a model that correctly answers a math problem when given a clean prompt but fails when a single token is corrupted. You suspect that some layer in the middle of the network is responsible for the recovery, so you try replacing the corrupted activation at layer 5 with the clean activation. The model recovers. But layer 5 is connected to layers 4 and 6, which are connected to layers 3 and 7, and so on. Which layers actually caused the recovery, and which merely passed the signal along? Running the model separately for every possible intervention is combinatorially intractable. How do you attribute the effect of an intervention to specific components without exhaustive ablation?

---

### Definition

**Attribution Patching** is a technique that attributes the effect of an activation intervention to specific layers or components by computing how much each component's activation contributes to the final output difference. It uses gradients to approximate causal impact without running the model separately for every possible ablation, providing a fast, scalable map of where an intervention mattered.

**How it works:**
```
Setup:
  Clean run:   x_clean -> ... -> layer_i -> ... -> output_clean
  Corrupt run: x_corrupt -> ... -> layer_i -> ... -> output_corrupt
  Patched run: x_corrupt -> ... -> layer_i_patched (from clean) -> ... -> output_patched

Goal: find which layers j have the largest causal influence on the recovery.

Method (gradient-based attribution):
  1. Compute output difference: delta_out = output_clean - output_corrupt
  2. For each layer j, compute gradient: grad_j = d(delta_out) / d(activation_j)
  3. Attribution score for layer j: score_j = grad_j * (activation_j_clean - activation_j_corrupt)
  4. Higher |score_j| means layer j contributed more to the output change.
```

**Key properties:**
- Approximates causal effects using first-order gradients; it is a linearization.
- Much faster than brute-force ablation: one backward pass versus 2^N forward passes.
- Can be applied at the granularity of layers, heads, neurons, or even individual dimensions.

**Why this matters:**
- Brute-force ablation of all 96 layers in a large transformer is impossible.
- Attribution patching narrows the search to a handful of critical layers for deeper investigation.
- It is the standard first step in mechanistic interpretability workflows.

---

### Real-Life Analogy

Imagine an orchestra playing a symphony. During rehearsal, the conductor replaces one musician's part with a recording from a previous, better performance, and the overall concert improves. The conductor wants to know which sections — strings, brass, woodwinds — were most responsible for the improvement. A brute-force approach would mean re-recording the symphony dozens of times, each time swapping a different section, and comparing every version. Attribution patching is like asking each section: "If your playing changed by this much, how much would the overall concert change?" The strings might report a large influence, meaning they carried the improvement. The percussion might report almost none, meaning they merely propagated the signal. The conductor now knows where to focus rehearsal time.

The trade-off is approximation error. Attribution patching assumes local linearity: it says that a small perturbation in layer 3 has an effect proportional to the gradient at layer 3. But neural networks are nonlinear. If the patched activation pushes a ReLU from negative to positive, the gradient changes discontinuously, and the linear approximation breaks down. In practice, attribution patching is accurate enough to rank components by importance but should be followed by direct activation patching (the actual intervention) on the top-ranked components to verify causal responsibility. It is a metal detector, not an X-ray: it tells you where to dig, but you still need to dig.

---

### Tiny Numeric Example

**Toy 3-layer MLP with hidden dimension 16:**
```
Clean input:    x_clean    = [0.5, -0.3, 0.2, ...] (8 dims)
Corrupt input:  x_corrupt  = [-0.5, -0.3, 0.2, ...] (first feature flipped)

Forward passes:
  output_clean:    [1.2, -0.4, 0.1, 0.8]
  output_corrupt:  [0.3, 0.1, -0.5, 0.2]
  delta_out:       [0.9, -0.5, 0.6, 0.6]
```

**Attribution scores via finite differences (eps=1e-3):**
```
Layer 1 perturbations:
  Unit 0:  perturb -> output change magnitude = 0.45 / 1e-3 = 450
  Unit 1:  perturb -> output change magnitude = 0.12 / 1e-3 = 120
  ...
  Mean attribution L1: 280

Layer 2 perturbations:
  Unit 0:  perturb -> output change magnitude = 0.82 / 1e-3 = 820
  Unit 1:  perturb -> output change magnitude = 0.05 / 1e-3 = 50
  ...
  Mean attribution L2: 410
```

**Direct patching results:**
```
Patch layer 1 activation (clean into corrupt):
  output_patched_l1: [1.0, -0.2, 0.0, 0.6]
  recovery: 60% of the way from corrupt to clean

Patch layer 2 activation (clean into corrupt):
  output_patched_l2: [1.15, -0.35, 0.08, 0.75]
  recovery: 92% of the way from corrupt to clean
```

**Attribution ranking versus actual recovery:**
```
Component   | Attribution Score | Actual Recovery When Patched
------------|-------------------|------------------------------
Layer 2     | 410               | 92%
Layer 1     | 280               | 60%
```

**The shift:** The attribution scores correctly rank layer 2 as more important than layer 1, matching the actual patching results. This ranking was obtained with 32 perturbations (16 per layer) instead of 2^2 = 4 full patched runs, a trivial saving here but a massive one for 96-layer transformers.

---

### Common Confusion

1. **"Attribution patching is the same as activation patching."** It is not. Activation patching is the actual forward pass with swapped activations. Attribution patching is the gradient-based measurement of where that swap mattered. One is the experiment; the other is the analysis.

2. **"Attribution scores are exact causal effects."** They are linear approximations. In regions of high nonlinearity (near ReLU thresholds, softmax boundaries), the approximation can be inaccurate. Direct patching should always be used to verify the top-ranked components.

3. **"Higher attribution means the component is always important."** Higher attribution means the component was important for this specific intervention. A different corruption or a different task might activate a completely different subgraph.

4. **"Attribution patching requires training."** It does not. It uses gradients from the frozen model. No weights are updated; only forward and backward passes are run.

5. **"You can only attribute to layers."** Attribution can be computed at any granularity: individual neurons, attention heads, MLP sublayers, or even specific token positions. Finer granularity costs more compute but yields more precise localization.

6. **"Zero attribution means a component is useless."** Zero attribution for one intervention does not mean the component is globally useless. It might be critical for other inputs or other tasks but inactive for this specific pair of clean and corrupt runs.

7. **"Attribution patching replaces mechanistic interpretability."** It is a tool within mechanistic interpretability, not a replacement. It guides where to look, but understanding what a component actually does still requires careful analysis of its weights, activations, and causal effects.

---

### Where It Is Used in Our Code

`src/phase100/phase100_mechinterp.py` — We implement a toy 3-layer MLP and compare clean, corrupted, and patched forward passes. We compute finite-difference attribution scores for each hidden unit in layers 1 and 2 by perturbing activations and measuring output change. We plot the attribution scores as bar charts and show how patching the highest-attribution layer recovers most of the clean output, validating the ranking.
