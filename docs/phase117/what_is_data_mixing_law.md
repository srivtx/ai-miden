## What Is a Data Mixing Law?

---

### The Problem

Chinchilla scaling laws tell us how many total tokens we need for a model of a given size, but they stay silent on the recipe. Should a 7B model see 33% web text, 33% code, and 33% math? Or is 60% web, 30% code, 10% math better? In practice, uniform mixing is the default, but it is almost never optimal. Some domains are information-dense and under-represented; others are abundant but redundant. Training with the wrong ratio wastes compute and leaves the model weak on high-value skills.

---

### Definition

**Data mixing laws** are empirical principles that determine the optimal proportion of each data domain in a pretraining corpus. Instead of guessing, they treat the mixing weights as trainable hyperparameters, using per-domain loss signals to reallocate budget toward the most beneficial sources.

**How it works:**
```
1. Train a small proxy model on a uniform mixture of all domains.
2. Measure per-domain validation loss.
3. Domains where loss remains high need more weight.
4. Reweight the mixture and retrain (or continue training the full model).
5. Result: higher weight on hard/informative domains, lower weight on easy/redundant ones.
```

**Key techniques:**
- **DoReMi (Domain Reweighting with Minimax):** trains a small reference model, then optimizes mixing weights to minimize worst-case per-domain excess loss.
- **Domain-level importance sampling:** sample each domain with probability proportional to its gradient norm or loss reduction rate.
- **Online reweighting:** update mixture weights during training as the model's weaknesses shift.

**Why this matters:**
- A 280M-parameter proxy model can find mixing weights that improve a 70B model's downstream performance by several percent.
- Code and math are typically underweighted in uniform mixes; natural dialogue is typically overweighted.
- The optimal mix changes with scale: larger models benefit more from hard domains.

---

### Real-Life Analogy

Imagine a high school student with one month to prepare for a composite exam covering history, physics, and literature. The student starts by dividing time equally: ten days each. After the first week, practice tests reveal history is already strong (90%), physics is moderate (70%), and literature is weak (50%). A smart student does not continue the even split. They shift time toward literature and physics, accepting that history will stay at 85% instead of 95%. The trade-off is deliberate: literature has the highest marginal return per hour studied. Data mixing is exactly this reallocation, but at billion-token scale. The cost of getting it wrong is not just a bad grade; it is millions of dollars of wasted GPU time training on data that barely improves the model.

---

### Tiny Numeric Example

**Three-domain pretraining (1B tokens total):**

**Uniform mix (33% each):**
```
Domain         | Weight | Final Loss | Downstream Acc
---------------|--------|------------|---------------
Easy text      | 0.33   | 1.50       | 78%
Code           | 0.33   | 2.80       | 55%
Math           | 0.33   | 3.20       | 48%
Overall PPL    |        | 2.50       |
```

**DoReMi-optimized mix:**
```
Domain         | Weight | Final Loss | Downstream Acc
---------------|--------|------------|---------------
Easy text      | 0.20   | 1.65       | 76%
Code           | 0.35   | 2.20       | 68%
Math           | 0.45   | 2.40       | 62%
Overall PPL    |        | 2.08       |
```

**The shift:** The model sacrificed 2 points on easy text but gained 13 points on code and 14 points on math. Overall perplexity dropped by 0.42, a significant gain for the same token budget.

---

### Common Confusion

1. **"Uniform mixing is fair and therefore optimal."** Fairness is not the goal; utility is. Uniform mixes systematically under-train hard domains.

2. **"DoReMi requires training the full model twice."** No. DoReMi uses a tiny proxy model (e.g., 280M parameters) to discover weights, then applies them to the large model once.

3. **"More tokens from a domain always help."** Diminishing returns set in quickly. After a point, extra web text barely changes loss, while the first billion tokens of code have a massive impact.

4. **"Data mixing laws are the same as Chinchilla scaling laws."** Chinchilla tells you *how many* total tokens to use. Data mixing tells you *which ratio* of domains to include.

5. **"You can set mixing weights once and keep them forever."** The optimal mix evolves. Early training benefits from easy data; later training needs hard data. Online reweighting adapts to this.

6. **"Reweighting hurts performance on domains that receive low weight."** It can, but the trade-off is usually favorable. If a domain drops from 78% to 76% while another rises from 48% to 62%, the net capability of the model increases.

7. **"Data mixing only applies to text pretraining."** Vision-language models mix image-caption pairs with interleaved web documents. Scientific models mix papers with code and protein sequences. The principle is universal.

---

### Where It Is Used in Our Code

`src/phase117/phase117_mixing_concepts.py` — We simulate three domains with different difficulty floors and learning speeds. We compare uniform mixing, a DoReMi-style optimal reweighting, and curriculum learning. We plot per-domain loss curves and mixing weight evolution to show why uniform mixing is suboptimal.
