# Phase 96 Summary: Sparse MoE Training at Scale

## What We Learned

- Mixture of Experts increases model capacity without proportional compute cost by sparsely activating only a subset of parameters per token.
- Load balancing is not an optional enhancement; unbalanced routing collapses training into a few overused experts and wastes the rest of the parameter budget.
- Expert Choice inverts the routing logic so that experts select tokens rather than tokens selecting experts, guaranteeing fixed compute per expert and eliminating capacity padding waste.
- The total parameter count grows with the number of experts, so memory and communication costs remain significant even though per-token compute is sparse.
- Sparse architectures require different optimization strategies than dense models, particularly around distributed training, gradient synchronization, and communication-aware batching.
- A well-tuned MoE can outperform a dense model with the same active parameter count, but a poorly tuned MoE often underperforms a much smaller dense baseline.

## Prerequisites

- Completion of Phases 0 through 95
- Solid understanding of feed-forward networks and multi-head self-attention
- Familiarity with distributed training basics and gradient synchronization

## Recommended Reading Order

1. `what_is_Mixture_of_Experts.md` — Start with the core architecture and the intuition behind sparse activation.
2. `what_is_Load_Balancing_Loss.md` — Learn why routing balance is critical and how the auxiliary loss enforces it.
3. `what_is_Expert_Choice.md` — Explore an alternative routing paradigm that trades token autonomy for hardware efficiency.

## Visual Outputs

- `src/phase96/phase96_moe.py` generates routing distribution histograms comparing token-choice and Expert Choice strategies, load-balancing loss curves across training steps, and per-expert activation frequency bar charts.

## Navigation

- Previous: [Phase 95](../phase95/SUMMARY.md)
- Next: [Phase 97](../phase97/SUMMARY.md)
