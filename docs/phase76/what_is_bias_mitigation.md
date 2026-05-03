# What is Bias Mitigation?

## 1. Why it exists (THE PROBLEM)

You have measured the bias. Your model approves men twice as often as women. Your fraud detector flags twice as many false positives for one neighborhood. Now what? **Measuring bias is only the first step.** Bias mitigation exists because detecting unfairness without fixing it is like diagnosing a disease and refusing treatment. The challenge is that bias is not a single bug you can patch; it is woven into the data, the objective function, and the decision threshold. Mitigation gives us systematic ways to unpick that weave.

## 2. Definition

**Bias mitigation** is the set of techniques used to reduce unfair disparities in machine learning predictions across demographic groups. The three main families are:

- **Pre-processing:** Changing the training data before the model sees it (re-sampling, re-weighting, learning fair representations).
- **In-processing:** Changing the training procedure itself (adding fairness constraints or penalties to the loss function).
- **Post-processing:** Changing the model's outputs after training (adjusting decision thresholds per group).

## 3. Real-life analogy

A restaurant kitchen keeps serving undercooked fish to tables near the window. They investigate three fixes:

- **Pre-processing:** They buy thicker cuts of fish for the window station so the same cooking time works for everyone.
- **In-processing:** They redesign the training manual so cooks check internal temperature, not just the clock.
- **Post-processing:** They assign a second cook to double-check every plate heading to the window.

All three reduce undercooked fish, but they intervene at different points in the pipeline.

## 4. Tiny numeric example

A training set has 200 examples:

| Group | Positive Labels | Negative Labels |
|-------|-----------------|-----------------|
| A     | 100             | 100             |
| B     | 50              | 150             |

The base rate for Group A is 50%; for Group B it is 25%. A model trained on this raw data will likely favor Group A.

- **Pre-processing (re-weighting):** Give every Group B positive sample a weight of 2.0 so the effective base rate becomes equal.
- **In-processing:** Add a penalty term to the loss: `Loss = CrossEntropy + lambda * |TPR_A - TPR_B|`. The model now trades a little accuracy for fairness.
- **Post-processing:** After training, set the decision threshold to 0.4 for Group B and 0.6 for Group A. This balances the approval rates without retraining.

All three reduce the demographic parity gap from 20 percentage points down to roughly 5.

## 5. Common confusion

- **"Mitigation eliminates bias completely."** No. It reduces disparities; perfect fairness is usually impossible when multiple fairness definitions conflict.
- **"You should always use the most sophisticated technique."** No. A simple post-processing threshold adjustment can be more transparent and auditable than a complex in-processing constraint.
- **"Pre-processing destroys real signal."** No. Re-weighting changes the relative importance of examples, but the underlying features remain intact.
- **"In-processing is the only principled approach."** No. Each family has trade-offs. In-processing changes the model; post-processing leaves the model untouched but changes decisions.
- **"Mitigation always hurts accuracy."** Not always. When bias stems from overfitting to spurious correlations, mitigation can improve generalization.
- **"You can apply mitigation without choosing a fairness definition."** No. You must decide whether you care about demographic parity, equalized odds, or another criterion before you pick a technique.

## 6. Where it is used in our code

In `src/phase76/phase76_fairness_bias.py`, we apply **re-weighting**, a pre-processing technique. Samples from the under-represented positive class in Group B receive higher weights during gradient descent, forcing the classifier to pay more attention to them. We then compare fairness metrics before and after re-weighting. In `src/phase76/phase76_fairness_bias_colab.py`, we apply an **in-processing** demographic parity constraint using fairlearn's `ExponentiatedGradient`, which modifies the training objective directly. We compare the unconstrained and constrained models side by side.
