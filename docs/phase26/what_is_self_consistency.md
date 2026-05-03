### 1. Why it exists (THE PROBLEM first)
Even with Chain of Thought, a model can produce a single reasoning chain that happens to be wrong. Sampling one answer is risky because a single unlucky sample can mislead us. We need a way to reduce variance by generating multiple answers and aggregating them into a more reliable final result.

### 2. Definition (very simple)
Self-Consistency is a decoding strategy where the model generates multiple independent answers to the same question (each with its own reasoning chain), and the final answer is chosen by majority vote. It is an ensemble method applied at inference time.

### 3. Real-life analogy
You are unsure of the answer to a trivia question. Instead of trusting your first guess, you ask five friends independently. Four say "Paris" and one says "London." You go with "Paris" because the majority agrees. Each friend might have different reasoning, but the consensus is more trustworthy than any single opinion.

### 4. Tiny numeric example
Question: "If a bat and ball cost $11 total, and the bat costs $10 more than the ball, how much does the ball cost?"

Sample 1 (wrong): "Bat = $10, ball = $1. Difference is $9. Hmm, that is not $10 more. Let me try again. Bat = $10.50, ball = $0.50. Answer: $0.50"

Sample 2 (correct): "Let ball = x. Bat = x + 10. Total: x + (x + 10) = 11. 2x + 10 = 11. 2x = 1. x = 0.50. Answer: $0.50"

Sample 3 (wrong): "$11 - $10 = $1. Answer: $1.00"

Sample 4 (correct): "x + (x + 10) = 11, 2x = 1, x = 0.50. Answer: $0.50"

Sample 5 (correct): "Ball = $0.50, bat = $10.50. Total $11. Answer: $0.50"

Votes: $0.50 appears 3 times, $1.00 appears 1 time, $10.50 appears 1 time.
Majority vote: **$0.50** (correct).

### 5. Common confusion
- **Self-Consistency is not training.** The model is not fine-tuned or updated. It is purely an inference-time technique.
- **It only works when answers can be compared.** For open-ended creative writing, there is no easy way to vote. It works best on math, multiple-choice, and structured reasoning.
- **It increases compute linearly.** 10 samples = 10x the inference cost. The accuracy gains usually justify the cost on hard problems but not on easy ones.
- **Majority vote is not always optimal.** If the model is systematically biased, all samples might be wrong in the same direction. Self-Consistency reduces random noise, not systematic error.
- **It is different from beam search.** Beam search keeps the top-k partial sequences at each step. Self-Consistency generates complete independent answers and votes at the end.

### 6. Where it is used in our code
`src/phase26/phase26_test_time_compute.py` generates multiple reasoning chains for the same math problem and uses majority voting to select the most consistent answer.
