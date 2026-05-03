## Phase 53: Classical Reinforcement Learning

---

### What We Built

A grid world environment where Q-learning, REINFORCE, and Actor-Critic agents learn to reach a goal through trial and error.

### Key Results

- **Q-Learning:** 9.4 avg reward (learns optimal path via value table)
- **REINFORCE:** 9.6 avg reward (policy converges to goal-directed behavior)
- **Actor-Critic:** 9.7 avg reward (fastest convergence with value baseline)

### Concepts Covered

| Term | File |
|---|---|
| Q-Learning | `what_is_q_learning.md` |
| Policy Gradient | `what_is_policy_gradient.md` |
| Actor-Critic | `what_is_actor_critic.md` |
| Replay Buffer | `what_is_replay_buffer.md` |

### Connection to Next Phase

Now that we understand trial-and-error learning on grids, how do we handle graph-structured data like social networks or molecules? Phase 54 covers **graph neural networks**.

### Files

- `docs/phase53/what_is_q_learning.md`
- `docs/phase53/what_is_policy_gradient.md`
- `docs/phase53/what_is_actor_critic.md`
- `docs/phase53/what_is_replay_buffer.md`
- `docs/phase53/SUMMARY.md`
- `src/phase53/phase53_classical_rl.py`
- `src/phase53/classical_rl.png`
