## What Is GRPO for Reasoning?

---

### The Problem

PPO (Proximal Policy Optimization, Phase 15) is the standard RL algorithm. It requires a value function (critic) to estimate advantages. Training a critic for reasoning tasks is expensive — the model must learn to estimate the expected reward of a partial reasoning chain, which is hard. Can we do RL without a critic?

---

### Definition

**GRPO (Group Relative Policy Optimization)** is a variant of PPO designed for reasoning tasks. It removes the critic network entirely and instead estimates advantages by comparing multiple outputs from the same prompt.

**How GRPO works:**
1. Sample a **group** of G outputs from the current policy for a single prompt
2. Compute a verifiable reward for each output (e.g., correct = 1, wrong = 0)
3. Compute the **mean reward** for the group
4. The **advantage** of each output is its reward minus the group mean
5. Update the policy to increase probability of above-average outputs, decrease below-average

**Key formula:**
```
Advantage_i = Reward_i - mean(Reward_1, ..., Reward_G)
```

**Why this works:**
- If the group average is low (e.g., 0.2), getting a reward of 1 is a strong positive signal
- If the group average is high (e.g., 0.8), getting a reward of 1 is only a mild positive signal
- The advantage is automatically scaled by the current difficulty of the problem

**Hyperparameters in DeepSeek-R1:**
- Group size G = 16 or 64
- Training on math, code, and logic puzzles
- No critic network at all

---

### Real-Life Analogy

A classroom taking a surprise quiz.
- **PPO (with critic):** The teacher tries to predict each student's score before grading. The teacher is often wrong. The prediction network is expensive to train.
- **GRPO:** The teacher grades all 30 quizzes, computes the class average (72%), and tells each student: "You scored 85%, which is +13 points above average. Good job." or "You scored 55%, which is -17 points below average. Study more."
- The teacher does not need to predict scores in advance. The relative comparison provides all the signal needed.
- As the class gets smarter, the average rises. A score of 85% might go from "excellent" to "average," automatically adjusting the difficulty scale.

---

### Tiny Numeric Example

**Prompt:** Solve `12 / 3 + 4 = ?`

**Ground truth:** 8

**Group of 4 outputs:**
```
Output 1: "12 / 3 = 4, 4 + 4 = 8" → Correct → Reward: 1
Output 2: "12 / 3 = 4, 4 + 4 = 8" → Correct → Reward: 1
Output 3: "12 / 3 = 3, 3 + 4 = 7" → Wrong   → Reward: 0
Output 4: "12 + 4 = 16"            → Wrong   → Reward: 0
```

**Group mean reward:** (1 + 1 + 0 + 0) / 4 = 0.5

**Advantages:**
```
Output 1: 1 - 0.5 = +0.5
Output 2: 1 - 0.5 = +0.5
Output 3: 0 - 0.5 = -0.5
Output 4: 0 - 0.5 = -0.5
```

**Policy update:**
- Increase probability of generating outputs like 1 and 2 (which show correct step-by-step reasoning)
- Decrease probability of outputs like 3 (wrong division) and 4 (wrong order of operations)

**Why this is better than a fixed baseline:**
- On easy problems where the model gets 90% correct, a correct answer is only +0.1 advantage
- On hard problems where the model gets 10% correct, a correct answer is +0.9 advantage
- The model automatically focuses on problems where it has the most room to improve

---

### Common Confusion

1. **"GRPO is completely different from PPO."** It is a minimal modification. It replaces the critic-computed advantage with a group-mean baseline. Everything else (clipped objective, entropy bonus) stays the same.

2. **"Group size must be large."** DeepSeek-R1 used G=16–64. Larger groups give more stable baselines but cost more compute per update. For small experiments, G=4–8 works.

3. **"GRPO only works for binary rewards."** No. It works for any scalar reward. The group mean subtraction works for continuous rewards too (e.g., partial credit on math problems).

4. **"GRPO is slower than PPO because it generates multiple outputs."** It generates multiple outputs per update, but it has no critic to train. In practice, the total compute is often lower because the critic is typically as large as the policy.

5. **"All outputs in a group must be unique."** No, sampling from the policy naturally produces diversity. If the policy is very confident, outputs might be similar, and the advantage signal shrinks — which is correct behavior.

---

### Where It Is Used in Our Code

`src/phase42/phase42_verifiable_rewards.py` — The `train_grpo()` function samples a group of outputs, computes rewards, calculates group-relative advantages, and updates the policy using REINFORCE with the group mean as a baseline.
