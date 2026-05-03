## What Is Mechanistic Interpretability?

---

### The Problem

Neural networks work, but nobody knows exactly how. A GPT-4 has 1.8 trillion parameters. Which ones handle arithmetic? Which ones know that Paris is in France? Which ones generate toxic outputs? If we cannot understand the internals, we cannot reliably fix bugs, ensure safety, or trust the system.

---

### Definition

**Mechanistic interpretability** is the research field that reverse-engineers neural networks to understand the specific computations performed by individual neurons, layers, and circuits.

**The goal:**
- Find a "neuron that detects dogs" or a "circuit that adds numbers"
- Understand how these components connect to produce behavior
- Predict how the model will behave on new inputs based on its internal structure

**Key techniques:**
1. **Activation visualization:** What inputs make a neuron fire most strongly?
2. **Activation patching:** If I swap this activation, does the output change?
3. **Sparse autoencoders:** Decompose neural activity into interpretable features
4. **Probing:** Train a simple classifier on hidden states to see what information they encode

**Why it matters:**
- **Safety:** Find and remove harmful capabilities before deployment
- **Debugging:** Understand why a model fails on specific inputs
- **Trust:** Verify that the model reasons the way we think it does
- **Efficiency:** Prune unused circuits to make models smaller

---

### Real-Life Analogy

A car engine.
- **Black-box evaluation:** You press the gas pedal and the car moves. You know it works, but if it breaks, you are stuck.
- **Mechanistic interpretability:** You open the hood. You see that the fuel injector mixes gasoline with air, the spark plug ignites it, the piston converts the explosion into rotation, and the crankshaft transfers power to the wheels. Now if the car sputters, you know to check the spark plug first.

Neural networks are engines with billions of parts. Mechanistic interpretability is building the repair manual.

---

### Tiny Numeric Example

**A tiny neural network that detects the word "cat":**
```
Input: one-hot vector for words ["the", "cat", "sat"]
Hidden layer: 2 neurons
Output: probability of "cat" being the next word
```

**Hidden activations:**
```
Input "the cat":   hidden = [0.9, 0.1]
Input "the dog":   hidden = [0.1, 0.9]
Input "the mat":   hidden = [0.2, 0.2]
```

**Interpretation:**
- Neuron 1 fires for "cat-like" contexts
- Neuron 2 fires for "dog-like" contexts
- The model has learned to separate these concepts in hidden space

**Activation patching:**
```
Corrupt "the cat" -> "the dog", but patch neuron 1 to its "cat" value.
Result: model still predicts "cat" even though the input says "dog".
Conclusion: Neuron 1 is causally responsible for the "cat" prediction.
```

---

### Common Confusion

1. **"Mechanistic interpretability is just looking at attention maps."** Attention maps are one tool, but mechanistic interpretability goes much deeper — individual neurons, circuits, and algorithms.

2. **"If we understand every neuron, we understand the model."** Not necessarily. Neurons interact in complex, non-linear ways. Understanding components is necessary but not sufficient.

3. **"Interpretability is only for safety researchers."** It is also useful for debugging, model compression, and discovering new algorithms that the model invented.

4. **"Small models are easy to interpret."** Even tiny models can have surprising emergent behaviors. Interpretability is hard at all scales.

5. **"Understanding one layer is enough."** Behavior often emerges from interactions across many layers. A "curiosity circuit" might span 10+ layers.

---

### Where It Is Used in Our Code

`src/phase46/phase46_mechanistic_interpretability.py` — We train a tiny model on a pattern-matching task, visualize which neurons fire for which patterns, and use activation patching to identify causal circuits.
