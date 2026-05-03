← [Previous: Phase 45: Quantization & GGUF](docs/phase45/SUMMARY.md) | [Next: Phase 47: Synthetic Data & Self-Improvement](docs/phase47/SUMMARY.md) →

---

## Phase 46: Mechanistic Interpretability

---

### What We Built

A demonstration of reverse-engineering a tiny neural network by analyzing its internal activations. We visualized hidden states, performed causal activation patching, trained a sparse autoencoder, and showed superposition in action.

### Key Results

- **Model accuracy:** 100% on 4-pattern classification
- **Activation visualization:** 2 hidden neurons develop distinct activation signatures for each pattern
- **Activation patching:** Neither neuron alone is sufficient; both contribute to predictions
- **Sparse autoencoder:** 93.8% sparsity with feature 0 firing for Pattern A and feature 3 for Pattern D
- **Superposition:** 2 neurons successfully represent 4 distinct patterns through overlapping encodings

### Concepts Covered

| Term | File |
|---|---|
| Mechanistic Interpretability | `what_is_mechanistic_interpretability.md` |
| Activation Patching | `what_is_activation_patching.md` |
| Sparse Autoencoder | `what_is_sparse_autoencoder.md` |
| Superposition | `what_is_superposition.md` |

### How It Works

1. Train a tiny model with fewer hidden neurons than output classes
2. Visualize how hidden activations cluster by input pattern
3. Patch individual neurons from clean to corrupted inputs to find causal components
4. Train a sparse autoencoder on hidden states to discover interpretable features
5. Observe that neurons participate in multiple pattern representations (superposition)

### Connection to Previous Phases

- **Phase 45 (Quantization):** Understanding internals helps identify which weights are safe to quantize aggressively
- **Phase 4 (Neural Networks):** We now look inside the black box we built
- **Phase 42 (Reasoning):** Interpretability reveals whether reasoning chains are genuine or coincidental

### Connection to Next Phase

Now that we can understand models, how do we make them improve themselves? In Phase 47, we explore **synthetic data and self-improvement** — techniques where models generate their own training data to bootstrap beyond human-labeled datasets.

### Files

- `docs/phase46/what_is_mechanistic_interpretability.md`
- `docs/phase46/what_is_activation_patching.md`
- `docs/phase46/what_is_sparse_autoencoder.md`
- `docs/phase46/what_is_superposition.md`
- `docs/phase46/SUMMARY.md`
- `src/phase46/phase46_mechanistic_interpretability.py`
- `src/phase46/phase46_mechanistic_interpretability_colab.py`
- `src/phase46/mechanistic_interpretability.png`

---

← [Previous: Phase 45: Quantization & GGUF](docs/phase45/SUMMARY.md) | [Next: Phase 47: Synthetic Data & Self-Improvement](docs/phase47/SUMMARY.md) →