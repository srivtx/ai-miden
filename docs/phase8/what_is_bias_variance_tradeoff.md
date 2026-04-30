# Bias vs. Variance Tradeoff

## 1. Why it exists (THE PROBLEM)

When building models, we face a fundamental tension:

- If the model is **TOO SIMPLE**, it misses the true pattern. This is **HIGH BIAS**.
- If the model is **TOO COMPLEX**, it memorizes noise. This is **HIGH VARIANCE**.
- We need to find the **SWEET SPOT** in the middle.

Every model makes errors. Those errors come from three sources:

1. **Bias:** the model is too simple to capture the truth
2. **Variance:** the model is too sensitive to training data noise
3. **Irreducible error:** noise we cannot eliminate

No model can escape this. A simple model has high bias. A complex model has high variance. Our job is to balance them.

---

## 2. Definition (very simple)

**Bias:** How far the model's average prediction is from the true answer. High bias = the model is consistently wrong in the same direction.

**Variance:** How much the model's predictions change if we train on different data. High variance = the model memorizes the specific training set.

Think of it this way:
- **Bias** is about how wrong you are on average.
- **Variance** is about how much you wiggle around when the data changes.

---

## 3. Real-life analogy

Imagine three archers shooting at a target:

**Archer A (High Bias, Low Variance):**
- Always hits the same spot — 2 feet to the LEFT of the bullseye.
- Very consistent. But consistently WRONG.
- This is a model that is too simple. It misses the pattern systematically.

**Archer B (Low Bias, High Variance):**
- Hits all over the target. Some near the center, some far away.
- On average, close to the bullseye. But wildly inconsistent.
- This is a model that is too complex. It memorizes noise and changes wildly with different training data.

**Archer C (Low Bias, Low Variance):**
- Hits consistently near the bullseye.
- This is the GOAL. A model that captures the true pattern without memorizing noise.

---

## 4. Tiny numeric example

True pattern: `y = x + 1` (a straight line)

Training data (noisy):

| x | y_true | y_noisy |
|---|---|---|
| 0 | 1 | 0.8 |
| 1 | 2 | 2.2 |
| 2 | 3 | 2.9 |

### Model A (too simple — constant): `y = 2`
- Predictions: [2, 2, 2]
- **Bias: HIGH.** It systematically misses the upward trend.
- **Variance: LOW.** No matter what data you give it, it always predicts 2.
- **Total error:** high

### Model B (just right — linear): `y = x + 1`
- Predictions: [1, 2, 3]
- **Bias: LOW.** On average, it captures the trend.
- **Variance: LOW.** With different training data, it still finds roughly the same line.
- **Total error:** low

### Model C (too complex — degree-10 polynomial)
- Predictions: [0.8, 2.2, 2.9] (perfect fit!)
- **Bias: LOW.** Fits training data perfectly.
- **Variance: HIGH.** With slightly different training data, the 10-degree polynomial would look completely different.
- **Total error:** high on new data

---

## 5. Common confusion

- **"Bias is NOT prejudice."** In ML, bias means "systematic error" — consistently missing in one direction.
- **"Variance is NOT statistical variance."** In ML, variance means "sensitivity to training data" — how much the model changes with different data.
- **"You CANNOT have both low bias and low variance for free."** There is always a tradeoff. You have to choose the right model complexity.
- **"More data reduces variance."** With infinite data, even complex models have low variance.
- **"L2 regularization reduces variance by forcing simplicity."** It increases bias slightly but reduces variance a lot.

---

## 6. Where it is used in our code

In our code, we will plot training loss vs. validation loss. As we add L2 regularization:

- **Training loss might go UP slightly** (we are no longer memorizing perfectly)
- **Validation loss goes DOWN** (we generalize better)
- This shows we moved from high variance toward the sweet spot.

The goal is to find the model complexity where validation loss is minimized — that is the sweet spot between bias and variance.
