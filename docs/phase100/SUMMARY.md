# Phase 100: Automated Circuit Discovery (MechInterp) — Summary

This phase introduced the field of mechanistic interpretability and the tools used to reverse-engineer neural networks from black-box weights to human-understandable circuits.

## What We Learned

- **Neural networks are not inherently opaque.** While billions of parameters resist direct inspection, localized subgraphs called circuits implement specific behaviors that can be isolated, labeled, and verified.

- **Causal intervention separates correlation from mechanism.** Techniques like activation patching and ablation determine whether a component is truly responsible for a behavior, not merely correlated with it.

- **Attribution patching scales causal search.** By using gradients to approximate the importance of each component, attribution patching narrows the search from billions of parameters to a handful of critical layers or heads without exhaustive experimentation.

- **Sparse autoencoders disentangle superposed features.** A strong sparsity penalty forces hidden units to represent single, interpretable concepts, turning dense activation soup into a labeled feature dictionary that researchers can inspect and intervene upon.

- **Mechanistic interpretability is a prerequisite for safe AI.** We cannot fix behaviors we do not understand. Circuit discovery provides the transparency needed to audit models, remove harmful capabilities, and predict failure modes before deployment.

## Prerequisites

- Completion of Phases 24-25 (attention mechanisms and transformers).
- Understanding of forward passes, activations, and gradients (Phases 4, 13).
- Familiarity with autoencoders and sparsity concepts (Phase 12).

## Recommended Reading Order

1. `what_is_Mechanistic_Interpretability.md` — Start with the big picture: what the field aims to achieve and why causal intervention matters.
2. `what_is_Attribution_Patching.md` — Learn the primary scaling tool: how to rank components by causal importance using gradients.
3. `what_is_Sparse_Autoencoder.md` — Finish with feature-level disentanglement: how to isolate individual concepts from superposed activations.

## Visual Outputs

Running `src/phase100/phase100_mechinterp.py` produces two plots:

- `phase100_attribution_patching.png` — Bar charts of attribution scores for each hidden unit in layers 1 and 2, showing which units have the largest causal influence on the output.
- `phase100_patching_effect.png` — Comparison of mean absolute output differences for clean-vs-corrupt and clean-vs-patched runs, quantifying how much recovery a single-layer patch achieves.

## Navigation

- **Previous:** Phase 99 — Video and 3D Generation
- **Next:** Phase 101 — Advanced Alignment
