## Phase 42: Reasoning with Verifiable Rewards

---

### What We Built

A tiny policy model trained entirely with **verifiable rewards** and **GRPO** (Group Relative Policy Optimization) to solve simple arithmetic problems. No human labels, no reward model, no supervised fine-tuning — just a correct/incorrect checker.

### Key Results

- **Before training:** 0% accuracy on simple arithmetic
- **After 100 epochs of GRPO:** 70% accuracy, 64.1% mean reward
- **Training signal:** +1 for correct answer, 0 for wrong answer
- **Baseline:** Group mean reward subtraction (no critic network needed)

### Concepts Covered

| Term | File |
|---|---|
| Verifiable Reward | `what_is_verifiable_reward.md` |
| GRPO for Reasoning | `what_is_grpo_for_reasoning.md` |
| Emergent Reasoning | `what_is_emergent_reasoning.md` |
| DeepSeek-R1 Reasoning Chain | `what_is_deepseek_r1_reasoning_chain.md` |

### Architecture

- **Position-wise softmax policy:** Each problem gets a learned embedding. Each output position has its own linear head.
- **REINFORCE update:** Proper policy gradient scaled by group-relative advantage.
- **Task domain:** Single-digit arithmetic (a+b, a-b where a,b in 1-4) to focus on the learning mechanism.

### How GRPO Works Here

1. Sample 8 outputs for the same problem
2. Check each answer against ground truth (+1 or 0)
3. Baseline = mean reward of the 8 outputs
4. Advantage = reward - baseline
5. Update policy to favor above-average outputs

### Connection to Previous Phases

- **Phase 15 (PPO):** GRPO removes the critic network entirely
- **Phase 23 (RLHF):** Replaces human preference with automatic verification
- **Phase 6 (Chain-of-Thought):** Reasoning chains emerge from RL rather than prompting
- **Phase 39 (Distillation):** Reasoning models can be distilled to smaller models

### Connection to Next Phase

Now that we can train models to reason with verifiable rewards, how do we combine multiple specialized models? In Phase 43, we explore **model merging and ensembles** — techniques to fuse trained weights without retraining.

### Files

- `docs/phase42/what_is_verifiable_reward.md`
- `docs/phase42/what_is_grpo_for_reasoning.md`
- `docs/phase42/what_is_emergent_reasoning.md`
- `docs/phase42/what_is_deepseek_r1_reasoning_chain.md`
- `docs/phase42/SUMMARY.md`
- `src/phase42/phase42_verifiable_rewards.py`
- `src/phase42/phase42_verifiable_rewards_colab.py`
- `src/phase42/verifiable_rewards.png`
