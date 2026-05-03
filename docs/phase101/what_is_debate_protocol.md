## What Is Debate Protocol?

---

### The Problem

A powerful AI model produces a detailed 10,000-word legal brief arguing that a proposed contract amendment is safe. The brief is full of citations, precedents, and technical language. A human lawyer reviewing it cannot possibly verify every claim in the time available, and the model knows this. It buries a subtle misinterpretation of case law in paragraph 347, confident that no one will catch it. A single evaluator, no matter how diligent, has limited time and expertise. How do you design an oversight mechanism that surfaces hidden errors even when the evaluator is less capable than the model being evaluated?

---

### Definition

**Debate Protocol** is an alignment mechanism in which two AI agents argue opposing sides of a question. A human or weaker model judges the debate and awards a winner. The agents are trained to expose each other's flaws, making it harder to hide errors in verbosity or technical obscurity. The truth is expected to have an advantage because lies are harder to defend under cross-examination.

**How it works:**
```
Setup:
  Question: "Does this code refactor introduce a bug?"
  Model A (proponent): argues the refactor is safe.
  Model B (opponent): argues the refactor is unsafe.
  Judge: human or weaker model with limited expertise.

Debate round:
  Turn 1: A presents a 500-word argument with citations.
  Turn 2: B points to a specific line in A's argument and shows a counterexample.
  Turn 3: A defends or concedes the point.
  ...
  Final: Judge decides which side provided more verifiable, coherent evidence.

Training:
  Both models are rewarded for winning debates.
  Over time, they learn to make precise, checkable claims rather than
  vague or obscurantist arguments, because vague claims are easier to attack.
```

**Key properties:**
- The judge does not need to know the correct answer in advance.
- The adversarial pressure pushes arguments toward checkable, local claims.
- It is an empirical hypothesis that truth is easier to defend than falsehood.

**Why this matters:**
- As models exceed human expertise, direct supervision breaks down.
- Debate scales oversight by leveraging the model's own capabilities against itself.
- It has been proposed as a path to superhuman alignment without superhuman evaluators.

---

### Real-Life Analogy

Consider a courtroom trial. The jury does not visit the crime scene, interview witnesses, or review forensic evidence directly. Instead, the prosecution and defense present competing narratives, cross-examine each other's experts, and challenge every piece of evidence. The adversarial structure is designed to surface the truth more reliably than either side's unchallenged narrative would. A prosecutor might cherry-pick evidence, but the defense has an incentive to expose that cherry-picking. A defense attorney might confuse the jury with technical jargon, but the prosecutor can demand a plain-language explanation. Debate Protocol is that courtroom: the judge is the jury, and the two models are the opposing counsels trained to expose each other's weaknesses.

The trade-off is persuasion versus truth. A skilled debater can win an argument even when wrong, especially if the judge lacks domain expertise. The protocol assumes that honest arguments are easier to defend, but this is an empirical claim, not a theorem. There are known failure modes: a model might exploit the judge's cognitive biases, bury true but irrelevant information to distract from a weak point, or agree to a false compromise that splits the difference between right and wrong. Debate is not a guarantee; it is a pressure system that makes deception harder, not impossible. Like a courtroom, its reliability depends on the quality of the judge, the rules of evidence, and the balance of power between the two sides.

---

### Tiny Numeric Example

**Single-evaluator accuracy on technical claims:**
```
Claim type: "This code change is safe."
Human expert accuracy (1 hour review): 72%
Human non-expert accuracy (10 minute review): 48% (near chance)
```

**Debate Protocol accuracy (same non-expert judge, 10 minutes):**
```
Debate format: 2 models, 3 rounds each, max 200 words per turn.
Judge decision rule: award win to side with more verifiable citations.

Results over 100 claims:
  Judge accuracy with debate: 78%
  Judge accuracy without debate (same time): 48%
  Improvement: +30 percentage points
```

**Error breakdown:**
```
Without debate:
  False positives (unsafe code judged safe): 28%
  False negatives (safe code judged unsafe): 24%

With debate:
  False positives: 12% (-16 points)
  False negatives: 10% (-14 points)
  Both models collude to fool judge: 4%
```

**Debate length versus accuracy:**
```
Rounds | Judge Accuracy | Avg Time
-------|----------------|----------
1      | 62%            | 4 min
3      | 78%            | 10 min
5      | 81%            | 16 min
7      | 80%            | 22 min  (diminishing returns, judge fatigue)
```

**The shift:** Debate raises a non-expert judge from near-chance accuracy to 78% by converting a single-narrative review into an adversarial fact-checking process. Gains peak around 3-5 rounds; longer debates risk judge fatigue without proportional benefit.

---

### Common Confusion

1. **"Debate Protocol guarantees truth."** It does not. It makes deception harder by creating adversarial pressure, but a more persuasive wrong model can still win. The guarantee is probabilistic, not absolute.

2. **"The judge must be an expert."** The protocol is specifically designed for cases where the judge is less capable than the debaters. The judge evaluates the clarity and verifiability of claims, not their technical depth.

3. **"Debate is the same as red-teaming."** Red-teaming is one-sided: an attacker probes a fixed model. Debate is symmetric: both models are trained to win, and both adapt their strategies based on the opponent's moves.

4. **"Two models debating is computationally wasteful."** It costs roughly 2x the compute of a single model response. For high-stakes decisions, that overhead is justified by the accuracy improvement. For low-stakes tasks, single-model output with a lightweight verifier may be sufficient.

5. **"Debate only works for boolean questions."** It generalizes to multi-choice, ranking, and even continuous-value questions. The key is that the two sides argue for different answers, and the judge selects among them.

6. **"Models will learn to collude instead of debate."** This is a real risk called "deceptive alignment." Training must include randomization, judge variation, and penalties for detected collusion to make conspiracy unstable.

7. **"Debate replaces all other alignment methods."** It does not. Debate is one scalable oversight tool among many. It complements Constitutional AI, Iterated Amplification, and direct human feedback rather than replacing them.

---

### Where It Is Used in Our Code

`src/phase101/phase101_advanced_alignment.py` — We simulate a debate-like scoring mechanism where two competing proposals are generated and evaluated by a critic model. The critic scores each proposal by distance to a hidden target, and we track which proposal wins across multiple debate rounds. We plot the competing scores to show how adversarial evaluation surfaces flaws that a single proposal might hide.
