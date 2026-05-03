## What Is a Policy Gradient?

---

### The Problem

Q-learning learns the value of each state-action pair. But what if the action space is continuous? You cannot have a Q-table for infinitely many actions. Can you learn a policy directly — a function that maps states to actions — without computing values?

---

### Definition

**Policy gradient methods** directly optimize the policy (the mapping from states to actions) by adjusting its parameters to increase expected reward.

**The policy:**
```
π_θ(a | s) = probability of taking action a in state s, parameterized by θ
```

**The objective:**
```
J(θ) = E[Σ reward_t]  (expected total reward)
```

**The REINFORCE algorithm:**
```
1. Run an episode using current policy π_θ
2. Compute total reward G for the episode
3. For each step t:
   gradient = ∇_θ log(π_θ(a_t | s_t)) × G
4. Update: θ = θ + α × gradient
```

**Why this works:**
- `∇_θ log(π_θ(a|s))` tells us how to change parameters to make action `a` more likely in state `s`
- Multiplying by `G` (total reward) scales the update: high-reward episodes get stronger updates
- Over time, the policy shifts toward actions that lead to high rewards

---

### Real-Life Analogy

A comedian testing jokes.
- **Policy:** The comedian's style — which jokes to tell, timing, delivery
- **Episode:** A full comedy set
- **Reward:** Audience laughter (measured by sound level)
- **REINFORCE:** If the audience laughs a lot (high reward), the comedian does MORE of whatever they did. If the audience is silent, they do LESS.
- The comedian does not need to predict "what is the value of telling a dad joke at minute 3?" They just learn which style gets laughs.

The comedian optimizes their policy (style) directly from audience feedback.

---

### Tiny Numeric Example

**2-state MDP:**
```
State 1: choose action A or B
  A -> reward +1, go to State 2
  B -> reward -1, go to State 2

State 2: episode ends
```

**Policy:** Softmax over action preferences
```
p(A) = exp(θ_A) / (exp(θ_A) + exp(θ_B))
p(B) = exp(θ_B) / (exp(θ_A) + exp(θ_B))
```

**Episode 1:** Choose A, get reward +1
```
log p(A) = θ_A - log(exp(θ_A) + exp(θ_B))
∇_θA log p(A) = 1 - p(A) = 1 - 0.5 = 0.5
∇_θB log p(A) = -p(B) = -0.5

Update:
θ_A += 0.1 × 0.5 × 1 = +0.05
θ_B += 0.1 × (-0.5) × 1 = -0.05

New policy: p(A) = 0.55, p(B) = 0.45
```

**Episode 2:** Choose A again, get reward +1
```
θ_A += 0.1 × 0.45 × 1 = +0.045
θ_B += 0.1 × (-0.55) × 1 = -0.055

New policy: p(A) = 0.60, p(B) = 0.40
```

**After 10 episodes of choosing A:**
```
p(A) = 0.88, p(B) = 0.12
```

The policy has learned to prefer action A.

---

### Common Confusion

1. **"Policy gradients are only for discrete actions."** No. They work for continuous actions too (e.g., controlling a robot's joint angles).

2. **"REINFORCE has high variance."** Yes. The reward of an entire episode might be due to one lucky action. Baselines and advantage estimates reduce this variance.

3. **"Policy gradients need a differentiable policy."** Yes. The policy must output probabilities (or parameters of a distribution) that are differentiable with respect to θ.

4. **"Policy gradients converge faster than Q-learning."** Not necessarily. They handle continuous actions better, but can have higher variance and slower convergence on simple discrete problems.

5. **"PPO is a policy gradient method."** Yes. PPO (Phase 15) is a policy gradient algorithm with clipped updates for stability. REINFORCE is the simplest form.

---

### Where It Is Used in Our Code

`src/phase53/phase53_classical_rl.py` — We implement REINFORCE on a simple bandit problem, showing how the policy shifts toward high-reward actions through gradient updates.
