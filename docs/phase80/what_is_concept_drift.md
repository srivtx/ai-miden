# What is Concept Drift?

## 1. Why it exists (THE PROBLEM)

Your model learned that sunny weather predicts high ice cream sales. Then a global pandemic hits, and people stop going outside even on sunny days. The *inputs* (weather) look the same, but the *relationship* between weather and sales has completely changed. Retraining on the old logic will never fix this because the underlying concept the model learned is now obsolete.

## 2. Definition

Concept drift happens when the conditional relationship between inputs and outputs `P(y | X)` changes over time, even if the input distribution `P(X)` stays the same.

## 3. Real-life analogy

You learned that flipping a light switch turns on the light. Then an electrician rewires your house so the switch now controls the fan. The switch looks the same, your action is the same, but the *outcome* has changed. The "concept" of what that switch does has drifted.

## 4. Tiny numeric example

Training relationship:
```
y = 2 * x + noise
```

Production relationship (after month 9):
```
y = -1.5 * x + noise
```

The input `x` still has the same mean and variance, but the slope flipped from positive to negative. The model will confidently predict the wrong direction.

## 5. Common confusion

- **"Concept drift is the same as data drift"** — No. Data drift is `P(X)` changing. Concept drift is `P(y|X)` changing. You can have one, both, or neither.
- **"If my inputs look stable, my model is fine"** — No. Stable inputs can still produce wrong outputs if the concept has drifted.
- **"Concept drift is easy to detect"** — It is actually harder than data drift because you need ground-truth labels (`y`) to see that the relationship broke. Without labels, you must infer it from prediction errors or proxy metrics.
- **"Retraining fixes concept drift automatically"** — Only if your new training data captures the new concept. If the new data still reflects the old relationship, retraining helps nothing.
- **"Concept drift is always sudden"** — No. It can be gradual (customer preferences slowly shift) or recurring (seasonal patterns that repeat yearly but were absent in training data).
- **"One model can handle all concepts forever"** — No. Some systems use ensembles or online learning to adapt to changing concepts in real time.
- **"Accuracy dropping always means concept drift"** — No. Accuracy can drop due to data drift, label noise, or a broken pipeline. Diagnosis matters.

## 6. Where it is used in our code

- `src/phase80/phase80_mlops.py`: We simulate concept drift in month 9 by changing the true coefficient in the data-generating process. Accuracy collapses even though the feature distributions look identical. We plot the timeline to show the delayed impact.
- `src/phase80/phase80_mlops_colab.py`: We monitor rolling accuracy on labeled production batches. When accuracy drops while input drift scores remain low, we flag concept drift and trigger a full retraining with a broader feature set.
