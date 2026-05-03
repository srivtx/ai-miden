## What Is Reasoning with Verifiable Rewards?

---

### The Problem

Test-time compute (Phase 26) showed that thinking longer improves answers. But how do you TRAIN a model to think deeply in the first place? RLHF (Phase 23) uses human preferences, but humans cannot judge complex mathematical proofs or long reasoning chains accurately. How do you train reasoning when the only feedback is "correct" or "incorrect"?

---

### Definition

**Reasoning with verifiable rewards** trains models through reinforcement learning on tasks where the final answer can be automatically verified:
- Math problems (exact answer match)
- Code (unit tests pass/fail)
- Logic puzzles (solution checks out)
- Chess moves (engine evaluation)

**DeepSeek-R1's approach:**
1. Start with a base model (DeepSeek-V3)
2. Use **GRPO** (Group Relative Policy Optimization — Phase 24)
3. Reward is +1 if final answer is correct, 0 if incorrect
4. The model learns to generate long reasoning chains (Chain of Thought) because that helps it get the right answer
5. Surprisingly, the model spontaneously develops useful behaviors: self-correction, backtracking, and structured thinking

**Key insight:** You do not need to teach reasoning explicitly. Just reward correct answers on hard problems, and the model figures out how to reason in order to maximize its reward.

---

### Real-Life Analogy

Teaching a student to solve puzzles without showing them the solution path.
- **Traditional teaching:** Show step-by-step solutions (supervised learning). The student memorizes patterns but struggles with novel problems.
- **Verifiable reward training:** Give the student puzzles and a checker. They get a cookie if the answer is right, nothing if wrong. The student tries different approaches, discovers that writing down intermediate steps helps catch errors, and gradually develops systematic problem-solving strategies.

The student might invent techniques you never taught them — like "let me verify this sub-problem before continuing" — because it increases their cookie rate.

---

### Tiny Numeric Example

**Task:** Solve `2 + 3 × 4 = ?`

**Correct answer:** 14 (follow order of operations)

**Model's reasoning chain:**
```
Step 1: I need to solve 2 + 3 × 4.
Step 2: Order of operations says multiplication before addition.
Step 3: 3 × 4 = 12.
Step 4: 2 + 12 = 14.
Answer: 14
```

**Checker:** `14 == 14` → Reward = +1

**Model's bad reasoning chain:**
```
Step 1: 2 + 3 = 5.
Step 2: 5 × 4 = 20.
Answer: 20
```

**Checker:** `20 != 14` → Reward = 0

**GRPO update:**
- Generate a group of 4 reasoning chains
- 2 get reward +1 (correct), 2 get reward 0 (incorrect)
- Mean group reward = 0.5
- Advantage for correct chains: +1 - 0.5 = +0.5
- Advantage for incorrect chains: 0 - 0.5 = -0.5
- Update policy to increase probability of correct chains

---

### Common Confusion

1. **"This is just longer CoT prompting."** No. The model is TRAINED to reason, not just prompted. The reasoning emerges from optimization.

2. **"Verifiable rewards only work for math and code."** Mostly true. Creative writing has no automatic verifier. But math, code, logic, and games all work well.

3. **"The model understands reasoning in a human sense."** No. It learns patterns that correlate with correct answers. But the reasoning chains are genuinely useful.

4. **"Process reward models (PRM) are required."** No. DeepSeek-R1 uses outcome rewards only (final answer correct/incorrect). PRM can help but is not necessary.

5. **"The model never makes reasoning mistakes."** It does. Verifiable rewards only check the final answer, not the path. A model can reason convincingly and still be wrong.

---

### Where It Is Used in Our Code

`src/phase42/phase42_verifiable_rewards.py` — A toy arithmetic task where the model generates reasoning chains. GRPO-style training rewards correct final answers. We visualize how reasoning length and accuracy improve over training.
