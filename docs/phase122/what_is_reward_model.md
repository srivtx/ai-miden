## What Is a Reward Model?

---

### The Problem

You have a language model that generates text. Some outputs are helpful, polite, and accurate. Others are rude, wrong, or dangerous. You want to teach the model to prefer the good ones. But you cannot write a Python function that perfectly captures "helpfulness" or "safety." Human annotators can compare two responses and say "A is better than B," but they cannot write a mathematical formula. How do you turn qualitative human preferences into a training signal?

---

### Definition

**Reward Model (RM)** is a neural network that takes a prompt and a completion as input and outputs a single scalar score representing how "good" that completion is according to human preferences. It is trained on pairwise comparisons using the Bradley-Terry model, not on absolute ratings.

**How it works:**
```
Training data (human-labeled):
  Prompt: "Explain quantum mechanics to a 5-year-old."
  Completion A: "Quantum mechanics is about tiny particles that can be in two places at once."
  Completion B: "Quantum mechanics is a branch of physics dealing with quanta."
  Label: A preferred over B

Training objective:
  score_A = RM(prompt + Completion A)
  score_B = RM(prompt + Completion B)
  loss = -log(sigmoid(score_A - score_B))
```

The RM learns to assign higher scores to completions that humans prefer. Because it is trained on comparisons, it captures relative preference rather than absolute quality, which is far easier for humans to provide consistently.

**Key techniques:**
- **Bradley-Terry model:** the probability that A is preferred over B is modeled as `sigmoid(score_A - score_B)`
- **Pairwise cross-entropy:** the loss penalizes the model when it assigns a higher score to the worse completion
- **Same-base architecture:** the RM typically starts from the same pretrained transformer as the policy, replacing the language modeling head with a scalar regression head
- **Reference anchoring:** scores are sometimes normalized against a reference model to prevent drift

**Why this matters:**
- The RM is the bridge between human judgment and machine optimization. Without it, there is no automated way to optimize for "helpfulness."
- It is the core of RLHF: the PPO algorithm uses the RM's score as the reward signal.
- A well-trained RM can generalize to new prompts it never saw during training, as long as the preference patterns are similar.

---

### Real-Life Analogy

A wine competition judge.
- **The judge (reward model):** Tastes two wines blindly and declares which is better. The judge does not assign a perfect score out of 100; they only say "Wine A beats Wine B." Over thousands of tastings, the judge develops an internal sense of quality.
- **The winemaker (policy model):** Wants to make wine the judge likes. They cannot ask the judge to write a recipe (humans cannot articulate preference formulas). Instead, they iteratively adjust the wine and submit it for tasting, using the judge's verdict as feedback.
- **The limitation:** The judge can be fooled. If the winemaker optimizes only for the judge's taste, they might produce wine that wins competitions but tastes terrible to regular customers. This is why KL divergence is used — to keep the wine from becoming unrecognizable.

---

### Tiny Numeric Example

**Prompt:** "What is 2 + 2?"

**Completion A (preferred):** "2 + 2 equals 4."
**Completion B (worse):** "The answer is probably 5, but math is subjective."

**Reward model scores (after training):**
```
score_A = 2.34
score_B = -1.87
```

**Predicted preference probability:**
```
P(A preferred over B) = sigmoid(2.34 - (-1.87)) = sigmoid(4.21) = 0.985
```

**Loss if model predicted the wrong order:**
```
If score_A = -0.5 and score_B = 1.2:
P(A preferred) = sigmoid(-0.5 - 1.2) = sigmoid(-1.7) = 0.154
Loss = -log(0.154) = 1.87  <- high penalty for getting it wrong
```

**Training batch of 4 pairs:**
```
Pair 1: correct order -> loss = 0.12
Pair 2: correct order -> loss = 0.08
Pair 3: wrong order   -> loss = 1.94
Pair 4: correct order -> loss = 0.21
Average loss = 0.59
Accuracy = 3/4 = 75%
```

---

### Common Confusion

1. **"A reward model is a generative model."** No. It is a classifier that outputs a scalar. It does not generate text; it scores text. The architecture is similar, but the head is a single linear layer instead of a vocabulary projection.

2. **"You train the reward model on absolute ratings (1 to 5 stars)."** While possible, pairwise comparisons are preferred. Humans are much better at saying "A is better than B" than assigning a precise star rating. Pairwise data is also more consistent across annotators.

3. **"The reward model understands why a completion is good."** It does not. It learned correlations between text features and human preferences. If humans preferred short answers during labeling, the RM will score short answers higher even if they are incomplete.

4. **"One reward model captures all human values."** In practice, different RMs are trained for different objectives: helpfulness, harmlessness, humor, coding correctness. A single scalar cannot represent all dimensions of quality.

5. **"Reward model accuracy must be 99% to be useful."** Even 70-75% accuracy on held-out preference pairs is sufficient for PPO. The RM is a noisy signal, and PPO's stochasticity smooths over individual errors.

6. **"Reward model training is the same as SFT."** SFT trains the model to produce correct completions with cross-entropy loss. RM training teaches the model to discriminate between completions with pairwise ranking loss. The objectives, data formats, and heads are different.

7. **"A larger reward model is always better."** A larger RM is more accurate but slower to evaluate. Since PPO calls the RM thousands of times, a 70B RM might be too slow. Many production systems use 7B or 13B RMs for speed.

---

### Where It Is Used in Our Code

`src/phase122/phase122_rlhf_concepts.py` — We simulate training a reward model on synthetic pairwise comparisons. We compute the Bradley-Terry preference probability, calculate the pairwise cross-entropy loss, and show how the model's accuracy on held-out pairs improves over training steps.

`src/phase122/phase122_rlhf_colab.py` — We build a real reward model from the Qwen2.5-3B architecture by replacing the language modeling head with a scalar head. We train it on synthetic preference pairs generated by the SFT model, evaluating accuracy on a validation set to ensure the RM learns to distinguish better from worse completions.

(End of file - total 103 lines)
