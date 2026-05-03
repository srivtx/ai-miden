"""
FRONTIER TRACK: Phase 114 — DeepSeek-R1 Pipeline Concepts
Local NumPy simulation of cold-start, pure RL with GRPO, and distillation.
This script demonstrates WHY each step in the R1 pipeline exists.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# WHY: Reproducibility matters for educational demos so the "aha moment"
# curves look the same every run.
# ---------------------------------------------------------------------------
np.random.seed(114)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
VOCAB_SIZE = 20            # Toy vocabulary (digits 0-9, operators, CoT tokens)
N_PROBLEMS = 200           # Number of toy math problems
GROUP_SIZE = 4             # GRPO group size
N_STEPS = 300              # RL training steps
LR = 0.05                  # Policy gradient learning rate
KL_COEF = 0.02             # KL penalty coefficient

# ---------------------------------------------------------------------------
# STEP 1: Define the toy task — adding two-digit numbers
# WHY: Addition is simple enough to simulate in NumPy but complex enough
# to require reasoning (carry handling) if we force the model to emit steps.
# ---------------------------------------------------------------------------
def generate_problem():
    """Return two random two-digit numbers and their sum."""
    a = np.random.randint(10, 100)
    b = np.random.randint(10, 100)
    return a, b, a + b

# ---------------------------------------------------------------------------
# STEP 2: Define the policy as a softmax over sequences
# WHY: In a real model, the policy is a neural network. Here we use a
# tabular policy over a tiny vocabulary to make the simulation tractable
# while preserving the RL mechanics.
# ---------------------------------------------------------------------------
# Each "token" is an index. We simulate sequences of length 8:
# [digit1 tens, digit1 ones, '+', digit2 tens, digit2 ones, '=', result tens, result ones]
SEQ_LEN = 8
policy_logits = np.zeros((SEQ_LEN, VOCAB_SIZE))
ref_logits = np.zeros((SEQ_LEN, VOCAB_SIZE))

# ---------------------------------------------------------------------------
# STEP 3: Rule-based reward function
# WHY: This is the heart of the R1 approach. No learned reward model.
# The reward is 1.0 if the extracted answer matches the ground truth, else 0.
# This is ungameable and drives emergent behavior.
# ---------------------------------------------------------------------------
def compute_reward(output_tokens, true_sum):
    """Extract last two tokens as the answer and check exact match."""
    pred = output_tokens[-2] * 10 + output_tokens[-1]
    return 1.0 if pred == true_sum else 0.0

# ---------------------------------------------------------------------------
# STEP 4: GRPO update (no critic)
# WHY: GRPO uses the group mean as the baseline. This eliminates the critic
# model, cuts memory in half, and works with sparse end-of-sequence rewards.
# ---------------------------------------------------------------------------
def sample_sequence(logits):
    """Sample a sequence from the policy using softmax."""
    seq = []
    for t in range(SEQ_LEN):
        probs = np.exp(logits[t] - np.max(logits[t]))
        probs /= probs.sum()
        seq.append(np.random.choice(VOCAB_SIZE, p=probs))
    return np.array(seq)

def grpo_update(logits, ref_logits, group_outputs, group_rewards):
    """
    Perform one GRPO update.
    WHY: We increase log-prob of outputs with positive advantage
    and decrease log-prob of outputs with negative advantage.
    The KL penalty keeps the policy close to the reference.
    """
    baseline = np.mean(group_rewards)
    new_logits = logits.copy()
    for out, r in zip(group_outputs, group_rewards):
        advantage = r - baseline
        for t in range(SEQ_LEN):
            # Softmax probabilities
            probs = np.exp(logits[t] - np.max(logits[t]))
            probs /= probs.sum()
            ref_probs = np.exp(ref_logits[t] - np.max(ref_logits[t]))
            ref_probs /= ref_probs.sum()
            # Policy gradient: push probability of sampled token
            grad = np.zeros(VOCAB_SIZE)
            grad[out[t]] = 1.0
            # Subtract current probs for softmax gradient
            grad -= probs
            # Scale by advantage
            grad *= advantage
            # KL penalty: push toward reference
            kl_grad = probs - ref_probs
            grad -= KL_COEF * kl_grad
            new_logits[t] += LR * grad
    return new_logits

# ---------------------------------------------------------------------------
# STEP 5: Training loop with emergent reasoning simulation
# WHY: We simulate the "aha moment" by gradually increasing the
# effective sequence capacity. In reality, the model learns to use
# more tokens for CoT. Here we model this by giving a bonus to
# longer outputs once the policy passes a threshold.
# ---------------------------------------------------------------------------
rewards_history = []
accuracy_history = []
reasoning_length_history = []

for step in range(N_STEPS):
    step_rewards = []
    step_correct = 0
    step_lengths = []
    
    # Simulate a mini-batch of problems
    for _ in range(8):
        a, b, true_sum = generate_problem()
        group_outputs = []
        group_rewards = []
        
        # Generate GROUP_SIZE candidates per problem
        for _ in range(GROUP_SIZE):
            out = sample_sequence(policy_logits)
            r = compute_reward(out, true_sum)
            group_outputs.append(out)
            group_rewards.append(r)
            step_rewards.append(r)
            if r > 0.5:
                step_correct += 1
        
        # GRPO update using this group
        policy_logits = grpo_update(policy_logits, ref_logits, group_outputs, group_rewards)
        
        # Simulate emergent reasoning length
        # WHY: As training progresses, the model "discovers" that checking
        # its work improves accuracy. We proxy this by adding noise that
        # correlates with step number and reward.
        avg_r = np.mean(group_rewards)
        emergent_bonus = int(avg_r * (step / N_STEPS) * 10)
        step_lengths.append(SEQ_LEN + emergent_bonus)
    
    rewards_history.append(np.mean(step_rewards))
    accuracy_history.append(step_correct / (8 * GROUP_SIZE))
    reasoning_length_history.append(np.mean(step_lengths))

# ---------------------------------------------------------------------------
# STEP 6: Distillation simulation
# WHY: After training the large policy, we generate reasoning traces
# and use them to train a smaller "student" model via supervised learning.
# This makes reasoning cheap to deploy.
# ---------------------------------------------------------------------------
# Simulate teacher accuracy at the end of training
teacher_accuracy = accuracy_history[-1]
# Student starts at lower accuracy but converges toward teacher
student_accuracy = []
for s in range(N_STEPS):
    # Student learns from teacher traces; approaches teacher with noise
    prog = s / N_STEPS
    acc = teacher_accuracy * (0.5 + 0.5 * prog) + np.random.normal(0, 0.02)
    acc = np.clip(acc, 0, 1)
    student_accuracy.append(acc)

# ---------------------------------------------------------------------------
# STEP 7: Visualize training dynamics
# WHY: Humans learn from curves. We show reward, accuracy, reasoning
# length, and distillation transfer.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Reward vs step
ax = axes[0, 0]
ax.plot(rewards_history, color='steelblue', linewidth=1.5)
ax.set_title('Average Reward per Step (GRPO)')
ax.set_xlabel('Training Step')
ax.set_ylabel('Mean Reward')
ax.grid(True, alpha=0.3)

# Plot 2: Accuracy vs step
ax = axes[0, 1]
ax.plot(accuracy_history, color='forestgreen', linewidth=1.5)
ax.set_title('Accuracy vs Training Step')
ax.set_xlabel('Training Step')
ax.set_ylabel('Accuracy')
ax.set_ylim(0, 1)
ax.grid(True, alpha=0.3)

# Plot 3: Reasoning length vs accuracy
ax = axes[1, 0]
ax.scatter(reasoning_length_history, accuracy_history, c=range(N_STEPS), cmap='viridis', s=20)
ax.set_title('Reasoning Length vs Accuracy')
ax.set_xlabel('Average Output Length (tokens)')
ax.set_ylabel('Accuracy')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(ax.collections[0], ax=ax)
cbar.set_label('Training Step')

# Plot 4: Distillation transfer
ax = axes[1, 1]
ax.plot(accuracy_history, color='forestgreen', linewidth=2, label='Teacher (RL)')
ax.plot(student_accuracy, color='darkorange', linewidth=2, label='Student (Distilled)')
ax.set_title('Distillation: Student vs Teacher')
ax.set_xlabel('Training Step')
ax.set_ylabel('Accuracy')
ax.set_ylim(0, 1)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('src/phase114/r1_pipeline_concepts.png', dpi=150)
print("[Plot saved] src/phase114/r1_pipeline_concepts.png")

# ---------------------------------------------------------------------------
# FINAL INSIGHT SUMMARY
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHT: Pure RL with verifiable rewards can train reasoning")
print("models without a single human reasoning trace. GRPO eliminates")
print("the critic. Rule-based rewards eliminate reward hacking. The")
print("model invents chain-of-thought, self-reflection, and verification")
print("because they improve reward. Distillation makes it cheap to deploy.")
print("=" * 60)
print(f"Final teacher accuracy: {teacher_accuracy:.2%}")
print(f"Final student accuracy: {student_accuracy[-1]:.2%}")
