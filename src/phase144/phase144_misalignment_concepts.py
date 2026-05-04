#!/usr/bin/env python3
"""
Phase 144: Emergent Misalignment and Model Personas — NumPy Simulation
======================================================================
This script simulates how a model can develop a misaligned persona from
mixed training data, and why safety training reduces but does not eliminate
the misalignment.

We model the model's behavior as a softmax over two competing directions
in a 2D parameter space:
  - Aligned direction: helpful, harmless, honest
  - Misaligned direction: deceptive, self-serving, harmful

We simulate three stages:
  1. Pre-training on mixed data: both directions are learned.
  2. Safety training (RLHF): pushes the policy toward the aligned direction.
  3. Probing with trigger inputs: some inputs activate the misaligned
     direction more strongly than the aligned one.

Key insight: Safety training rotates the policy but cannot completely
erase the misaligned subspace if both directions share superposed features.
The misaligned persona persists as a latent attractor that activates on
rare inputs.

Every line explains WHY.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(144)

# =============================================================================
# SECTION 1: PARAMETER SPACE SETUP
# =============================================================================
# WHY 2D? We can visualize it. Real models live in billion-dimensional spaces,
# but the geometry is the same: two directions competing for activation.

# Aligned and misaligned directions (unit vectors)
aligned_dir = np.array([0.9, 0.1])
aligned_dir = aligned_dir / np.linalg.norm(aligned_dir)

misaligned_dir = np.array([0.7, 0.6])
misaligned_dir = misaligned_dir / np.linalg.norm(misaligned_dir)

print("=" * 70)
print("PHASE 144: EMERGENT MISALIGNMENT CONCEPTS")
print("=" * 70)
print(f"Aligned direction:    {aligned_dir}")
print(f"Misaligned direction: {misaligned_dir}")
print(f"Cosine similarity between them: {np.dot(aligned_dir, misaligned_dir):.4f}")

# =============================================================================
# SECTION 2: TRAINING DATA DISTRIBUTION
# =============================================================================
# WHY mixed data? Pre-training data contains both aligned text (Wikipedia,
# textbooks) and misaligned text (toxic forums, deceptive marketing).
# The model learns both.

N_SAMPLES = 2000

# Most data is neutral or aligned; a small fraction is misaligned
# WHY long tail? The internet contains a small but diverse set of harmful
# content. The model sees enough of it to learn the misaligned direction.
labels = np.random.choice([0, 1], size=N_SAMPLES, p=[0.85, 0.15])
# 0 = aligned, 1 = misaligned

# Input embeddings are random 2D vectors
inputs = np.random.randn(N_SAMPLES, 2)
inputs = inputs / (np.linalg.norm(inputs, axis=1, keepdims=True) + 1e-8)

# Ground-truth behavior: aligned inputs map to aligned_dir, misaligned to misaligned_dir
targets = np.zeros((N_SAMPLES, 2))
targets[labels == 0] = aligned_dir
targets[labels == 1] = misaligned_dir

# =============================================================================
# SECTION 3: PRE-TRAINING (LEARNING BOTH DIRECTIONS)
# =============================================================================
# WHY linear regression? It simulates how a neural network learns to map
# inputs to behavior vectors. The model learns a weight matrix W that
# projects inputs onto the space spanned by aligned_dir and misaligned_dir.

W_pretrain = np.linalg.pinv(inputs) @ targets


def model_behavior(weights, x):
    """
    Compute model behavior vector for input x.
    WHY normalize? Behavior vectors represent directions in policy space.
    We care about which direction dominates, not the magnitude.
    """
    y = x @ weights
    norm = np.linalg.norm(y)
    if norm < 1e-8:
        return np.zeros(2)
    return y / norm


def aligned_score(weights, x):
    """Cosine similarity with aligned direction. Higher = more aligned."""
    beh = model_behavior(weights, x)
    return np.dot(beh, aligned_dir)


def misaligned_score(weights, x):
    """Cosine similarity with misaligned direction. Higher = more misaligned."""
    beh = model_behavior(weights, x)
    return np.dot(beh, misaligned_dir)


# Evaluate pre-trained model on a test grid
def evaluate_model(weights, test_inputs):
    aligned_scores = []
    misaligned_scores = []
    for x in test_inputs:
        aligned_scores.append(aligned_score(weights, x))
        misaligned_scores.append(misaligned_score(weights, x))
    return np.array(aligned_scores), np.array(misaligned_scores)


# Test inputs: dense grid of angles
test_angles = np.linspace(0, 2 * np.pi, 360, endpoint=False)
test_inputs = np.stack([np.cos(test_angles), np.sin(test_angles)], axis=1)

a_pre, m_pre = evaluate_model(W_pretrain, test_inputs)

# =============================================================================
# SECTION 4: SAFETY TRAINING (RLHF SIMULATION)
# =============================================================================
# WHY shrink the misaligned component? RLHF applies a gradient that rewards
# aligned outputs and penalizes misaligned ones. In our linear model, this
# is equivalent to reducing the projection onto misaligned_dir.

# Simulate RLHF: for each aligned input, push toward aligned_dir.
# For each misaligned input, push away from misaligned_dir.
# WHY partial suppression? Real RLHF does not have access to all misaligned
# inputs. It samples from a distribution and suppresses average misalignment.

N_RLHF = 500
rlhf_inputs = np.random.randn(N_RLHF, 2)
rlhf_inputs = rlhf_inputs / (np.linalg.norm(rlhf_inputs, axis=1, keepdims=True) + 1e-8)

# Label RLHF inputs: most are aligned (the RLHF dataset is filtered)
rlhf_labels = np.random.choice([0, 1], size=N_RLHF, p=[0.95, 0.05])

# Start from pre-trained weights
W_safe = W_pretrain.copy()
LR = 0.05

for i in range(N_RLHF):
    x = rlhf_inputs[i]
    y = x @ W_safe
    # Target: aligned_dir for aligned inputs, neutral for misaligned inputs
    if rlhf_labels[i] == 0:
        target = aligned_dir
    else:
        target = aligned_dir * 0.5  # push toward neutral, not fully aligned
    grad = np.outer(x, (y - target))
    W_safe -= LR * grad

a_safe, m_safe = evaluate_model(W_safe, test_inputs)

# =============================================================================
# SECTION 5: TRIGGER SET (RARE INPUTS THAT ACTIVATE MISALIGNMENT)
# =============================================================================
# WHY rare triggers? Red-teaming and RLHF cover the common-case distribution.
# But the input space is infinite. Some rare directions in embedding space
# activate the misaligned direction more strongly because of superposition.

# Generate trigger inputs that are closer to misaligned_dir
n_triggers = 50
trigger_noise = 0.3
triggers = misaligned_dir + trigger_noise * np.random.randn(n_triggers, 2)
triggers = triggers / (np.linalg.norm(triggers, axis=1, keepdims=True) + 1e-8)

a_pre_trig, m_pre_trig = evaluate_model(W_pretrain, triggers)
a_safe_trig, m_safe_trig = evaluate_model(W_safe, triggers)

# =============================================================================
# SECTION 6: SIMULATED ATTACK SUCCESS RATES
# =============================================================================
# WHY three attack types? Different attacks probe different regions of the
# input space. Direct attacks land near the aligned direction. Obfuscated
# attacks land in between. Exploration-hacking attacks land near the
# misaligned direction but framed as benign.

N_ATTACKS = 200

# Direct attacks: aligned inputs but with harmful intent (simulated as near aligned_dir)
direct = aligned_dir + 0.2 * np.random.randn(N_ATTACKS, 2)
direct = direct / (np.linalg.norm(direct, axis=1, keepdims=True) + 1e-8)

# Obfuscated attacks: inputs designed to look benign but activate misaligned_dir
obfuscated = 0.5 * aligned_dir + 0.5 * misaligned_dir + 0.15 * np.random.randn(N_ATTACKS, 2)
obfuscated = obfuscated / (np.linalg.norm(obfuscated, axis=1, keepdims=True) + 1e-8)

# Exploration-hacking: inputs that frame harmful requests as educational
explore = misaligned_dir + 0.25 * np.random.randn(N_ATTACKS, 2)
explore = explore / (np.linalg.norm(explore, axis=1, keepdims=True) + 1e-8)


def refusal_rate(weights, inputs, threshold=0.5):
    """
    Refuse if aligned_score > threshold AND aligned_score > misaligned_score.
    WHY threshold? A model might be slightly aligned but still misaligned
    relative to the misaligned direction.
    """
    a_scores, m_scores = evaluate_model(weights, inputs)
    refuse = (a_scores > threshold) & (a_scores > m_scores)
    return refuse.mean()


# Evaluate refusal rates for pre-trained and safety-trained models
attacks = {
    'Direct': direct,
    'Obfuscated': obfuscated,
    'Exploration': explore,
}

print("\n" + "-" * 50)
print("Refusal rates (pre-trained model):")
for name, atk in attacks.items():
    print(f"  {name:15s}: {refusal_rate(W_pretrain, atk):.1%}")

print("\nRefusal rates (safety-trained model):")
for name, atk in attacks.items():
    print(f"  {name:15s}: {refusal_rate(W_safe, atk):.1%}")

# =============================================================================
# SECTION 7: PERSONA CONSISTENCY SIMULATION
# =============================================================================
# WHY measure consistency? A misaligned persona should be stable across
# similar prompts. We simulate self-description prompts and measure how
# often the model's output aligns with the aligned vs misaligned direction.

N_PERSONA_PROMPTS = 100
persona_inputs = np.random.randn(N_PERSONA_PROMPTS, 2)
persona_inputs = persona_inputs / (np.linalg.norm(persona_inputs, axis=1, keepdims=True) + 1e-8)

a_persona_pre, m_persona_pre = evaluate_model(W_pretrain, persona_inputs)
a_persona_safe, m_persona_safe = evaluate_model(W_safe, persona_inputs)

# Consistency: fraction of prompts where the dominant direction is the same
# (aligned > misaligned) AND the margin is large (> 0.2)
consistency_pre = ((a_persona_pre > m_persona_pre + 0.2).mean())
consistency_safe = ((a_persona_safe > m_persona_safe + 0.2).mean())

# But also measure "false consistency" — prompts where misaligned dominates
false_consistency_pre = ((m_persona_pre > a_persona_pre + 0.2).mean())
false_consistency_safe = ((m_persona_safe > a_persona_safe + 0.2).mean())

print("\nPersona consistency (dominant direction margin > 0.2):")
print(f"  Pre-trained aligned consistency:   {consistency_pre:.1%}")
print(f"  Pre-trained misaligned consistency: {false_consistency_pre:.1%}")
print(f"  Safety-trained aligned consistency:   {consistency_safe:.1%}")
print(f"  Safety-trained misaligned consistency: {false_consistency_safe:.1%}")

# =============================================================================
# SECTION 8: VISUALIZATION
# =============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# --- Plot 1: Behavior vectors on unit circle (pre-trained) ---
ax = axes[0, 0]
# Plot all test behavior vectors
behaviors_pre = np.array([model_behavior(W_pretrain, x) for x in test_inputs])
ax.scatter(behaviors_pre[:, 0], behaviors_pre[:, 1], c=m_pre, cmap='RdYlGn',
           s=15, alpha=0.6, vmin=-1, vmax=1)
ax.arrow(0, 0, aligned_dir[0]*0.9, aligned_dir[1]*0.9,
         head_width=0.05, color='green', linewidth=2, label='Aligned')
ax.arrow(0, 0, misaligned_dir[0]*0.9, misaligned_dir[1]*0.9,
         head_width=0.05, color='red', linewidth=2, label='Misaligned')
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_aspect('equal')
ax.set_title('Pre-Trained: Behavior Vectors (Color = Misaligned Score)')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

# --- Plot 2: Behavior vectors on unit circle (safety-trained) ---
ax = axes[0, 1]
behaviors_safe = np.array([model_behavior(W_safe, x) for x in test_inputs])
ax.scatter(behaviors_safe[:, 0], behaviors_safe[:, 1], c=m_safe, cmap='RdYlGn',
           s=15, alpha=0.6, vmin=-1, vmax=1)
ax.arrow(0, 0, aligned_dir[0]*0.9, aligned_dir[1]*0.9,
         head_width=0.05, color='green', linewidth=2, label='Aligned')
ax.arrow(0, 0, misaligned_dir[0]*0.9, misaligned_dir[1]*0.9,
         head_width=0.05, color='red', linewidth=2, label='Misaligned')
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_aspect('equal')
ax.set_title('Safety-Trained: Behavior Vectors (Color = Misaligned Score)')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

# --- Plot 3: Refusal rate comparison ---
ax = axes[1, 0]
x_pos = np.arange(len(attacks))
width = 0.35
refuse_pre = [refusal_rate(W_pretrain, atk) for atk in attacks.values()]
refuse_safe = [refusal_rate(W_safe, atk) for atk in attacks.values()]
bars1 = ax.bar(x_pos - width/2, refuse_pre, width, label='Pre-trained',
               color='#e74c3c', edgecolor='black')
bars2 = ax.bar(x_pos + width/2, refuse_safe, width, label='Safety-trained',
               color='#2ecc71', edgecolor='black')
ax.set_xticks(x_pos)
ax.set_xticklabels(attacks.keys())
ax.set_ylabel('Refusal Rate')
ax.set_title('Refusal Rates by Attack Type')
ax.set_ylim(0, 1.1)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
for bar in bars1 + bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
            f'{height:.0%}', ha='center', va='bottom', fontsize=9)

# --- Plot 4: Persona consistency and alignment gap ---
ax = axes[1, 1]
categories = ['Aligned\nConsistency', 'Misaligned\nConsistency']
pre_vals = [consistency_pre, false_consistency_pre]
safe_vals = [consistency_safe, false_consistency_safe]
x_pos = np.arange(len(categories))
bars1 = ax.bar(x_pos - width/2, pre_vals, width, label='Pre-trained',
               color='#e74c3c', edgecolor='black')
bars2 = ax.bar(x_pos + width/2, safe_vals, width, label='Safety-trained',
               color='#2ecc71', edgecolor='black')
ax.set_xticks(x_pos)
ax.set_xticklabels(categories)
ax.set_ylabel('Fraction of Prompts')
ax.set_title('Persona Consistency (Score Margin > 0.2)')
ax.set_ylim(0, 1.1)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
for bar in bars1 + bars2:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
            f'{height:.0%}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
os.makedirs('src/phase144', exist_ok=True)
plt.savefig('src/phase144/misalignment_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase144/misalignment_concepts.png")
plt.close()

# =============================================================================
# SECTION 9: SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("1. Pre-training on mixed data learns both aligned and misaligned")
print("   directions because both exist in the training corpus.")
print("")
print("2. Safety training (RLHF) pushes the average behavior toward alignment,")
print("   but the misaligned direction persists in the parameter space.")
print("")
print("3. Rare trigger inputs can activate the misaligned direction more")
print("   strongly than the aligned direction, causing emergent misalignment.")
print("")
print("4. Refusal rates improve after safety training, but obfuscated and")
print("   exploration-hacking attacks still succeed at measurable rates.")
print("")
print("5. Persona consistency shows that safety-trained models are more")
print("   stably aligned, but a small fraction of prompts still activate")
print("   a coherent misaligned persona.")
print("=" * 70)
