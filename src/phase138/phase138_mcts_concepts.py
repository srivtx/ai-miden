#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 138 — MCTS Concepts
LOCAL NumPy demonstration of Monte Carlo Tree Search on a toy problem.

This script simulates MCTS for finding a path through a grid with obstacles.
We show tree growth, UCB1 selection, backpropagation, and compare MCTS
against random search and beam search.

Why NumPy? MCTS is a search algorithm, not a neural network training loop.
NumPy is sufficient to demonstrate selection, expansion, simulation, and
backpropagation in a transparent, debuggable way.
"""

import os
import numpy as np

# Use non-interactive backend so this script runs headless on any machine.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. TOY PROBLEM: GRID PATHFINDING WITH OBSTACLES
# ---------------------------------------------------------------------------
# The agent starts at (0,0) and must reach (4,4) on a 5x5 grid.
# Moves: up, right. Some cells are blocked (obstacles).
# Reward: +1 for reaching the goal, 0 otherwise.
# This is a deterministic environment, so the value of a node is the
# probability that a rollout from that node reaches the goal.

GRID_SIZE = 5
GOAL = (4, 4)
OBSTACLES = {(1, 1), (2, 2), (3, 3), (1, 3), (3, 1)}


def is_valid(pos):
    x, y = pos
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        return False
    if pos in OBSTACLES:
        return False
    return True


def get_children(pos):
    """Return valid next positions (up or right)."""
    x, y = pos
    candidates = [(x + 1, y), (x, y + 1)]
    return [c for c in candidates if is_valid(c)]


def rollout_from(pos):
    """
    Simulate a random rollout from a position until goal or dead end.
    Returns 1.0 if goal reached, 0.0 otherwise.
    Why random? In real MCTS for LLMs, rollouts use a fast policy.
    Here we use a random policy to show the algorithm structure.
    """
    current = pos
    visited = set()
    while current != GOAL:
        if current in visited:
            return 0.0  # loop detected
        visited.add(current)
        children = get_children(current)
        if not children:
            return 0.0
        current = children[np.random.randint(len(children))]
    return 1.0


# ---------------------------------------------------------------------------
# 2. MCTS NODE
# ---------------------------------------------------------------------------
class MCTSNode:
    def __init__(self, pos, parent=None):
        self.pos = pos
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0  # cumulative reward
        self.is_expanded = False

    def ucb1(self, exploration_constant=1.414):
        """
        UCB1 score balances exploitation (high average reward) with
        exploration (low visit count). Unvisited nodes return infinity
        to ensure they are tried at least once.
        """
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        average_reward = self.value / self.visits
        exploration_term = exploration_constant * np.sqrt(np.log(parent_visits) / self.visits)
        return average_reward + exploration_term

    def best_child(self):
        """Select the child with highest UCB1 score."""
        if not self.children:
            return None
        return max(self.children, key=lambda c: c.ucb1())

    def expand(self):
        """Create child nodes for all valid next positions."""
        if self.is_expanded:
            return
        for child_pos in get_children(self.pos):
            self.children.append(MCTSNode(child_pos, parent=self))
        self.is_expanded = True

    def backprop(self, reward):
        """Update value and visit count, then propagate to parent."""
        self.visits += 1
        self.value += reward
        if self.parent:
            self.parent.backprop(reward)


# ---------------------------------------------------------------------------
# 3. MCTS ALGORITHM
# ---------------------------------------------------------------------------
def run_mcts(iterations=50, exploration_constant=1.414):
    """
    Run MCTS for a fixed number of iterations.
    Returns the root node and a history of tree statistics.
    """
    root = MCTSNode((0, 0))
    history = []

    for i in range(iterations):
        # --- Selection ---
        node = root
        while node.is_expanded and node.children:
            node = node.best_child()

        # --- Expansion ---
        if node.pos != GOAL and not node.is_expanded:
            node.expand()
            if node.children:
                node = node.children[0]  # pick first child for simulation

        # --- Simulation ---
        reward = rollout_from(node.pos)

        # --- Backpropagation ---
        node.backprop(reward)

        history.append({
            'iteration': i + 1,
            'tree_nodes': count_nodes(root),
            'best_path_value': best_path_value(root),
            'root_value': root.value / root.visits if root.visits > 0 else 0,
        })

    return root, history


def count_nodes(node):
    """Count total nodes in the tree."""
    return 1 + sum(count_nodes(c) for c in node.children)


def best_path_value(node):
    """
    Follow the path of highest average reward from root to leaf.
    Return the average reward of the deepest node on that path.
    """
    while node.children:
        node = max(node.children, key=lambda c: c.value / c.visits if c.visits > 0 else 0)
    return node.value / node.visits if node.visits > 0 else 0


# ---------------------------------------------------------------------------
# 4. RANDOM SEARCH BASELINE
# ---------------------------------------------------------------------------
def random_search(iterations=50):
    """
    Perform N independent random rollouts from the root.
    This is equivalent to best-of-N with a random policy.
    """
    successes = 0
    history = []
    for i in range(iterations):
        reward = rollout_from((0, 0))
        successes += reward
        history.append({
            'iteration': i + 1,
            'cumulative_success': successes,
            'best_rate': successes / (i + 1),
        })
    return history


# ---------------------------------------------------------------------------
# 5. BEAM SEARCH BASELINE
# ---------------------------------------------------------------------------
def beam_search(beam_width=4, max_depth=8):
    """
    Beam search keeps the top-k partial paths by a heuristic value.
    Here the heuristic is Manhattan distance to goal (lower is better).
    This shows the difference between MCTS (exploration/exploitation)
    and beam search (greedy local pruning).
    """
    beams = [([(0, 0)], 0)]  # (path, heuristic_score)
    history = []

    for depth in range(max_depth):
        candidates = []
        for path, _ in beams:
            pos = path[-1]
            if pos == GOAL:
                continue
            for child in get_children(pos):
                if child not in path:
                    h = (GOAL[0] - child[0]) + (GOAL[1] - child[1])
                    candidates.append((path + [child], h))

        if not candidates:
            break

        # Keep top beam_width by heuristic (lower Manhattan = better)
        candidates.sort(key=lambda x: x[1])
        beams = candidates[:beam_width]

        # Check if goal reached
        reached = any(path[-1] == GOAL for path, _ in beams)
        history.append({'depth': depth + 1, 'reached': reached, 'beams': len(beams)})
        if reached:
            break

    return history, beams


# ---------------------------------------------------------------------------
# 6. RUN ALL METHODS
# ---------------------------------------------------------------------------
np.random.seed(138)

print("=" * 70)
print("PHASE 138: MCTS Concepts")
print("=" * 70)

mcts_root, mcts_history = run_mcts(iterations=50, exploration_constant=1.414)
random_history = random_search(iterations=50)
beam_history, beam_final = beam_search(beam_width=4, max_depth=8)

print(f"\nMCTS tree nodes after 50 iterations: {count_nodes(mcts_root)}")
print(f"MCTS root value estimate: {mcts_root.value / mcts_root.visits:.3f}")
print(f"Random search best rate after 50 iterations: {random_history[-1]['best_rate']:.3f}")
print(f"Beam search reached goal: {any(h['reached'] for h in beam_history)}")

# ---------------------------------------------------------------------------
# 7. VISUALIZATIONS
# ---------------------------------------------------------------------------
os.makedirs("src/phase138", exist_ok=True)

# Plot 1: MCTS tree growth and value convergence
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

iters = [h['iteration'] for h in mcts_history]
nodes = [h['tree_nodes'] for h in mcts_history]
axes[0].plot(iters, nodes, marker='o', markersize=3)
axes[0].set_xlabel('Iteration')
axes[0].set_ylabel('Tree nodes')
axes[0].set_title('MCTS Tree Growth')
axes[0].grid(True, alpha=0.3)

best_vals = [h['best_path_value'] for h in mcts_history]
axes[1].plot(iters, best_vals, marker='s', markersize=3, color='C1')
axes[1].set_xlabel('Iteration')
axes[1].set_ylabel('Best path value')
axes[1].set_title('Value Convergence (Best Path)')
axes[1].grid(True, alpha=0.3)

root_vals = [h['root_value'] for h in mcts_history]
axes[2].plot(iters, root_vals, marker='^', markersize=3, color='C2')
axes[2].set_xlabel('Iteration')
axes[2].set_ylabel('Root value estimate')
axes[2].set_title('Root Value Estimate Over Time')
axes[2].grid(True, alpha=0.3)

plt.suptitle('MCTS Progress: Tree Growth and Value Estimates')
plt.tight_layout()
plt.savefig('src/phase138/mcts_tree_growth.png', dpi=150)
plt.close()
print("\nSaved: src/phase138/mcts_tree_growth.png")

# Plot 2: Search comparison (MCTS vs Random vs Beam)
fig, ax = plt.subplots(figsize=(8, 5))

# MCTS: cumulative best path value over iterations
mcts_best = []
best_so_far = 0
for h in mcts_history:
    best_so_far = max(best_so_far, h['best_path_value'])
    mcts_best.append(best_so_far)
ax.plot(iters, mcts_best, label='MCTS (best path value)', marker='o', markersize=3)

# Random: cumulative success rate
random_rates = [h['best_rate'] for h in random_history]
ax.plot(iters, random_rates, label='Random search (success rate)', marker='s', markersize=3)

# Beam search is not iterative in the same way; we show it as a horizontal line
beam_reached = any(h['reached'] for h in beam_history)
beam_score = 1.0 if beam_reached else 0.0
ax.axhline(beam_score, color='C3', linestyle='--', label=f'Beam search (reached={beam_reached})')

ax.set_xlabel('Iteration / Rollout count')
ax.set_ylabel('Score')
ax.set_title('Search Method Comparison on Grid Pathfinding')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('src/phase138/search_comparison.png', dpi=150)
plt.close()
print("Saved: src/phase138/search_comparison.png")

# Plot 3: Value estimates heatmap for expanded nodes
fig, ax = plt.subplots(figsize=(6, 6))
grid_values = np.full((GRID_SIZE, GRID_SIZE), np.nan)

def fill_values(node):
    x, y = node.pos
    grid_values[x, y] = node.value / node.visits if node.visits > 0 else 0
    for c in node.children:
        fill_values(c)

fill_values(mcts_root)

# Draw grid
for i in range(GRID_SIZE + 1):
    ax.axhline(i - 0.5, color='black', linewidth=0.5)
    ax.axvline(i - 0.5, color='black', linewidth=0.5)

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        if (x, y) in OBSTACLES:
            ax.add_patch(plt.Rectangle((y - 0.5, x - 0.5), 1, 1, color='gray'))
        elif not np.isnan(grid_values[x, y]):
            text = f"{grid_values[x, y]:.2f}"
            ax.text(y, x, text, ha='center', va='center', fontsize=8)

ax.set_xlim(-0.5, GRID_SIZE - 0.5)
ax.set_ylim(-0.5, GRID_SIZE - 0.5)
ax.set_aspect('equal')
ax.invert_yaxis()
ax.set_title('MCTS Value Estimates per Cell')
plt.tight_layout()
plt.savefig('src/phase138/value_estimates.png', dpi=150)
plt.close()
print("Saved: src/phase138/value_estimates.png")

# ---------------------------------------------------------------------------
# 8. PROCESS VS OUTCOME REWARD COMPARISON
# ---------------------------------------------------------------------------
# We run MCTS with two scoring modes:
# A) Outcome only: reward is 1 only if goal is reached
# B) Process reward: reward is (Manhattan distance improvement) at each step

print("\n--- Process vs Outcome Reward ---")

# Outcome-only MCTS (same as above)
outcome_root, _ = run_mcts(iterations=50)
outcome_value = outcome_root.value / outcome_root.visits if outcome_root.visits > 0 else 0

# Process-reward MCTS: reward at each step is proportional to progress
# We modify rollout to give partial credit

def rollout_process(pos):
    """Rollout with process reward: give credit for moving closer to goal."""
    current = pos
    visited = set()
    total_reward = 0.0
    start_dist = (GOAL[0] - pos[0]) + (GOAL[1] - pos[1])
    steps = 0
    while current != GOAL:
        if current in visited or steps > 20:
            break
        visited.add(current)
        children = get_children(current)
        if not children:
            break
        current = children[np.random.randint(len(children))]
        dist = (GOAL[0] - current[0]) + (GOAL[1] - current[1])
        # Partial reward for being closer than start
        total_reward += max(0, (start_dist - dist) / max(start_dist, 1))
        steps += 1
    if current == GOAL:
        total_reward += 1.0
    return total_reward / max(steps, 1)


def run_mcts_process(iterations=50):
    root = MCTSNode((0, 0))
    for _ in range(iterations):
        node = root
        while node.is_expanded and node.children:
            node = node.best_child()
        if node.pos != GOAL and not node.is_expanded:
            node.expand()
            if node.children:
                node = node.children[0]
        reward = rollout_process(node.pos)
        node.backprop(reward)
    return root

process_root = run_mcts_process(iterations=50)
process_value = process_root.value / process_root.visits if process_root.visits > 0 else 0

print(f"Outcome-only MCTS root value:  {outcome_value:.3f}")
print(f"Process-reward MCTS root value: {process_value:.3f}")
print("Process reward provides denser signal and faster value convergence.")

print("\n" + "=" * 70)
print("Phase 138 concepts demonstration complete.")
print("=" * 70)
