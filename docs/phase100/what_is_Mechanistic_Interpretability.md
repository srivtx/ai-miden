## What Is Mechanistic Interpretability?

---

### The Problem

A large language model can write essays, debug code, and translate languages, but if you open it up, you find only billions of numbers — weights and activations — with no labels, no comments, and no obvious structure. You can measure that it works, but you cannot point to any specific part and say "this component handles subject-verb agreement" or "this circuit detects lies." Without that understanding, you cannot fix harmful behaviors, cannot trust the model in high-stakes settings, and cannot predict how it will behave on new inputs. How do you reverse-engineer a neural network into human-understandable algorithms?

---

### Definition

**Mechanistic Interpretability** is the research program of reverse-engineering neural networks to identify human-understandable circuits — subgraphs of weights and activations that implement specific tasks — and to understand how representations are built layer by layer. It seeks causal explanations, not just correlations: it intervenes on specific components and observes whether behaviors change.

**How it works:**
```
Standard interpretability (correlational):
  Input -> Model -> Output
  "What inputs activate this neuron?" -> attention heatmap, saliency map
  Limitation: shows correlation, not causation.

Mechanistic interpretability (causal):
  Input -> Model -> Output
  "If I ablate this attention head, does the output change?" -> yes/no
  "If I patch this activation, does the behavior recover?" -> yes/no
  Goal: build a circuit diagram of the model's computation.
```

**Key techniques:**
- **Activation patching:** swap activations between clean and corrupted runs to localize function.
- **Attribution patching:** use gradients to approximate causal importance without exhaustive search.
- **Sparse autoencoders:** disentangle superposed features into interpretable units.
- **Circuit tracing:** follow the flow of information from input tokens to output tokens through specific attention heads and MLP neurons.

**Why this matters:**
- Researchers have identified "induction heads" that implement in-context learning [A]...[A] -> [B].
- Ablating specific heads reduces gender bias in pronoun resolution.
- Understanding circuits is a prerequisite for safe, auditable AI systems.

---

### Real-Life Analogy

Imagine a mechanical watch that keeps perfect time. You can observe that it works — the hands move, the date advances, the alarm rings — but the case is sealed. Standard interpretability is like studying the watch by measuring how temperature and magnetism affect its accuracy. You learn correlations, but you still do not know what is inside. Mechanistic interpretability is like opening the case and examining each gear, spring, and escapement. You discover that gear 17 drives the minute hand, that spring 4 stores energy for the alarm, and that the escapement converts rotational motion into discrete ticks. More importantly, you can remove gear 17 and confirm that the minute hand stops, proving causation rather than mere correlation.

The trade-off is scale. A watch has a few dozen components; a large transformer has hundreds of billions. You cannot trace every gear in a billion-parameter model by hand. Mechanistic interpretability relies on automation: attribution patching to find important components, sparse autoencoders to label features, and automated circuit extraction to build subgraphs. But automation introduces its own errors. A sparse autoencoder might mislabel a feature, or attribution patching might rank a component highly due to nonlinearity rather than true causation. The field is still young, and its methods are approximate. The watch analogy holds, but the watchmaker is now using statistical tools to inspect a billion gears, and some gears remain stubbornly opaque.

---

### Tiny Numeric Example

**Toy transformer: 2 layers, 4 attention heads per layer, d_model=64.**
```
Total attention heads: 2 * 4 = 8
Total parameters: ~500,000
Task: copy repeated tokens (induction pattern [A]...[A] -> [B])
```

**Ablating each head and measuring task accuracy:**
```
Head      | Ablated Accuracy | Drop from baseline (98%)
----------|------------------|--------------------------
Layer 1-0 | 97%              | -1%  (not critical)
Layer 1-1 | 96%              | -2%  (minor role)
Layer 1-2 | 45%              | -53% (CRITICAL — induction head)
Layer 1-3 | 95%              | -3%  (minor role)
Layer 2-0 | 97%              | -1%
Layer 2-1 | 50%              | -48% (CRITICAL — induction head)
Layer 2-2 | 94%              | -4%
Layer 2-3 | 96%              | -2%
```

**Circuit size for the induction task:**
```
Total components in model:    8 attention heads + 2 MLP layers + embeddings
Components in induction circuit: 2 attention heads (Layer 1-2 and Layer 2-1)
Circuit fraction:             2 / 8 = 25% of attention heads
```

**Information flow through the circuit:**
```
Input tokens: [A] [B] [C] [A] [D]
                  ^
Layer 1-2 (induction head): attends from position 4 ([A]) back to position 1 ([A])
                            copies the token that followed the first [A], which is [B]
Layer 2-1 (induction head): receives [B] signal from Layer 1-2
                            predicts [B] as the next token after the second [A]
Output: [A] [B] [C] [A] [D] [B]  <- correct induction completion
```

**The shift:** Out of eight attention heads, only two are causally necessary for this specific task. Mechanistic interpretability isolates them, enabling targeted understanding and intervention without analyzing the entire model.

---

### Common Confusion

1. **"Mechanistic interpretability is the same as standard interpretability."** It is not. Standard methods like saliency maps and attention heatmaps are correlational. Mechanistic interpretability seeks causal understanding through interventions like ablation and patching.

2. **"It requires reading every parameter by hand."** No. The field relies heavily on automation: gradient-based attribution, sparse autoencoders, and circuit extraction algorithms trace thousands of components automatically. Human effort is focused on validating and labeling the discovered circuits.

3. **"A full circuit diagram of GPT-4 exists."** It does not. Current work has mapped small circuits in small models. Scaling to billion-parameter models is an open research problem, and partial circuit maps are the current state of the art.

4. **"If you find a circuit, you understand the whole model."** A circuit explains one behavior on one task. A model may have thousands of overlapping circuits for different tasks, and some behaviors may not decompose into clean circuits at all.

5. **"Mechanistic interpretability is only for safety."** Safety is a major motivation, but the field also advances capabilities by revealing inefficiencies, guiding architecture design, and enabling model editing without full retraining.

6. **"It only applies to transformers."** The principles are model-agnostic. Circuits have been studied in CNNs (curve detectors, texture detectors), RNNs, and even biological neural networks. Transformers are simply the most studied target today.

7. **"Understanding a circuit lets you predict all model behavior."** Not necessarily. Circuits interact in nonlinear ways. Two individually understood circuits may produce emergent behavior when combined that neither predicts alone.

---

### Where It Is Used in Our Code

`src/phase100/phase100_mechinterp.py` — We build a toy 3-layer MLP and demonstrate the core mechanistic interpretability workflow: we run clean and corrupted forward passes, perform activation patching, compute finite-difference attribution scores for each layer, and visualize which hidden units contribute most to the output difference. This mirrors the real-world pipeline of localize-then-verify that drives circuit discovery in large models.
