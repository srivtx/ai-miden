## What Is GRPO?

---

### The Problem

Standard Proximal Policy Optimization (PPO) for language models requires four models running simultaneously: the policy model (the one being trained), the reference model (for KL penalty), the value model (critic), and the reward model. The critic is especially expensive. It must estimate the expected future reward for every token in a sequence, which means it is often as large as the policy itself. At the 70B scale, having two 70B models in memory is prohibitive. Worse, the critic is trained on the same sparse rewards as the policy, so it is noisy and slow to converge. For reasoning tasks where the only feedback is "correct" or "incorrect" at the end of a long chain-of-thought, training a critic to predict per-token value is almost impossible. GRPO removes the critic entirely.

---

### Definition

**GRPO (Group Relative Policy Optimization)** is a reinforcement learning algorithm that trains a policy without a critic model. Instead of estimating value with a separate network, GRPO generates a group of candidate outputs for each prompt, computes rewards for each, and uses the relative advantage within the group to update the policy. The baseline is the group mean, not a learned value function.

**How it works:**
```
For each training step:
  1. Sample a prompt (e.g., a math problem).
  2. Generate G outputs from the current policy (the "group").
  3. Compute reward r_i for each output i using a rule (e.g., exact match).
  4. Compute group mean: baseline = (1/G) * sum(r_i)
  5. For each output, advantage A_i = r_i - baseline
  6. Update policy to increase probability of outputs with A_i > 0
  7. Apply KL penalty against a reference model to prevent drift
```

**Key properties:**
- **No critic:** The group mean serves as the baseline, eliminating the need for a value model.
- **Relative advantage:** An output is good not in absolute terms, but relative to the other outputs in its group. This normalizes reward scale automatically.
- **Token-level loss:** The advantage is applied uniformly to all tokens in a sequence, weighted by the policy's log-probability.

**Why this matters:**
- GRPO cuts memory usage by roughly 50% compared to PPO because the critic is deleted.
- It works with sparse, end-of-sequence rewards because the group comparison happens at the sequence level.
- It is simpler to implement, more stable, and scales to larger models.

---

### Real-Life Analogy

Imagine a basketball coach trying to improve a player's free-throw shooting.
- **PPO (with critic):** The coach hires a sports analyst who watches every shot attempt and predicts, before the ball is released, whether it will go in. The analyst's prediction is the "baseline." If the analyst predicted a miss but the shot goes in, the player gets positive reinforcement. The problem: the analyst is expensive, often wrong, and must be trained alongside the player. On trick shots the analyst has never seen, the baseline is useless.
- **GRPO:** The coach tells the player to take 10 free throws in a row. The player makes 6. Instead of an analyst, the coach uses the group average (60%) as the baseline. Each made shot gets positive credit (it was above average). Each missed shot gets negative credit (below average). The player adjusts their form based on which attempts in the group were better than the others. No analyst needed.
- **The trade-off:** The player learns more slowly at first because 10 shots is a small sample. But the feedback is honest — there is no analyst to game or overfit. Over thousands of groups of 10, the player's true skill emerges. GRPO trades the instant (but noisy) feedback of a critic for the honest (but sample-limited) feedback of relative comparison.

---

### Tiny Numeric Example

**Prompt: "What is 12 + 15?" Generate G = 4 outputs.**

**Outputs and rewards (exact match, correct = 27):**
```
Output 1: "27"        → reward = 1.0
Output 2: "27"        → reward = 1.0
Output 3: "26"        → reward = 0.0
Output 4: "28"        → reward = 0.0
```

**Group statistics:**
```
Mean reward (baseline):  (1.0 + 1.0 + 0.0 + 0.0) / 4 = 0.5
```

**Advantages:**
```
A_1 = 1.0 - 0.5 = +0.5
A_2 = 1.0 - 0.5 = +0.5
A_3 = 0.0 - 0.5 = -0.5
A_4 = 0.0 - 0.5 = -0.5
```

**Policy update (simplified):**
```
Loss = - sum( A_i * log_prob(policy, output_i) ) + KL_penalty
```

**Result:** The policy increases probability of outputs 1 and 2 (positive advantage) and decreases probability of outputs 3 and 4 (negative advantage). The model learns that "27" is better without ever being told what 12 + 15 equals — it only knows that "27" beat the group average.

**KL penalty:** A reference model (the initial policy) penalizes the current policy if it drifts too far. This prevents the policy from collapsing to a single answer or exploiting spurious patterns.

---

### Common Confusion

1. **"GRPO does not need a reward model."** It does not need a learned reward model or a critic, but it still needs a reward function. The reward can be rule-based (exact match) or learned, but the algorithm itself only requires the scalar reward per output.

2. **"The group mean is the same as a running average of all past rewards."** No. The group mean is computed from outputs generated from the same prompt in the same batch. It is prompt-specific, not global. A hard prompt might have a group mean of 0.1; an easy prompt might have 0.9. GRPO normalizes within each prompt.

3. **"GRPO gives per-token rewards."** No. GRPO gives one reward per output. The advantage is broadcast to all tokens in the output equally. This is a limitation, but it is exactly why GRPO works for sparse end-of-sequence rewards where per-token labels do not exist.

4. **"GRPO is only for math and coding."** It was popularized for reasoning tasks, but the algorithm applies to any RL problem with a policy and a scalar reward. The key requirement is that you can generate multiple outputs per prompt.

5. **"GRPO cannot handle continuous rewards."** It can. If rewards are continuous (e.g., 0.7, 0.8, 0.9), the relative advantages still work. The group mean baseline normalizes any reward scale.

6. **"A larger group size always helps."** Larger groups give a more stable baseline, but they linearly increase compute per gradient step. In practice, group sizes of 4 to 16 are common. Diminishing returns appear beyond that.

7. **"GRPO eliminates the need for a reference model."** No. The reference model is still used for the KL divergence penalty. Without it, the policy can collapse or exploit spurious correlations in the reward function.

---

### Where It Is Used in Our Code

`src/phase114/phase114_r1_pipeline_concepts.py` — We simulate a toy addition task, generate a group of 4 candidate answers per problem, compute exact-match rewards, derive relative advantages against the group mean, and perform a policy gradient update. We show that the policy improves over steps without any critic network.

`src/phase114/phase114_r1_training_colab.py` — We load Qwen2.5-3B-Instruct, implement a full GRPO training loop on GSM8K math problems with group size 4, exact-match rewards, and KL penalty against the frozen reference model. We track accuracy and show that the model's reasoning traces grow longer and more reflective as training progresses.

(End of file - total 97 lines)
