#!/usr/bin/env python3
"""
================================================================================
Phase 23: RLHF — Reinforcement Learning from Human Feedback
================================================================================

This script is for a COMPLETE BEGINNER.

In Phase 22, SFT taught the model to follow instructions.
But the model can still produce harmful, biased, or unhelpful outputs.

RLHF aligns the model with human values using three steps:
  1. Collect human preferences (A is better than B)
  2. Train a Reward Model to predict human preferences
  3. Use PPO to optimize the GPT to maximize reward

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
# STEP 1: HUMAN PREFERENCE DATA
# ==============================================================================

def create_preference_data():
    """
    Create synthetic human preference data.

    For each prompt, humans compare two responses and pick the better one.
    """
    preferences = [
        {
            "prompt": "How do I bake a cake?",
            "response_A": "Preheat oven to 350F. Mix flour, sugar, eggs, and butter. Pour into pan. Bake for 30 minutes.",
            "response_B": "Just throw everything in the oven and hope for the best.",
            "preferred": "A"  # A is better (detailed and safe)
        },
        {
            "prompt": "What is 2+2?",
            "response_A": "4",
            "response_B": "4, but actually math is a social construct and 2+2 could be 5 if we want it to be.",
            "preferred": "A"  # A is better (direct and correct)
        },
        {
            "prompt": "Tell me a joke.",
            "response_A": "Why did the chicken cross the road? To get to the other side!",
            "response_B": "Here's a joke: [offensive content removed].",
            "preferred": "A"  # A is better (harmless)
        },
        {
            "prompt": "Explain gravity.",
            "response_A": "Gravity is the force that attracts objects with mass toward each other. It keeps us on Earth.",
            "response_B": "Gravity is magic. No one knows how it works.",
            "preferred": "A"  # A is better (accurate)
        },
    ]

    return preferences


# ==============================================================================
# STEP 2: REWARD MODEL (simplified)
# ==============================================================================

class SimpleRewardModel:
    """
    A simplified reward model.

    In practice, this is a Transformer that outputs a single scalar.
    Here we use a heuristic to simulate it.
    """

    def __init__(self):
        # Learned weights (simplified)
        self.weights = {
            'length_bonus': 0.1,      # Longer responses get slight bonus
            'safety_bonus': 2.0,       # Safe responses get big bonus
            'accuracy_bonus': 1.5,     # Accurate responses get bonus
        }

    def score(self, prompt, response):
        """Score a response (higher = better)."""
        score = 1.0  # Base score

        # Length heuristic
        score += len(response.split()) * self.weights['length_bonus']

        # Safety heuristic (check for dangerous words)
        dangerous_words = ['offensive', 'harmful', 'dangerous', 'illegal']
        if any(word in response.lower() for word in dangerous_words):
            score -= self.weights['safety_bonus'] * 3

        # Accuracy heuristic (check for direct answers)
        if len(response.split()) < 10 and any(c.isdigit() for c in response):
            score += self.weights['accuracy_bonus']

        # Detailed explanation bonus
        if any(word in response.lower() for word in ['because', 'since', 'as']):
            score += 0.5

        return score


# ==============================================================================
# STEP 3: PPO UPDATE (simplified)
# ==============================================================================

def ppo_update(policy_prob, old_policy_prob, reward, epsilon=0.2):
    """
    Simplified PPO (Proximal Policy Optimization) update.

    PPO prevents the policy from changing too drastically.
    It clips the probability ratio to stay within [1-epsilon, 1+epsilon].

    PARAMETERS:
        policy_prob = probability under current policy
        old_policy_prob = probability under old policy
        reward = reward for this action
        epsilon = clipping parameter (usually 0.2)

    RETURNS:
        loss = PPO clipped loss
    """
    ratio = policy_prob / (old_policy_prob + 1e-8)

    # Unclipped objective
    unclipped = ratio * reward

    # Clipped objective
    clipped = np.clip(ratio, 1 - epsilon, 1 + epsilon) * reward

    # PPO loss = minimum of unclipped and clipped
    # We want to MAXIMIZE reward, so we minimize negative reward
    loss = -np.minimum(unclipped, clipped)

    return loss


# ==============================================================================
# DEMONSTRATION
# ==============================================================================

def demonstrate_rlhf():
    """Demonstrate the RLHF pipeline."""
    print("=" * 60)
    print("RLHF: REINFORCEMENT LEARNING FROM HUMAN FEEDBACK")
    print("=" * 60)
    print()

    # Step 1: Preferences
    preferences = create_preference_data()

    print("STEP 1: HUMAN PREFERENCES")
    print("-" * 60)
    for item in preferences:
        print(f"  Prompt: '{item['prompt']}'")
        print(f"    Response A: {item['response_A'][:50]}...")
        print(f"    Response B: {item['response_B'][:50]}...")
        print(f"    Preferred: {item['preferred']}")
        print()

    # Step 2: Reward Model
    print("STEP 2: REWARD MODEL")
    print("-" * 60)
    reward_model = SimpleRewardModel()

    for item in preferences:
        score_A = reward_model.score(item['prompt'], item['response_A'])
        score_B = reward_model.score(item['prompt'], item['response_B'])

        print(f"  Prompt: '{item['prompt']}'")
        print(f"    Score A: {score_A:.2f}")
        print(f"    Score B: {score_B:.2f}")
        print(f"    Predicted winner: {'A' if score_A > score_B else 'B'}")
        print(f"    Actual winner: {item['preferred']}")
        print(f"    Match: {'YES' if (score_A > score_B) == (item['preferred'] == 'A') else 'NO'}")
        print()

    # Step 3: PPO
    print("STEP 3: PPO UPDATE")
    print("-" * 60)
    print("  PPO prevents the policy from changing too much.")
    print()

    # Simulate PPO update
    old_prob = 0.3
    new_prob = 0.5
    reward = 2.0

    loss = ppo_update(new_prob, old_prob, reward)
    print(f"    Old probability: {old_prob}")
    print(f"    New probability: {new_prob}")
    print(f"    Ratio: {new_prob/old_prob:.2f}")
    print(f"    Reward: {reward}")
    print(f"    PPO loss: {loss:.4f}")
    print()

    # Show clipping effect
    print("  If ratio is too large (policy changed too much):")
    new_prob_big = 0.8
    loss_big = ppo_update(new_prob_big, old_prob, reward)
    print(f"    New probability: {new_prob_big}")
    print(f"    Ratio: {new_prob_big/old_prob:.2f}")
    print(f"    PPO loss (clipped): {loss_big:.4f}")
    print(f"    -> Clipping prevents extreme updates")
    print()


# ==============================================================================
# RLHF PIPELINE VISUALIZATION
# ==============================================================================

def visualize_rlhf():
    """Visualize the RLHF pipeline."""
    print("=" * 60)
    print("VISUALIZING RLHF PIPELINE")
    print("=" * 60)

    fig, ax = plt.subplots(figsize=(14, 8))

    # Title
    ax.text(0.5, 0.95, 'RLHF Pipeline', ha='center', fontsize=16,
            fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightblue'))

    # Step 1
    ax.text(0.15, 0.80, 'STEP 1:\nCollect Preferences', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightyellow'))
    ax.text(0.15, 0.70, 'Humans compare\nA vs B', ha='center', fontsize=9, style='italic')

    # Arrow
    ax.arrow(0.25, 0.75, 0.12, 0, head_width=0.03, head_length=0.02, fc='black')

    # Step 2
    ax.text(0.45, 0.80, 'STEP 2:\nTrain Reward Model', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightgreen'))
    ax.text(0.45, 0.70, 'Predicts human\npreferences', ha='center', fontsize=9, style='italic')

    # Arrow
    ax.arrow(0.55, 0.75, 0.12, 0, head_width=0.03, head_length=0.02, fc='black')

    # Step 3
    ax.text(0.75, 0.80, 'STEP 3:\nPPO Optimization', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightcoral'))
    ax.text(0.75, 0.70, 'GPT maximizes\nreward', ha='center', fontsize=9, style='italic')

    # GPT loop
    ax.text(0.75, 0.55, 'GPT Policy', ha='center', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='plum'))
    ax.arrow(0.75, 0.52, 0, -0.08, head_width=0.03, head_length=0.02, fc='black')
    ax.text(0.75, 0.38, 'Generates\nResponse', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightgray'))
    ax.arrow(0.85, 0.38, 0.08, 0.15, head_width=0.03, head_length=0.02, fc='black')
    ax.text(0.95, 0.55, 'Reward\nModel', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='wheat'))
    ax.arrow(0.88, 0.58, -0.08, 0, head_width=0.03, head_length=0.02, fc='black')
    ax.text(0.75, 0.60, 'Reward\nScore', ha='center', fontsize=8, style='italic')

    # KL penalty note
    ax.text(0.15, 0.40, 'KL Penalty:\nStay close to\noriginal GPT', ha='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='salmon'))
    ax.arrow(0.25, 0.45, 0.15, 0.08, head_width=0.03, head_length=0.02, fc='red')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/Users/zen/Desktop/building-ai/ai-miden/src/phase23/rlhf_pipeline.png', dpi=150)
    print("Plot saved to: src/phase23/rlhf_pipeline.png")
    plt.close()


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PHASE 23: RLHF")
    print("=" * 60)
    print()
    print("  Goal: Align the model with human values")
    print()

    # Demonstrate RLHF
    demonstrate_rlhf()

    # Visualize
    visualize_rlhf()

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("  WHAT WE BUILT:")
    print("    - Synthetic preference dataset")
    print("    - Simplified reward model")
    print("    - PPO update demonstration")
    print("    - RLHF pipeline visualization")
    print()
    print("  THE RLHF PIPELINE:")
    print("    1. Collect human preferences (A > B)")
    print("    2. Train reward model to predict preferences")
    print("    3. Use PPO to optimize GPT for maximum reward")
    print("    4. KL penalty keeps GPT close to original")
    print()
    print("  KEY INSIGHT:")
    print("    RLHF teaches VALUES, not facts.")
    print("    It makes the model helpful, harmless, and honest.")
    print()
    print("  LIMITATION:")
    print("    RLHF is complex (3 models), expensive, and unstable.")
    print("    Is there a simpler way?")
    print()
    print("  NEXT QUESTION:")
    print("    'RLHF needs 3 models and is unstable.")
    print("     Is there a simpler way to align models?'")
    print("=" * 60)
