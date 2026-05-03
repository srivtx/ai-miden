import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

np.random.seed(42)

# --- Toy Reasoning Chain Simulation ---
# A reasoning problem requires N steps.
# At each step, the model is correct with probability p.
# If any step is wrong, the final answer is wrong.

num_steps = 8
p_correct = 0.85
num_chains_single = 1000
num_samples_sc = 10  # self-consistency: number of chains to vote


def run_chain(num_steps, p_correct):
    steps = np.random.rand(num_steps) < p_correct
    return steps.all()


# Single chain accuracy
single_correct = np.mean([run_chain(num_steps, p_correct) for _ in range(num_chains_single)])
print(f"Single chain accuracy (p={p_correct}, {num_steps} steps): {single_correct:.3f}")

# Self-consistency: sample N chains, majority vote decides answer.
# We assume that if the majority of chains are fully correct, the vote is correct.
# More realistically, even incorrect chains might agree by chance, but we keep it simple.

def self_consistency_accuracy(num_samples, num_steps, p_correct, trials=1000):
    correct_votes = 0
    for _ in range(trials):
        outcomes = [run_chain(num_steps, p_correct) for _ in range(num_samples)]
        if np.sum(outcomes) > num_samples / 2:
            correct_votes += 1
    return correct_votes / trials


sc_accuracy = self_consistency_accuracy(num_samples_sc, num_steps, p_correct)
print(f"Self-consistency accuracy ({num_samples_sc} samples): {sc_accuracy:.3f}")

# Sweep over step probabilities
p_range = np.linspace(0.5, 0.99, 50)
single_accs = [np.mean([run_chain(num_steps, p) for _ in range(500)]) for p in p_range]
sc_accs = [self_consistency_accuracy(num_samples_sc, num_steps, p, trials=300) for p in p_range]

plt.figure(figsize=(9, 5))
plt.plot(p_range, single_accs, label='Single Chain', color='crimson', linewidth=2)
plt.plot(p_range, sc_accs, label=f'Self-Consistency (N={num_samples_sc})', color='steelblue', linewidth=2)
plt.xlabel('Per-Step Correctness Probability')
plt.ylabel('Final Answer Accuracy')
plt.title('Reasoning Accuracy: Single Chain vs Self-Consistency')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.ylim(0, 1.05)
plt.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), 'phase98_self_consistency.png')
plt.savefig(out_path)
print("Saved plot to", out_path)

# Also show how accuracy drops with more steps
step_range = range(2, 21)
single_accs_steps = [np.mean([run_chain(s, p_correct) for _ in range(500)]) for s in step_range]
sc_accs_steps = [self_consistency_accuracy(num_samples_sc, s, p_correct, trials=300) for s in step_range]

plt.figure(figsize=(9, 5))
plt.plot(step_range, single_accs_steps, label='Single Chain', marker='o', color='crimson')
plt.plot(step_range, sc_accs_steps, label=f'Self-Consistency (N={num_samples_sc})', marker='s', color='steelblue')
plt.xlabel('Number of Reasoning Steps')
plt.ylabel('Final Answer Accuracy')
plt.title('Accuracy vs Chain Length (p_correct=0.85)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.ylim(0, 1.05)
plt.tight_layout()
out_path2 = os.path.join(os.path.dirname(__file__), 'phase98_steps_vs_accuracy.png')
plt.savefig(out_path2)
print("Saved plot to", out_path2)
