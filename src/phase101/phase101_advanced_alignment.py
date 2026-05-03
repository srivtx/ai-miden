"""
Phase 101: Advanced Alignment
NumPy simulation of a critique-and-revise loop.
A model generates an answer, a critic scores it, and revision improves the score iteratively.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

np.random.seed(101)


def generate_answer(proposal_dim=10):
    """Simulate a model generating an answer vector."""
    return np.random.randn(proposal_dim)


def critic_score(proposal, target, noise_std=0.5):
    """
    Critic scores how close the proposal is to a hidden target.
    Lower score is better (distance-based).
    """
    distance = np.linalg.norm(proposal - target)
    noise = np.random.normal(0, noise_std)
    return distance + noise


def revise(proposal, target_estimate, step_size=0.3):
    """
    Revision moves the proposal toward the critic's best estimate of the target.
    """
    direction = target_estimate - proposal
    return proposal + step_size * direction


def simulate_critique_and_revise(
    n_iterations=20,
    n_debates=5,
    proposal_dim=10,
    output_dir="."
):
    """
    Run a critique-and-revise loop.
    Also simulate a simple debate: two competing proposals, critic picks the better one.
    """
    target = np.random.randn(proposal_dim)

    # --- Critique-and-Revise Loop ---
    proposal = generate_answer(proposal_dim)
    scores = []
    proposals = [proposal.copy()]

    for i in range(n_iterations):
        score = critic_score(proposal, target, noise_std=0.3)
        scores.append(score)

        # Critic provides a noisy estimate of the target direction
        target_estimate = target + np.random.normal(0, 0.5, size=proposal_dim)
        proposal = revise(proposal, target_estimate, step_size=0.3)
        proposals.append(proposal.copy())

    # --- Debate Simulation ---
    debate_scores_a = []
    debate_scores_b = []
    winners = []
    for _ in range(n_debates):
        prop_a = generate_answer(proposal_dim)
        prop_b = generate_answer(proposal_dim)
        score_a = critic_score(prop_a, target, noise_std=0.2)
        score_b = critic_score(prop_b, target, noise_std=0.2)
        debate_scores_a.append(score_a)
        debate_scores_b.append(score_b)
        winners.append("A" if score_a < score_b else "B")

    # --- Plotting ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Score over iterations
    ax = axes[0]
    ax.plot(range(1, n_iterations + 1), scores, marker="o")
    ax.set_title("Critique-and-Revise: Score Over Iterations")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Critic Score (lower is better)")
    ax.grid(True, linestyle="--", alpha=0.5)

    # Plot 2: Debate outcomes
    ax = axes[1]
    x = np.arange(n_debates)
    width = 0.35
    ax.bar(x - width/2, debate_scores_a, width, label="Proposal A")
    ax.bar(x + width/2, debate_scores_b, width, label="Proposal B")
    ax.set_title("Debate Protocol: Competing Proposals")
    ax.set_xlabel("Debate Round")
    ax.set_ylabel("Critic Score (lower is better)")
    ax.set_xticks(x)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    out_path = os.path.join(output_dir, "phase101_advanced_alignment.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot to {out_path}")

    # Print summary
    print("Phase 101 Summary:")
    print(f"  Initial score: {scores[0]:.3f}")
    print(f"  Final score:   {scores[-1]:.3f}")
    print(f"  Debate winners: {winners}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulate_critique_and_revise(output_dir=script_dir)
