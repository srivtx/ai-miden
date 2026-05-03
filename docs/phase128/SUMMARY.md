# Phase 128 Summary: Safety RLHF (Rejection Sampling + Safety Rewards)

## What We Learned

1. **Safety RLHF shifts the policy toward refusal at the weight level, not just the prompt level.** Post-hoc filtering and system prompts are probabilistic. Training with safety rewards changes the model's output distribution so refusal is the default for harmful requests.

2. **Rejection sampling is the simplest safety training method: generate N responses, discard unsafe ones, and fine-tune on the remainder.** It requires no PPO, no critic, and no reward model. It is often sufficient for moderate safety gains.

3. **Constitutional AI scales safety training without linear human annotation cost.** The model critiques and revises its own outputs using explicit principles, then trains on the revised outputs. The principles are auditable and compact.

4. **The safety-helpfulness trade-off is unavoidable.** A model that refuses harmful requests will occasionally refuse benign ones. The Pareto frontier is the set of optimal trade-offs, and the exact position is a product decision.

## Prerequisites

- Phase 24: DPO and RLHF (policy gradients, KL penalties, reward models)
- Phase 50: Evaluating Language Models (metrics, benchmarks, trade-offs)
- Phase 70: Domain Adaptation (fine-tuning concepts, freezing components)

## Recommended Reading Order

1. `what_is_safety_rlhf.md` — Safety-specific reward models, harmlessness vs helpfulness, and the HHH framework
2. `what_is_rejection_sampling.md` — Best-of-n filtering, filtered SFT, and why simplicity beats complexity
3. `what_is_constitutional_ai_training.md` — Self-critique, self-revision, and training on revised outputs
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase128/safety_training_concepts.png` — Policy evolution for harmful and benign prompts, safety vs helpfulness trade-off curve, and Pareto frontier from the NumPy simulation.
- `src/phase128/safety_rlhf_results.png` — Training loss on safe responses, and safety/helpfulness rate comparison before and after rejection sampling SFT on the real Qwen model.

## Navigation

- **Previous:** Phase 127: Vision-Language Fine-tuning (LLaVA-style)
- **Next:** Phase 129 (see curriculum)
