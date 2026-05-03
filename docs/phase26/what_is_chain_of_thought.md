### 1. Why it exists (THE PROBLEM first)
Large language models often jump straight to an answer, which leads to errors on multi-step problems like math or logic puzzles. A model that immediately says "The answer is 27" might have silently made a mistake in step 3. We need a way to force the model to show its work so errors are visible and correctable.

### 2. Definition (very simple)
Chain of Thought (CoT) prompting is the technique of asking a model to generate intermediate reasoning steps before giving its final answer. Instead of answering directly, the model writes out its thinking process, making each step explicit and inspectable.

### 3. Real-life analogy
A student is given a hard word problem. If they write only the final number, the teacher cannot tell where they went wrong. If the student shows every step — "First I converted miles to kilometers, then I divided by speed, then I added the delay" — the teacher can spot errors and the student is more likely to catch their own mistakes.

### 4. Tiny numeric example
Prompt without CoT:
```
Q: A train travels 60 km/h. How far does it go in 2.5 hours?
A: 150
```
The model might say 120 (wrong) or 150 (right), but you cannot tell why.

Prompt with CoT:
```
Q: A train travels 60 km/h. How far does it go in 2.5 hours?
A: Let's think step by step.
   Distance = Speed x Time
   Distance = 60 km/h x 2.5 h
   Distance = 150 km
   The answer is 150 km.
```
Even if the model makes a mistake — "60 x 2 = 120, plus half of 60 = 30, total 150" — you can see the reasoning and verify it.

### 5. Common confusion
- **CoT is not a model architecture change.** It is a prompting technique. You do not retrain the model; you simply change the prompt to ask for step-by-step reasoning.
- **It does not guarantee correctness.** A model can generate plausible-sounding but wrong reasoning steps. CoT makes errors easier to spot, not impossible.
- **Zero-shot CoT exists.** You can add "Let's think step by step" to any prompt without providing examples. Few-shot CoT gives example reasoning chains in the prompt.
- **Not all problems benefit.** Simple factual questions ("What is the capital of France?") do not need CoT. It helps most on math, logic, and multi-step reasoning.
- **CoT increases token count.** More tokens = slower inference and higher cost. The trade-off is accuracy for speed.

### 6. Where it is used in our code
`src/phase26/phase26_test_time_compute.py` demonstrates a tiny arithmetic solver with and without CoT prompting, showing accuracy improvement when intermediate steps are required.
