# Phase 96: Sparse MoE Training at Scale — Summary

This phase introduced Mixture of Experts (MoE), a technique that increases model capacity without proportional compute cost by activating only a subset of parameters per token.

## Key Concepts

- **Mixture of Experts (MoE):** A gating network routes each token to a small subset of expert networks. Only the selected experts are computed, making large models more efficient.
- **Load Balancing Loss:** An auxiliary training loss that penalizes uneven token distribution across experts, preventing bottlenecks and ensuring all experts learn.
- **Expert Choice:** A routing strategy where experts select tokens rather than tokens selecting experts, guaranteeing fixed load per expert and reducing padding waste.

## Takeaway
MoE lets you train models with trillions of parameters on hardware sized for billions, provided you manage routing balance and memory efficiently.

## Navigation

- **Previous:** Phase 95
- **Next:** Phase 97 — Extreme Context Windows (100K+)
