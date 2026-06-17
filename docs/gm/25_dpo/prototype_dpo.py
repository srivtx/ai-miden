"""
Minimal DPO (Direct Preference Optimization).

The problem: How do you tell a model that completion A is better than
completion B? RLHF (Reinforcement Learning from Human Feedback) requires:
training a reward model, then PPO fine-tuning, then KL penalty. Complex.
DPO skips the RL entirely: convert the preference into a classification
loss directly on the policy model.

RLHF:   policy -> reward model -> PPO -> updated policy
DPO:    (good, bad) pair -> binary cross-entropy -> updated policy

  loss = -log(sigma(beta * (log P_model(good)/P_ref(good) -
                             log P_model(bad)/P_ref(bad))))

The intuition: When the model assigns higher probability to "good" than
to "bad" (relative to a reference model), the loss is low. When it
prefers "bad" over "good", the loss is high. Beta controls how far
the model can deviate from the reference.
"""

import torch
import torch.nn.functional as F


def dpo_loss(
    pi_logps_good,  # log prob of "good" completion under current model
    pi_logps_bad,  # log prob of "bad" completion under current model
    ref_logps_good,  # log prob of "good" completion under reference model
    ref_logps_bad,  # log prob of "bad" completion under reference model
    beta=0.1,
):
    """
    Direct Preference Optimization loss.

    All inputs are scalar log-probabilities (sum of log-probs over tokens).

    The core formula:
      loss = -log(sigma(beta * (log(pi_good/ref_good) - log(pi_bad/ref_bad))))
           = -log(sigma(beta * (log_ratio_good - log_ratio_bad)))

    where sigma is the sigmoid function.
    """
    pi_ratio_good = pi_logps_good - ref_logps_good
    pi_ratio_bad = pi_logps_bad - ref_logps_bad

    logits = pi_ratio_good - pi_ratio_bad
    loss = -F.logsigmoid(beta * logits)

    return loss.mean()


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DPO (Direct Preference Optimization) Demo")
    print("=" * 60)

    torch.manual_seed(42)

    # Scenario: 5 preference pairs
    # Each pair: (good_completion, bad_completion)
    # Model that ALWAYS prefers good over bad should have low loss
    # Model that is random should have high loss

    print(f"\n{'=' * 60}")
    print("Case 1: Model strongly prefers good over bad")
    print(f"{'=' * 60}")

    # Reference model: log probs for good/bad completions
    ref_good = torch.tensor([-5.0, -3.0, -8.0, -2.0, -6.0])  # 5 examples
    ref_bad = torch.tensor([-4.0, -4.0, -7.0, -3.0, -5.0])

    # Current model: much higher log-prob for good, lower for bad
    pi_good = torch.tensor([-2.0, -1.0, -3.0, -1.0, -2.0])  # improved
    pi_bad = torch.tensor([-6.0, -7.0, -12.0, -5.0, -10.0])  # worse

    loss1 = dpo_loss(pi_good, pi_bad, ref_good, ref_bad, beta=0.1)
    print(f"  Loss: {loss1.item():.6f} (low = model prefers good over bad)")

    print(f"\n{'=' * 60}")
    print("Case 2: Model prefers bad over good (wrong)")
    print(f"{'=' * 60}")

    # Current model: higher log-prob for BAD completions
    pi_good_wrong = torch.tensor([-8.0, -6.0, -12.0, -4.0, -9.0])
    pi_bad_wrong = torch.tensor([-2.0, -1.0, -4.0, -1.0, -3.0])

    loss2 = dpo_loss(pi_good_wrong, pi_bad_wrong, ref_good, ref_bad, beta=0.1)
    print(f"  Loss: {loss2.item():.6f} (high = model preferences are reversed)")

    print(f"\n{'=' * 60}")
    print("Case 3: Model is random (same prob for both)")
    print(f"{'=' * 60}")

    pi_good_rand = torch.tensor([-4.0, -4.0, -7.0, -3.0, -5.0])
    pi_bad_rand = torch.tensor([-4.0, -4.0, -7.0, -3.0, -5.0])

    loss3 = dpo_loss(pi_good_rand, pi_bad_rand, ref_good, ref_bad, beta=0.1)
    print(f"  Loss: {loss3.item():.6f} (mid = no preference signal)")

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Strong preference for good: loss={loss1.item():.4f}")
    print(f"  Strong preference for bad:  loss={loss2.item():.4f}")
    print(f"  Random (no preference):     loss={loss3.item():.4f}")

    # What beta controls
    print(f"\n{'=' * 60}")
    print("Effect of beta:")
    for b in [0.01, 0.1, 0.5, 1.0]:
        l = dpo_loss(pi_good, pi_bad, ref_good, ref_bad, beta=b)
        print(f"  beta={b:.2f}: loss={l.item():.6f}")
    print(f"\n  Smaller beta -> gentler optimization, model stays closer to ref")
    print(f"  Larger beta  -> stronger push toward preferences")

    print(f"\nKey insight: DPO trains a model to prefer 'good' completions")
    print(f"without a separate reward model or RL step. Just compute")
    print(f"log-probabilities for the good and bad completions under both")
    print(f"the current and reference model, then apply the DPO loss.")
