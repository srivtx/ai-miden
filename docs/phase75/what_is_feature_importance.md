# What is Feature Importance?

## 1. Why it exists (THE PROBLEM)

You have trained a model with 50 input features. You know it works well, but you do not know which features are actually driving the predictions. If you could rank them, you could:
- Simplify the model by dropping useless features.
- Debug data leakage (if "patient_id" is the top feature, something is wrong).
- Communicate to stakeholders which variables matter.

Feature importance answers: *"Which inputs have the biggest impact on the model's output, on average?"*

## 2. Definition (very simple)

**Feature importance** is a measure of how much each input feature contributes to a model's predictions across the entire dataset. It is a *global* explanation: it describes the model as a whole, not one specific prediction.

Common methods:
- **Model-based**: Linear coefficients, tree-based splits (Gini importance).
- **Permutation importance**: Randomly shuffle one feature and measure how much accuracy drops.
- **SHAP importance**: Average the absolute SHAP values for each feature across all samples.

## 3. Real-life analogy

You are baking 100 cakes, and each cake uses flour, sugar, eggs, and vanilla. Some cakes turn out great, some terrible. You want to know which ingredient matters most.

- **Model-based**: The recipe card lists proportions. You look at the ratios.
- **Permutation importance**: You swap the flour in 10 random cakes with random flour from the pantry. If quality crashes, flour is important.
- **SHAP**: You interview each cake and ask: "How much did flour help or hurt your score?" You average the answers.

## 4. Tiny numeric example

Dataset with 3 features and a linear model:
```
prediction = 3.0*x0 + 0.5*x1 + 0.0*x2
```

**Model-based importance**: `[3.0, 0.5, 0.0]` — x0 dominates.

**Permutation importance**:
1. Baseline MSE on 5 samples: `0.10`
2. Shuffle x0 → MSE jumps to `2.50` → importance = `2.40`
3. Shuffle x1 → MSE jumps to `0.35` → importance = `0.25`
4. Shuffle x2 → MSE stays `0.10` → importance = `0.00`

Ranking: x0 > x1 > x2.

## 5. Common confusion (5+ bullet points)

- **Importance is not causal**: A feature can be highly important because it is correlated with the true cause. If umbrellas are important for predicting rain, it does not mean umbrellas cause rain.
- **Correlated features share importance**: If x0 and x1 are perfectly correlated, permutation importance may split credit unpredictably between them, or give one all the credit and the other none.
- **Negative coefficients are still important**: In linear models, a large negative coefficient means the feature strongly influences the output. Do not ignore sign; importance is about magnitude of effect.
- **Tree default importance is biased**: Scikit-learn's "feature importance" for trees (mean decrease in impurity) is biased toward high-cardinality features. Use permutation importance or SHAP instead.
- **Zero importance does not mean useless globally**: A feature might only matter for a small subgroup. Global importance can miss local effects.
- **SHAP importance averages away direction**: If a feature pushes predictions up for half the samples and down for the other half, its mean absolute SHAP value can look small even though it is highly influential.

## 6. Where it is used in our code

- `src/phase75/phase75_xai_numpy.py` — Computes exact SHAP values for a 4-feature toy problem. We average absolute SHAP values across test samples to build a global importance bar chart.
- `src/phase75/phase75_xai_colab.py` — Uses PyTorch to compute gradient-based feature importance on a small network.
