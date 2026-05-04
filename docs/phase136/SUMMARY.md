# Phase 136 Summary: Neural Scaling Laws Beyond Chinchilla

## What We Learned

1. **Chinchilla optimizes training loss, not total cost of ownership.** The optimal model for deployment depends on inference volume, latency requirements, and hardware constraints. A smaller model with more training data can have lower lifetime cost than a larger Chinchilla-optimal model.

2. **Inference-aware scaling shifts the optimal frontier toward smaller models.** When inference dominates the budget, the cost-optimal choice is a compact, overtrained model rather than a large model trained at the Chinchilla ratio. This explains the commercial success of models like LLaMA 3 8B.

3. **Overtraining improves downstream performance even when training loss plateaus.** Training beyond the Chinchilla-optimal token count yields diminishing returns on perplexity but significant gains on reasoning and instruction-following. The data-to-parameter ratio is a design choice, not a fixed constant.

4. **Extreme-scale scaling faces the data wall and benchmark saturation.** High-quality text is finite. Multimodal data scales differently. Standard benchmarks are approaching ceilings. Future progress may require algorithmic innovation, synthetic data, and test-time compute, not just raw scale.

## Prerequisites

- Phase 49: Advanced Optimizers (training dynamics, learning curves, convergence)
- Phase 50: Evaluating Language Models (benchmarks, metrics, and their limitations)
- Phase 135: In-Context Learning and Emergent Capabilities (scaling as the driver of emergence)

## Recommended Reading Order

1. `what_is_inference_aware_scaling.md` — Total cost of ownership, training vs inference economics, and the shifting optimal frontier
2. `what_is_overtraining.md` — Training beyond Chinchilla, why excess data helps, and the small-model advantage
3. `what_is_scaling_at_extreme_scale.md` — The data wall, benchmark saturation, multimodal scaling, and economic limits
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase136/scaling_concepts.png` — Chinchilla-optimal line, inference-aware frontier, overtraining benefit curves, and scaling surfaces with theoretical limits
- `src/phase136/scaling_results.png` — Cost comparison table, optimal model size vs usage plot, and scaling curves from real model evaluation

## Navigation

- **Previous:** Phase 135: In-Context Learning and Emergent Capabilities
- **Next:** Phase 137 (see curriculum)
