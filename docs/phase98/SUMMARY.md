# Phase 98: System-2 Reasoning and o1-Style Training — Summary

This phase explored methods for making models think longer and more reliably at inference time, shifting from intuitive System-1 responses to deliberate System-2 reasoning.

## What We Learned

- **Chain-of-Thought (CoT) decomposes hard problems.** By forcing the model to generate explicit intermediate steps, CoT turns one impossible leap into a series of manageable hops, improving accuracy on multi-step reasoning from roughly 30% to 75% in toy simulations.

- **Self-Consistency turns noise into signal.** Sampling multiple independent CoT chains and taking a majority vote raises accuracy further by allowing correct reasoning to outvote isolated errors, though compute cost scales linearly with sample count.

- **Process Reward Models provide step-level supervision.** Unlike outcome-only evaluators, PRMs score every intermediate step, enabling early pruning of bad reasoning paths and reducing search effort by up to 75% in our simulations.

- **Inference-time compute can substitute for model size.** A smaller model with 10x more inference-time search can outperform a larger model with greedy decoding, suggesting that "thinking longer" is a viable scaling dimension orthogonal to parameter count.

- **These techniques are composable.** CoT provides the reasoning structure, Self-Consistency provides the aggregation, and PRMs provide the guidance. Together they form the foundation of o1-style training and System-2 architectures.

## Prerequisites

- Familiarity with transformer inference and token sampling (phases 22-25).
- Understanding of basic probability and combinatorics.
- Completion of Phase 70 (Domain Adaptation) is helpful but not required.

## Recommended Reading Order

1. `what_is_Chain-of-Thought.md` — Start here. CoT is the foundation; everything else builds on it.
2. `what_is_Self-Consistency.md` — The natural next step: how to aggregate multiple CoT samples.
3. `what_is_Process_Reward_Model.md` — The most advanced concept: how to supervise and search over the steps themselves.

## Visual Outputs

Running `src/phase98/phase98_system2_reasoning.py` produces two plots:

- `phase98_self_consistency.png` — Accuracy of single-chain decoding versus self-consistency across a range of per-step correctness probabilities.
- `phase98_steps_vs_accuracy.png` — Accuracy decay as reasoning chain length increases, showing how self-consistency mitigates the compounding-error problem.

## Navigation

- **Previous:** Phase 97 — Extreme Context Windows (100K+)
- **Next:** Phase 99 — Video and 3D Generation
