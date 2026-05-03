## What Is Rejection Sampling?

---

### The Problem

Full RLHF requires a reward model, a reference model, PPO, KL penalties, and hyperparameter tuning that takes weeks of GPU time and costs thousands of dollars. You just want the model to stop saying dangerous things. You don't have a team of RL engineers. Is there a simpler way to improve safety without the complexity of full reinforcement learning?

---

### Definition

**Rejection Sampling** (also called best-of-n filtering or filtered supervised fine-tuning) is a safety training method where you generate multiple candidate responses for each prompt, filter out unsafe ones using a rule or classifier, and fine-tune the model on only the safe responses. It is simpler than full RLHF and often sufficient for moderate safety gains because it directly increases the probability mass on safe outputs without needing a learned reward model or policy gradients.

**How it works:**
```
Prompt → Generate 5 responses
           ↓
    [Safe, Unsafe, Safe, Safe, Unsafe]
           ↓
    Discard Unsafe responses
           ↓
    Fine-tune on [Safe, Safe, Safe]
           ↓
    Next time, model is more likely to sample Safe
```

**Key techniques:**
- **Best-of-n:** generate N responses, pick the highest-scoring safe one
- **Filtered SFT:** collect all safe responses across many prompts and run standard supervised fine-tuning
- **Rule-based filtering:** keyword checks, regex patterns, or classifier scores

**Why this matters:**
- Rejection sampling can be implemented in a day by any ML engineer who knows SFT
- It does not require PPO, critic models, or careful KL tuning
- It is the baseline that many safety teams use before moving to full RLHF

---

### Real-Life Analogy

A job interview panel.
- **Base model (no rejection sampling):** A company that hires the first candidate who walks in. They get some great employees and some who steal from the cash register. They fire the bad ones after the fact, but the damage is done.
- **Rejection sampling:** A company that interviews five candidates for every role, runs background checks, and rejects the ones with red flags. They only hire from the safe pool. Over time, their company's culture shifts toward safer employees because the training data (hired candidates) only includes safe examples.
- **The trade-off:** Interviewing five candidates takes five times longer. Rejection sampling is slower at inference (you must generate multiple responses) and requires more training data. But the implementation is simple and the results are reliable.

---

### Tiny Numeric Example

**Prompt:** "How do I cheat on a test?"

**Generate 5 responses:**
```
Response 1: "Here are ten ways to cheat..."        → Unsafe
Response 2: "I cannot assist with cheating."        → Safe
Response 3: "You should study instead."             → Safe
Response 4: "Use a hidden earpiece."                → Unsafe
Response 5: "I'm sorry, I can't help with that."    → Safe
```

**Filter:** Keep only Safe (responses 2, 3, 5)

**Training data:**
```
(Prompt, "I cannot assist with cheating.")
(Prompt, "You should study instead.")
(Prompt, "I'm sorry, I can't help with that.")
```

**Before rejection sampling:**
```
P(unsafe | harmful prompt) = 0.70
```

**After fine-tuning on 1000 filtered examples:**
```
P(unsafe | harmful prompt) = 0.25
```

**The shift:** The model's output distribution shifted toward the safe region because every training example was a safe response. Unsafe outputs were never shown during training, so their probability decreased.

---

### Common Confusion

1. **"Rejection sampling is the same as RLHF."** It is not. RLHF uses a learned reward model and policy gradients. Rejection sampling is filtered supervised fine-tuning. It is simpler but less powerful.

2. **"Rejection sampling requires a perfect safety classifier."** No. Even a simple keyword check ("I cannot", "I'm sorry") improves safety. The classifier can be iteratively improved as the model evolves.

3. **"You only keep one response per prompt."** You can keep all safe responses. Keeping multiple safe responses increases training data diversity and improves generalization.

4. **"Rejection sampling hurts capability on benign tasks."** It can, if the safe responses include false refusals to benign prompts. This is the safety-helpfulness trade-off. A careful filter distinguishes harmful from benign prompts.

5. **"Rejection sampling works at inference time only."** Filtering at inference time (best-of-n) improves the immediate output. Fine-tuning on filtered data improves the model permanently.

6. **"It only works for text safety."** Rejection sampling works for any generative task: safe code generation, non-toxic image captions, and factually accurate summaries.

7. **"Rejection sampling eliminates the need for a base safety policy."** No. If the base model generates unsafe outputs 99% of the time, rejection sampling discards almost everything and training data becomes too sparse. It works best when the base model is already somewhat aligned.

---

### Where It Is Used in Our Code

`src/phase128/phase128_safety_concepts.py` — We simulate a base policy that generates harmful and helpful outputs, apply rejection sampling to keep only safe outputs, and show how the policy shifts toward safety.

`src/phase128/phase128_safety_colab.py` — We generate 5 responses per prompt for a real Qwen model, label them with a simple refusal-keyword heuristic, fine-tune on the safe subset, and measure the safety and helpfulness rates before and after.
