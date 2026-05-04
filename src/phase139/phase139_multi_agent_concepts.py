#!/usr/bin/env python3
"""
Phase 139: Multi-Agent Training Concepts — NumPy Simulation
=============================================================
This script demonstrates three core multi-agent dynamics using only NumPy:

  1. Cooperative training (shared reward) leads to mutual cooperation.
  2. Competitive training (individual reward) leads to mutual defection.
  3. Adversarial training (zero-sum) leads to mixed-strategy equilibrium.

We use the iterated prisoner's dilemma because it is the simplest
environment where collaboration, competition, and game-theoretic
emergence are all visible in a 2x2 reward matrix.

Each agent has a memory-1 policy: its probability of cooperating
depends on the outcome of the previous round. This allows strategies
like tit-for-tat to emerge naturally from gradient updates.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(139)

# =============================================================================
# SECTION 1: CONFIGURATION AND REWARD MATRIX
# =============================================================================
# The prisoner's dilemma payoff matrix:
#   Both cooperate  -> (R, R) = (3, 3)
#   A cooperates, B defects -> (S, T) = (0, 5)
#   A defects, B cooperates -> (T, S) = (5, 0)
#   Both defect     -> (P, P) = (1, 1)
# This ordering (T > R > P > S) makes defection a dominant strategy in a
# single round, but repeated play enables reciprocity.

R = 3.0   # Reward for mutual cooperation
T = 5.0   # Temptation to defect
S = 0.0   # Sucker's payoff
P = 1.0   # Punishment for mutual defection

EPISODES = 3000
STEPS_PER_EPISODE = 20
GAMMA = 0.95          # discount factor for future rewards
LR = 0.15             # policy-gradient learning rate
BASELINE_DECAY = 0.9  # exponential moving average for baseline

# =============================================================================
# SECTION 2: MEMORY-1 POLICY REPRESENTATION
# =============================================================================
# A memory-1 agent conditions its action on the previous joint action.
# There are four possible previous outcomes, indexed as:
#   0: (C, C)   both cooperated
#   1: (C, D)   A cooperated, B defected
#   2: (D, C)   A defected, B cooperated
#   3: (D, D)   both defected
# The policy is a vector of 4 logits.  p_coop = sigmoid(logit).
# This is rich enough to represent tit-for-tat: high p_coop for state 0,
# low for state 2, etc.

class Memory1Agent:
    """
    WHY memory-1? In the iterated prisoner's dilemma, knowing what happened
    last round is sufficient to implement tit-for-tat, grim trigger, and
    many other famous strategies. Memory-0 (stateless) can only play
    always-cooperate or always-defect, which misses the emergence story.
    """
    def __init__(self):
        # Initialize to near-random (small logits -> p ~ 0.5)
        self.theta = np.random.randn(4) * 0.1

    def coop_prob(self, state):
        """Return probability of cooperating given the previous state."""
        return 1.0 / (1.0 + np.exp(-self.theta[state]))

    def sample(self, state):
        """Sample an action and compute log-probability gradient."""
        p = self.coop_prob(state)
        action = 1 if np.random.rand() < p else 0  # 1 = Cooperate, 0 = Defect
        # Gradient of log pi w.r.t theta for this state:
        # d/dtheta [ a*log(p) + (1-a)*log(1-p) ] = a - p
        grad = np.zeros(4)
        grad[state] = action - p
        return action, grad, p

# =============================================================================
# SECTION 3: EPISODE ROLLOUT
# =============================================================================
# WHY separate rollout from update? Policy-gradient methods require the full
# trajectory to compute discounted returns. Mixing forward and backward
# inside the same loop would make return computation messy.

def run_episode(agent_a, agent_b):
    """
    Run one episode of iterated prisoner's dilemma.
    Returns:
      actions_a, actions_b: arrays of shape (STEPS_PER_EPISODE,)
      rewards_a, rewards_b: arrays of shape (STEPS_PER_EPISODE,)
      grads_a, grads_b:     lists of gradient vectors per step
      states:               array of previous joint states
    """
    actions_a = np.zeros(STEPS_PER_EPISODE, dtype=int)
    actions_b = np.zeros(STEPS_PER_EPISODE, dtype=int)
    rewards_a = np.zeros(STEPS_PER_EPISODE)
    rewards_b = np.zeros(STEPS_PER_EPISODE)
    grads_a = []
    grads_b = []
    states = np.zeros(STEPS_PER_EPISODE, dtype=int)

    # Initial state: assume both cooperated in the previous (imaginary) round.
    state = 0

    for t in range(STEPS_PER_EPISODE):
        states[t] = state
        a, grad_a, _ = agent_a.sample(state)
        b, grad_b, _ = agent_b.sample(state)
        actions_a[t] = a
        actions_b[t] = b

        # Compute rewards based on joint action
        if a == 1 and b == 1:
            rewards_a[t] = R
            rewards_b[t] = R
        elif a == 1 and b == 0:
            rewards_a[t] = S
            rewards_b[t] = T
        elif a == 0 and b == 1:
            rewards_a[t] = T
            rewards_b[t] = S
        else:
            rewards_a[t] = P
            rewards_b[t] = P

        grads_a.append(grad_a)
        grads_b.append(grad_b)

        # Next state is determined by this round's joint action
        # Encoding: 0=(C,C), 1=(C,D), 2=(D,C), 3=(D,D)
        state = (1 - a) * 2 + (1 - b)  # simpler mapping:
        if a == 1 and b == 1:
            state = 0
        elif a == 1 and b == 0:
            state = 1
        elif a == 0 and b == 1:
            state = 2
        else:
            state = 3

    return actions_a, actions_b, rewards_a, rewards_b, grads_a, grads_b, states

# =============================================================================
# SECTION 4: POLICY-GRADIENT UPDATE (REINFORCE)
# =============================================================================
# WHY REINFORCE instead of actor-critic? Because the state space is tiny
# (4 states) and the episode is short. A learned critic would add complexity
# without benefit. The moving-average baseline is enough to reduce variance.

def compute_returns(rewards, gamma):
    """Compute discounted returns for an episode."""
    returns = np.zeros_like(rewards)
    G = 0.0
    for t in reversed(range(len(rewards))):
        G = rewards[t] + gamma * G
        returns[t] = G
    return returns

def train_agents(agent_a, agent_b, reward_mode='individual', episodes=EPISODES):
    """
    Train two agents with policy gradient.

    reward_mode:
      'individual' -> each agent gets only its own reward (competition)
      'shared'     -> both agents get the sum of rewards (cooperation)
      'zero_sum'   -> agent_a gets +r_a, agent_b gets -r_a (adversarial)
    """
    baseline_a = 0.0
    baseline_b = 0.0

    # History for plotting
    hist_reward_a = []
    hist_reward_b = []
    hist_theta_a = []
    hist_theta_b = []
    hist_mutual_coop = []  # fraction of steps where both cooperated

    for ep in range(episodes):
        actions_a, actions_b, rewards_a, rewards_b, grads_a, grads_b, states = run_episode(agent_a, agent_b)

        mutual = (actions_a == 1) & (actions_b == 1)
        if reward_mode == 'shared':
            # WHY add a mutual-cooperation bonus? Without it, shared reward
            # can collapse into a suboptimal equilibrium where one agent
            # free-rides on the other's passivity. The bonus makes mutual
            # cooperation the unambiguous global optimum.
            rewards_a = rewards_a + rewards_b + mutual.astype(float) * 4.0
            rewards_b = rewards_a.copy()
        elif reward_mode == 'zero_sum':
            rewards_b = -rewards_a.copy()

        returns_a = compute_returns(rewards_a, GAMMA)
        returns_b = compute_returns(rewards_b, GAMMA)

        # Update moving-average baseline
        baseline_a = BASELINE_DECAY * baseline_a + (1 - BASELINE_DECAY) * returns_a.mean()
        baseline_b = BASELINE_DECAY * baseline_b + (1 - BASELINE_DECAY) * returns_b.mean()

        advantage_a = returns_a.mean() - baseline_a
        advantage_b = returns_b.mean() - baseline_b

        # REINFORCE: theta += lr * advantage * sum(grads)
        # WHY sum? The gradient of the episodic objective is the sum of
        # per-step log-policy gradients weighted by returns. We approximate
        # with the mean return for the whole episode because the state space
        # is tiny and the policy is state-conditioned.
        total_grad_a = np.zeros(4)
        total_grad_b = np.zeros(4)
        for t in range(STEPS_PER_EPISODE):
            total_grad_a += grads_a[t]
            total_grad_b += grads_b[t]

        agent_a.theta += LR * advantage_a * total_grad_a
        agent_b.theta += LR * advantage_b * total_grad_b

        hist_reward_a.append(rewards_a.sum())
        hist_reward_b.append(rewards_b.sum())
        hist_mutual_coop.append(np.mean(mutual.astype(float)))
        if ep % 50 == 0:
            hist_theta_a.append(agent_a.theta.copy())
            hist_theta_b.append(agent_b.theta.copy())

    return hist_reward_a, hist_reward_b, np.array(hist_theta_a), np.array(hist_theta_b), np.array(hist_mutual_coop)

# =============================================================================
# SECTION 5: RUN THREE SCENARIOS
# =============================================================================
# WHY three scenarios? The point of this phase is that the *same* learning
# algorithm produces radically different behaviors depending on incentives.
# Showing competition, cooperation, and adversarial training side-by-side
# makes the incentive-dependence unmistakable.

print("="*70)
print("PHASE 139: MULTI-AGENT TRAINING CONCEPTS")
print("="*70)

scenarios = {}

print("\n--- Scenario 1: Competitive (individual rewards) ---")
agent_a = Memory1Agent()
agent_b = Memory1Agent()
ra, rb, theta_a, theta_b, mc = train_agents(agent_a, agent_b, reward_mode='individual')
scenarios['Competitive'] = (agent_a, agent_b, ra, rb, theta_a, theta_b, mc)
print(f"Final A theta: {np.round(agent_a.theta, 2)}")
print(f"Final B theta: {np.round(agent_b.theta, 2)}")

print("\n--- Scenario 2: Cooperative (shared rewards) ---")
agent_a = Memory1Agent()
agent_b = Memory1Agent()
ra, rb, theta_a, theta_b, mc = train_agents(agent_a, agent_b, reward_mode='shared')
scenarios['Cooperative'] = (agent_a, agent_b, ra, rb, theta_a, theta_b, mc)
print(f"Final A theta: {np.round(agent_a.theta, 2)}")
print(f"Final B theta: {np.round(agent_b.theta, 2)}")

print("\n--- Scenario 3: Adversarial (zero-sum) ---")
agent_a = Memory1Agent()
agent_b = Memory1Agent()
ra, rb, theta_a, theta_b, mc = train_agents(agent_a, agent_b, reward_mode='zero_sum')
scenarios['Adversarial'] = (agent_a, agent_b, ra, rb, theta_a, theta_b, mc)
print(f"Final A theta: {np.round(agent_a.theta, 2)}")
print(f"Final B theta: {np.round(agent_b.theta, 2)}")

# =============================================================================
# SECTION 6: VISUALIZATION
# =============================================================================
# We produce four plots:
#   1. Average reward per episode (smoothed) for all three scenarios.
#   2. Evolution of cooperate-after-cooperate probability (state 0).
#   3. Final policy heatmaps for cooperative scenario.
#   4. Final policy heatmaps for competitive scenario.

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# --- Plot 1: Smoothed reward curves ---
ax = axes[0, 0]
window = 100
for name, (_, _, ra, rb, _, _, _) in scenarios.items():
    smooth_a = np.convolve(ra, np.ones(window)/window, mode='valid')
    smooth_b = np.convolve(rb, np.ones(window)/window, mode='valid')
    ax.plot(smooth_a, label=f'{name} A', linewidth=2)
    ax.plot(smooth_b, label=f'{name} B', linewidth=2, linestyle='--')
ax.set_xlabel('Episode')
ax.set_ylabel('Total Episode Reward (smoothed)')
ax.set_title('Reward Dynamics: Incentives Shape Behavior')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# --- Plot 2: Mutual cooperation rate over training ---
# WHY mutual cooperation rate? It directly measures coordination.
# A high rate means both agents are jointly choosing the cooperative
# action, regardless of whether their individual state policies are symmetric.
ax = axes[0, 1]
for name, (_, _, _, _, _, _, mc) in scenarios.items():
    ax.plot(mc, label=f'{name}', linewidth=2)
ax.set_xlabel('Episode')
ax.set_ylabel('Fraction of Mutual Cooperation')
ax.set_title('Emergence of Coordination')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1)

# --- Plot 3: Cooperative final policy heatmap ---
ax = axes[1, 0]
state_labels = ['(C,C)', '(C,D)', '(D,C)', '(D,D)']
a_coop, b_coop, _, _, _, _, _ = scenarios['Cooperative']
probs = np.stack([a_coop.coop_prob(np.arange(4)), b_coop.coop_prob(np.arange(4))], axis=0)
im = ax.imshow(probs, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(4))
ax.set_xticklabels(state_labels)
ax.set_yticks([0, 1])
ax.set_yticklabels(['Agent A', 'Agent B'])
ax.set_title('Final Policy: Cooperative Scenario')
for i in range(2):
    for j in range(4):
        ax.text(j, i, f'{probs[i, j]:.2f}', ha='center', va='center', color='black')
plt.colorbar(im, ax=ax)

# --- Plot 4: Competitive final policy heatmap ---
ax = axes[1, 1]
a_comp, b_comp, _, _, _, _, _ = scenarios['Competitive']
probs = np.stack([a_comp.coop_prob(np.arange(4)), b_comp.coop_prob(np.arange(4))], axis=0)
im = ax.imshow(probs, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(4))
ax.set_xticklabels(state_labels)
ax.set_yticks([0, 1])
ax.set_yticklabels(['Agent A', 'Agent B'])
ax.set_title('Final Policy: Competitive Scenario')
for i in range(2):
    for j in range(4):
        ax.text(j, i, f'{probs[i, j]:.2f}', ha='center', va='center', color='black')
plt.colorbar(im, ax=ax)

plt.tight_layout()
os.makedirs('src/phase139', exist_ok=True)
plt.savefig('src/phase139/multi_agent_concepts.png', dpi=150, bbox_inches='tight')
print("\nSaved plot to src/phase139/multi_agent_concepts.png")
plt.close()

# =============================================================================
# SECTION 7: SUMMARY
# =============================================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
for name, (a, b, ra, rb, _, _, mc) in scenarios.items():
    print(f"\n{name}:")
    print(f"  Agent A final P(C|CC): {a.coop_prob(0):.3f}")
    print(f"  Agent B final P(C|CC): {b.coop_prob(0):.3f}")
    print(f"  Avg mutual cooperation (last 100 ep): {np.mean(mc[-100:]):.3f}")
    print(f"  Avg reward A (last 100 ep): {np.mean(ra[-100:]):.1f}")
    print(f"  Avg reward B (last 100 ep): {np.mean(rb[-100:]):.1f}")

print("\nKey lessons:")
print("  1. Reward structure is the dominant factor in multi-agent behavior.")
print("  2. Shared rewards drive cooperation; individual rewards drive defection.")
print("  3. Memory-1 policies are sufficient for tit-for-tat-like emergence.")
print("  4. Zero-sum training pushes agents toward mixed-strategy equilibria.")
print("  5. The same algorithm (REINFORCE) produced three different societies.")
print("="*70)
