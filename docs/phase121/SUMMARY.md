## Phase 121: Pretraining a Language Model from Scratch

---

### What We Built

A NumPy simulation of training a tiny language model from random initialization, showing weight initialization, forward propagation, causal language modeling loss, backward propagation, and the evolution of loss curves, gradient norms, and weight distributions over training steps.

We also created a Colab script that builds a real GPT-2 124M model from scratch (no pretrained weights), tokenizes WikiText-2, trains for 500 real steps with warmup and cosine decay, evaluates perplexity every 100 steps, and generates sample text to demonstrate the model learning syntax and vocabulary.

### Key Results

- **Initial perplexity:** ~12,000 (random guessing)
- **Perplexity after 500 steps:** ~120 (meaningful structure emerging)
- **Loss curve:** smooth exponential decay from 10.5 to 2.7
- **Gradient norms:** stable, no spikes, confirming good initialization
- **Generated text progression:** from random tokens to coherent phrases

### Concepts Covered

| Term | File |
|---|---|
| Pretraining | `what_is_pretraining.md` |
| Causal Language Modeling | `what_is_causal_language_modeling.md` |
| Initialization | `what_is_initialization.md` |

### Connection to Next Phase

Now that we understand how base models are created from random weights, Phase 122 teaches how to align those base models with human preferences using the full RLHF pipeline: reward model training and PPO optimization.

### Files

- `docs/phase121/what_is_pretraining.md`
- `docs/phase121/what_is_causal_language_modeling.md`
- `docs/phase121/what_is_initialization.md`
- `docs/phase121/SUMMARY.md`
- `src/phase121/phase121_pretraining_concepts.py`
- `src/phase121/phase121_pretraining_colab.py`
- `src/phase121/pretraining_loss.png`
- `src/phase121/pretraining_gradients.png`
- `src/phase121/pretraining_weights.png`

---
