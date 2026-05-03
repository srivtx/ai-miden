## Phase 47: Synthetic Data & Self-Improvement

---

### What We Built

A demonstration of how models can generate their own training data, filter it with automatic verifiers, and iteratively improve themselves without new human labels.

### Key Results

- **Human-only baseline:** 100% accuracy on simple arithmetic (with 100 examples)
- **Synthetic generation:** 500/500 candidates passed verification from the trained model
- **Self-improvement:** 5 iterations maintaining 100% accuracy with growing synthetic datasets
- **Constitutional AI:** Principle-enforced training pushes predictions toward cleaner integer values

### Concepts Covered

| Term | File |
|---|---|
| Synthetic Data | `what_is_synthetic_data.md` |
| Iterative Self-Improvement | `what_is_iterative_self_improvement.md` |
| Constitutional AI | `what_is_constitutional_ai.md` |
| Rejection Sampling | `what_is_rejection_sampling.md` |

### How It Works

1. Train a base model on small human-labeled dataset
2. Generate many candidate solutions on new prompts
3. Run automatic verifier to keep only correct answers
4. Fine-tune model on verified synthetic data
5. Repeat: improved model generates even better synthetic data

### Connection to Previous Phases

- **Phase 46 (Interpretability):** Understanding internals helps design better verifiers
- **Phase 42 (Reasoning):** Verifiable rewards are the verifier engine for synthetic data
- **Phase 22 (SFT):** Synthetic data replaces expensive human annotation

### Connection to Next Phase

Now that models can improve themselves with synthetic data, can they also adapt during inference on a single example? In Phase 48, we explore **test-time training** — adapting the model at inference time without any pre-collected dataset.

### Files

- `docs/phase47/what_is_synthetic_data.md`
- `docs/phase47/what_is_iterative_self_improvement.md`
- `docs/phase47/what_is_constitutional_ai.md`
- `docs/phase47/what_is_rejection_sampling.md`
- `docs/phase47/SUMMARY.md`
- `src/phase47/phase47_synthetic_data.py`
- `src/phase47/phase47_synthetic_data_colab.py`
- `src/phase47/synthetic_data.png`
