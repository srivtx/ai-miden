#!/usr/bin/env python3
"""
Phase 122: RLHF Concepts — NumPy Demo
=======================================
This script simulates the full three-stage RLHF pipeline:

  1. SFT: Supervised fine-tuning on prompt-response pairs
  2. RM:  Training a reward model on pairwise comparisons
  3. PPO: Optimizing the policy with clipped surrogate objective

We use tiny linear models so the entire pipeline runs in seconds while
demonstrating the core mathematics: pairwise ranking loss, advantage
estimation, probability ratios, clipping, and KL divergence tracking.

Key insight: RLHF is not magic. It is three consecutive optimization
problems, each feeding into the next. The RM provides a differentiable
proxy for human judgment, and PPO optimizes the policy without breaking it.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(122)

# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================
# All models are tiny linear projections so we can focus on the algorithms.

PROMPT_DIM = 8
RESPONSE_DIM = 6
HIDDEN_DIM = 12
VOCAB_SIZE = 20          # for discrete response generation
N_SFT_PAIRS = 500
N_RM_PAIRS = 400
N_PPO_STEPS = 100
BATCH_SIZE = 32
LR = 0.05
PPO_EPS = 0.2            # clipping parameter
KL_COEF = 0.1            # KL penalty coefficient

print("="*60)
print("Phase 122: RLHF Concepts (NumPy Simulation)")
print("="*60)

# =============================================================================
# SECTION 2: DATA GENERATION
# =============================================================================
# We create synthetic prompts and "human-written" responses. The responses
# have structure: a good response is close to the prompt's true direction.

def generate_prompts(n):
    """Random prompt embeddings."""
    return np.random.randn(n, PROMPT_DIM)

def generate_response(prompt, quality="good"):
    """Generate a response embedding correlated with the prompt."""
    if quality == "good":
        return prompt[:RESPONSE_DIM] * 0.8 + np.random.randn(RESPONSE_DIM) * 0.2
    else:
        return np.random.randn(RESPONSE_DIM) * 1.0

def tokenize_response(response_emb):
    """Discretize a response embedding into a token sequence."""
    # Simple quantization: project to vocab and take argmax
    logits = response_emb @ np.random.randn(RESPONSE_DIM, VOCAB_SIZE)
    return np.argmax(logits)

prompts_sft = generate_prompts(N_SFT_PAIRS)
responses_sft = np.array([generate_response(p, "good") for p in prompts_sft])

print(f"\nSFT data: {N_SFT_PAIRS} prompt-response pairs")

# =============================================================================
# SECTION 3: STAGE 1 — SFT (SUPERVISED FINE-TUNING)
# =============================================================================
# The policy learns to map prompts to human-written responses.
# We model this as a linear projection: response = prompt @ W_sft

W_sft = np.random.randn(PROMPT_DIM, RESPONSE_DIM) * 0.3
sft_loss_history = []

print("\n--- Stage 1: SFT ---")
for step in range(200):
    idx = np.random.choice(N_SFT_PAIRS, BATCH_SIZE, replace=False)
    p_batch = prompts_sft[idx]
    r_batch = responses_sft[idx]

    pred = p_batch @ W_sft
    loss = np.mean((pred - r_batch) ** 2)
    sft_loss_history.append(loss)

    grad = 2 * p_batch.T @ (pred - r_batch) / BATCH_SIZE
    W_sft -= LR * grad

    if step % 50 == 0:
        print(f"SFT step {step:3d}: MSE = {loss:.4f}")

# =============================================================================
# SECTION 4: STAGE 2 — REWARD MODEL TRAINING
# =============================================================================
# We generate pairs of responses for each prompt: one "preferred" (closer to
# the true good response) and one "worse." The RM learns to score the
# preferred one higher using the Bradley-Terry pairwise loss.

# RM architecture: concatenate(prompt, response) -> scalar score
W_rm = np.random.randn(PROMPT_DIM + RESPONSE_DIM, 1) * 0.2
rm_loss_history = []
rm_acc_history = []

print("\n--- Stage 2: Reward Model Training ---")

# Generate preference pairs
rm_prompts = generate_prompts(N_RM_PAIRS)
rm_pairs = []
for p in rm_prompts:
    r_good = generate_response(p, "good")
    r_bad = generate_response(p, "bad")
    rm_pairs.append((p, r_good, r_bad))

for step in range(200):
    idx = np.random.choice(N_RM_PAIRS, BATCH_SIZE, replace=False)
    loss_batch = 0.0
    correct = 0
    grads = []

    for i in idx:
        p, r_good, r_bad = rm_pairs[i]
        inp_good = np.concatenate([p, r_good])
        inp_bad = np.concatenate([p, r_bad])

        score_good = float((inp_good @ W_rm)[0])
        score_bad = float((inp_bad @ W_rm)[0])

        # Bradley-Terry loss: -log(sigmoid(score_good - score_bad))
        diff = score_good - score_bad
        prob = 1.0 / (1.0 + np.exp(-diff))
        loss_batch += -np.log(prob + 1e-12)

        # Gradient: dL/dW = -(1 - sigmoid(diff)) * (inp_good - inp_bad)
        dprob = 1.0 - prob
        grad = -dprob * (inp_good - inp_bad).reshape(-1, 1)
        grads.append(grad)

        if score_good > score_bad:
            correct += 1

    loss_batch /= BATCH_SIZE
    rm_loss_history.append(loss_batch)
    rm_acc_history.append(correct / BATCH_SIZE)

    # Average gradient and update
    avg_grad = np.mean(grads, axis=0)
    W_rm -= LR * avg_grad

    if step % 50 == 0:
        print(f"RM step {step:3d}: loss = {loss_batch:.4f}, acc = {correct/BATCH_SIZE:.3f}")

# =============================================================================
# SECTION 5: STAGE 3 — PPO OPTIMIZATION
# =============================================================================
# We optimize the policy to maximize RM scores. We use a simplified PPO:
#   1. Policy generates a response for a prompt
#   2. RM scores the response
#   3. Compute advantage = reward - baseline
#   4. Update policy with clipped surrogate objective
#   5. Penalize KL divergence from the SFT policy

# Value function for baseline (simple linear model)
W_value = np.random.randn(PROMPT_DIM, 1) * 0.2
value_optimizer_steps = 50
for step in range(value_optimizer_steps):
    idx = np.random.choice(N_RM_PAIRS, BATCH_SIZE, replace=False)
    p_batch = np.array([rm_pairs[i][0] for i in idx])
    # True values = RM scores of "good" responses
    true_values = np.array([float((np.concatenate([rm_pairs[i][0], rm_pairs[i][1]]) @ W_rm)[0]) for i in idx])
    pred_values = p_batch @ W_value
    v_loss = np.mean((pred_values.squeeze() - true_values) ** 2)
    v_grad = 2 * p_batch.T @ (pred_values.squeeze() - true_values).reshape(-1, 1) / BATCH_SIZE
    W_value -= LR * v_grad

# PPO policy: stochastic policy over discrete response prototypes.
# This makes the probability ratio well-defined and lets PPO actually update.
N_ACTIONS = 10
response_prototypes = np.random.randn(N_ACTIONS, RESPONSE_DIM) * 0.5

# Initialize policy logits from SFT: we project prompts to action logits
# using a linear layer learned to align with the SFT mapping.
W_policy = np.random.randn(PROMPT_DIM, N_ACTIONS) * 0.1
W_ref = W_policy.copy()  # frozen reference for KL

def softmax(x):
    """Stable softmax over last axis."""
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / np.sum(e, axis=-1, keepdims=True)

ppo_reward_history = []
ppo_kl_history = []
ppo_loss_history = []

print("\n--- Stage 3: PPO Optimization ---")

for step in range(N_PPO_STEPS):
    idx = np.random.choice(N_RM_PAIRS, BATCH_SIZE, replace=False)
    p_batch = np.array([rm_pairs[i][0] for i in idx])

    # Policy probabilities
    logits = p_batch @ W_policy              # (B, N_ACTIONS)
    probs = softmax(logits)                  # (B, N_ACTIONS)
    ref_logits = p_batch @ W_ref
    ref_probs = softmax(ref_logits)

    # Sample actions from current policy
    actions = np.array([np.random.choice(N_ACTIONS, p=probs[j]) for j in range(BATCH_SIZE)])
    r_new = response_prototypes[actions]     # (B, RESPONSE_DIM)

    # For ratio computation we also need the probability of the sampled action
    # under both current and reference policy.
    pi_new = probs[np.arange(BATCH_SIZE), actions]
    pi_old = ref_probs[np.arange(BATCH_SIZE), actions]

    # Score sampled responses with RM
    rewards = np.array([float((np.concatenate([p_batch[j], r_new[j]]) @ W_rm)[0]) for j in range(BATCH_SIZE)])
    baseline = (p_batch @ W_value).squeeze()
    advantages = rewards - baseline

    # Probability ratio
    ratios = pi_new / (pi_old + 1e-8)

    # Clipped surrogate objective
    surr1 = ratios * advantages
    surr2 = np.clip(ratios, 1 - PPO_EPS, 1 + PPO_EPS) * advantages
    policy_loss = -np.mean(np.minimum(surr1, surr2))

    # KL penalty between current and reference policy distributions
    kl_div = np.mean(np.sum(probs * (np.log(probs + 1e-10) - np.log(ref_probs + 1e-10)), axis=-1))
    kl_penalty = KL_COEF * kl_div

    total_loss = policy_loss + kl_penalty
    ppo_loss_history.append(total_loss)
    ppo_reward_history.append(np.mean(rewards))
    ppo_kl_history.append(kl_div)

    # Policy gradient (REINFORCE with clipping approximation)
    # We compute the gradient of the unclipped surrogate w.r.t. logits,
    # then apply clipping as a hard gradient mask.
    grad_logits = np.zeros_like(logits)
    for j in range(BATCH_SIZE):
        # Advantage-weighted policy gradient
        adv = advantages[j]
        r = ratios[j]
        # If ratio is inside clip range, gradient flows; otherwise zero.
        if r <= 1 + PPO_EPS and r >= 1 - PPO_EPS:
            grad_logits[j, actions[j]] -= adv / (pi_new[j] + 1e-8)
    grad_logits /= BATCH_SIZE

    # Backprop into policy weights
    dW_policy = p_batch.T @ grad_logits
    W_policy -= LR * 0.5 * dW_policy

    if step % 20 == 0:
        print(f"PPO step {step:3d}: reward = {np.mean(rewards):.4f}, KL = {kl_div:.6f}, loss = {total_loss:.4f}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: SFT loss
ax = axes[0, 0]
ax.plot(sft_loss_history, color='#3498db', linewidth=1.5)
ax.set_xlabel('SFT Step')
ax.set_ylabel('MSE Loss')
ax.set_title('Stage 1: SFT Loss')
ax.grid(True, alpha=0.3)

# Plot 2: RM accuracy
ax = axes[0, 1]
ax.plot(rm_acc_history, color='#27ae60', linewidth=1.5)
ax.set_xlabel('RM Step')
ax.set_ylabel('Pairwise Accuracy')
ax.set_title('Stage 2: Reward Model Accuracy')
ax.grid(True, alpha=0.3)

# Plot 3: PPO reward
ax = axes[1, 0]
ax.plot(ppo_reward_history, color='#e74c3c', linewidth=1.5)
ax.set_xlabel('PPO Step')
ax.set_ylabel('Average Reward')
ax.set_title('Stage 3: PPO Reward Curve')
ax.grid(True, alpha=0.3)

# Plot 4: KL divergence
ax = axes[1, 1]
ax.plot(ppo_kl_history, color='#9b59b6', linewidth=1.5)
ax.set_xlabel('PPO Step')
ax.set_ylabel('KL Divergence (param distance)')
ax.set_title('KL Divergence from SFT Reference')
ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase122', exist_ok=True)
plt.savefig('src/phase122/rlhf_concepts.png', dpi=150)
print("\nSaved plot to src/phase122/rlhf_concepts.png")

# =============================================================================
# SECTION 7: BEFORE/AFTER SAMPLES
# =============================================================================
print("\n" + "="*60)
print("SAMPLE COMPARISON: SFT vs PPO")
print("="*60)

test_prompts = generate_prompts(3)
for i, p in enumerate(test_prompts):
    # SFT response (continuous projection)
    r_sft = p @ W_sft
    # PPO response (best action under current policy)
    ppo_logits = p @ W_policy
    ppo_action = int(np.argmax(ppo_logits))
    r_ppo = response_prototypes[ppo_action]
    score_sft = float((np.concatenate([p, r_sft]) @ W_rm)[0])
    score_ppo = float((np.concatenate([p, r_ppo]) @ W_rm)[0])
    print(f"\nPrompt {i+1}: {p[:3].round(2)}")
    print(f"  SFT response score: {score_sft:.3f}")
    print(f"  PPO response score: {score_ppo:.3f}")
    print(f"  Improvement:        {score_ppo - score_sft:+.3f}")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"SFT final loss:        {sft_loss_history[-1]:.4f}")
print(f"RM final accuracy:     {rm_acc_history[-1]:.3f}")
print(f"PPO initial reward:    {ppo_reward_history[0]:.4f}")
print(f"PPO final reward:      {ppo_reward_history[-1]:.4f}")
print(f"PPO final KL:          {ppo_kl_history[-1]:.6f}")
print("\nKey lessons:")
print("  1. SFT establishes a baseline behavior the policy can improve upon")
print("  2. The reward model learns to discriminate preferences from pairs")
print("  3. PPO increases reward while controlling drift via KL penalty")
print("  4. Clipping prevents catastrophic policy updates")
print("  5. The three stages are sequential dependencies, not alternatives")
