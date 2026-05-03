"""
Phase 109: World Models & Model-Based RL
NumPy simulation of a learned dynamics model:
predict next state from current state + action.
Use it for simple MPC (roll out actions, pick best).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

np.random.seed(42)


def true_dynamics(state, action):
    """True environment dynamics (unknown to agent)."""
    # Simple 2D dynamics: position and velocity
    pos, vel = state[0], state[1]
    next_vel = vel * 0.9 + action[0] - 0.1 * pos
    next_pos = pos + next_vel * 0.1
    return np.array([next_pos, next_vel])


def learned_dynamics(state, action, W):
    """Learned linear approximation of dynamics."""
    x = np.concatenate([state, action])
    return W @ x


def train_learned_dynamics(num_samples=1000):
    """Collect data and fit a linear dynamics model."""
    X = []
    Y = []
    for _ in range(num_samples):
        s = np.random.randn(2)
        a = np.random.randn(1)
        s_next = true_dynamics(s, a)
        X.append(np.concatenate([s, a]))
        Y.append(s_next)
    X = np.array(X)
    Y = np.array(Y)
    # Least squares: W = (X^T X)^{-1} X^T Y
    W = np.linalg.pinv(X) @ Y
    return W.T  # shape (2, 3)


def mpc_select_action(state, W, horizon=10, num_candidates=100):
    """Simple MPC: sample random action sequences, pick best predicted return."""
    best_reward = -1e9
    best_action = np.array([0.0])
    for _ in range(num_candidates):
        s = state.copy()
        total_reward = 0.0
        for t in range(horizon):
            a = np.random.randn(1) * 0.5
            s = learned_dynamics(s, a, W)
            # Reward: keep position near 0, velocity near 0
            total_reward += -s[0] ** 2 - 0.1 * s[1] ** 2 - 0.01 * a[0] ** 2
        if total_reward > best_reward:
            best_reward = total_reward
            best_action = a  # last action of best sequence (simplified)
    return best_action


def main():
    W = train_learned_dynamics()
    print("Learned dynamics matrix W (2 x 3):")
    print(np.round(W, 3))
    print()

    # Test: compare true vs learned on random states
    test_states = np.random.randn(5, 2)
    test_actions = np.random.randn(5, 1)
    print("Validation: true vs predicted next state")
    for s, a in zip(test_states, test_actions):
        true_next = true_dynamics(s, a)
        pred_next = learned_dynamics(s, a, W)
        print(f"  state={np.round(s,2)} action={np.round(a,2)}")
        print(f"    true={np.round(true_next,3)} pred={np.round(pred_next,3)}")
    print()

    # Simulate an episode with MPC
    state = np.array([2.0, 0.0])  # Start far from target
    states = [state.copy()]
    actions = []
    for step in range(50):
        a = mpc_select_action(state, W, horizon=10, num_candidates=50)
        state = true_dynamics(state, a)
        states.append(state.copy())
        actions.append(a[0])

    states = np.array(states)
    actions = np.array(actions)

    print(f"Final state after 50 steps: {np.round(states[-1], 3)}")

    # Plot trajectory
    fig, axes = plt.subplots(2, 1, figsize=(8, 6))
    axes[0].plot(states[:, 0], label='Position', color='blue')
    axes[0].plot(states[:, 1], label='Velocity', color='orange')
    axes[0].axhline(0, color='black', linestyle='--', alpha=0.3)
    axes[0].set_ylabel('State value')
    axes[0].set_title('MPC Control Trajectory (Learned Dynamics)')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(actions, label='Action', color='green')
    axes[1].set_xlabel('Step')
    axes[1].set_ylabel('Action')
    axes[1].legend()
    axes[1].grid(True)

    fig.tight_layout()
    fig.savefig('src/phase109/mpc_trajectory.png')
    print("Saved plot to src/phase109/mpc_trajectory.png")


if __name__ == '__main__':
    main()
