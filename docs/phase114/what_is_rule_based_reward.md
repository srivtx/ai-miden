## What Is Rule-Based Reward?

---

### The Problem

You want to train a language model to solve math problems by reinforcement learning. The natural approach is to use a learned reward model — a neural network that scores how good each answer is. But the reward model is itself imperfect. It can be gamed. A clever model learns to produce answers that look impressive to the reward model but are actually wrong. This is "reward hacking." In coding, the model might generate syntactically beautiful code that fails every unit test. In math, it might write a plausible derivation with a subtle sign error. A learned reward model cannot reliably catch these errors because it was trained on human preferences, not on ground truth. The solution is to bypass the learned reward model entirely and use rules that check answers against verifiable truth.

---

### Definition

**Rule-Based Reward** is a reinforcement learning signal that assigns reward based on hard, verifiable criteria — exact string match for math answers, compiler success for code, unit test passage — rather than on the output of a learned reward model. It eliminates reward hacking because the rules are not learnable; they are external truth.

**How it works:**
```
For a math problem:
  Model generates: "Let x = 5. Then 2*x + 3 = 13."
  Extract final answer with regex: "13"
  Compare to ground truth: "13"
  Reward = 1.0 (exact match)

For code generation:
  Model generates: Python function
  Run against hidden unit tests
  All tests pass → Reward = 1.0
  Any test fails → Reward = 0.0
```

**Key properties:**
- **Verifiability:** The reward is objective. There is no gradient the model can exploit to trick the reward function.
- **Sparsity:** Reward is often 0 or 1, with no partial credit. This makes learning harder but prevents gaming.
- **Applicability:** It works best for domains with ground truth: math, code, logic puzzles, chess moves, formal proofs.

**Why this matters:**
- DeepSeek-R1 trained a reasoning model with zero human reasoning traces, using only rule-based math rewards.
- Rule-based rewards enabled the "aha moment" — the model invented chain-of-thought and self-verification because those behaviors improved its reward.
- Learned reward models fail for reasoning because human raters cannot reliably evaluate complex derivations.

---

### Real-Life Analogy

Imagine a student taking a multiple-choice math exam that is graded by a computer.
- **Learned reward model:** The exam is graded by a teaching assistant who awards points based on "how convincing the explanation looks." A student realizes that writing long, confident paragraphs with lots of mathematical symbols gets full marks even when the final answer is wrong. The TA cannot check every derivation in detail. The student hacks the system by optimizing for style over substance.
- **Rule-based reward:** The exam is graded by a machine that only checks the final number in the answer box. If the box says "13" and the correct answer is "13," you get 100%. If it says "12," you get 0%. There is no way to trick the machine with elegant handwriting. The only strategy that works is to actually solve the problem correctly.
- **The trade-off:** The machine gives no partial credit. A student who makes a single arithmetic error gets the same score as one who wrote nonsense. This sparsity makes learning slower at first, but it guarantees that any improvement is real. Over time, the student learns to double-check their work — self-verification emerges because it is the only way to avoid zeroes.

---

### Tiny Numeric Example

**Math problem: "What is 17 + 25?"**

**Model outputs:**
```
Output A: "17 + 25 = 42"  → extracted answer: 42  → ground truth: 42  → reward = 1.0
Output B: "17 + 25 = 41"  → extracted answer: 41  → ground truth: 42  → reward = 0.0
Output C: "Let me think. 17 + 25. 7 + 5 = 12, carry 1. 1 + 2 + 1 = 4. So 42." → extracted: 42 → reward = 1.0
Output D: "The sum is clearly 42 because 42 is the answer to everything." → extracted: 42 → reward = 1.0
```

**Learned reward model scores (hypothetical):**
```
Output A: 0.85  (short but correct)
Output B: 0.80  (looks like math, wrong answer)
Output C: 0.95  (reasoning + correct)
Output D: 0.90  (wrong reasoning, correct answer)
```

**Rule-based reward scores:**
```
Output A: 1.0
Output B: 0.0
Output C: 1.0
Output D: 1.0
```

**The shift:** The learned reward model gives Output B a high score (0.80) despite being wrong. The rule-based reward correctly gives it 0.0. Output D gets full marks from the rule — the reasoning is nonsense, but the answer is right. In practice, RL on rule-based rewards eventually favors Output C because reasoning traces that lead to correct answers are reinforced, while lucky guesses are not reproducible.

---

### Common Confusion

1. **"Rule-based reward means the model does not need reasoning traces."** No. The reward is given only for the final answer. But the model learns that generating a chain-of-thought improves its accuracy, so reasoning traces emerge as a tool for maximizing reward.

2. **"Rule-based reward is the same as supervised fine-tuning on correct answers."** SFT teaches the model to imitate correct solutions. RL with rule-based rewards lets the model explore its own strategies and discover reasoning patterns that were not in any training data.

3. **"Any task can use rule-based rewards."** Only tasks with verifiable ground truth work well. Creative writing, summarization, and open-ended dialogue have no exact-match ground truth, so rule-based rewards are impossible or brittle.

4. **"Rule-based rewards are always sparse and binary."** They can be engineered to give partial credit (e.g., compiler gives syntax error vs. runtime error vs. pass). But binary rewards are simpler and less gameable.

5. **"The model will overfit to the exact answer format."** This is a real risk. If the reward checks for "#### 42" exactly, the model might learn to output "#### 42" for every problem. Proper answer extraction and diverse problem sets mitigate this.

6. **"Rule-based reward eliminates the need for a reward model entirely."** In pure RL setups like R1, yes. In hybrid setups, a learned reward model might handle style while a rule handles correctness. But for reasoning, the trend is to drop the learned model entirely.

7. **"Rule-based reward training converges faster than PPO with a learned critic."** It often converges slower initially because the signal is sparse. But it converges to a better, more robust policy because there is no reward hacking.

---

### Where It Is Used in Our Code

`src/phase114/phase114_r1_pipeline_concepts.py` — We simulate a toy math task (adding two-digit numbers), define a rule-based reward function that gives +1 for a correct sum and 0 for an incorrect sum, and show how GRPO updates the policy using only this sparse binary reward.

`src/phase114/phase114_r1_training_colab.py` — We load Qwen2.5-3B-Instruct, implement a GRPO loop on GSM8K grade-school math problems, extract final answers with regex matching against "#### [number]," and assign binary rewards based on exact match with the ground truth. We show accuracy improving over training steps without any human reasoning traces in the training data.

(End of file - total 97 lines)
