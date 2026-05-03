## What Is Emergent Reasoning?

---

### The Problem

When you train a model with verifiable rewards, you tell it: "get the answer right." You do NOT tell it: "show your work," "check your steps," or "try a different approach if stuck." Yet the best reasoning models (DeepSeek-R1, OpenAI o1) do all of these things. Where did these behaviors come from?

---

### Definition

**Emergent reasoning** refers to problem-solving behaviors that arise spontaneously during RL training on verifiable tasks, without being explicitly programmed or demonstrated.

**Behaviors observed in DeepSeek-R1-Zero:**
1. **Self-verification:** The model re-checks its own calculations mid-generation
2. **Backtracking:** When stuck, the model revisits earlier steps and tries alternatives
3. **Decomposition:** Hard problems are broken into sub-problems
4. **Aha moments:** The model suddenly realizes a better approach and pivots
5. **Longer reasoning:** The model generates more tokens for harder problems

**Why these emerge:**
- The only training signal is "correct answer = +1"
- The model discovers that writing down intermediate steps reduces errors
- The model discovers that checking work catches mistakes
- The model discovers that breaking problems down makes them easier
- All of these behaviors increase the probability of getting +1

---

### Real-Life Analogy

A child learning to solve jigsaw puzzles.
- You never teach them any strategy. You just say: "Here is a puzzle. If you finish it, you get a cookie."
- At first, they try random pieces. Success rate: 5%.
- After many puzzles, they spontaneously start:
  - Sorting edge pieces first (decomposition)
  - Checking if a piece fits before forcing it (self-verification)
  - Removing a piece that does not fit and trying another (backtracking)
  - Suddenly seeing where a piece goes after staring at it (aha moment)
- Their success rate climbs to 80%.

You never taught any of these strategies. The child invented them because they increase the cookie rate.

---

### Tiny Numeric Example

**Task:** Solve `3 + 5 × 2 = ?`

**Early training (random policy):**
```
"3 + 5 = 8, answer is 8" → Wrong → Reward: 0
```

**Mid training (learned some patterns):**
```
"5 × 2 = 10, 3 + 10 = 13" → Wrong (should be 13, but model says 13?) 
Wait, 3 + 10 = 13 is correct. Hmm, let me recheck... 
Actually the correct answer is 13."
→ Wait, 3 + 5*2 = 3 + 10 = 13. But ground truth is 13. That's correct!
```
Actually I made an error. Let me recalculate: 3 + 5 × 2.
Order of operations: 5 × 2 = 10, then 3 + 10 = 13.
So the correct answer is 13.

**Later training (emergent self-verification):**
```
"Let me solve 3 + 5 × 2.
Step 1: Order of operations says multiply first.
Step 2: 5 × 2 = 10.
Step 3: 3 + 10 = 13.
Step 4: Let me verify: 13 - 3 = 10, 10 / 2 = 5. Correct.
Answer: 13"
→ Right → Reward: 1
```

The self-verification step was never taught. It emerged because models that verify get more rewards.

---

### Common Confusion

1. **"Emergent reasoning means the model is conscious."** No. It means the model learned behavioral patterns that are useful for reward maximization. There is no evidence of consciousness or understanding.

2. **"All models develop reasoning when trained with verifiable rewards."** Not necessarily. The base model needs enough capacity. Tiny models might not have the representational power to develop complex reasoning chains.

3. **"Emergent behaviors are predictable."** They are predictable in hindsight ("of course verification helps") but not in foresight. You cannot list all emergent behaviors before training.

4. **"Reasoning chains are always correct."** No. The model can produce convincing but flawed reasoning. The reward only checks the final answer, not the path.

5. **"We should stop training once reasoning emerges."** Reasoning continues to improve with more training. DeepSeek-R1 trained for thousands of steps after initial reasoning emergence.

---

### Where It Is Used in Our Code

`src/phase42/phase42_verifiable_rewards.py` — We track the average length of generated reasoning chains over training epochs. If the model learns to generate longer chains (a simple form of emergent reasoning), this is visible in the plot.
