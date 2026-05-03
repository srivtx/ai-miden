← [Previous: Phase 74: Recommendation Systems](docs/phase74/SUMMARY.md) | [Next: Phase 76: Fairness & Bias](docs/phase76/SUMMARY.md) →

---

# Phase 75: Explainable AI (XAI) — Summary

## Overview

Phase 75 confronts the black-box problem. After building powerful models in prior phases, we now ask: *why* did the model make that prediction? Explainability is not a luxury — it is a prerequisite for debugging, trust, and legal compliance in high-stakes domains.

## Documents

| Document | Topic |
|----------|-------|
| `what_is_model_explainability.md` | The need for global and local explanations of black-box models |
| `what_is_feature_importance.md` | Ranking which inputs drive predictions across the whole dataset |
| `what_is_lime.md` | Local surrogate models that explain one prediction at a time |
| `what_is_attention_visualization.md` | Reading attention heatmaps as a window into Transformer behavior |

## Code

| Script | Purpose |
|--------|---------|
| `src/phase75/phase75_xai_numpy.py` | NumPy concept demo: tiny MLP, saliency via backprop, exact SHAP for 4 features, LIME surrogate, and single-head attention heatmap |
| `src/phase75/phase75_xai_colab.py` | PyTorch real-workflow: vanilla saliency, SmoothGrad, Integrated Gradients, and multi-head attention visualization |

## Key Takeaways

1. **There is no single explanation.** Saliency, SHAP, LIME, and attention answer different questions. Use multiple methods and compare.
2. **Explanations can lie.** A method tells you what *it* thinks the model is doing. Always sanity-check by verifying that important features align with domain knowledge.
3. **Local ≠ global.** A feature can matter globally but not locally, and vice versa. Always ask whether you need a global audit or a single-decision justification.
4. **Attention is not causation.** High attention weight does not guarantee the model used that information. It is a clue, not proof.
5. **Start with gradients.** If you have autograd, vanilla saliency is one line of code. It is a fast first-pass before investing in expensive methods like exact SHAP.

## Outputs

- `src/phase75/xai_numpy.png` — 2x2 grid: saliency bar chart, SHAP values, LIME coefficients, attention heatmap
- `src/phase75/xai_colab.png` — 2x3 grid: three gradient methods, two attention heads, method comparison

---

← [Previous: Phase 74: Recommendation Systems](docs/phase74/SUMMARY.md) | [Next: Phase 76: Fairness & Bias](docs/phase76/SUMMARY.md) →
