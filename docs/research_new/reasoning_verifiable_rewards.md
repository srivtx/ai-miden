# Research: Reasoning with Verifiable Rewards (DeepSeek-R1)

**Status:** Missing from course. Should be Phase 42, extension of Phase 26.
**Last Updated:** May 2026
**Sources:** DeepSeek-R1 (Jan 2025), OpenAI o1/o3 (2024), Process Reward Models

---

## 1. The Problem

Test-time compute (Phase 26) showed that thinking longer improves answers. But how do you TRAIN a model to think deeply in the first place? RLHF (Phase 23) uses human preferences, but humans cannot judge complex mathematical proofs or long reasoning chains accurately. How do you train reasoning when the only feedback is "correct" or "incorrect"?

## 2. What It Is

**Reasoning with verifiable rewards** trains models through reinforcement learning on tasks where the final answer can be automatically verified:
- Math problems (exact answer match)
- Code (unit tests pass/fail)
- Logic puzzles (solution checks out)
- Chess moves (engine evaluation)

**DeepSeek-R1's approach:**
1. Start with a base model (DeepSeek-V3)
2. Use **Group Relative Policy Optimization (GRPO)** — no critic model needed
3. Reward is +1 if final answer is correct, 0 if incorrect
4. The model learns to generate long reasoning chains (Chain of Thought) because that helps it get the right answer
5. Surprisingly, the model spontaneously develops useful behaviors: self-correction, backtracking, and structured thinking

**Key insight:** You do not need to teach reasoning explicitly. Just reward correct answers on hard problems, and the model figures out how to reason in order to maximize its reward.

## 3. Real-World Analogy

Teaching a student to solve puzzles without showing them the solution path.
- **Traditional teaching:** Show the student step-by-step solutions (supervised learning). The student memorizes patterns but struggles with novel problems.
- **Verifiable reward training:** Give the student puzzles and a checker. They get a cookie if the answer is right, nothing if wrong. The student tries different approaches, discovers that writing down intermediate steps helps catch errors, and gradually develops systematic problem-solving strategies.

The student might invent techniques you never taught them — like "let me verify this sub-problem before continuing" — because it increases their cookie rate.

## 4. Key Technical Details

### GRPO for Reasoning
```
1. For each problem, generate a group of K reasoning chains
2. Check each chain's final answer against ground truth
3. Reward = 1 if correct, 0 if incorrect
4. Advantage = reward - mean(group_rewards)
5. Update policy to increase probability of high-advantage chains
```

### Cold Start Problem
DeepSeek-R1-Zero (the first attempt) struggled with readability — its reasoning chains were garbled. To fix this:
1. Collect a small set of high-quality reasoning traces with clear CoT formatting
2. Fine-tune the base model on this "cold start" data
3. Then apply GRPO

This produced DeepSeek-R1 with both strong reasoning and readable outputs.

### Emergent Behaviors
During RL training, DeepSeek-R1 spontaneously developed:
- **Self-verification:** Checking its own answers
- **Backtracking:** Revisiting earlier steps when stuck
- **Decomposition:** Breaking hard problems into sub-problems
- **Aha moments:** Suddenly realizing a better approach mid-generation

None of these were explicitly programmed. They emerged from reward maximization.

## 5. Common Confusion

- **This is not just longer CoT prompting.** The model is TRAINED to reason, not just prompted. The reasoning emerges from optimization.
- **Verifiable rewards only work for certain tasks.** Math and code work great. Creative writing does not (no automatic verifier).
- **The model does not "understand" in a human sense.** It learns patterns that correlate with correct answers. But the reasoning chains are genuinely useful.
- **Not all reasoning is correct.** The model can reason convincingly and still be wrong. Verifiable rewards only check the final answer, not the reasoning path.
- **This is different from process reward models (PRM).** PRM (Phase 26) rewards each step. Verifiable rewards only reward the final answer. GRPO uses outcome rewards, not process rewards.

## 6. What We Would Build

A toy reasoning trainer where:
- The task is simple arithmetic with multiple steps
- A "teacher" model generates reasoning traces
- GRPO-style training rewards correct final answers
- We visualize how the model's reasoning length and accuracy improve over training

## 7. Why It Matters Now

- **DeepSeek-R1** matched OpenAI o1 on math benchmarks at 1/50th the cost
- **OpenAI o3** pushes this even further on extremely hard reasoning tasks
- **This is the hottest area in AI training** as of early 2025
- It enables AI to solve competition math, generate correct code, and prove theorems

## 8. Connection to Existing Phases

- **Phase 26 (Test-Time Compute):** We saw that longer thinking helps. This phase trains models to think longer.
- **Phase 24 (GRPO):** DeepSeek-R1 uses GRPO as its RL algorithm.
- **Phase 23 (RLHF):** Verifiable rewards replace human preference models with automatic checkers.
- **Phase 33 (MoE):** DeepSeek-V3 (the base for R1) uses MoE architecture.

---

## References

- DeepSeek-AI (2025): "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning"
- OpenAI (2024): "Learning to Reason with LLMs" (o1)
- Shao et al. (2024): "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models"
