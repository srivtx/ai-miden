"""
Phase 117: Data Mixing Laws and Curriculum Learning
NumPy simulation of three domains with different difficulty and information content.

We compare three training strategies:
1. Uniform mixing   — equal exposure to all domains every step.
2. Optimal mixing   — DoReMi-style fixed reweighting toward harder domains.
3. Curriculum       — easy data first, then medium, then hard.

Every line explains WHY we chose that parameter or equation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend so scripts do not block in headless environments.
import matplotlib.pyplot as plt

np.random.seed(117)

# -----------------------------------------------------------------------------
# Domain definitions
# -----------------------------------------------------------------------------
# Each domain has:
#   init  — loss at step 0 (higher = harder to learn from scratch)
#   floor — theoretical minimum loss after infinite exposure
#   alpha — learning speed (how fast exposure drives loss toward floor)
#
# Hard domains have higher init and floor, but also the most headroom for
# improvement.  Data mixing laws say we should overweight them because the
# marginal utility per token is larger.
DOMAINS = {
    'Easy':   {'init': 2.0, 'floor': 1.0, 'alpha': 0.05},
    'Medium': {'init': 3.5, 'floor': 1.5, 'alpha': 0.03},
    'Hard':   {'init': 5.0, 'floor': 2.0, 'alpha': 0.02},
}

N_STEPS = 300  # Enough steps to see curvature and final separation.


def run_schedule(weights_schedule):
    """
    Simulate training given a per-step weight vector for each domain.

    The model's loss on domain d at step t is driven by cumulative exposure.
    We use exponential decay toward a floor: more exposure → lower loss.
    If exposure stops, we apply a tiny forgetting drift so that stopping
    easy data to focus on hard data has a real (but small) cost.
    """
    losses = {d: np.zeros(N_STEPS) for d in DOMAINS}
    exposure = {d: 0.0 for d in DOMAINS}  # Running sum of weights received.

    for t in range(N_STEPS):
        for d, params in DOMAINS.items():
            # Exponential decay: loss = floor + (init - floor) * exp(-alpha * exposure)
            loss = params['floor'] + (params['init'] - params['floor']) * np.exp(-params['alpha'] * exposure[d])
            # Tiny Gaussian noise so curves look like real SGD, not sterile math.
            loss += np.random.randn() * 0.02
            losses[d][t] = loss

            # Today's weight adds to tomorrow's cumulative exposure.
            exposure[d] += weights_schedule[d][t]

            # Forgetting drift: if a domain is starved (weight < 0.05),
            # slowly erode its exposure so the loss creeps back up slightly.
            if weights_schedule[d][t] < 0.05:
                exposure[d] = max(0.0, exposure[d] - 0.01)

    return losses


def main():
    # -------------------------------------------------------------------------
    # 1. Uniform mixing — the naive baseline.
    # -------------------------------------------------------------------------
    uniform = {d: np.full(N_STEPS, 1.0 / 3.0) for d in DOMAINS}
    loss_uniform = run_schedule(uniform)

    # -------------------------------------------------------------------------
    # 2. Optimal mixing — hand-crafted to mimic what DoReMi discovers.
    #    Harder domains get more weight because they improve more per token.
    # -------------------------------------------------------------------------
    optimal = {
        'Easy':   np.full(N_STEPS, 0.15),  # Easy domain saturates fast; extra tokens are wasted.
        'Medium': np.full(N_STEPS, 0.30),  # Moderate headroom needs moderate weight.
        'Hard':   np.full(N_STEPS, 0.55),  # Hard domain has the most room to improve.
    }
    loss_optimal = run_schedule(optimal)

    # -------------------------------------------------------------------------
    # 3. Curriculum learning — schedule difficulty over time.
    #    Phase 1: mostly easy (stable gradients, foundation building).
    #    Phase 2: shift to medium (introduce complexity gradually).
    #    Phase 3: mostly hard (refine on the hardest material).
    # -------------------------------------------------------------------------
    curriculum = {d: np.zeros(N_STEPS) for d in DOMAINS}
    third = N_STEPS // 3

    curriculum['Easy'][:third]       = 0.85
    curriculum['Easy'][third:2*third] = 0.10
    curriculum['Easy'][2*third:]     = 0.05

    curriculum['Medium'][:third]       = 0.15
    curriculum['Medium'][third:2*third] = 0.60
    curriculum['Medium'][2*third:]     = 0.20

    curriculum['Hard'][:third]       = 0.00  # Hard data is withheld early to avoid noisy gradients.
    curriculum['Hard'][third:2*third] = 0.30
    curriculum['Hard'][2*third:]     = 0.75

    loss_curriculum = run_schedule(curriculum)

    # -------------------------------------------------------------------------
    # Print final numbers so the user sees the quantitative comparison.
    # -------------------------------------------------------------------------
    print(f"Final losses after {N_STEPS} steps:")
    for d in DOMAINS:
        print(f"  {d:6s} — Uniform: {loss_uniform[d][-1]:.3f} | "
              f"Optimal: {loss_optimal[d][-1]:.3f} | "
              f"Curriculum: {loss_curriculum[d][-1]:.3f}")

    # -------------------------------------------------------------------------
    # Plot 1: Loss curves per domain, one subplot per strategy.
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    colors = {'Easy': 'green', 'Medium': 'orange', 'Hard': 'red'}
    strategies = [
        ('Uniform', loss_uniform),
        ('Optimal (DoReMi-style)', loss_optimal),
        ('Curriculum', loss_curriculum),
    ]
    for ax, (name, losses) in zip(axes, strategies):
        for d in DOMAINS:
            ax.plot(losses[d], label=d, color=colors[d], alpha=0.8)
        ax.set_title(f'{name} Mixing')
        ax.set_xlabel('Training Step')
        ax.set_ylabel('Domain Loss')
        ax.legend()
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('src/phase117/mixing_comparison.png')
    print("Saved src/phase117/mixing_comparison.png")

    # -------------------------------------------------------------------------
    # Plot 2: Curriculum weight evolution.
    #    Shows the reader exactly when each domain enters the mix.
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    steps = np.arange(N_STEPS)
    for d in DOMAINS:
        ax.plot(steps, curriculum[d], label=f'{d} (Curriculum)', color=colors[d], linewidth=2)
    ax.set_title('Curriculum Learning: Domain Weight Evolution')
    ax.set_xlabel('Training Step')
    ax.set_ylabel('Sampling Weight')
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('src/phase117/mixing_weights.png')
    print("Saved src/phase117/mixing_weights.png")

    # -------------------------------------------------------------------------
    # Plot 3: Capability gaps — bar chart of final loss per domain.
    #    A gap is a domain where loss is still high relative to the floor.
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(DOMAINS))
    width = 0.25
    for i, (name, losses) in enumerate(strategies):
        vals = [losses[d][-1] for d in DOMAINS]
        offset = (i - 1) * width  # center the groups
        ax.bar(x + offset, vals, width, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(list(DOMAINS.keys()))
    ax.set_ylabel('Final Loss')
    ax.set_title('Capability Gaps: Final Loss by Domain and Strategy')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    fig.tight_layout()
    fig.savefig('src/phase117/capability_gaps.png')
    print("Saved src/phase117/capability_gaps.png")


if __name__ == '__main__':
    main()
