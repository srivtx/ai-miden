## What Is Q-Learning?

---

### The Problem

An agent explores a maze. When it reaches the cheese, it gets +10 reward. When it hits a wall, it gets -1. The agent does not know the maze layout. How does it learn which actions lead to the best outcomes through trial and error?

---

### Definition

**Q-Learning** is a model-free reinforcement learning algorithm that learns the value of taking a specific action in a specific state.

**The Q-value:**
```
Q(s, a) = expected total future reward starting from state s, taking action a
```

**The Q-learning update rule:**
```
Q(s, a) = Q(s, a) + α × [r + γ × max_a'(Q(s', a')) - Q(s, a)]
```

Where:
- `s` = current state
- `a` = action taken
- `r` = immediate reward
- `s'` = next state
- `α` = learning rate
- `γ` = discount factor (how much we care about future rewards)
- `max_a'(Q(s', a'))` = best Q-value from the next state

**Why this works:**
- The agent explores randomly at first
- When it stumbles on cheese, the Q-value for that action increases
- Over time, high Q-values propagate backward through the maze
- The agent learns the optimal path without ever seeing a map

---

### Real-Life Analogy

A rat in a maze.
- **First attempt:** The rat wanders randomly. It bumps into walls (-1), takes wrong turns, but eventually finds cheese (+10). It remembers: "at this junction, turning RIGHT led to cheese eventually."
- **Second attempt:** The rat remembers some good moves. It gets to the cheese faster. It updates its memory: "turning LEFT here is even better because it leads to the right junction sooner."
- **Hundredth attempt:** The rat knows the optimal path. It runs directly to the cheese. Every junction has a learned "Q-value" for each direction.

The rat never saw a map. It learned purely from rewards.

---

### Tiny Numeric Example

**Simple maze (3 states):**
```
State A --(right)--> State B --(right)--> Cheese (+10)
State A --(left)-->  Wall (-1)
State B --(left)-->  State A
```

**Initialize Q-table:**
```
       Right  Left
State A   0     0
State B   0     0
```

**Episode 1:**
```
A -> Right -> B, reward=0
B -> Right -> Cheese, reward=10

Update Q(B, Right):
Q(B, Right) = 0 + 0.1 × [10 + 0.9 × 0 - 0] = 1.0

Update Q(A, Right):
Q(A, Right) = 0 + 0.1 × [0 + 0.9 × 1.0 - 0] = 0.09
```

**Episode 2:**
```
A -> Right -> B, reward=0
B -> Right -> Cheese, reward=10

Update Q(B, Right):
Q(B, Right) = 1.0 + 0.1 × [10 + 0.9 × 1.0 - 1.0] = 1.99

Update Q(A, Right):
Q(A, Right) = 0.09 + 0.1 × [0 + 0.9 × 1.99 - 0.09] = 0.27
```

**After 100 episodes:**
```
       Right   Left
State A  8.1   -0.5
State B  9.0   -0.2
```

The agent has learned that RIGHT is good at both states, and LEFT is bad.

---

### Common Confusion

1. **"Q-learning needs a model of the environment."** No. It is model-free. It learns from experience without knowing transition probabilities.

2. **"Q-learning only works for small state spaces."** The tabular version does. Deep Q-Networks (DQN) use neural networks to approximate Q-values for large/continuous state spaces.

3. **"The agent always takes the action with highest Q-value."** Not during training. It uses epsilon-greedy: mostly exploit (best action), sometimes explore (random action).

4. **"Q-learning and SARSA are the same."** SARSA uses the actual next action taken (on-policy). Q-learning uses the maximum Q-value of the next state (off-policy).

5. **"Q-learning converges to the optimal policy."** Yes, with infinite exploration and a decaying learning rate. In practice, it approximates the optimal policy.

---

### Where It Is Used in Our Code

`src/phase53/phase53_classical_rl.py` — A Q-learning agent learns to navigate a grid world to reach a goal, demonstrating how Q-values propagate from the reward backward through the state space.
