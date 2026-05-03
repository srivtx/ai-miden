## What Is Activation Patching?

---

### The Problem

You found a neuron that fires strongly when the input contains the number "7." But correlation is not causation. Maybe the neuron is just correlated with something else that happens to co-occur with 7. How do you prove that this neuron CAUSES the model to behave differently?

---

### Definition

**Activation patching** is a causal intervention where you replace ("patch") the activation of a specific neuron or layer from a "corrupted" run with the activation from a "clean" run, then observe whether the output changes.

**The method:**
1. **Clean run:** Run the model on input A. Record activation at layer L.
2. **Corrupted run:** Run the model on input B (similar but missing some feature). Record activation at layer L.
3. **Patched run:** Run on input B, but replace activation at layer L with the clean activation from step 1.
4. **Compare:** If the patched output is closer to the clean output than the corrupted output, the activation at layer L is causally responsible for the behavior.

**Why this works:**
- It isolates the effect of a single activation
- It proves causation, not just correlation
- It can be applied to any layer, any neuron, any attention head

---

### Real-Life Analogy

A car that stalls when it is cold.
- **Correlation:** You notice the stall happens on winter mornings. Maybe it is the battery?
- **Activation patching:** You take the battery from a warm car (clean run) and put it in the cold car (corrupted run) while keeping everything else cold. If the car starts, the battery was causally responsible. If it still stalls, the battery was just correlated.

By swapping one component at a time, you can isolate exactly which part causes the behavior.

---

### Tiny Numeric Example

**Model that outputs 1 if the input sum > 5, else 0.**

**Clean input:** [3, 4] -> sum = 7 -> output = 1
**Corrupted input:** [1, 2] -> sum = 3 -> output = 0

**Hidden layer activations:**
```
Clean:   h_clean   = [0.8, 0.2]
Corrupt: h_corrupt = [0.3, 0.1]
```

**Patched run (corrupt input, but h[0] = 0.8 from clean):**
```
Input: [1, 2]
Hidden: [0.8, 0.1]  # neuron 0 patched, neuron 1 from corrupt
Output: 0.7 -> rounds to 1
```

**Result:** Patching neuron 0 flips the output from 0 to 1. Neuron 0 is causally responsible for the "sum > 5" detection.

**Patched run (corrupt input, but h[1] = 0.2 from clean):**
```
Hidden: [0.3, 0.2]
Output: 0.2 -> rounds to 0
```

**Result:** Patching neuron 1 does NOT flip the output. Neuron 1 is not causally responsible.

---

### Common Confusion

1. **"Activation patching is the same as ablation."** Ablation sets an activation to zero. Patching replaces it with a value from a different input. They answer different questions.

2. **"Patching proves a neuron is sufficient for a behavior."** It proves the neuron is necessary in the causal chain, but other neurons might also be involved. The behavior might require multiple patches.

3. **"You can only patch one neuron at a time."** You can patch entire layers, attention heads, or groups of neurons. The technique scales.

4. **"Patching is too expensive for large models."** It requires two forward passes per patch, which is feasible for research-scale analysis. For GPT-4-scale models, you patch strategically, not exhaustively.

5. **"Patching results are always clear-cut."** Sometimes patching has a partial effect. This is still informative — it tells you the component contributes but is not solely responsible.

---

### Where It Is Used in Our Code

`src/phase46/phase46_mechanistic_interpretability.py` — We run clean and corrupted inputs through a tiny model, patch individual hidden neurons, and measure how much the output changes. This identifies which neurons are causally responsible for specific pattern detection.
