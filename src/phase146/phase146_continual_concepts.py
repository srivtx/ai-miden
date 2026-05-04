"""
Phase 146: Continual Pretraining for LLMs — Concepts
Demonstrates catastrophic forgetting and replay-buffer mitigation using NumPy.
Uses only NumPy and Matplotlib (no PyTorch) so it runs locally.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Simulation setup: three tasks with different "ideal" weight directions
# ---------------------------------------------------------------------------
# We simulate a linear model that must align its weight vector with each task.
# Task A: old knowledge (e.g., 2020 geography)
# Task B: old knowledge (e.g., 2023 APIs)
# Task C: new knowledge (e.g., 2024 medical guidelines)
# The weight vector is 2D so we can visualize it easily.

np.random.seed(146)

# Each task is defined by a target direction (unit vector).
task_A = np.array([1.0, 0.2])
task_B = np.array([0.3, 1.0])
task_C = np.array([-0.8, 0.6])

# Normalize to unit length
task_A = task_A / np.linalg.norm(task_A)
task_B = task_B / np.linalg.norm(task_B)
task_C = task_C / np.linalg.norm(task_C)

tasks = [task_A, task_B, task_C]
task_names = ['Task A (Old)', 'Task B (Old)', 'Task C (New)']

# ---------------------------------------------------------------------------
# 2. Accuracy function: cosine similarity between weights and task direction
# ---------------------------------------------------------------------------
# WHY cosine: measures alignment regardless of magnitude, matching how
# neural networks often use normalized features.

def accuracy(weights, task_vec):
    """Return accuracy between 0 and 100 based on cosine similarity."""
    w_norm = weights / (np.linalg.norm(weights) + 1e-8)
    sim = np.dot(w_norm, task_vec)
    # Map similarity [-1, 1] to [0, 100]
    return float((sim + 1) / 2 * 100)

# ---------------------------------------------------------------------------
# 3. Naive continual training: train on each task sequentially
# ---------------------------------------------------------------------------
# WHY naive first: establishes the catastrophic forgetting baseline.
# We use simple gradient descent on a mean-squared-error loss to align
# the weights with the current task vector.

learning_rate = 0.15
epochs_per_task = 30

weights_naive = np.array([0.5, 0.5], dtype=float)  # random initialization

history_naive = []  # list of (epoch, acc_A, acc_B, acc_C)

for task_idx, task_vec in enumerate(tasks):
    for epoch in range(epochs_per_task):
        # Gradient of MSE loss w.r.t. weights: -2 * (target - weights)
        grad = -2 * (task_vec - weights_naive)
        weights_naive -= learning_rate * grad

        acc_A = accuracy(weights_naive, task_A)
        acc_B = accuracy(weights_naive, task_B)
        acc_C = accuracy(weights_naive, task_C)
        history_naive.append((task_idx * epochs_per_task + epoch, acc_A, acc_B, acc_C))

history_naive = np.array(history_naive)

# ---------------------------------------------------------------------------
# 4. Continual training with replay buffer
# ---------------------------------------------------------------------------
# WHY replay works: mixing old data forces the weights to stay aligned
# with previous tasks while learning the new one.

weights_replay = np.array([0.5, 0.5], dtype=float)
history_replay = []
replay_fraction = 0.3  # 30% old tasks, 70% current task

for task_idx, task_vec in enumerate(tasks):
    for epoch in range(epochs_per_task):
        # Compute gradient for current task
        grad_current = -2 * (task_vec - weights_replay)

        # Compute gradient for replay (average over all previous tasks)
        if task_idx > 0:
            replay_tasks = tasks[:task_idx]
            grad_replay = np.mean([-2 * (t - weights_replay) for t in replay_tasks], axis=0)
        else:
            grad_replay = np.zeros_like(weights_replay)

        # Mix gradients
        grad_mixed = (1 - replay_fraction) * grad_current + replay_fraction * grad_replay
        weights_replay -= learning_rate * grad_mixed

        acc_A = accuracy(weights_replay, task_A)
        acc_B = accuracy(weights_replay, task_B)
        acc_C = accuracy(weights_replay, task_C)
        history_replay.append((task_idx * epochs_per_task + epoch, acc_A, acc_B, acc_C))

history_replay = np.array(history_replay)

# ---------------------------------------------------------------------------
# 5. Print final results
# ---------------------------------------------------------------------------
print('=' * 70)
print('Phase 146: Continual Pretraining — Catastrophic Forgetting Demo')
print('=' * 70)

print("\n--- Naive Sequential Training ---")
print(f"Final accuracy Task A: {history_naive[-1, 1]:.1f}%")
print(f"Final accuracy Task B: {history_naive[-1, 2]:.1f}%")
print(f"Final accuracy Task C: {history_naive[-1, 3]:.1f}%")
print(f"Average accuracy: {np.mean(history_naive[-1, 1:]):.1f}%")

print("\n--- Replay Buffer (30% old data) ---")
print(f"Final accuracy Task A: {history_replay[-1, 1]:.1f}%")
print(f"Final accuracy Task B: {history_replay[-1, 2]:.1f}%")
print(f"Final accuracy Task C: {history_replay[-1, 3]:.1f}%")
print(f"Average accuracy: {np.mean(history_replay[-1, 1:]):.1f}%")

# ---------------------------------------------------------------------------
# 6. Visualization 1: Accuracy over time (forgetting curves)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

epochs_naive = history_naive[:, 0]
ax.plot(epochs_naive, history_naive[:, 1], label='Task A (Old)', color='steelblue', lw=2)
ax.plot(epochs_naive, history_naive[:, 2], label='Task B (Old)', color='coral', lw=2)
ax.plot(epochs_naive, history_naive[:, 3], label='Task C (New)', color='seagreen', lw=2)

# Mark task boundaries
task_boundaries = [epochs_per_task, 2 * epochs_per_task]
for tb in task_boundaries:
    ax.axvline(tb, color='gray', linestyle='--', alpha=0.5)
    ax.text(tb + 1, 10, f'Switch to Task {"B" if tb == epochs_per_task else "C"}',
            rotation=90, va='bottom', fontsize=9, color='gray')

ax.set_xlabel('Training Epoch')
ax.set_ylabel('Accuracy (%)')
ax.set_title('Naive Continual Training: Catastrophic Forgetting')
ax.legend(loc='upper right')
ax.set_ylim(0, 105)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase146/phase146_forgetting_curve_naive.png', dpi=150)
plt.close()
print("\nSaved plot: src/phase146/phase146_forgetting_curve_naive.png")

# ---------------------------------------------------------------------------
# 7. Visualization 2: Replay buffer comparison
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

for ax_idx, (label, hist) in enumerate([('Naive', history_naive), ('Replay Buffer (30%)', history_replay)]):
    ax = axes[ax_idx]
    ax.plot(hist[:, 0], hist[:, 1], label='Task A (Old)', color='steelblue', lw=2)
    ax.plot(hist[:, 0], hist[:, 2], label='Task B (Old)', color='coral', lw=2)
    ax.plot(hist[:, 0], hist[:, 3], label='Task C (New)', color='seagreen', lw=2)
    for tb in task_boundaries:
        ax.axvline(tb, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Training Epoch')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title(label)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 105)
    ax.grid(True, alpha=0.3)

plt.suptitle('Continual Learning: Naive vs Replay Buffer', fontsize=12)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('src/phase146/phase146_replay_comparison.png', dpi=150)
plt.close()
print("Saved plot: src/phase146/phase146_replay_comparison.png")

# ---------------------------------------------------------------------------
# 8. Visualization 3: Retention bar chart (final accuracy per task)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(3)
width = 0.35
naive_final = history_naive[-1, 1:]
replay_final = history_replay[-1, 1:]

bars1 = ax.bar(x - width/2, naive_final, width, label='Naive', color='coral', edgecolor='black')
bars2 = ax.bar(x + width/2, replay_final, width, label='Replay (30%)', color='seagreen', edgecolor='black')

ax.set_ylabel('Final Accuracy (%)')
ax.set_title('Final Task Retention: Naive vs Replay')
ax.set_xticks(x)
ax.set_xticklabels(task_names)
ax.legend()
ax.set_ylim(0, 105)

for bar in bars1 + bars2:
    height = bar.get_height()
    ax.annotate(f'{height:.0f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('src/phase146/phase146_retention_bar_chart.png', dpi=150)
plt.close()
print("Saved plot: src/phase146/phase146_retention_bar_chart.png")

# ---------------------------------------------------------------------------
# 9. Visualization 4: Weight vector trajectory in 2D
# ---------------------------------------------------------------------------
# WHY visualize weights: shows geometrically why forgetting happens.
# Naive training pulls the weight vector all the way to the new task,
# abandoning previous alignments. Replay keeps it in the middle.

fig, ax = plt.subplots(figsize=(7, 7))

# Plot task directions as arrows from origin
for tvec, name, color in zip(tasks, task_names, ['steelblue', 'coral', 'seagreen']):
    ax.annotate('', xy=(tvec[0], tvec[1]), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=color, lw=3))
    ax.text(tvec[0]*1.15, tvec[1]*1.15, name, color=color, fontsize=10, fontweight='bold')

# We will re-run a lightweight version to capture weight trajectories
weights = np.array([0.5, 0.5], dtype=float)
naive_traj = [weights.copy()]
for task_idx, task_vec in enumerate(tasks):
    for _ in range(epochs_per_task):
        grad = -2 * (task_vec - weights)
        weights -= learning_rate * grad
        naive_traj.append(weights.copy())
naive_traj = np.array(naive_traj)

weights = np.array([0.5, 0.5], dtype=float)
replay_traj = [weights.copy()]
for task_idx, task_vec in enumerate(tasks):
    for _ in range(epochs_per_task):
        grad_current = -2 * (task_vec - weights)
        if task_idx > 0:
            replay_tasks = tasks[:task_idx]
            grad_replay = np.mean([-2 * (t - weights) for t in replay_tasks], axis=0)
        else:
            grad_replay = np.zeros_like(weights)
        grad_mixed = (1 - replay_fraction) * grad_current + replay_fraction * grad_replay
        weights -= learning_rate * grad_mixed
        replay_traj.append(weights.copy())
replay_traj = np.array(replay_traj)

ax.plot(naive_traj[:, 0], naive_traj[:, 1], 'o-', color='coral', markersize=3, label='Naive trajectory')
ax.plot(replay_traj[:, 0], replay_traj[:, 1], 's-', color='seagreen', markersize=3, label='Replay trajectory')

ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axhline(0, color='black', lw=0.5)
ax.axvline(0, color='black', lw=0.5)
ax.set_aspect('equal')
ax.set_title('Weight Vector Trajectory: Naive vs Replay')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase146/phase146_weight_trajectory.png', dpi=150)
plt.close()
print("Saved plot: src/phase146/phase146_weight_trajectory.png")

print("\nPhase 146 concept demonstration complete.")
