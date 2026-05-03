## What Is Ensemble Learning?

---

### The Problem

A single model makes mistakes. A decision tree overfits. A neural network underfits if too small. A linear model misses nonlinear patterns. Is there a way to combine multiple models so that their mistakes cancel out and their correct predictions reinforce each other?

---

### Definition

**Ensemble learning** is the technique of combining multiple models to produce a better prediction than any single model could achieve alone. The key idea is that a group of diverse, moderately accurate models will make different errors, and averaging their predictions reduces variance.

**Types of ensembles:**

**Bagging (Bootstrap Aggregating):**
```
1. Create M bootstrap samples (random subsets with replacement) from training data
2. Train M independent models, one on each sample
3. Final prediction = average (regression) or majority vote (classification)
```
- Example: Random Forest
- Reduces variance, prevents overfitting

**Boosting:**
```
1. Train model 1 on all data
2. Train model 2 on data weighted by model 1's errors
3. Train model 3 on data weighted by combined errors of models 1-2
4. Final prediction = weighted combination of all models
```
- Example: AdaBoost, Gradient Boosting, XGBoost
- Reduces bias, turns weak learners into strong learners

**Stacking:**
```
1. Train multiple diverse models on the same data
2. Train a "meta-learner" to combine their predictions
3. Final prediction = meta-learner(model1_pred, model2_pred, ...)
```
- Example: Combining a neural network, random forest, and SVM
- The meta-learner learns which model to trust for which inputs

**Why ensembles work (the wisdom of crowds):**
- If each model has error rate ε < 0.5 and errors are independent
- The probability that a majority of M models are wrong decreases exponentially
- With M=101 models each with ε=0.4, majority vote error is only 0.02

---

### Real-Life Analogy

The game show "Who Wants to Be a Millionaire" and the "Ask the Audience" lifeline.
- **Single model:** You ask one random person in the audience. They might know, they might guess.
- **Ensemble:** You ask the entire audience and take the majority vote. Individually, many people are wrong. But collectively, the audience is right ~90% of the time.
- **Why it works:** Different people have different knowledge. The person who knows history offsets the person who knows sports. Their errors are uncorrelated, so they cancel out.

**Bagging** is like asking 100 different audiences (each slightly different people) and averaging their answers.
**Boosting** is like asking experts one at a time, with each expert focusing on the questions previous experts got wrong.
**Stacking** is like having a panel of specialists (history expert, sports expert, science expert) and a moderator who decides which expert to trust on each question.

---

### Tiny Numeric Example

**3 models, binary classification:**
```
Model 1 accuracy: 60% (errors on examples 2, 4)
Model 2 accuracy: 60% (errors on examples 1, 3)
Model 3 accuracy: 60% (errors on examples 2, 3)

True labels: [1, 1, -1, -1]

Model 1 predictions: [1, -1, -1, 1]  (errors on 2, 4)
Model 2 predictions: [-1, 1, 1, -1]  (errors on 1, 3)
Model 3 predictions: [1, -1, 1, -1]  (errors on 2, 3)

Majority vote:
Example 1: [1, -1, 1] → 2 votes for 1, 1 for -1 → predict 1 ✓
Example 2: [-1, 1, -1] → 2 votes for -1, 1 for 1 → predict -1 ✓
Example 3: [-1, 1, 1] → 2 votes for 1, 1 for -1 → predict 1 ✗ (true is -1)
Example 4: [1, -1, -1] → 2 votes for -1, 1 for 1 → predict -1 ✓

Ensemble accuracy: 75% (better than any single model!)
```

The errors were uncorrelated, so they canceled out.

---

### Common Confusion

1. **"Ensembles are just averaging predictions."** Averaging is the simplest form. Boosting and stacking are more sophisticated.

2. **"More models always means better performance."** Diminishing returns. After a point, adding identical models helps nothing. Diversity matters more than quantity.

3. **"Ensembles are slow at inference."** Yes. You must run every model. Solutions: model distillation (train a single model to mimic the ensemble), or pruning weak models.

4. **"Ensembles fix underfitting."** Bagging fixes overfitting (high variance). Boosting fixes underfitting (high bias). They address different problems.

5. **"Deep learning made ensembles obsolete."** No. Ensembles of neural networks still win competitions. Even a single ResNet is an ensemble of residual paths.

---

### Where It Is Used in Our Code

`src/phase56/phase56_gradient_boosting.py` — We demonstrate bagging (averaging multiple noisy predictors), boosting (sequential residual correction), and a simple ensemble of diverse models, showing how combining models beats any single model.
