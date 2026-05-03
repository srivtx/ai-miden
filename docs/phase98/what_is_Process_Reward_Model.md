## What Is Process Reward Model?

---

### The Problem

A model generates a ten-step proof to solve a math problem. The final answer is wrong, but the proof is so long and technical that a human grader cannot pinpoint where the logic broke. An Outcome Reward Model (ORM) only scores the final result, so it knows the proof failed but has no signal about which step to blame. Without step-level feedback, the model cannot learn which parts of its reasoning to fix. How do you provide a training signal for every link in the chain, not just the last one?

---

### Definition

A **Process Reward Model (PRM)** is a trained model or scoring function that assigns a reward to each intermediate step of a reasoning chain, not merely to the final output. By scoring every step, the PRM enables search algorithms to prune bad partial paths early and provides fine-grained gradients for training chain-of-thought generators.

**How it works:**
```
Reasoning chain:   Step 1 -> Step 2 -> Step 3 -> Step 4 -> Final Answer
ORM scores:        [ignore] [ignore] [ignore] [ignore] -> 0.0 (wrong)
PRM scores:        1.0      1.0      0.2      0.1      -> 0.0 (wrong)
                           ^
                           |
                    Step 3 is the problem. Backtrack here.
```

**Key properties:**
- Scores are typically binary (correct / incorrect) or continuous (confidence).
- Can be trained on human step labels, automated theorem provers, or model-based critiques.
- Enables Monte Carlo Tree Search and beam search over reasoning steps.

**Why this matters:**
- An ORM only tells you that a proof failed; a PRM tells you where.
- PRM-guided search can explore 10x fewer nodes than exhaustive search by pruning early.
- It is the critical component for training models that "think longer" without human labels at every length.

---

### Real-Life Analogy

Imagine a student submitting a ten-page calculus proof to a professor. The professor could grade it the lazy way: read only the final line, see that it does not match the expected result, and hand back a failing grade with no comments. The student learns nothing except that the proof is wrong somewhere. Now imagine the professor grades it the hard way: reading every line, placing a checkmark next to valid steps, and circling the exact line where an integration by parts was misapplied. The student now knows precisely which skill to practice. The Process Reward Model is that diligent professor. It does not just judge the outcome; it supervises the process.

The trade-off is annotation cost. Grading every line of every proof takes ten times as long as grading only the final answer. Training a PRM requires a dataset of step-level labels, which are expensive to collect from humans and tricky to generate automatically. Automated verifiers work for math and code but struggle for open-ended reasoning. There is also a risk of false precision: a PRM might confidently flag a correct step as wrong because it was trained on a narrow distribution of solution styles. Like any automated grader, it is a useful but imperfect substitute for human oversight.

---

### Tiny Numeric Example

**Search tree with Outcome Reward Model:**
```
Step 1: 3 candidate continuations
Step 2: 3 candidates each -> 9 partial chains
Step 3: 3 candidates each -> 27 partial chains
Step 4: 3 candidates each -> 81 full chains
ORM evaluates: 81 final answers
Correct answer found? Yes, after 81 evaluations.
```

**Search tree with Process Reward Model:**
```
Step 1: 3 candidates. PRM scores: [0.9, 0.3, 0.2]. Prune the 0.2 branch.
Step 2: 2 candidates * 3 = 6 partial chains.
       PRM scores top continuations: [0.8, 0.7, 0.4, 0.3, 0.2, 0.1]
       Prune below 0.5 threshold -> keep 2 chains.
Step 3: 2 candidates * 3 = 6 partial chains.
       PRM scores: [0.9, 0.8, 0.6, 0.5, 0.3, 0.1]
       Prune below 0.5 -> keep 4 chains.
Step 4: 4 full chains evaluated by ORM.
Correct answer found? Yes, after 4 + 6 + 6 + 4 = 20 evaluations.
```

**Evaluation count comparison:**
```
Method              | Evaluations | Correct answer found
--------------------|-------------|----------------------
Exhaustive search   | 81          | Yes
ORM + random sample | 10          | Maybe (no step guidance)
PRM-guided beam     | 20          | Yes (with early pruning)
```

**The shift:** The PRM reduces the search space by 75% while maintaining correctness, because it stops investing compute in partial chains that have already gone off track.

---

### Common Confusion

1. **"A PRM is the same as an ORM with more granularity."** The architecture may be similar, but the training data and usage are fundamentally different. An ORM is trained on (full chain, final correctness) pairs. A PRM is trained on (step, step correctness) pairs, which requires a different labeling pipeline.

2. **"PRMs eliminate the need for final-answer checking."** They do not. A chain can have all correct intermediate steps and still arrive at a wrong conclusion due to a missing final transformation. PRMs and ORMs are complementary.

3. **"PRMs are easy to train automatically."** Only in domains with automated verifiers like math and code. For open-ended reasoning, step labels still require expensive human annotation or model-based distillation, which introduces its own biases.

4. **"A high PRM score guarantees the step is correct."** No. The PRM is a learned model, not an oracle. It can be overconfident on out-of-distribution reasoning styles or adversarially fooled by plausible-looking nonsense.

5. **"PRMs are only useful for math."** They apply to any multi-step task: code synthesis, logical deduction, theorem proving, and even physical reasoning. Any domain where intermediate states can be checked benefits from process supervision.

6. **"PRM-guided search is always better than sampling."** The overhead of running the PRM at every step adds latency. For short chains or low-stakes tasks, simple self-consistency may be cheaper and equally effective.

7. **"PRMs train the generator directly."** Typically they train a separate critic model. The generator is then trained with reinforcement learning or filtered supervised learning using the PRM's scores as rewards or filters.

---

### Where It Is Used in Our Code

`src/phase98/phase98_system2_reasoning.py` — We simulate reasoning chains with per-step correctness probabilities and show how an outcome-only evaluator cannot locate errors, while a process-level evaluator can identify the first wrong step. We compare search efficiency with and without step-level pruning, and we plot how accuracy scales with the number of sampled chains under different scoring strategies.
