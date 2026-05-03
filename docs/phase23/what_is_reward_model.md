### 1. Why it exists (THE PROBLEM first)
We want an AI to produce "helpful and harmless" responses, but no one can write a clean mathematical formula for those qualities. We cannot simply code a rule that says "if the text contains X, score = 10." What we *can* do is collect human judgments: humans look at two responses and say "A is better than B." A reward model turns those judgments into a single predictive score.

### 2. Definition (very simple)
A reward model is a neural network that takes a (prompt, response) pair and outputs a single scalar number representing how good that response is, trained on datasets of human preference comparisons so that it learns to mimic human ranking judgments.

### 3. Real-life analogy
A food critic tastes a dish and gives it a score from 1 to 10. They never derived a formula for "deliciousness"; they learned to score by comparing many dishes over many years. Similarly, the reward model learns to score text by observing thousands of human comparisons.

### 4. Tiny numeric example
For the same prompt, the reward model scores two candidate responses:
- **Response A:** 8.5
- **Response B:** 3.2

Because A > B, the model's loss function pushes it to widen that gap. The underlying RL algorithm then uses these scores to update the policy.

### 5. Common confusion
- **A reward model is not a loss function.** It is a separate model that *produces* a signal; the loss function for the policy is built around maximizing that signal.
- **It is not used in DPO.** Direct Preference Optimization skips the reward model entirely and optimizes from preferences directly.
- **It outputs a scalar, not a probability distribution.** Unlike the language model, it returns one number per (prompt, response) pair.
- **It is trained on comparisons, not absolute scores.** Humans say "A is better than B," not "A is an 8.5," and the model learns relative ranking.
- **A reward model can become a bottleneck.** If its training data is biased, the whole RLHF pipeline inherits that bias.

### 6. Where it is used in our code
Brief mention: The reward model is instantiated as a separate transformer head in our RLHF stage and is used to score completions before PPO updates are applied.
