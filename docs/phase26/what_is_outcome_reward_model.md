### 1. Why it exists (THE PROBLEM first)
The simplest way to judge a model's reasoning is to check whether the final answer is correct. If the answer is right, the reasoning was good enough. This is easy to implement because final answers are easy to verify (especially for math problems with known solutions). However, it misses everything that happens along the way.

### 2. Definition (very simple)
An Outcome Reward Model (ORM) is a model that assigns a single reward based only on the final output, ignoring the intermediate reasoning steps. It answers one question: "Was the final answer correct?"

### 3. Real-life analogy
A teacher who grades only the final exam score. If you get 95%, the teacher assumes you studied well. If you get 40%, the teacher assumes you did not. But the teacher never sees that you understood chapters 1-4 perfectly and only failed chapter 5. The feedback is coarse: pass or fail, with no detail about where you struggled.

### 4. Tiny numeric example
Problem: What is 15% of 80?

Reasoning Chain A:
"10% of 80 = 8. 5% of 80 = 4. 8 + 4 = 12. Answer: 12"
- ORM: Correct answer = +1.0

Reasoning Chain B:
"15% = 0.15. 0.15 x 80 = 12. Answer: 12"
- ORM: Correct answer = +1.0

Reasoning Chain C:
"15% of 80 = 15 x 80 = 1200. Then divide by 100 = 12. Answer: 12"
- ORM: Correct answer = +1.0 (even though the intermediate step 15 x 80 = 1200 is weird, the final answer is right)

Reasoning Chain D:
"15% of 80 = 0.15 x 80 = 12.0. But I think the answer is 12.5."
- ORM: Wrong answer = -1.0 (even though the reasoning was almost perfect)

The ORM cannot distinguish between elegant reasoning (B), weird-but-lucky reasoning (C), and almost-perfect reasoning with a silly final mistake (D).

### 5. Common confusion
- **ORM is not useless.** It is simple, cheap, and works well for problems where the final answer is all that matters. Most RLHF systems use ORMs because they are easier to build.
- **ORM + CoT is common.** You generate a reasoning chain but only reward the final answer. This still gets much of CoT's benefit (better reasoning through explicit steps) without the cost of step-level labels.
- **ORMs are easier to automate.** For math problems, you can use a Python interpreter to check the final answer. PRMs need human judgment or another model for every step.
- **The trade-off is granularity.** ORM = coarse, cheap, scalable. PRM = fine-grained, expensive, more informative.

### 6. Where it is used in our code
`src/phase26/phase26_test_time_compute.py` compares ORM scoring (final answer only) against PRM scoring (step by step) on the same reasoning chains, showing when each succeeds and fails.
