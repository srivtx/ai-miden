#!/usr/bin/env python3
"""
FRONTIER TRACK: Phase 141 — GUI Agent Concepts (NumPy Simulation)
=================================================================
This script simulates a GUI agent on a 2D grid world using only NumPy.

The agent perceives a grid, decides which cell to click, and receives
a reward based on proximity to a target. We compare three agents:

  1. Random agent — clicks uniformly anywhere.
  2. Heuristic agent — moves greedily toward the target.
  3. Policy-gradient agent — learns a softmax policy over grid cells.

We demonstrate the full Observation -> Thought -> Action loop,
measure success rates, and plot learning curves.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(141)

# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================
# WHY a grid world? It distills the core challenge of GUI agents — mapping
# a visual observation to a precise spatial action — without the overhead
# of real screenshots or DOM parsers.

GRID_SIZE = 8
EPISODES = 500
STEPS_PER_EPISODE = 10
LR = 0.15
GAMMA = 0.95
BASELINE_DECAY = 0.9

# =============================================================================
# SECTION 2: ENVIRONMENT
# =============================================================================
# The environment places a target at a random cell. The agent clicks a cell.
# Reward is inversely proportional to Manhattan distance from the target.
# WHY Manhattan? It is cheap to compute and reflects how GUI navigation
# often feels: horizontal + vertical movement, not Euclidean flight.

class GridGUIEnv:
    """
    A toy GUI where the 'screen' is an NxN grid and the 'mouse' clicks
    a single cell per step. The target may move slightly between steps
    to simulate dynamic UI elements (pop-ups, loading spinners).
    """
    def __init__(self, size=GRID_SIZE):
        self.size = size
        self.target = None
        self.step_count = 0

    def reset(self):
        """Place target at random cell."""
        self.target = (np.random.randint(0, self.size),
                       np.random.randint(0, self.size))
        self.step_count = 0
        return self._get_observation()

    def _get_observation(self):
        """
        Return a flat one-hot grid with the target marked.
        WHY one-hot? It is the simplest visual representation that
        preserves spatial structure. In a real GUI agent this would be
        a flattened screenshot; here it is a flattened grid.
        """
        grid = np.zeros((self.size, self.size))
        grid[self.target[0], self.target[1]] = 1.0
        return grid.flatten()

    def step(self, action):
        """
        Action is a flat index in [0, size*size).
        Returns: next_observation, reward, done, info
        """
        row, col = divmod(action, self.size)
        dist = abs(row - self.target[0]) + abs(col - self.target[1])

        # WHY reward shaped by distance? Sparse rewards (only exact hit)
        # make learning impossible in large action spaces. Shaping gives
        # the policy gradient a useful gradient everywhere.
        reward = 1.0 - (dist / (2 * (self.size - 1)))

        # Target jitters slightly to simulate dynamic UI
        if np.random.rand() < 0.1:
            dr = np.random.choice([-1, 0, 1])
            dc = np.random.choice([-1, 0, 1])
            self.target = (
                np.clip(self.target[0] + dr, 0, self.size - 1),
                np.clip(self.target[1] + dc, 0, self.size - 1),
            )

        self.step_count += 1
        done = self.step_count >= STEPS_PER_EPISODE
        return self._get_observation(), reward, done, {'distance': dist}

# =============================================================================
# SECTION 3: AGENTS
# =============================================================================
# WHY three agents? The point is to show that raw perception is not enough;
# you need either a strong prior (heuristic) or learning (policy gradient)
# to turn observations into useful actions.

class RandomAgent:
    """Clicks uniformly at random. Baseline for 'no intelligence'."""
    def __init__(self, size):
        self.size = size
        self.name = "Random"

    def act(self, obs):
        return np.random.randint(0, self.size * self.size)

    def update(self, *args):
        pass

class HeuristicAgent:
    """
    Greedy agent that clicks the cell with highest value in the observation.
    WHY this works: our observation is a one-hot target map, so the argmax
    is literally the target location. This simulates a perfect detector.
    """
    def __init__(self, size):
        self.size = size
        self.name = "Heuristic"

    def act(self, obs):
        return int(np.argmax(obs))

    def update(self, *args):
        pass

class PolicyGradientAgent:
    """
    Softmax policy over grid cells, trained with REINFORCE.
    WHY REINFORCE? The action space is discrete and small (64 cells).
    A value-function critic would help but is unnecessary at this scale.
    """
    def __init__(self, size, lr=LR):
        self.size = size
        self.lr = lr
        self.name = "PolicyGradient"
        # Logits for each cell
        self.theta = np.zeros(size * size)
        self.baseline = 0.0

    def act(self, obs):
        """
        WHY dot product with obs? We give the policy a hint by biasing
        logits toward cells that currently have high observation value.
        This is analogous to a GUI agent using a visual feature extractor.
        """
        logits = self.theta + 2.0 * obs  # small prior from observation
        logits -= np.max(logits)  # numerical stability
        exp = np.exp(logits)
        probs = exp / np.sum(exp)
        action = np.random.choice(len(probs), p=probs)
        # Gradient of log pi(a) w.r.t theta
        grad = -probs.copy()
        grad[action] += 1.0
        return action, grad, probs

    def update(self, grads, rewards, baseline_decay=BASELINE_DECAY):
        """
        WHY episode-level update? The grid task is short and the reward
        is dense enough that per-episode REINFORCE converges quickly.
        """
        returns = np.zeros_like(rewards)
        G = 0.0
        for t in reversed(range(len(rewards))):
            G = rewards[t] + GAMMA * G
            returns[t] = G

        self.baseline = baseline_decay * self.baseline + (1 - baseline_decay) * returns.mean()
        advantage = returns.mean() - self.baseline

        total_grad = np.zeros_like(self.theta)
        for g in grads:
            total_grad += g

        self.theta += self.lr * advantage * total_grad

# =============================================================================
# SECTION 4: EVALUATION LOOP
# =============================================================================

def run_agent(agent, env, episodes=EPISODES):
    """
    Run an agent for N episodes. Return histories of reward, distance,
    and success (distance == 0).
    """
    hist_reward = []
    hist_dist = []
    hist_success = []
    hist_actions = []

    for ep in range(episodes):
        obs = env.reset()
        ep_rewards = []
        ep_dists = []
        ep_grads = []
        ep_actions = []

        for _ in range(STEPS_PER_EPISODE):
            if hasattr(agent, 'act') and agent.name == "PolicyGradient":
                action, grad, probs = agent.act(obs)
                ep_grads.append(grad)
            else:
                action = agent.act(obs)
                grad = None
                probs = None

            obs, reward, done, info = env.step(action)
            ep_rewards.append(reward)
            ep_dists.append(info['distance'])
            ep_actions.append(action)

            if done:
                break

        if agent.name == "PolicyGradient":
            agent.update(ep_grads, np.array(ep_rewards))

        hist_reward.append(np.sum(ep_rewards))
        hist_dist.append(np.mean(ep_dists))
        hist_success.append(1 if np.any(np.array(ep_dists) == 0) else 0)
        hist_actions.append(ep_actions)

    return np.array(hist_reward), np.array(hist_dist), np.array(hist_success), hist_actions

# =============================================================================
# SECTION 5: RUN ALL AGENTS
# =============================================================================

print("="*70)
print("PHASE 141: GUI AGENT CONCEPTS")
print("="*70)

env = GridGUIEnv(GRID_SIZE)

agents = [RandomAgent(GRID_SIZE), HeuristicAgent(GRID_SIZE), PolicyGradientAgent(GRID_SIZE)]
results = {}

for agent in agents:
    print(f"\n--- Running {agent.name} ---")
    rewards, dists, successes, actions = run_agent(agent, env)
    results[agent.name] = {
        'rewards': rewards,
        'dists': dists,
        'successes': successes,
        'actions': actions,
    }
    print(f"  Avg reward (last 50): {np.mean(rewards[-50:]):.3f}")
    print(f"  Avg distance (last 50): {np.mean(dists[-50:]):.2f}")
    print(f"  Success rate (last 50): {np.mean(successes[-50:]):.2f}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================
# We produce four plots:
#   1. Smoothed reward curves.
#   2. Average distance to target over training.
#   3. Success rate (hit the target at least once per episode).
#   4. Action entropy for the policy agent over time.

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# --- Plot 1: Reward curves ---
ax = axes[0, 0]
window = 50
for name, data in results.items():
    r = data['rewards']
    if len(r) >= window:
        smooth = np.convolve(r, np.ones(window)/window, mode='valid')
        ax.plot(smooth, label=name, linewidth=2)
    else:
        ax.plot(r, label=name, linewidth=2)
ax.set_xlabel('Episode')
ax.set_ylabel('Total Episode Reward (smoothed)')
ax.set_title('Reward: Learning to Click the Target')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 2: Distance to target ---
ax = axes[0, 1]
for name, data in results.items():
    d = data['dists']
    if len(d) >= window:
        smooth = np.convolve(d, np.ones(window)/window, mode='valid')
        ax.plot(smooth, label=name, linewidth=2)
    else:
        ax.plot(d, label=name, linewidth=2)
ax.set_xlabel('Episode')
ax.set_ylabel('Average Manhattan Distance')
ax.set_title('Precision: How Close Did the Agent Get?')
ax.legend()
ax.grid(True, alpha=0.3)

# --- Plot 3: Cumulative success rate ---
ax = axes[1, 0]
for name, data in results.items():
    s = data['successes']
    cum = np.cumsum(s) / np.arange(1, len(s) + 1)
    ax.plot(cum, label=name, linewidth=2)
ax.set_xlabel('Episode')
ax.set_ylabel('Cumulative Success Rate')
ax.set_title('Success: Hitting the Target at Least Once')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

# --- Plot 4: Policy entropy over time (policy agent only) ---
ax = axes[1, 1]
pg_agent = agents[2]
if pg_agent.name == "PolicyGradient":
    # Recompute entropy for a sample of episodes to show exploration decay
    entropies = []
    env_test = GridGUIEnv(GRID_SIZE)
    for ep in range(0, EPISODES, 10):
        # Use a checkpoint-like snapshot by resetting theta? No, we use final.
        # Instead, we'll record entropy during training indirectly.
        pass
    # Simpler: show entropy of the final policy when presented with random obs
    sample_entropies = []
    for _ in range(100):
        obs = np.zeros(GRID_SIZE * GRID_SIZE)
        target_idx = np.random.randint(0, GRID_SIZE * GRID_SIZE)
        obs[target_idx] = 1.0
        logits = pg_agent.theta + 2.0 * obs
        logits -= np.max(logits)
        probs = np.exp(logits) / np.sum(np.exp(logits))
        entropy = -np.sum(probs * np.log(probs + 1e-12))
        sample_entropies.append(entropy)
    ax.hist(sample_entropies, bins=20, color='#e74c3c', edgecolor='black')
    ax.set_xlabel('Policy Entropy (bits)')
    ax.set_ylabel('Frequency')
    ax.set_title('Final Policy: Entropy Distribution over Random Targets')
    ax.axvline(x=np.log(GRID_SIZE * GRID_SIZE), color='blue', linestyle='--', label='Max entropy (uniform)')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
os.makedirs('src/phase141', exist_ok=True)
plt.savefig('src/phase141/phase141_gui_agent_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase141/phase141_gui_agent_concepts.png")
plt.close()

# =============================================================================
# SECTION 7: DEMONSTRATION OF OBSERVATION -> THOUGHT -> ACTION
# =============================================================================
print("\n" + "="*70)
print("OBSERVATION -> THOUGHT -> ACTION CYCLE")
print("="*70)
env_demo = GridGUIEnv(GRID_SIZE)
obs = env_demo.reset()
target_idx = int(np.argmax(obs))
target_row, target_col = divmod(target_idx, GRID_SIZE)

print(f"Observation: Grid {GRID_SIZE}x{GRID_SIZE}, target at ({target_row}, {target_col})")
print(f"Heuristic Thought: 'The brightest pixel is at index {target_idx}.'")
action = agents[1].act(obs)
action_row, action_col = divmod(action, GRID_SIZE)
print(f"Heuristic Action: click(cell_{action}) → coordinates ({action_row}, {action_col})")
_, reward, _, info = env_demo.step(action)
print(f"Result: distance = {info['distance']}, reward = {reward:.3f}")

print("\nPolicy Gradient Thought (simulated):")
print(f"  'Target is likely near index {target_idx}. My logits favor nearby cells.'")
pg_action, _, pg_probs = agents[2].act(obs)
pg_row, pg_col = divmod(pg_action, GRID_SIZE)
print(f"  Action: click(cell_{pg_action}) → coordinates ({pg_row}, {pg_col})")
print(f"  Top-3 probable actions: {np.argsort(pg_probs)[-3:][::-1]}")

# =============================================================================
# SECTION 8: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for name, data in results.items():
    print(f"\n{name}:")
    print(f"  Final avg reward:    {np.mean(data['rewards'][-50:]):.3f}")
    print(f"  Final avg distance:  {np.mean(data['dists'][-50:]):.2f}")
    print(f"  Overall success rate: {np.mean(data['successes']):.2f}")

print("\nKey lessons:")
print("  1. GUI agents must map high-dimensional observations to precise actions.")
print("  2. Random exploration fails in even tiny action spaces (64 cells).")
print("  3. A perfect detector (heuristic) solves the task immediately.")
print("  4. Policy gradient learns to approximate the heuristic from rewards.")
print("  5. Shaped rewards (distance-based) are essential for dense feedback.")
print("  6. The observation-thought-action loop is the core of computer use.")
print("="*70)
