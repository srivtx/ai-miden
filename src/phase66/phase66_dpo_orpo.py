"""
Phase 66: DPO & ORPO Concept Demo

Demonstrates Direct Preference Optimization and Odds Ratio Preference
Optimization using only NumPy. Shows how a policy model shifts probability
mass toward chosen responses and away from rejected responses.

WHY: Before running billion-parameter models, we must understand the loss
functions that drive alignment. This script makes the math concrete.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend so scripts do not hang
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(66)

# ---------------------------------------------------------------------------
# WHY: We simulate a language model that produces logits for two possible
# completions of the same prompt: "chosen" (preferred) and "rejected" (bad).
# Instead of a full vocabulary, we use two logits to keep the demo focused
# on the loss mechanics.
# ---------------------------------------------------------------------------

# Reference model log-probabilities (frozen)
# These represent an SFT model's average log-probabilities for the two responses.
ref_log_p_chosen = -0.80
ref_log_p_rejected = -0.95

# Initial policy logits (start slightly worse than reference)
policy_dpo = np.array([0.0, 0.0], dtype=np.float64)
policy_orpo = np.array([0.0, 0.0], dtype=np.float64)

# Hyperparameters
beta = 0.5
lambda_orpo = 0.5
learning_rate = 0.3
training_steps = 150


def softmax(logits):
    """WHY: softmax turns raw scores into probabilities that sum to 1."""
    e = np.exp(logits - np.max(logits))  # subtract max for numerical stability
    return e / np.sum(e)


def sigmoid(x):
    """WHY: sigmoid squashes any real number into (0, 1)."""
    return 1.0 / (1.0 + np.exp(-x))


def compute_dpo_loss(policy_logits, ref_chosen, ref_rejected, beta):
    """
    WHY: DPO loss directly penalizes the policy when the gap between chosen
    and rejected is smaller than the reference gap. No reward model needed.

    Formula (from user specification):
    loss = -log sigmoid(beta * (log_pi_chosen - log_pi_rejected)
                               - beta * (log_ref_chosen - log_ref_rejected))
    """
    policy_log_probs = np.log(softmax(policy_logits) + 1e-10)
    pi_c = policy_log_probs[0]
    pi_r = policy_log_probs[1]

    # The DPO objective compares policy margin to reference margin
    margin_policy = pi_c - pi_r
    margin_ref = ref_chosen - ref_rejected
    diff = beta * (margin_policy - margin_ref)

    loss = -np.log(sigmoid(diff) + 1e-10)
    return loss


def compute_orpo_loss(policy_logits, lambda_orpo):
    """
    WHY: ORPO combines SFT (learn to generate chosen) with preference
    (learn to reject bad) in one loss. No reference model needed.

    Formula (from user specification):
    loss = SFT_loss - lambda * log sigmoid(odds_ratio)

    We compute odds_ratio as the log-odds difference:
    log_odds_chosen = log(p_chosen / (1 - p_chosen))
    log_odds_rejected = log(p_rejected / (1 - p_rejected))
    odds_ratio = log_odds_chosen - log_odds_rejected
    """
    probs = softmax(policy_logits)
    p_c = probs[0]
    p_r = probs[1]

    # SFT term: negative log-likelihood of the chosen response
    sft_loss = -np.log(p_c + 1e-10)

    # Odds ratio term: how much more likely is chosen than rejected
    odds_c = p_c / (1.0 - p_c + 1e-10)
    odds_r = p_r / (1.0 - p_r + 1e-10)
    log_odds_ratio = np.log(odds_c) - np.log(odds_r)

    # User-specified formula: SFT loss - lambda * log sigmoid(odds_ratio)
    # Since log(sigmoid(x)) is negative for all real x, this expression adds
    # a positive penalty that shrinks as the policy improves, pushing the model
    # to increase the odds ratio. This is exactly equivalent to the standard
    # ORPO formulation: sft_loss + lambda * (-log sigmoid(odds_ratio)).
    loss = sft_loss - lambda_orpo * np.log(sigmoid(log_odds_ratio) + 1e-10)
    return loss


def numerical_gradient(loss_fn, logits, eps=1e-5):
    """
    WHY: Finite differences let us compute gradients without manual calculus.
    For a 2-parameter demo this is simple, readable, and exact enough.
    """
    grad = np.zeros_like(logits)
    for i in range(len(logits)):
        plus = logits.copy()
        plus[i] += eps
        minus = logits.copy()
        minus[i] -= eps
        grad[i] = (loss_fn(plus) - loss_fn(minus)) / (2.0 * eps)
    return grad


# Storage for plotting
dpo_loss_hist = []
orpo_loss_hist = []
dpo_p_chosen = []
dpo_p_rejected = []
orpo_p_chosen = []
orpo_p_rejected = []

# ---------------------------------------------------------------------------
# Training loop
# WHY: We train two independent policies so we can compare DPO and ORPO
# side-by-side on identical starting points.
# ---------------------------------------------------------------------------
for step in range(training_steps):
    # ---- DPO update ----
    loss_dpo = compute_dpo_loss(
        policy_dpo, ref_log_p_chosen, ref_log_p_rejected, beta
    )
    dpo_loss_hist.append(loss_dpo)
    probs_dpo = softmax(policy_dpo)
    dpo_p_chosen.append(probs_dpo[0])
    dpo_p_rejected.append(probs_dpo[1])

    grad_dpo = numerical_gradient(
        lambda x: compute_dpo_loss(x, ref_log_p_chosen, ref_log_p_rejected, beta),
        policy_dpo,
    )
    policy_dpo -= learning_rate * grad_dpo  # gradient descent

    # ---- ORPO update ----
    loss_orpo = compute_orpo_loss(policy_orpo, lambda_orpo)
    orpo_loss_hist.append(loss_orpo)
    probs_orpo = softmax(policy_orpo)
    orpo_p_chosen.append(probs_orpo[0])
    orpo_p_rejected.append(probs_orpo[1])

    grad_orpo = numerical_gradient(
        lambda x: compute_orpo_loss(x, lambda_orpo),
        policy_orpo,
    )
    policy_orpo -= learning_rate * grad_orpo  # gradient descent

# ---------------------------------------------------------------------------
# Plotting
# WHY: Visual proof that both methods push probability mass from rejected
# toward chosen, but ORPO also enforces a minimum SFT loss.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle("Phase 66: DPO vs ORPO Probability Shift", fontsize=14)

# DPO loss curve
ax = axes[0, 0]
ax.plot(dpo_loss_hist, color="blue", linewidth=2)
ax.set_title("DPO Loss")
ax.set_xlabel("Training Step")
ax.set_ylabel("Loss")
ax.grid(True, alpha=0.3)

# ORPO loss curve
ax = axes[0, 1]
ax.plot(orpo_loss_hist, color="green", linewidth=2)
ax.set_title("ORPO Loss")
ax.set_xlabel("Training Step")
ax.set_ylabel("Loss")
ax.grid(True, alpha=0.3)

# DPO probabilities
ax = axes[1, 0]
ax.plot(dpo_p_chosen, label="Chosen", color="green", linewidth=2)
ax.plot(dpo_p_rejected, label="Rejected", color="red", linewidth=2)
ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
ax.set_title("DPO: Probability Shift")
ax.set_xlabel("Training Step")
ax.set_ylabel("Probability")
ax.legend()
ax.grid(True, alpha=0.3)

# ORPO probabilities
ax = axes[1, 1]
ax.plot(orpo_p_chosen, label="Chosen", color="green", linewidth=2)
ax.plot(orpo_p_rejected, label="Rejected", color="red", linewidth=2)
ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
ax.set_title("ORPO: Probability Shift")
ax.set_xlabel("Training Step")
ax.set_ylabel("Probability")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out_path = "src/phase66/dpo_orpo.png"
plt.savefig(out_path, dpi=150)
print(f"Saved plot to {out_path}")

# ---------------------------------------------------------------------------
# Final numeric report
# WHY: Concrete numbers prove the concept better than curves alone.
# ---------------------------------------------------------------------------
print("\n--- Final Results ---")
print(f"DPO final chosen prob:    {dpo_p_chosen[-1]:.4f}")
print(f"DPO final rejected prob:  {dpo_p_rejected[-1]:.4f}")
print(f"ORPO final chosen prob:   {orpo_p_chosen[-1]:.4f}")
print(f"ORPO final rejected prob: {orpo_p_rejected[-1]:.4f}")
