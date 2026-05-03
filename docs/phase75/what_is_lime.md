# What is LIME?

## 1. Why it exists (THE PROBLEM)

Global explanations tell you what matters *on average*, but they can hide critical local behavior. A model might use income for most decisions, but reject one specific applicant because of a low credit score. If you only look at global importance, you miss that story.

**LIME** (Local Interpretable Model-agnostic Explanations) was invented to solve this. It explains *one prediction at a time* by building a simple, interpretable model in the neighborhood around that instance.

## 2. Definition (very simple)

**LIME** is a local explanation technique that:
1. Takes the instance you want to explain.
2. Generates many perturbed (slightly changed) versions of that instance.
3. Feeds those perturbed samples through the original black-box model to get predictions.
4. Weights the perturbed samples by how close they are to the original instance.
5. Fits a simple, interpretable model (usually linear regression) to the weighted samples.
6. Uses the simple model's coefficients as the explanation.

The core idea: *"The complex model is too hard to explain globally, but locally it might behave like a straight line."*

## 3. Real-life analogy

You are trying to understand why a GPS routed you through a back road. Instead of reading the entire GPS algorithm, you zoom into your neighborhood and ask: "If I had started one block north, one block south, etc., what route would the GPS pick?"

You discover that within a 3-block radius, the GPS consistently avoids the main street because of a known traffic pattern. That local rule is your explanation. It does not describe the entire GPS, but it explains *your* route.

## 4. Tiny numeric example

Original instance: `x = [2.0, 1.0]` with true label `1`.

Black-box model: A tiny MLP we cannot read.

**Step 1 — Perturb**: Sample 5 neighbors:
```
[2.1, 1.2] → pred 0.92
[1.9, 0.8] → pred 0.88
[2.5, 1.1] → pred 0.95
[1.5, 1.0] → pred 0.70
[2.0, 0.5] → pred 0.65
```

**Step 2 — Weight**: Closer points get higher weight. Using Euclidean distance:
```
weights = [0.95, 0.95, 0.70, 0.60, 0.50]
```

**Step 3 — Fit linear model**: Weighted linear regression on the 5 samples.
```
intercept = 0.10
coef_feature_0 = 0.20
coef_feature_1 = 0.15
```

**Explanation**: For this specific instance near `[2.0, 1.0]`, increasing feature 0 by 1 unit raises the model's confidence by ~0.20, and feature 1 by ~0.15. Feature 0 is slightly more important *locally*.

## 5. Common confusion (5+ bullet points)

- **LIME is not the model**: LIME fits a surrogate model. The coefficients describe the local surrogate, not the original model. If the original model is highly non-linear in that neighborhood, the surrogate can be misleading.
- **The neighborhood matters**: LIME uses a kernel width parameter that defines "local." Too wide, and the surrogate averages over too much behavior. Too narrow, and you have too few samples to fit a line.
- **LIME is model-agnostic but data-dependent**: It works on any model, but the quality of the explanation depends heavily on how you perturb the data. For categorical features, random perturbation is not straightforward.
- **Stability**: LIME can give different explanations for the same instance if you change the random seed, because the perturbed samples change.
- **Does not work well with correlated features**: If two features always move together in the data, perturbing one independently creates unrealistic samples, and the surrogate assigns weird coefficients.
- **Local does not mean causal**: Even locally, correlation is not causation. LIME tells you what the model responds to, not what truly causes the outcome in the real world.

## 6. Where it is used in our code

- `src/phase75/phase75_xai_numpy.py` — Implements LIME from scratch on a 4-feature toy MLP. We perturb one instance with Gaussian noise, weight by RBF kernel, fit weighted least squares, and plot the coefficients.
- `src/phase75/phase75_xai_colab.py` — Uses PyTorch to demonstrate LIME-like behavior with autograd and interpolation.
