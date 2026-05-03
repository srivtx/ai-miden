## What Is an Actor-Critic?

---

### The Problem

Q-learning learns values but struggles with continuous actions. Policy gradients learn policies directly but have high variance — one lucky episode can cause a huge parameter update. Can you combine the best of both: the low variance of value learning with the direct policy optimization of policy gradients?

---

### Definition

**Actor-Critic** is a reinforcement learning architecture with two components:
1. **Actor:** The policy network that decides which action to take
2. **Critic:** The value network that estimates how good the current state is

**How they work together:**
```
1. Actor takes action a in state s
2. Environment returns reward r and next state s'
3. Critic computes V(s) = expected future reward from state s
4. Advantage = r + γ×V(s') - V(s)  (how much better than expected)
5. Actor update: increase probability of a if advantage > 0
6. Critic update: improve V(s) prediction toward actual return
```

**Why this reduces variance:**
- REINFORCE uses total episode reward (high variance)
- Actor-Critic uses the advantage (temporal difference error), which is much lower variance
- The critic provides a baseline that stabilizes learning

**Advantage function:**
```
A(s, a) = Q(s, a) - V(s)
```
- If A > 0: action a is better than average
- If A < 0: action a is worse than average

---

### Real-Life Analogy

A director and a film critic.
- **Actor (director):** Decides how to shoot each scene. "Should the actor whisper or shout here?"
- **Critic (film critic):** Watches the scene and predicts how audiences will rate it. "This scene will get 7/10."
- **Advantage:** After the movie releases, actual audience rating is 8/10. The critic underestimated by 1 point. The director learns: "my choice to whisper worked better than the critic expected."
- The director improves their choices. The critic improves their predictions. They learn together.

The critic's predictions provide a stable baseline. The director does not need to wait for the full box office result (high variance) — they get feedback scene-by-scene.

---

### Tiny Numeric Example

**State s1, two actions:**
```
Action A: reward +1, go to s2 (terminal, value=0)
Action B: reward +0, go to s2 (terminal, value=0)
```

**Critic estimates:**
```
V(s1) = 0.5, V(s2) = 0
```

**Actor takes Action A:**
```
Actual return = 1 + 0.9×0 = 1.0
Advantage = 1.0 - V(s1) = 1.0 - 0.5 = +0.5

Actor update: increase probability of A (advantage is positive)
Critic update: V(s1) should be closer to 1.0
  V(s1) = 0.5 + 0.1 × (1.0 - 0.5) = 0.55
```

**Next episode, Actor takes Action B:**
```
Actual return = 0 + 0.9×0 = 0
Advantage = 0 - V(s1) = 0 - 0.55 = -0.55

Actor update: decrease probability of B (advantage is negative)
Critic update: V(s1) should be closer to 0
  V(s1) = 0.55 + 0.1 × (0 - 0.55) = 0.495
```

**After many episodes:**
```
V(s1) converges to 0.5 (average of A and B)
Actor converges to p(A) = 1.0 (always choose A)
```

The actor learns the optimal policy. The critic learns accurate values.

---

### Common Confusion

1. **"Actor-Critic is just Q-learning with a policy."** Related but different. Q-learning uses Q-values directly. Actor-Critic uses a separate value baseline to reduce variance.

2. **"The critic must be perfect."** No. Even a rough critic provides enough baseline to reduce variance significantly.

3. **"Actor-Critic is only for deep RL."** No. It works with tabular representations too. But it shines with neural networks (A3C, PPO, SAC).

4. **"The actor and critic share parameters."** Sometimes yes (shared layers), sometimes no (separate networks). Sharing reduces computation but can cause interference.

5. **"Actor-Critic eliminates all variance."** It reduces variance but does not eliminate it. Techniques like GAE (Generalized Advantage Estimation) further reduce it.

---

### Where It Is Used in Our Code

`src/phase53/phase53_classical_rl.py` — We implement a tabular actor-critic agent on a grid world, showing how the critic's value estimates stabilize the actor's policy updates.
