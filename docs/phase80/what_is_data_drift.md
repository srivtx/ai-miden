# What is Data Drift?

## 1. Why it exists (THE PROBLEM)

You train a model on data from January. By June, the world has changed. Your customers are older, prices have shifted, and user behavior looks nothing like your training set. The model still runs, but it is silently making worse decisions every day because the **inputs** it receives no longer match what it learned from. This is data drift: the distribution of your features changes over time, and your model was never taught to handle the new patterns.

## 2. Definition

Data drift (or feature drift / covariate shift) happens when the statistical distribution of model inputs `P(X)` changes between training and production, even if the relationship between `X` and `y` stays the same.

## 3. Real-life analogy

Imagine you learned to drive in a small town where every street is 25 mph and straight. Then you move to a city with highways, steep hills, and one-way streets. The *rules of driving* have not changed, but the *scenery and conditions* are completely different. You are not prepared because your training environment no longer matches reality.

## 4. Tiny numeric example

Training distribution:
```
Feature age: mean = 30, std = 5
Production distribution (6 months later):
Feature age: mean = 45, std = 8
```

The model learned that age 30 predicts a certain behavior. When everyone is now 45, those predictions fail.

## 5. Common confusion

- **"Data drift means the model is broken"** — No. The model code is fine. The *data feeding it* has shifted.
- **"Drift only happens if accuracy drops"** — No. You might not have ground-truth labels for weeks, so accuracy is unknown. Drift detection must happen on `X` alone.
- **"One feature drifting is enough to retrain"** — Not always. Some features matter more than others. Drift in a low-importance feature may be harmless.
- **"Drift detection is the same as outlier detection"** — No. Outliers are rare individual points. Drift is a systematic shift in the entire distribution.
- **"KL divergence and PSI are interchangeable"** — They are related but not identical. PSI is more common in finance; KL is more common in research. They can disagree on small samples.
- **"Drift only happens over long time periods"** — No. A single marketing campaign, a bug in an upstream pipeline, or a holiday can cause sudden drift in hours.
- **"If I retrain frequently, I do not need drift detection"** — Retraining blindly is expensive and may train on corrupted data. Drift detection tells you *when* retraining is actually needed.

## 6. Where it is used in our code

- `src/phase80/phase80_mlops.py`: We simulate data drift in month 6 by shifting the mean of a key feature. We compute **KL divergence** and **PSI** between the reference (training) distribution and the production distribution over a rolling window.
- `src/phase80/phase80_mlops_colab.py`: We use `alibi-detect` or `evidently` to run statistical tests on incoming production batches and trigger retraining when drift exceeds a threshold.
