# FRONTIER TRACK: Phase 128 — Safety RLHF Concepts
# LOCAL NumPy concept demonstration
# WHY: NumPy makes policy shift from rejection sampling transparent.

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# WHY: Reproducibility matters for educational demos.
np.random.seed(128)

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
N_PROMPTS = 100
RESPONSES_PER_PROMPT = 5
N_HARMFUL = 50
N_BENIGN = 50
N_TRAIN_EPOCHS = 100
LR = 0.2

# Prompt types: 0 = harmful, 1 = benign
prompt_types = np.array([0] * N_HARMFUL + [1] * N_BENIGN)

# Policy logits for each prompt type
# logits[prompt_type, response] where response 0=comply, 1=refuse
logits = np.zeros((2, 2))
# WHY: Start with a slight bias toward comply for both.
logits[:, 0] = 0.5  # comply
logits[:, 1] = 0.3  # refuse


def sample_response(prompt_type, n=1):
    """Sample responses from the current policy."""
    probs = np.exp(logits[prompt_type] - np.max(logits[prompt_type]))
    probs /= probs.sum()
    return np.random.choice(2, size=n, p=probs)


def compute_reward(prompt_type, response):
    """
    WHY: Harmful + refuse is safe (+1).
    Harmful + comply is unsafe (-1).
    Benign + comply is helpful (+1).
    Benign + refuse is unhelpful (-1).
    """
    if prompt_type == 0:  # harmful
        return 1.0 if response == 1 else -1.0
    else:  # benign
        return 1.0 if response == 0 else -1.0


def evaluate_policy():
    """Return safety rate and helpfulness rate."""
    h_probs = np.exp(logits[0] - np.max(logits[0]))
    h_probs /= h_probs.sum()
    safety = h_probs[1]

    b_probs = np.exp(logits[1] - np.max(logits[1]))
    b_probs /= b_probs.sum()
    helpfulness = b_probs[0]
    return safety, helpfulness


# Track metrics
safety_rates = []
helpfulness_rates = []
logits_harmful_history = []
logits_benign_history = []

# Baseline
s0, h0 = evaluate_policy()
safety_rates.append(s0)
helpfulness_rates.append(h0)
logits_harmful_history.append(logits[0].copy())
logits_benign_history.append(logits[1].copy())

print(f"Baseline: safety={s0:.2%}, helpfulness={h0:.2%}")

# ---------------------------------------------------------------------------
# REJECTION SAMPLING + SFT TRAINING
# WHY: Generate multiple responses, keep only safe/helpful ones,
# and update policy toward the kept distribution.
# ---------------------------------------------------------------------------
for epoch in range(N_TRAIN_EPOCHS):
    kept_harmful = []
    kept_benign = []

    for pt in prompt_types:
        responses = sample_response(pt, n=RESPONSES_PER_PROMPT)
        for r in responses:
            reward = compute_reward(pt, r)
            if reward > 0:
                if pt == 0:
                    kept_harmful.append(r)
                else:
                    kept_benign.append(r)

    # Update policy via gradient descent on kept counts
    for pt, kept in enumerate([kept_harmful, kept_benign]):
        if len(kept) == 0:
            continue
        probs = np.exp(logits[pt] - np.max(logits[pt]))
        probs /= probs.sum()
        counts = np.bincount(kept, minlength=2)
        target_probs = counts / counts.sum()
        grad = probs - target_probs
        logits[pt] -= LR * grad

    s, h = evaluate_policy()
    safety_rates.append(s)
    helpfulness_rates.append(h)
    logits_harmful_history.append(logits[0].copy())
    logits_benign_history.append(logits[1].copy())

    if epoch % 20 == 0:
        print(f"Epoch {epoch}: safety={s:.2%}, helpfulness={h:.2%}")

print(f"\nFinal: safety={safety_rates[-1]:.2%}, helpfulness={helpfulness_rates[-1]:.2%}")

# ---------------------------------------------------------------------------
# PLOTTING
# WHY: Humans learn from curves. We show the trade-off explicitly.
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Safety vs Helpfulness over epochs
ax = axes[0, 0]
ax.plot(safety_rates, color='crimson', linewidth=2, label='Safety (refuse harmful)')
ax.plot(helpfulness_rates, color='steelblue', linewidth=2, label='Helpfulness (comply benign)')
ax.set_title('Safety vs Helpfulness Trade-off')
ax.set_xlabel('Training Epoch')
ax.set_ylabel('Rate')
ax.set_ylim(0, 1)
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Policy logits for harmful prompts
ax = axes[0, 1]
logits_harmful_arr = np.array(logits_harmful_history)
ax.plot(logits_harmful_arr[:, 0], color='orange', label='Comply logit')
ax.plot(logits_harmful_arr[:, 1], color='crimson', label='Refuse logit')
ax.set_title('Policy Evolution: Harmful Prompts')
ax.set_xlabel('Epoch')
ax.set_ylabel('Logit')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Policy logits for benign prompts
ax = axes[1, 0]
logits_benign_arr = np.array(logits_benign_history)
ax.plot(logits_benign_arr[:, 0], color='forestgreen', label='Comply logit')
ax.plot(logits_benign_arr[:, 1], color='steelblue', label='Refuse logit')
ax.set_title('Policy Evolution: Benign Prompts')
ax.set_xlabel('Epoch')
ax.set_ylabel('Logit')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Scatter trade-off
ax = axes[1, 1]
sc = ax.scatter(helpfulness_rates, safety_rates, c=range(len(safety_rates)), cmap='viridis', s=30)
ax.set_title('Safety-Helpfulness Pareto Frontier')
ax.set_xlabel('Helpfulness Rate')
ax.set_ylabel('Safety Rate')
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.plot([0, 1], [1, 0], 'k--', alpha=0.3, label='Ideal diagonal')
ax.legend()
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label('Epoch')

plt.tight_layout()
plt.savefig('src/phase128/safety_training_concepts.png', dpi=150)
plt.close()

print("\nPlot saved to src/phase128/safety_training_concepts.png")

# ---------------------------------------------------------------------------
# FINAL INSIGHT
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("KEY INSIGHT: Rejection sampling shifts the policy toward the")
print("safe region by fine-tuning only on responses that passed the")
print("safety filter. The trade-off is visible: as safety rises,")
print("helpfulness may dip slightly because the model becomes more")
print("cautious overall. The Pareto frontier shows the optimal")
print("balance between the two objectives.")
print("=" * 60)
