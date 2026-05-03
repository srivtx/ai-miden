### 1. Why it exists (THE PROBLEM first)
Outcome reward models only judge the final answer. A model could reach the right answer through completely wrong reasoning (lucky guess) or reach the wrong answer after almost-correct reasoning. We need feedback at each step so the model learns HOW to reason, not just WHAT to output.

### 2. Definition (very simple)
A Process Reward Model (PRM) is a model that scores each intermediate reasoning step individually, not just the final result. It provides fine-grained feedback during the reasoning chain, allowing the model to learn which individual steps are good and which are flawed.

### 3. Real-life analogy
A basketball coach who only watches the final score cannot tell if the team won because of good strategy or lucky shots. A Process Reward Model is like a coach who reviews every play: "That pass was perfect (+1), that shot selection was poor (-1), that defensive rotation was excellent (+1)." The team learns from every action, not just the final whistle.

### 4. Tiny numeric example
Problem: Solve 2x + 6 = 14

Step 1: "Subtract 6 from both sides: 2x = 8"
- PRM score: +1.0 (correct operation)

Step 2: "Divide both sides by 2: x = 4"
- PRM score: +1.0 (correct operation)

Step 3: "Check: 2(4) + 6 = 14. Correct."
- PRM score: +1.0 (correct verification)

Total PRM reward: +3.0

Now imagine a wrong chain:
Step 1: "Subtract 6 from both sides: 2x = 8" (+1.0)
Step 2: "Divide by 4: x = 2" (-1.0, wrong divisor)
Step 3: "Check: 2(2) + 6 = 10. Not 14." (+0.5, caught the error but too late)

The PRM immediately flags Step 2 as wrong. An Outcome Reward Model might give +0.5 for catching the error at the end, but the PRM identifies exactly where the mistake happened.

### 5. Common confusion
- **PRM is not the same as CoT.** CoT is about generating reasoning steps. PRM is about EVALUATING each step. They work together: CoT produces the chain, PRM grades it.
- **PRMs are expensive to train.** You need human annotators to label every step as correct or incorrect, which is far more work than labeling final answers.
- **PRMs can be used at test time too.** You can use a PRM to guide search: at each step, try multiple continuations and pick the one with the highest PRM score.
- **They are not perfect.** A PRM might miss subtle errors or overvalue verbose but vacuous steps. Training data quality matters enormously.
- **OpenAI's o1 uses PRMs.** The breakthrough of o1-style reasoning comes partly from training on step-level rewards, not just final-answer rewards.

### 6. Where it is used in our code
`src/phase26/phase26_test_time_compute.py` simulates a Process Reward Model that scores each arithmetic step, showing how step-level feedback identifies exactly where reasoning goes wrong.
