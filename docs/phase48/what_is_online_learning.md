## What Is Online Learning?

---

### The Problem

The world changes. News happens. Trends shift. A model trained on 2023 data is outdated by 2024. Re-training from scratch every day is impossibly expensive. How do you update a model continuously as new data arrives?

---

### Definition

**Online learning** is training a model sequentially, one example or one batch at a time, updating the model immediately after each observation without retraining on all past data.

**The process:**
```
For each new data point (x_t, y_t):
  1. Make prediction using current model
  2. Observe true label y_t
  3. Compute loss between prediction and y_t
  4. Update model with one gradient step
  5. Discard (x_t, y_t) or store it briefly
```

**Key properties:**
- **Memory efficient:** Does not store all historical data
- **Adaptive:** Responds immediately to distribution shifts
- **Low latency:** Each update is fast

**Challenges:**
- **Catastrophic forgetting:** New data overwrites old knowledge
- **Noise sensitivity:** Outliers can corrupt the model
- **Learning rate decay:** Must shrink updates over time for stability

---

### Real-Life Analogy

A stock trader.
- **Batch learning:** The trader reads all historical market data, builds a model, and uses it for the next year without updates. When a market crash happens, the model is useless.
- **Online learning:** The trader updates their strategy after every trade. If a new pattern emerges (e.g., meme stocks), they adapt within hours. They never store all historical trades — just the current model parameters.

The trader's knowledge is a moving average, continuously updated.

---

### Tiny Numeric Example

**Task:** Predict next value in sequence.

**Sequence:** 2, 4, 6, 8, 10, 12, ... (true pattern: y = 2x)

**Online learning:**
```
Initial model: y = 1.0 × x (random guess)

Step 1: see (x=1, y=2), predict 1.0, error = +1.0
        Update: y = 1.1 × x

Step 2: see (x=2, y=4), predict 2.2, error = +1.8
        Update: y = 1.3 × x

Step 3: see (x=3, y=6), predict 3.9, error = +2.1
        Update: y = 1.5 × x

... (after 20 steps)

Step 20: see (x=20, y=40), predict 39.8, error = +0.2
         Update: y = 2.0 × x (converged)
```

The model converges to the true pattern without ever storing all 20 data points.

**Distribution shift:**
```
Steps 1-20: pattern is y = 2x (model learns y = 2.0 × x)
Step 21: pattern changes to y = 3x
          predict 42, true = 63, error = +21
          Update: y = 2.1 × x
Step 22: predict 66, true = 66, error = 0
          Model adapted to new pattern in 2 steps
```

---

### Common Confusion

1. **"Online learning is just SGD with batch_size=1."** SGD with batch_size=1 samples randomly from the full dataset. Online learning processes data in arrival order and often discards old data.

2. **"Online learning causes catastrophic forgetting."** It can, if not managed. Techniques like experience replay (keeping a buffer of old examples) and elastic weight consolidation mitigate this.

3. **"Online learning is only for simple models."** It works for neural networks too, though large models need techniques like LoRA to make updates efficient.

4. **"Online learning converges to the same solution as batch learning."** Only if the data is independent and identically distributed (i.i.d.). With distribution shift, online learning adapts while batch learning would need retraining.

5. **"Online learning requires constant compute."** Yes, but each update is a single gradient step. For large models, you might use parameter-efficient updates (LoRA) to keep costs manageable.

---

### Where It Is Used in Our Code

`src/phase48/phase48_test_time_training.py` — We implement online learning on a sequence of data points with a distribution shift mid-sequence. The model adapts to the new pattern within a few steps without retraining from scratch.
