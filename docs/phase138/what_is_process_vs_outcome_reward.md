## What Is Process vs. Outcome Reward?

---

### The Problem

You train a model to solve math problems and reward it only when the final numerical answer is correct. The model learns to guess the right answer occasionally but never learns how to reason step by step. It produces answers like "The answer is 42" with no intermediate work. When it is wrong, you have no signal about where the reasoning broke down. How do you reward not just the destination, but the journey?

---

### Definition

**Outcome reward** evaluates only the final output of a reasoning chain. It gives a score of 1 if the answer is correct and 0 if it is wrong. It is sparse, cheap to compute, and easy to define — but it provides no feedback about which reasoning step failed.

**Process reward** evaluates each intermediate step of a reasoning chain. It gives a partial score after every step, indicating whether the reasoning so far is on track. It is dense, informative, and enables precise error localization — but it requires a model or human to judge each step, which is expensive.

**Comparison:**
```
Problem: "15 - 3 * 2 = ?"
Reasoning chain:
  Step 1: "First multiply 3 * 2 = 6"
  Step 2: "Then subtract 15 - 6 = 9"
  Final answer: "9"

Outcome reward:
  Step 1 → no signal
  Step 2 → no signal
  Final → 1.0 (correct)

Process reward:
  Step 1 → 1.0 (correct order of operations)
  Step 2 → 1.0 (correct subtraction)
  Final → 1.0 (correct answer)

If the chain were:
  Step 1: "First subtract 15 - 3 = 12"
  Step 2: "Then multiply 12 * 2 = 24"
  Final answer: "24"

Outcome reward:
  Final → 0.0 (wrong)
  (No idea where the error was.)

Process reward:
  Step 1 → 0.0 (wrong order of operations)
  Step 2 → 0.0 (based on wrong prior step)
  Final → 0.0
  (The error is localized to step 1.)
```

**Why process rewards are better for search:**
- They provide a value estimate for every node in the search tree, not just leaf nodes
- They enable early pruning: a node with a low process reward is unlikely to lead to a good final answer
- They make training more sample-efficient: the model gets feedback at every step, not just at the end
- They align with human pedagogy: a teacher corrects a student at the first mistake, not after the final exam

---

### Real-Life Analogy

Learning to cook with two different instructors.
- **Outcome reward instructor:** Tastes only the final dish. If it is delicious, you get an A. If it is terrible, you get an F. You have no idea whether you ruined it by over-salting at step 3, burning the garlic at step 5, or forgetting the main ingredient at step 1. You just know the final result failed.
- **Process reward instructor:** Watches you at every step. "You are chopping the onions too coarsely — fix that." "The pan is too hot — lower the flame." "You added salt twice — remove some." Each step gets immediate feedback. When the dish fails, the instructor knows exactly where you went wrong and can correct it.
- **The result:** The process-reward student learns faster, makes fewer mistakes, and can debug failures. The outcome-reward student learns slowly and cannot self-correct.

---

### Tiny Numeric Example

**Task:** Evaluate "(4 + 6) / 2"

**Correct chain:**
```
Step 1: "4 + 6 = 10"        → process reward: 1.0
Step 2: "10 / 2 = 5"        → process reward: 1.0
Final:   "5"                → outcome reward: 1.0
```

**Incorrect chain A (wrong order):**
```
Step 1: "6 / 2 = 3"         → process reward: 0.0  (wrong order)
Step 2: "4 + 3 = 7"         → process reward: 0.0  (based on error)
Final:   "7"                → outcome reward: 0.0
```

**Incorrect chain B (arithmetic error):**
```
Step 1: "4 + 6 = 10"        → process reward: 1.0
Step 2: "10 / 2 = 6"        → process reward: 0.0  (arithmetic error)
Final:   "6"                → outcome reward: 0.0
```

**Training signal comparison:**
```
Method            |  Signal per chain  |  Error localization
------------------|-------------------|--------------------
Outcome reward    |  1 scalar           |  None
Process reward    |  N scalars          |  Exact step
```

With process rewards, the model knows that chain A failed at step 1 (order of operations) and chain B failed at step 2 (division error). With outcome rewards, both chains get the same "0" signal with no differentiation.

---

### Common Confusion

1. **"Process reward means human annotators check every step."** Not necessarily. Process reward models (PRMs) are trained neural networks that automatically score each step. They are expensive to train (requires human-labeled step data) but cheap to run at inference time.

2. **"Outcome rewards are useless."** They are not useless; they are just less informative. For simple tasks where the model already reasons well, outcome rewards are sufficient and much cheaper. Process rewards shine in complex multi-step reasoning where errors compound.

3. **"Process rewards prevent all errors."** No. A process reward model can itself be wrong. It might give a high score to a step that looks correct but contains a subtle logical flaw. Process rewards reduce error but do not eliminate it.

4. **"You can derive process rewards from outcome rewards by unrolling."** In theory, yes — if you have enough samples, you can attribute final outcomes to individual steps (credit assignment). In practice, this is hard because of compounding errors and long chains. Direct process supervision is more effective.

5. **"Process rewards are only for math."** Math is the canonical example because steps are verifiable. But process rewards apply to any structured task: code debugging (each line), legal reasoning (each premise), scientific argumentation (each claim). Any task with intermediate structure benefits.

6. **"Process reward models must be larger than the policy model."** Not necessarily. A small PRM can supervise a large policy if the verification task is simpler than the generation task. For arithmetic, a tiny model can check each step. For open-ended reasoning, the PRM might need to be large.

7. **"MCTS requires process rewards to work."** MCTS can work with outcome rewards alone (leaf scoring only). However, it works much better with process rewards because intermediate value estimates guide selection and pruning. Process rewards turn MCTS from a blind leaf-gambling algorithm into a directed search.

---

### Where It Is Used in Our Code

`src/phase138/phase138_mcts_concepts.py` — We implement both outcome-only and process-based scoring for the toy grid-path problem. In outcome-only mode, only the final path correctness matters. In process-based mode, we give partial credit for moving closer to the goal at each step. We compare how quickly each method finds the optimal path.

`src/phase138/phase138_mcts_colab.py` — We use a correctness checker as a weak outcome reward for math problems. We discuss how a process reward model (evaluating each reasoning step for mathematical validity) would improve the search, and we simulate process guidance by scoring intermediate steps with a lightweight arithmetic parser.
