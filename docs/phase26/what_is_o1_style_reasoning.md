### 1. Why it exists (THE PROBLEM first)
Traditional LLMs spend the same amount of compute on every question, whether it is "What is 2+2?" or "Prove Fermat's Last Theorem." Hard problems need more thinking time, but standard autoregressive generation produces an answer in one forward pass. We need a way for the model to dynamically allocate more computation to harder problems.

### 2. Definition (very simple)
o1-style reasoning (pioneered by OpenAI's o1 model) is the paradigm of training models to generate long chains of reasoning — sometimes thousands of tokens — before producing a final answer. The model learns to explore different approaches, backtrack from dead ends, verify intermediate results, and generally "think longer" when faced with difficult problems.

### 3. Real-life analogy
A timed quiz forces every student to finish in 10 minutes, regardless of the question difficulty. A take-home exam lets students spend 30 minutes on easy questions and 3 hours on hard ones. o1-style reasoning is like giving the model a take-home exam: it can use as much compute as the problem demands, revising and checking its work along the way.

### 4. Tiny numeric example
Standard LLM on a hard problem:
```
Q: Find the sum of all prime numbers between 10 and 30.
A: 11 + 13 + 17 + 19 + 23 + 29 = 112
```
(One pass, 10 tokens, no verification. If it missed 29, the error is invisible.)

o1-style reasoning on the same problem:
```
Q: Find the sum of all prime numbers between 10 and 30.
A: Let me list numbers 10-30 and check primality:
   10: even, not prime
   11: prime (only divisible by 1 and 11)
   12: even, not prime
   13: prime
   14: even, not prime
   15: divisible by 3 and 5, not prime
   16: even, not prime
   17: prime
   18: even, not prime
   19: prime
   20: even, not prime
   21: 3 x 7, not prime
   22: even, not prime
   23: prime
   24: even, not prime
   25: 5 x 5, not prime
   26: even, not prime
   27: 3 x 9, not prime
   28: even, not prime
   29: prime
   30: even, not prime
   Primes: 11, 13, 17, 19, 23, 29
   Sum: 11 + 13 = 24; 24 + 17 = 41; 41 + 19 = 60; 60 + 23 = 83; 83 + 29 = 112
   Verify: 112. Correct.
```
(Multiple passes, 150+ tokens, self-verification, explicit enumeration. Harder to make an invisible mistake.)

### 5. Common confusion
- **o1 is not just longer CoT.** It is trained with reinforcement learning on Process Reward Models to prefer longer, more thorough reasoning. The model learns that spending more tokens often yields better answers.
- **It is not free.** More tokens = more compute = more cost and latency. The trade-off is deliberate: accuracy at the expense of speed.
- **Not all tasks need it.** For simple Q&A, o1-style reasoning is wasteful. It shines on math, coding, science, and complex planning.
- **The model learns to manage its own budget.** Through training, it learns when to stop thinking and when to keep exploring. This is different from simply setting a high max_token limit.
- **Test-time compute scaling is the key insight.** Instead of only scaling model size (bigger model = better), you can also scale inference time (more thinking = better). Both axes matter.

### 6. Where it is used in our code
`src/phase26/phase26_test_time_compute.py` simulates o1-style reasoning by giving a model multiple "thinking tokens" to explore different solution paths before committing to a final answer, comparing accuracy against a single-pass baseline.
