## What Is Chain-of-Thought?

---

### The Problem

A large language model is asked to solve a problem that requires several intermediate deductions: calculating a total bill with tax and tip, or determining whether a logical syllogism is valid. The model tries to produce the final answer in a single leap, and because the leap is too far, it hallucinates a number or misapplies a rule. The error is invisible — there is no audit trail showing where the reasoning broke down. How do you force the model to decompose hard problems into verifiable steps?

---

### Definition

**Chain-of-Thought (CoT)** is a prompting and training technique in which the model generates an explicit sequence of intermediate reasoning steps before emitting the final answer. By externalizing its reasoning, the model turns one hard jump into a series of easier hops, each of which can be checked, corrected, or learned from.

**How it works:**
```
Standard prompt: "A train travels 60 mph for 2 hours, then 40 mph for 3 hours. What is the average speed?"
Standard answer: "48 mph" (may be correct or a lucky guess)

Chain-of-Thought prompt: "Explain your reasoning step by step."
CoT answer:
  Step 1: Distance 1 = 60 mph * 2 hours = 120 miles.
  Step 2: Distance 2 = 40 mph * 3 hours = 120 miles.
  Step 3: Total distance = 120 + 120 = 240 miles.
  Step 4: Total time = 2 + 3 = 5 hours.
  Step 5: Average speed = 240 / 5 = 48 mph.
```

**Key properties:**
- Can be elicited via few-shot examples or explicit instructions.
- Can be trained into the model by fine-tuning on step-by-step solutions.
- Makes errors localizable: if Step 3 is wrong, you know exactly where to intervene.

**Why this matters:**
- CoT improves accuracy on multi-step math from 17% to 78% in some benchmarks.
- It enables Process Reward Models to score individual steps, not just final answers.
- It produces interpretable reasoning that humans can audit and trust.

---

### Real-Life Analogy

Imagine solving a complex Sudoku puzzle entirely in your head. You stare at the grid, try to hold all the constraints simultaneously, and after thirty seconds you write down a number. If the number is wrong, you have no idea whether you made a counting error in the top-left box or misread a rule in the bottom-right. Now imagine solving the same puzzle with a pencil and paper, writing small candidate numbers in each cell, crossing them out as you eliminate possibilities, and annotating each placement with the rule that justified it. The written record does not just help you reach the answer — it makes every mistake visible the moment it happens, and it allows someone else to verify your logic without re-solving the puzzle from scratch. Chain-of-Thought is that pencil and paper: it is the model showing its work.

The trade-off is verbosity and compute. A CoT response might be ten times longer than a direct answer, which increases inference cost and latency. In time-critical applications — like real-time voice assistants — the extra tokens may be unacceptable. There is also a subtle failure mode: the model can generate plausible-sounding but logically hollow steps, a phenomenon sometimes called "fake reasoning." The steps look structured, but they do not actually constrain the final answer. CoT is powerful only when the reasoning is genuine, which is why it pairs well with verifiers and Process Reward Models.

---

### Tiny Numeric Example

**Direct-answer accuracy on a 20-question arithmetic test:**
```
Model without CoT:  6/20 correct (30%)
Model with CoT:    15/20 correct (75%)
```

**Error analysis of the 5 wrong CoT answers:**
```
Question 7:  Step 2 had a carry error. Final answer wrong.
Question 12: Step 4 used wrong formula. Steps 1-3 were correct.
Question 15: Step 1 misread the prompt. Propagated to final answer.
Question 18: All steps correct, but final transcription error.
Question 19: Fake reasoning — steps were grammatical but not logically connected.
```

**Step-level accuracy on Question 7 with and without correction:**
```
Step 1 (read prompt):    Correct
Step 2 (multiply):       Wrong  -> 42 * 3 = 126, model wrote 136
Step 3 (add):            Correct given wrong input (136 + 10 = 146)
Final answer:            146 (wrong)

If Step 2 is corrected to 126:
  Step 3 becomes 126 + 10 = 136
  Final answer: 136 (correct)
```

**The shift:** CoT does not eliminate errors, but it makes them local and fixable. A single-step correction turns a wrong answer into a right one, whereas a direct-answer model offers no surface for intervention.

---

### Common Confusion

1. **"Chain-of-Thought is just longer output."** Length alone does not constitute CoT. The output must contain structured, logically sequential steps that lead to the final answer. A rambling essay is not CoT.

2. **"CoT always improves accuracy."** It improves multi-step reasoning, but for simple factual retrieval it adds noise. Asking a model to "think step by step" before answering "What is the capital of France?" can cause it to hallucinate false intermediates.

3. **"CoT is only a prompting trick."** It can be trained into the model. Datasets of step-by-step solutions can be used for supervised fine-tuning, making CoT the default behavior rather than an ad-hoc prompt.

4. **"If the steps look correct, the answer is correct."** Not necessarily. A model can produce plausible-looking steps that contain a subtle error in step 3, then recover the right final answer by coincidence. Conversely, correct steps can be followed by a transcription error in the final line.

5. **"CoT makes the model truly reason."** This is debated. The model is still predicting tokens conditioned on the prompt. Whether that counts as "reasoning" depends on philosophical framing. CoT improves reliability, but it does not grant the model a human-like reasoning module.

6. **"You need special model architectures for CoT."** No. Any decoder-only transformer can generate CoT given the right prompt or fine-tuning data. No architectural changes are required.

7. **"CoT and Self-Consistency are the same thing."** CoT is the structure of reasoning within one sample. Self-Consistency is the aggregation of many samples. They are orthogonal: you can have CoT without Self-Consistency, and Self-Consistency without CoT (though they work best together).

---

### Where It Is Used in Our Code

`src/phase98/phase98_system2_reasoning.py` — We simulate reasoning chains where each step has an independent correctness probability. We compare the success rate of a single leap (direct answer) against a step-by-step chain, and we show how the stepwise structure makes error location possible. We also sweep over chain length to demonstrate where CoT provides the largest accuracy advantage.
