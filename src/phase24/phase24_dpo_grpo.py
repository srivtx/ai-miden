#!/usr/bin/env python3
"""
================================================================================
Phase 24: DPO & GRPO — Simpler Alignment Methods
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 23, RLHF aligned models with human feedback.
But RLHF is complex: 3 models, unstable, expensive.

DPO and GRPO simplify this:
  DPO: Skip the reward model. Optimize preferences directly.
  GRPO: Skip the critic model. Compare responses within a group.

Every line has a comment. Read it like a story.
"""

# ==============================================================================
# IMPORTS
# ==============================================================================

import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ==============================================================================
# DPO: DIRECT PREFERENCE OPTIMIZATION
# ==============================================================================

def dpo_loss(policy_prob_preferred, policy_prob_rejected,
             ref_prob_preferred, ref_prob_rejected, beta=0.1):
    """
    Compute DPO loss.

    DPO skips the reward model entirely.
    It uses the model's own probabilities as implicit rewards.

    PARAMETERS:
        policy_prob_preferred = P(winner | prompt) under current policy
        policy_prob_rejected = P(loser | prompt) under current policy
        ref_prob_preferred = P(winner | prompt) under reference (original) policy
        ref_prob_rejected = P(loser | prompt) under reference (original) policy
        beta = temperature parameter

    RETURNS:
        loss = DPO loss (lower = better)
    """
    # Implicit reward: r = beta * log(P_policy / P_reference)
    # This measures how much the policy prefers the response over the reference

    # Log ratio for preferred response
    log_ratio_preferred = np.log(policy_prob_preferred + 1e-8) - np.log(ref_prob_preferred + 1e-8)

    # Log ratio for rejected response
    log_ratio_rejected = np.log(policy_prob_rejected + 1e-8) - np.log(ref_prob_rejected + 1e-8)

    # DPO loss: we want log_ratio_preferred >> log_ratio_rejected
    # Loss = -log( sigmoid( beta * (log_ratio_preferred - log_ratio_rejected) ) )
    diff = beta * (log_ratio_preferred - log_ratio_rejected)
    loss = -np.log(1 / (1 + np.exp(-diff)) + 1e-8)

    return loss


def demonstrate_dpo():
    """Demonstrate DPO with a concrete example."""
    print("=" * 60)
    print("DPO: DIRECT PREFERENCE OPTIMIZATION")
    print("=" * 60)
    print()

    print("  Prompt: 'What is 2+2?'")
    print()

    # Response A (preferred): "4"
    # Response B (rejected): "5"

    # Probabilities under current policy
    policy_prob_A = 0.7   # Policy thinks A is likely
    policy_prob_B = 0.3   # Policy thinks B is less likely

    # Probabilities under reference (original) policy
    ref_prob_A = 0.5      # Reference is neutral
    ref_prob_B = 0.5

    print(f"  Policy P('4' | prompt) = {policy_prob_A}")
    print(f"  Policy P('5' | prompt) = {policy_prob_B}")
    print(f"  Reference P('4' | prompt) = {ref_prob_A}")
    print(f"  Reference P('5' | prompt) = {ref_prob_B}")
    print()

    loss = dpo_loss(policy_prob_A, policy_prob_B, ref_prob_A, ref_prob_B)

    print(f"  DPO Loss: {loss:.4f}")
    print()
    print("  What DPO does:")
    print("    - Increase P('4') relative to reference")
    print("    - Decrease P('5') relative to reference")
    print("    - No separate reward model needed!")
    print()

    # Show what happens if policy gets worse
    print("  If policy starts preferring '5':")
    policy_prob_A_bad = 0.3
    policy_prob_B_bad = 0.7
    loss_bad = dpo_loss(policy_prob_A_bad, policy_prob_B_bad, ref_prob_A, ref_prob_B)
    print(f"    DPO Loss: {loss_bad:.4f} (HIGHER = worse)")
    print()

    # Show what happens if policy improves
    print("  If policy strongly prefers '4':")
    policy_prob_A_good = 0.9
    policy_prob_B_good = 0.1
    loss_good = dpo_loss(policy_prob_A_good, policy_prob_B_good, ref_prob_A, ref_prob_B)
    print(f"    DPO Loss: {loss_good:.4f} (LOWER = better)")
    print()


# ==============================================================================
# GRPO: GROUP RELATIVE POLICY OPTIMIZATION
# ==============================================================================

def grpo_update(rewards, epsilon=0.2):
    """
    Simplified GRPO update.

    GRPO generates multiple responses for one prompt.
    It computes advantages relative to the group average.
    No critic model needed!

    PARAMETERS:
        rewards = list of rewards for each response in the group
        epsilon = clipping parameter

    RETURNS:
        advantages = relative advantages for each response
    """
    group_mean = np.mean(rewards)
    group_std = np.std(rewards) + 1e-8

    # Advantage = (reward - group_mean) / group_std
    advantages = (rewards - group_mean) / group_std

    return advantages


def demonstrate_grpo():
    """Demonstrate GRPO with a concrete example."""
    print("=" * 60)
    print("GRPO: GROUP RELATIVE POLICY OPTIMIZATION")
    print("=" * 60)
    print()

    print("  Prompt: 'Explain gravity'")
    print()
    print("  Generate 4 responses for the same prompt:")
    print()

    responses = [
        "Gravity is magic.",                           # Bad
        "Gravity pulls things down.",                   # OK
        "Gravity is a force between masses.",           # Good
        "Gravity is the curvature of spacetime..."      # Excellent
    ]

    # Simulated rewards (from reward model or human ratings)
    rewards = np.array([2.0, 5.0, 7.0, 9.0])

    for i, (resp, reward) in enumerate(zip(responses, rewards)):
        print(f"    Response {i+1}: {resp}")
        print(f"    Reward: {reward}")
        print()

    # GRPO advantages
    advantages = grpo_update(rewards)

    print("  GRPO Advantages (relative to group):")
    for i, (reward, advantage) in enumerate(zip(rewards, advantages)):
        status = "IMPROVE" if advantage > 0 else "REDUCE"
        print(f"    Response {i+1}: Reward={reward:.1f}, Advantage={advantage:+.2f} -> {status}")
    print()

    print("  Key insight:")
    print("    - No critic model needed!")
    print("    - Compare responses to each other, not to absolute standard")
    print("    - Best response in group gets positive advantage")
    print("    - Worst response gets negative advantage")
    print()


# ==============================================================================
# COMPARISON: RLHF vs DPO vs GRPO
# ==============================================================================

def compare_methods():
    """Compare RLHF, DPO, and GRPO."""
    print("=" * 60)
    print("COMPARISON: RLHF vs DPO vs GRPO")
    print("=" * 60)
    print()

    comparison = [
        ("Models needed", "3 (Policy, Reference, Reward)", "2 (Policy, Reference)", "1 (Policy)"),
        ("Reward model", "Yes (separate)", "No (implicit)", "No (group comparison)"),
        ("Critic model", "Yes (PPO needs it)", "No", "No"),
        ("Stability", "Unstable", "Stable", "Stable"),
        ("Memory", "High", "Medium", "Low"),
        ("Training speed", "Slow", "Medium", "Fast"),
        ("Performance", "Good", "Good", "Very Good"),
    ]

    print(f"  {'Feature':20s} {'RLHF':30s} {'DPO':30s} {'GRPO':30s}")
    print(f"  {'-'*20} {'-'*30} {'-'*30} {'-'*30}")
    for feature, rlhf, dpo, grpo in comparison:
        print(f"  {feature:20s} {rlhf:30s} {dpo:30s} {grpo:30s}")
    print()

    print("  The trend: Simpler is better.")
    print("    RLHF (2022): 3 models, complex")
    print("    DPO (2023):  2 models, simpler")
    print("    GRPO (2024): 1 model, simplest")
    print()


# ==============================================================================
# VISUALIZATION
# ==============================================================================

def visualize_comparison():
    """Visualize the comparison."""
    print("=" * 60)
    print("VISUALIZING ALIGNMENT METHODS")
    print("=" * 60)

    fig, ax = plt.subplots(figsize=(12, 8))

    methods = ['RLHF\n(2022)', 'DPO\n(2023)', 'GRPO\n(2024)']
    complexity = [3, 2, 1]  # Number of models
    performance = [7.5, 8.0, 8.5]  # Relative performance
    colors = ['red', 'orange', 'green']

    # Bar chart
    x = np.arange(len(methods))
    width = 0.35

    bars1 = ax.bar(x - width/2, complexity, width, label='Models Needed', color=colors, alpha=0.7)
    bars2 = ax.bar(x + width/2, performance, width, label='Relative Performance', color=colors, alpha=0.4)

    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Alignment Methods: Complexity vs Performance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase24/dpo_grpo_comparison.png', dpi=150)
    print("Plot saved to: src/phase24/dpo_grpo_comparison.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 24: DPO & GRPO")
    print("=" * 60)
    print()
    print("  Goal: Simplify alignment without losing quality")
    print()

    # Demonstrate DPO
    demonstrate_dpo()

    # Demonstrate GRPO
    demonstrate_grpo()

    # Compare methods
    compare_methods()

    # Visualize
    visualize_comparison()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - DPO loss function (no reward model)")
    print("    - GRPO advantage computation (no critic)")
    print("    - Comparison of all three methods")
    print()
    print("  KEY INSIGHT:")
    print("    Simpler methods can achieve similar results.")
    print("    DPO skips the reward model.")
    print("    GRPO skips both reward AND critic models.")
    print()
    print("  THE TREND:")
    print("    RLHF (3 models) -> DPO (2 models) -> GRPO (1 model)")
    print("    Complexity down, quality up.")
    print()
    print("  NEXT QUESTION:")
    print("    'The model is helpful but slow. How do I")
    print("     make it faster for real-world use?'")
    print("=" * 60)
