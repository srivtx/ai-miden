## What Is a Verifiable Reward?

---

### The Problem

In RLHF (Phase 23), a reward model scores how good a response is. But who scores the reward model? For creative writing, there is no right answer. For math problems, there is. How do you train AI to reason when you can automatically check if the final answer is correct?

---

### Definition

A **verifiable reward** is a training signal that can be computed automatically by checking the model's output against a ground-truth answer or a set of rules.

**Examples:**
- **Math:** `model_answer == correct_answer` → +1 or 0
- **Code:** `unit_tests_pass(model_code)` → +1 or 0
- **Logic puzzle:** `is_valid_solution(model_output)` → +1 or 0
- **Chess:** `engine_evaluation(model_move) > threshold` → +1 or 0

**Contrast with human preference rewards:**
- Human preference: "This response is more helpful" (subjective, expensive to collect)
- Verifiable reward: "This answer equals 42" (objective, instant, free)

**Why verifiable rewards are powerful:**
- No human labelers needed
- No reward model training needed
- The signal is exact, not noisy
- The model can train on millions of problems automatically

---

### Real-Life Analogy

A student practicing math problems with an answer key.
- **Human preference (RLHF):** The student writes an essay. A teacher grades it. The teacher might be tired, biased, or inconsistent. The student waits days for feedback.
- **Verifiable reward:** The student solves 100 algebra problems. The answer key instantly marks each one right or wrong. The student knows immediately what to fix. They can practice 1000 problems in an afternoon.

The answer key does not care about handwriting, creativity, or style. It only cares about the final number. This is exactly what verifiable rewards do.

---

### Tiny Numeric Example

**Task:** Solve `15 - 7 × 2 = ?`

**Ground truth:** 1 (order of operations: multiply first, then subtract)

**Model outputs 4 chains:**
```
Chain 1: "15 - 7 = 8, 8 × 2 = 16" → Answer: 16 → Wrong → Reward: 0
Chain 2: "7 × 2 = 14, 15 - 14 = 1" → Answer: 1  → Right → Reward: 1
Chain 3: "15 - 7 × 2 = 16" → Answer: 16 → Wrong → Reward: 0
Chain 4: "7 × 2 = 14, 15 - 14 = 1" → Answer: 1  → Right → Reward: 1
```

**Mean reward:** 0.5

**Advantages:**
```
Chain 1: 0 - 0.5 = -0.5
Chain 2: 1 - 0.5 = +0.5
Chain 3: 0 - 0.5 = -0.5
Chain 4: 1 - 0.5 = +0.5
```

**Policy update:** Increase probability of chains 2 and 4 (which show correct reasoning). Decrease probability of chains 1 and 3.

---

### Common Confusion

1. **"Verifiable rewards are just accuracy."** Yes, for classification. For code, it is "do all tests pass?" For math, it is "does the final expression simplify to the correct value?"

2. **"The model gets rewarded for correct reasoning steps."** No. Basic verifiable rewards only check the final answer. The model could have nonsense reasoning but stumble on the right answer and still get +1. Process reward models (PRM) fix this by checking each step.

3. **"Verifiable rewards work for any task."** No. They only work when there is an automatic checker. Creative writing, open-ended advice, and subjective judgments still need human feedback.

4. **"Verifiable rewards are too sparse."** Sometimes. If the model gets 1% accuracy initially, most rewards are 0. But the relative advantage within a group still provides signal. And as the model improves, the signal gets richer.

5. **"Checker errors destroy training."** If the checker has bugs (e.g., marks correct answers as wrong), the model learns the wrong thing. The checker must be reliable.

---

### Where It Is Used in Our Code

`src/phase42/phase42_verifiable_rewards.py` — The `check_answer()` function implements a verifiable reward for simple arithmetic. Correct answers get +1, incorrect get 0.
