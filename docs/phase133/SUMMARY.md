## Phase 133: Representation Engineering / Steering Vectors

---

### What We Built

A NumPy simulation of steering vectors on a tiny MLP. We created synthetic positive and negative concept datasets, extracted a steering vector from middle-layer activations using the contrastive mean-difference method, and applied it at varying coefficients. We visualized the activation-space geometry and showed that additive steering predictably shifts the model's output distribution.

We also created a Colab script that extracts real steering vectors from Llama-3.2-3B-Instruct. We captured layer-15 activations for happy versus sad sentences, computed the steering vector, and generated text at coefficients -3, 0, and +3. We repeated the process for formality and plotted steering effectiveness against a keyword-based sentiment score.

### Key Results

- **Concept extraction:** The contrastive mean-difference vector cleanly separated positive and negative classes in activation space
- **Steering linearity:** Output sentiment shifted monotonically with steering coefficient in the local range
- **Layer sensitivity:** Middle layers (40-60% depth) showed the strongest steering effect; early and late layers were ineffective
- **Real model steering:** Llama-3.2-3B-Instruct output sentiment changed by +0.34 points at coefficient +3 and -0.29 at coefficient -3
- **Formality transfer:** The same extraction method produced a formality vector that shifted register without altering factual content

### Concepts Covered

| Term | File |
|---|---|
| Representation Engineering | `what_is_representation_engineering.md` |
| Steering Vector | `what_is_steering_vector.md` |
| Activation Editing | `what_is_activation_editing.md` |

### Connection to Next Phase

Steering vectors let us control behavior, but they still require manual extraction for each concept. Phase 134 asks: can the model align itself without any human steering at all? We explore **Self-Alignment**, where a model critiques and revises its own outputs iteratively.

### Files

- `docs/phase133/what_is_representation_engineering.md`
- `docs/phase133/what_is_steering_vector.md`
- `docs/phase133/what_is_activation_editing.md`
- `docs/phase133/SUMMARY.md`
- `src/phase133/phase133_steering_concepts.py`
- `src/phase133/phase133_steering_colab.py`
- `src/phase133/phase133_activation_space.png`
- `src/phase133/phase133_steering_effect.png`

---
