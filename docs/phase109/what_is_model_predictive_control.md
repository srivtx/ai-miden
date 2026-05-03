## What Is Model Predictive Control (MPC)?

---

### The Problem

Even with an accurate world model, an agent cannot blindly execute a long plan. Models are imperfect, and unexpected disturbances push the real state away from predictions. A plan made 50 steps ago may be irrelevant now because the world changed. A quadcopter that committed to a thrust sequence from its starting position will crash if a gust of wind shifts it off course. How do you use a model to choose actions without committing to a plan that will fail?

---

### Definition

**Model Predictive Control** is an online planning method that uses a dynamics model to simulate future trajectories over a finite horizon. At each timestep, it evaluates multiple candidate action sequences, selects the one with the best predicted return, executes only the first action, and then re-plans from the new state.

**How it works:**
```
Current state → Sample 100 action sequences → Simulate each for 10 steps
Score each sequence by predicted cumulative reward
Execute the first action of the best sequence
Observe new state → Repeat
Result: robust control that compensates for model error by constant re-planning
```

**Key techniques:**
- **Receding horizon:** only the first action is executed, then the horizon shifts forward one step
- **Trajectory sampling:** random, cross-entropy, or gradient-based search over action sequences
- **Warm-starting:** using the previous plan as an initialization for the next optimization

**Why this matters:**
- Compensates for model inaccuracies by never committing to long plans
- Handles unexpected disturbances because it re-plans at every step
- Works with any differentiable or learned dynamics model, linear or nonlinear

---

### Real-Life Analogy

MPC is like driving with a GPS that recalculates the route every 10 seconds. You look ahead at possible routes, pick the best one, drive for 10 seconds, and then re-evaluate based on your new position. If a road is closed or traffic appears, the next recalculation adapts. You never blindly follow a plan made miles ago.

The trade-off is computational cost. Recalculating constantly requires more compute than following a single plan, but the robustness gain is worth it in dynamic environments. A GPS that recalculates every second gives smoother routes but drains your phone battery faster. MPC faces the same tension: shorter replanning intervals improve robustness but increase computational load per step.

---

### Tiny Numeric Example

**State:** [position=2.0, velocity=0.0], target: [0, 0]

**Open-loop plan (10 steps, no re-planning):**
```
Predicted final state after 10 steps: [0.05, 0.02]
Actual final state (model error accumulates): [0.34, 0.18]
Deviation from target: 0.35
```

**MPC with horizon=10, re-planning every step:**
```
Step 0: best action = -0.42, execute, observe true next state
Step 1: re-plan from new state, best action = -0.38, execute
Step 2: re-plan, best action = -0.35, execute
...
Step 9: re-plan, best action = -0.05
Actual final state: [0.08, 0.03]
Deviation from target: 0.085
```

**Comparison:**
```
Open-loop deviation:  0.35
MPC deviation:        0.085
Improvement:          75% reduction
```

MPC reduces final deviation by 75% by correcting model error at each step rather than letting it compound.

---

### Common Confusion

1. **"MPC is the same as open-loop planning."** Open-loop planning commits to an entire action sequence upfront. MPC executes only the first action and re-plans from the observed new state, making it closed-loop and robust.

2. **"MPC requires a perfect model."** It explicitly compensates for imperfect models by frequent re-planning; it works better with accurate models but is robust to moderate error.

3. **"MPC is a learning algorithm."** MPC is a control strategy. It can use a learned model, but it does not learn the model itself; the model is trained separately.

4. **"Longer planning horizons always improve MPC."** Very long horizons amplify model error and make optimization harder; horizons of 5-20 steps often work best in practice.

5. **"MPC only works for continuous actions."** While common in continuous control, MPC variants exist for discrete actions using tree search, sampling, or learned action embeddings.

6. **"MPC and Dreamer are interchangeable."** Dreamer trains a policy via imagined rollouts. MPC directly selects actions online using the model. They can complement each other but solve different problems.

7. **"MPC is too slow for real-time control."** With learned models and GPU-based sampling, modern MPC runs at 50-1000 Hz in robotics and autonomous driving.

---

### Where It Is Used in Our Code

`src/phase109/phase109_world_models.py` — We implement a simplified MPC controller that samples 50 random action sequences over a 10-step horizon using a learned linear dynamics model. At each step, it evaluates predicted cumulative reward, executes the first action of the best sequence in the true environment, and re-plans from the resulting state. The resulting trajectory is plotted and saved as `src/phase109/mpc_trajectory.png`.
