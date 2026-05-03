## What Is PPO?

---

### The Problem

You have a policy (a language model) that generates text, and you have a reward model that scores the text. You want to update the policy to maximize those scores. But standard policy gradient methods are unstable: a single bad batch can cause catastrophic updates, the policy might overfit to the reward model's quirks, and the variance of gradient estimates is so high that training oscillates wildly. How do you optimize the policy without breaking it?

---

### Definition

**Proximal Policy Optimization (PPO)** is a policy gradient reinforcement learning algorithm that constrains how far the policy can change in a single update. It uses a "clipped" surrogate objective to prevent overly aggressive steps, a learned value function to reduce gradient variance, and a KL-divergence penalty to keep the optimized policy close to its original behavior.

**How it works:**
```
1. Collect trajectories:      policy generates completions for a batch of prompts
2. Score with RM:             reward model assigns a scalar score to each completion
3. Compute advantages:        A = reward - value_function_estimate (baseline reduces variance)
4. Calculate probability ratio: r_t = pi_new(action) / pi_old(action)
5. Clipped objective:         L_clip = min(r_t * A, clip(r_t, 1-eps, 1+eps) * A)
6. Update policy:             maximize L_clip - c1 * value_loss + c2 * KL_penalty
```

The clip prevents the new policy from becoming too different from the old policy on any single action. The value baseline turns raw rewards into advantages, so the gradient only reflects whether an action was better or worse than expected.

**Key techniques:**
- **Clipped surrogate objective:** the core innovation of PPO; if the probability ratio moves outside `[1 - epsilon, 1 + epsilon]`, the gradient is clipped, preventing destructive large updates
- **Generalized Advantage Estimation (GAE):** a weighted average of multi-step advantages that balances bias and variance
- **Value function baseline:** a separate neural network estimates the expected reward for a state, reducing the variance of policy gradients by an order of magnitude
- **KL penalty:** an additional loss term `beta * KL(pi_new || pi_ref)` prevents the policy from drifting into regions where it generates gibberish that the RM happens to score highly

**Why this matters:**
- PPO is the algorithm used by OpenAI for InstructGPT, by Anthropic for Constitutional AI, and by most major RLHF pipelines.
- It is far more stable than vanilla policy gradient or TRPO (which requires expensive constrained optimization).
- The clip and KL constraints mean you can run PPO for thousands of steps without the policy collapsing into repetitive nonsense.

---

### Real-Life Analogy

Adjusting a recipe with a strict limit on how much any ingredient can change.
- **Vanilla policy gradient:** You taste the soup and decide to add salt. You dump in a cup. The soup is ruined. You have no mechanism to bound your adjustments.
- **PPO:** You taste the soup and decide to add salt. Your kitchen scale automatically stops you at one teaspoon past the original amount. If the taste improves, you keep the change. If it gets worse, you revert. You can iterate safely because no single step is catastrophic.
- **The value baseline:** Instead of judging each batch of soup on absolute taste (which varies with your hunger), you compare it to your expected taste for that recipe. This isolates the effect of your change from random mood fluctuations.

---

### Tiny Numeric Example

**Old policy probability of generating token "helpful":** `pi_old = 0.4`
**New policy probability after update:** `pi_new = 0.8`
**Advantage (how much better than expected):** `A = 1.5`
**Clip epsilon:** `eps = 0.2`

**Probability ratio:**
```
r = pi_new / pi_old = 0.8 / 0.4 = 2.0
```

**Unclipped objective:**
```
r * A = 2.0 * 1.5 = 3.0
```

**Clipped objective:**
```
clip(r, 1-0.2, 1+0.2) = clip(2.0, 0.8, 1.2) = 1.2
clipped = 1.2 * 1.5 = 1.8
```

**Final surrogate loss:**
```
L = min(3.0, 1.8) = 1.8
```

**Why this matters:** Without clipping, the optimizer would push aggressively to increase the probability of "helpful" from 0.4 to 0.8 (or higher), potentially causing the policy to collapse into always saying "helpful" regardless of context. With clipping, the effective gradient is bounded, forcing gradual, stable improvement.

**KL divergence check:**
```
KL(pi_new || pi_ref) = 0.8 * log(0.8/0.4) + 0.2 * log(0.2/0.6) = 0.28 nats
If target_KL = 0.1: penalty = 0.28 > 0.1 -> reduce learning rate or increase beta
```

---

### Common Confusion

1. **"PPO is only for robotics and games."** While PPO was invented for continuous control, it is now the standard for language model alignment because it handles high-dimensional action spaces (the vocabulary) and long trajectories (token sequences) robustly.

2. **"The clip parameter prevents any policy change."** It prevents large changes on individual actions. The policy can still change significantly across many small, safe steps. Epsilon=0.2 allows up to 20% change per token per update.

3. **"PPO does not need a value function."** Technically true (you can use vanilla policy gradient), but without a baseline the variance is so high that convergence is impractical for language models. The value function is essential.

4. **"KL penalty and clipping do the same thing."** They are complementary. Clipping bounds per-action probability ratios during the update. KL penalty penalizes overall divergence from the reference policy across the distribution. Clipping prevents local spikes; KL prevents global drift.

5. **"Higher rewards always mean a better policy."** The reward model can be gamed. A policy that learns to output "The answer is excellent and you are excellent" might get high RM scores but be useless. This is called reward hacking, and it is why KL penalties and human evaluation are necessary.

6. **"PPO updates the reward model."** No. PPO updates the policy. The reward model is frozen during PPO training. If you update the RM during PPO, the goalposts move and the policy chases a moving target.

7. **"One PPO step means one gradient update."** In practice, one PPO "step" collects a batch of trajectories, then performs multiple epochs of mini-batch gradient updates on that batch. This improves sample efficiency.

---

### Where It Is Used in Our Code

`src/phase122/phase122_rlhf_concepts.py` — We simulate PPO optimization on a toy policy. We collect trajectories, compute advantages with a value baseline, calculate the clipped surrogate objective, and update the policy while tracking KL divergence from the reference policy.

`src/phase122/phase122_rlhf_colab.py` — We use the TRL library's `PPOTrainer` to perform real PPO on Qwen2.5-3B. We generate completions, score them with our trained reward model, compute clipped policy gradients with the TRL PPO objective, and monitor KL divergence and reward curves over 50 PPO steps.

(End of file - total 102 lines)
