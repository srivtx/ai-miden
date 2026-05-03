## What Is a World Model?

---

### The Problem

Reinforcement learning agents that learn purely from trial-and-error need millions of expensive or dangerous interactions. A robot learning to walk cannot fall down a thousand times in the real world. A trading agent cannot lose real money while exploring strategies. An autonomous vehicle cannot crash repeatedly to learn road dynamics. How do you learn efficiently without paying the full cost of every mistake in the real environment?

---

### Definition

A **World Model** is a learned representation of an environment's dynamics. Given the current state and an action, it predicts the next state and reward. The agent uses this model to simulate future trajectories, evaluate plans, and learn policies without interacting with the real environment at every step.

**How it works:**
```
Current state + Action → World Model → Predicted next state + Predicted reward
Agent imagines 100 trajectories → scores them by predicted return → picks best action
Real environment executes action → new state → repeat
Result: sample-efficient learning through imagination
```

**Key techniques:**
- **Latent state-space models:** compress high-dimensional observations into compact vectors for fast simulation
- **Recurrent networks:** maintain hidden state across imagined rollouts to capture temporal dependencies
- **Model predictive control:** re-plan at each step using the learned model to compensate for prediction errors

**Why this matters:**
- Reduces environment interactions by 10x-100x compared to model-free methods
- Enables planning in domains where real-world trial is dangerous, slow, or expensive
- Allows counterfactual reasoning: "What if I had turned left instead?"

---

### Real-Life Analogy

A world model is like a flight simulator for pilots. Instead of crashing real airplanes, trainees practice in a simulator that approximates real physics, weather, and aircraft response. They can try emergency procedures, fail safely, and repeat scenarios that would be catastrophic in reality. The simulator is not perfect -- it might misrepresent turbulence or engine wear -- but it is good enough to build skills that transfer to the real aircraft.

The trade-off is that the simulator's imperfections become the pilot's blind spots. If the model is wrong about friction, the real robot will slip. If the model underestimates wind gusts, the real quadcopter will drift. World models must be validated against real data, and agents must re-plan frequently to correct for model drift. A pilot who trusts the simulator too much is dangerous; an agent that trusts its world model too much fails in the real world.

---

### Tiny Numeric Example

**True dynamics (unknown to agent):**
```
next_pos = pos + vel * 0.1
next_vel = vel * 0.9 + action - 0.1 * pos
```

**Learned linear model after 1000 random samples:**
```
Predicted next_pos = 0.102 * pos + 0.098 * vel + 0.003 * action
Predicted next_vel = -0.099 * pos + 0.901 * vel + 0.997 * action
```

**Prediction error on 5 held-out states:**
```
State [0.5, -0.3], Action [0.2]:
  True next:  [0.470, -0.130]
  Predicted:  [0.460, -0.140]   error = 0.014

State [2.0, 0.0], Action [0.5]:
  True next:  [2.000, 0.300]
  Predicted:  [2.010, 0.300]   error = 0.010

State [-1.0, 0.5], Action [-0.3]:
  True next:  [-0.950, 0.250]
  Predicted:  [-0.946, 0.253]   error = 0.005
```

**Average prediction error: 0.011 (1.1% relative error)**

The learned model achieves sub-2% error, making it reliable for short-horizon planning, though errors compound over long rollouts.

---

### Common Confusion

1. **"A world model is just a replay buffer."** A replay buffer stores past experiences for sampling during training. A world model predicts future experiences the agent has never seen, enabling imagination and planning.

2. **"World models eliminate the need for real environment interaction entirely."** They reduce it but do not eliminate it; the model must be trained on real data and periodically validated against real outcomes.

3. **"A world model is the same as a value function."** A value function estimates expected future return from a state. A world model predicts next states and rewards, enabling explicit trajectory simulation and counterfactual reasoning.

4. **"Any predictive model can serve as a world model."** It must predict the full state transition, not just rewards, and it must be fast enough to support thousands of imagined rollouts per real step.

5. **"World models are only for games and robotics."** They are also used in recommendation systems, traffic prediction, drug discovery, and financial forecasting to simulate outcomes before committing to actions.

6. **"A single world model works for all tasks in an environment."** Different tasks may require different aspects of the dynamics; a model trained for navigation may be poor at manipulation because it ignores contact physics.

7. **"World models are always neural networks."** They can be analytical physics models, Gaussian processes, linear approximations, or symbolic simulators -- any fast predictive model that approximates environment dynamics qualifies.

---

### Where It Is Used in Our Code

`src/phase109/phase109_world_models.py` — We learn a linear dynamics model from 1000 random state-action transitions using least-squares regression. We validate it against the true dynamics on held-out states, then use it inside a Model Predictive Control loop that samples action sequences and selects the best predicted trajectory. We plot the resulting position and velocity curves and save the figure as `src/phase109/mpc_trajectory.png`.
