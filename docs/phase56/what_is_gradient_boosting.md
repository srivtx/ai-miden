## What Is Gradient Boosting?

---

### The Problem

A single decision tree is powerful but prone to overfitting. A shallow tree is stable but too weak to capture complex patterns. What if you could train many weak trees sequentially, where each new tree fixes the mistakes of all previous trees combined? This is the core idea behind gradient boosting.

---

### Definition

**Gradient Boosting** is an ensemble technique that builds models sequentially. Each new model is trained to predict the residual errors (gradients) of the combined predictions of all previous models. The final prediction is the sum of all individual model predictions.

**How it works (for regression):**
```
1. Start with a simple initial prediction (e.g., the mean of all targets)
2. Compute residuals: actual - predicted
3. Train a weak learner (e.g., a shallow decision tree) to predict these residuals
4. Update the overall prediction: prediction += learning_rate * tree_prediction
5. Compute new residuals using the updated prediction
6. Repeat steps 3-5 for N rounds
```

**Key insight:**
- Each tree learns the "gradient" (direction and magnitude) of the loss function with respect to the current predictions
- This is functional gradient descent: instead of updating parameters, you add functions (trees)
- The learning rate shrinks each tree's contribution, forcing the model to learn gradually and preventing overfitting

**Why this matters:**
- Gradient boosting dominates structured data competitions (Kaggle, etc.)
- It is the foundation of XGBoost, LightGBM, and CatBoost — the most popular libraries for tabular data
- It achieves state-of-the-art results on many tasks without neural networks

---

### Real-Life Analogy

A team of consultants fixing a company's budget.
- **Initial prediction:** The CEO guesses the budget will be $1M.
- **Residual 1:** The actual budget needed is $1.2M. The residual (error) is +$200K.
- **Consultant 1 (Tree 1):** Analyzes the data and says "you forgot marketing costs." They predict the residual is +$150K.
- **Updated prediction:** $1M + 0.1 × $150K = $1.015M (learning rate = 0.1)
- **Residual 2:** $1.2M - $1.015M = +$185K
- **Consultant 2 (Tree 2):** Says "you also forgot IT infrastructure." They predict +$100K.
- **Updated prediction:** $1.015M + 0.1 × $100K = $1.025M
- **After 100 consultants:** The prediction converges to $1.2M.

Each consultant does not redo the full analysis. They only fix what the previous consultants missed.

---

### Tiny Numeric Example

**Dataset:**
```
x = [1, 2, 3, 4]
y = [2, 4, 6, 8]  (true function: y = 2x)
```

**Initial prediction (mean of y):**
```
F0(x) = mean([2, 4, 6, 8]) = 5.0 for all x
```

**Round 1:**
```
Residuals (r1) = y - F0(x) = [2-5, 4-5, 6-5, 8-5] = [-3, -1, 1, 3]

Train Tree 1 to predict r1 from x.
Tree 1 splits at x <= 2:
  Left (x=1,2): predicts mean residual = (-3 + -1)/2 = -2.0
  Right (x=3,4): predicts mean residual = (1 + 3)/2 = 2.0

Update (learning rate = 0.5):
F1(x) = F0(x) + 0.5 × Tree1(x)

x=1: F1 = 5.0 + 0.5 × (-2.0) = 4.0
x=2: F1 = 5.0 + 0.5 × (-2.0) = 4.0
x=3: F1 = 5.0 + 0.5 × 2.0 = 6.0
x=4: F1 = 5.0 + 0.5 × 2.0 = 6.0
```

**Round 2:**
```
Residuals (r2) = y - F1(x) = [2-4, 4-4, 6-6, 8-6] = [-2, 0, 0, 2]

Tree 2 splits at x <= 1:
  Left (x=1): predicts -2.0
  Right (x=2,3,4): predicts mean = (0 + 0 + 2)/3 = 0.67

Update:
x=1: F2 = 4.0 + 0.5 × (-2.0) = 3.0
x=2: F2 = 4.0 + 0.5 × 0.67 = 4.33
x=3: F2 = 6.0 + 0.5 × 0.67 = 6.33
x=4: F2 = 6.0 + 0.5 × 0.67 = 6.33
```

**After 10 rounds:** The predictions converge toward [2, 4, 6, 8].

---

### Common Confusion

1. **"Gradient boosting is just adding trees."** Not quite. It adds trees that specifically predict the negative gradient of the loss. Random forests add independent trees and average them.

2. **"More trees always means better performance."** Too many trees overfit. You need early stopping or limit max_depth/learning_rate.

3. **"Gradient boosting only works for regression."** It works for classification too. The residuals become the gradient of the log-loss (classification error).

4. **"A learning rate of 1.0 is best."** No. Lower learning rates (0.01-0.1) with more trees almost always outperform high learning rates with few trees.

5. **"Gradient boosting is outdated because of neural networks."** False. For tabular data, gradient boosting still often beats deep learning.

---

### Where It Is Used in Our Code

`src/phase56/phase56_gradient_boosting.py` — We implement gradient boosting from scratch on a 1D regression task, showing how each tree reduces the residual error and how the ensemble prediction converges to the true function.
