# Phase 137 Summary: Advanced Mechanistic Interpretability (Circuits in 7B Models)

## What We Learned

1. **Circuit discovery finds the minimal subgraph of a model that implements a specific task.** By ablating components and measuring performance drops, we can identify which attention heads, MLP neurons, and edges actually matter for a behavior.
2. **Indirect Object Identification (IOI) is a canonical interpretability task.** Resolving "She" to "Mary" in "John threw the ball to Mary. She caught it." requires attention copying, name suppression, and logit boosting — functions that map to specific heads.
3. **Faithfulness means the circuit behaves like the full model; completeness means it contains only necessary components.** A circuit can be faithful but bloated, or complete but too small to replicate behavior. Both criteria must be satisfied.
4. **Automated circuit finding scales ablation studies from toy models to 7B parameters.** Greedy pruning, edge attribution (ACDC), and activation patching provide systematic ways to shrink the model without destroying task performance.
5. **Understanding circuits enables targeted editing.** If you know which heads implement a behavior, you can amplify, suppress, or remove them without retraining the entire model.

## Prerequisites

- Phase 20: Sampling and Temperature (how models generate tokens)
- Phase 45: Quantization (model internals and compression)
- Phase 110: Test-Time Compute Scaling (search and verification)

## Recommended Reading Order

1. `what_is_circuit_discovery.md` — Automated circuit finding, ablations, edge and node attribution
2. `what_is_indirect_object_identification.md` — The IOI task and how transformers resolve pronouns
3. `what_is_faithfulness_and_completeness.md` — Why a discovered circuit must be both accurate and minimal
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase137/circuit_graph.png` — The minimal circuit discovered by greedy pruning, showing nodes and edges.
- `src/phase137/node_importance.png` — Bar chart of component importance scores from ablation study.
- `src/phase137/faithfulness_curve.png` — Task accuracy versus circuit size, showing the trade-off between minimality and faithfulness.
- `src/phase137/head_importance_llama.png` — Colab output: attention head importance ranking for IOI in Llama-3B.
- `src/phase137/ablation_impact_llama.png` — Colab output: IOI accuracy drop per ablated head versus random baseline.

## Navigation

- **Previous:** Phase 136 (see curriculum)
- **Next:** [Phase 138: Test-Time Search (MCTS for LLMs)](../phase138/SUMMARY.md)
