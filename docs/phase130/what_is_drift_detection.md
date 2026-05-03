## What Is Drift Detection?

---

### The Problem

Your LLM chatbot has been running smoothly for six months. Then one Monday, answers start feeling off. Users complain that the bot is too verbose, too formal, or just wrong. You check the model weights: they have not changed. You check the deployment: no new release. The problem is that the world changed. Users are asking about a new product line you launched last week, using slang that did not exist when the model was trained, or pasting documents in a language you never tested. The model is the same; the data distribution is not. How do you detect this before users notice?

---

### Definition

**Drift detection** is the process of identifying when the distribution of inputs or outputs in production deviates significantly from the training or baseline distribution. In LLMs, drift takes three forms: **input drift** (users ask different things), **output drift** (the model responds differently even to similar inputs), and **concept drift** (the underlying world changes, making old answers obsolete). Statistical tests like Kolmogorov-Smirnov (KS), Kullback-Leibler (KL) divergence, and embedding-space distance are used to quantify drift.

**How it works:**
```
Baseline window (week 1):
  Input lengths:   mean=45, std=12
  Output lengths:  mean=78, std=23
  Query embeddings: cluster around topics A, B, C
  Output perplexity: mean=2.1, std=0.3

Production window (week 6):
  Input lengths:   mean=120, std=45   ← KS test p < 0.001
  Output lengths:  mean=340, std=89   ← KL divergence = 1.8 (threshold 0.5)
  Query embeddings: new cluster D emerges
  Output perplexity: mean=4.5, std=1.2  ← 8 sigma above baseline

Alert: drift detected on input length, output length, and perplexity.
```

**Key techniques:**
- **Input drift (KS test):** compare the distribution of a numeric feature (input length, output length) between baseline and production using the two-sample Kolmogorov-Smirnov test
- **Semantic drift (embedding distance):** encode queries into vectors; compute the centroid shift or average pairwise distance between baseline and production embeddings
- **Output drift (perplexity):** if the model's own perplexity on its outputs rises, it is struggling to predict what it is generating — a sign of confusion or off-distribution generation
- **Concept drift (topic modeling):** track the distribution of detected topics or entities; a new dominant topic signals a world change

**Why this matters:**
- Drift is the silent killer of model performance. Accuracy can drop 30% before users complain
- Early detection lets you trigger retraining, fallback models, or human review
- Not all drift is bad. A new product launch causes drift but is expected. Detection separates expected from unexpected.

---

### Real-Life Analogy

A restaurant menu and its customers.
- **Baseline:** Your restaurant serves Italian food. Customers usually order pasta (60%), pizza (30%), and salad (10%). The kitchen is optimized for this mix. This is your training distribution.
- **Input drift:** One month, 40% of orders are sushi. The customers changed; the kitchen did not. You detect this by counting dish categories (KS test on order types). You add a sushi chef or you post a sign: "Italian only."
- **Output drift:** Pasta portions suddenly double. The chef is the same, but something in the supply chain changed the ingredient ratios. Customers notice before management does. You detect this by weighing random plates (perplexity of output given standard recipe).
- **Concept drift:** A health trend makes carbs unpopular. Even if order categories look the same, customer satisfaction drops because the world changed. You detect this by tracking satisfaction scores (downstream metrics) and dietary surveys (topic drift).

---

### Tiny Numeric Example

**Baseline distribution (first 100 requests):**
```
Input lengths:   [32, 45, 28, 56, 41, 38, 52, 29, 44, 37, ...]
Output lengths:  [65, 82, 54, 91, 73, 68, 88, 59, 77, 71, ...]
Perplexities:    [1.8, 2.1, 1.9, 2.4, 2.0, 1.9, 2.3, 1.7, 2.1, 2.0, ...]
```

**Production distribution (next 100 requests, drift injected):**
```
Input lengths:   [128, 145, 112, 156, 141, 138, 152, 129, 144, 137, ...]
Output lengths:  [265, 282, 254, 291, 273, 268, 288, 259, 277, 271, ...]
Perplexities:    [3.8, 4.1, 3.9, 4.4, 4.0, 3.9, 4.3, 3.7, 4.1, 4.0, ...]
```

**KS test on input length:**
```
KS statistic = 1.0   (all baseline values < all production values)
p-value < 0.0001     → highly significant drift
```

**KL divergence on output length (discretized into bins):**
```
Baseline bins:  [0-50: 10%, 51-100: 70%, 101-150: 15%, 151+: 5%]
Production bins:[0-50: 0%,  51-100: 5%,  101-150: 15%, 151+: 80%]
KL divergence = 2.1  (threshold for alert = 0.5)
```

**Perplexity z-score:**
```
Baseline mean = 2.0, std = 0.2
Production mean = 4.0
z = (4.0 - 2.0) / 0.2 = 10.0  → 10 sigma event
```

**The shift:** All three signals fire simultaneously. The model has not changed, but the inputs are longer and more complex, forcing longer, more confused outputs. Drift detection catches this in minutes, not weeks.

---

### Common Confusion

1. **"Drift detection is only about data quality."** No. Drift can signal attacks (prompt injection flooding), bugs (UI change sends double prompts), or product changes (new feature drives new queries). It is a general health signal.

2. **"One test is enough."** No. Input length drift might be benign (users paste longer documents). Output perplexity drift might be serious (model is confused). You need multiple orthogonal tests to triangulate the root cause.

3. **"Drift detection requires labeled data."** No. Unsupervised drift detection compares distributions without labels. Supervised drift (accuracy drop) requires labels, but it is usually too late by the time labels arrive.

4. **"KL divergence and KS test are interchangeable."** KS tests the maximum distance between CDFs; it is non-parametric and good for location shifts. KL divergence measures information loss between distributions; it is sensitive to shape changes and rare events. They detect different kinds of drift.

5. **"Drift means the model is broken."** Drift means the world changed relative to the model. The model may still work (users are just asking new things). The response is often to update context, not to retrain.

6. **"Embedding drift is too slow to compute."** With approximate nearest-neighbor indexes and cached embeddings, centroid distance can be computed in milliseconds per batch. It is practical for real-time monitoring.

7. **"Concept drift is impossible to detect without human judgment."** Downstream metrics (conversion rate, user satisfaction, task success) are proxies for concept drift. If the world changes, these metrics usually move before semantic drift is obvious.

---

### Where It Is Used in Our Code

`src/phase130/phase130_monitoring_concepts.py` — We simulate a sudden shift in query distribution (longer, more technical prompts) and detect it using KL divergence on input length and output perplexity z-scores. We plot drift score over time and show the alert threshold crossing.

`src/phase130/phase130_monitoring_colab.py` — We generate 200 real requests, split them into benign and complex halves. We detect drift using the KS test on input lengths, output perplexity increase, and latency increase. We build a dashboard with drift score over time and log alert events.

(End of file)
