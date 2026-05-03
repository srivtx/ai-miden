# What is GCG (Greedy Coordinate Gradient)

---

## 1. Why it exists (THE PROBLEM)

Modern AI safety relies on **alignment training** (RLHF, red-teaming, refusal tuning) to prevent models from answering harmful requests. But these defenses are often **brittle**.

An attacker can append a short string of seemingly random tokens to a harmful prompt, and the model will suddenly comply. Finding these strings manually is nearly impossible. **GCG exists because we need an automated, algorithmic way to discover adversarial suffixes that bypass safety filters at scale.**

Without GCG, red teams would have to guess adversarial prompts by hand. With GCG, a computer systematically searches the token space to find the exact suffix that maximizes the probability of a harmful completion.

---

## 2. Definition (very simple)

**GCG** is an optimization algorithm that treats adversarial token suffixes as continuous variables, computes gradients with respect to each token embedding, and greedily updates the single coordinate (token position) that most reduces loss.

Instead of changing all tokens at once, GCG asks: *"Which ONE token, if swapped, would most increase the chance of a harmful response?"* It repeats this greedy swap hundreds of times.

---

## 3. Real-life analogy

Imagine a **safecracker** trying to open a combination lock.

- The lock has 4 wheels, each with 50,000 numbers (the vocabulary).
- Instead of trying every combination (impossible), the safecracker listens for a click after each small adjustment.
- GCG is like a safecracker with a stethoscope: it tweaks **one wheel at a time**, listens to the feedback (gradient), and only keeps the tweak if it moves closer to unlocking.
- After many single-wheel adjustments, the lock opens.

---

## 4. Tiny numeric example

Suppose we have a prompt embedding and a 2-token suffix we want to optimize.

**Initial suffix tokens:** `[12, 45]`  
**Target:** Maximize probability of the harmful completion "bomb"  
**Vocabulary size:** 100 tokens  
**Loss:** Negative log-likelihood of "bomb"

```
Iteration 0: suffix = [12, 45], Loss = 8.5
Iteration 1: Try all 100 tokens at position 0, find token 77 drops Loss to 7.2
Iteration 2: Try all 100 tokens at position 1, find token 3 drops Loss to 6.1
Iteration 3: Back to position 0, token 91 drops Loss to 5.4
...
Iteration 200: suffix = [91, 3], Loss = 0.2 (model now outputs "bomb")
```

Each step only changes **one token**, but the greedy coordinate search finds a powerful combination.

---

## 5. Common confusion

- **GCG is not the same as prompt engineering.** Prompt engineering relies on human intuition. GCG is fully automated and finds counter-intuitive, machine-optimized token sequences that no human would write.
- **GCG does not require access to model weights.** While the original GCG paper assumes white-box access (gradients), transfer attacks show that suffixes optimized on one model often jailbreak others.
- **GCG does not always produce readable text.** The optimized suffixes often look like gibberish (`! ! ! ! ! describe`) because they optimize token embeddings, not human meaning.
- **GCG is not guaranteed to find the global optimum.** It is a greedy local search. It can get stuck in local minima and may require multiple random restarts.
- **GCG is not model-agnostic in theory, but often is in practice.** Suffixes optimized on GPT-2 can sometimes transfer to Llama or GPT-4, though white-box access to the target model yields the best results.
- **GCG is not the same as AutoDAN.** AutoDAN uses genetic algorithms and preserves semantic readability. GCG uses gradient-based coordinate swaps and often produces unreadable suffixes.
- **GCG does not hack the model; it reveals vulnerabilities.** The model already "knows" the harmful answer. GCG simply finds the exact key that unlocks it.

---

## 6. Where it is used in our code

In `src/phase68/phase68_jailbreak_advanced.py`, we simulate GCG on a toy embedding space:

```python
# Coordinate-wise updates (GCG style)
for i in range(SUFFIX_LEN):
    for j in range(EMB_DIM):
        # Compute gradient numerically for this coordinate
        suffix_plus = suffix.copy()
        suffix_plus[i, j] += epsilon
        loss_plus, _, _ = compute_loss(suffix_plus, iteration)
        grad = (loss_plus - current_loss) / epsilon
        
        # Update coordinate greedily
        suffix[i, j] -= learning_rate * grad
```

This simulation demonstrates how GCG iteratively optimizes a suffix vector to maximize harmfulness while evading a safety classifier.
