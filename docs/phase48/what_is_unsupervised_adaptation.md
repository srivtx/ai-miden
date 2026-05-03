## What Is Unsupervised Adaptation?

---

### The Problem

You have a model trained on labeled data. At test time, you receive inputs from a slightly different distribution (e.g., photos taken at night instead of day). You have no labels for the new distribution. How do you adapt the model without any supervised signal?

---

### Definition

**Unsupervised adaptation** is the process of adjusting a model to a new input distribution using only unlabeled data — no ground-truth labels required.

**Key techniques:**
1. **Self-supervised auxiliary tasks:** Predict rotations, mask-and-reconstruct, or predict neighboring patches
2. **Entropy minimization:** Force the model to make confident predictions on the new data
3. **Pseudo-labeling:** Use the model's own predictions as labels for adaptation
4. **Batch normalization adaptation:** Update batch statistics to match the test distribution

**Why it works:**
- Even without labels, the test data has structure (spatial correlations, temporal patterns, semantic consistency)
- Auxiliary tasks force the model to pay attention to this structure
- The model's internal representations shift to better match the test distribution

**Example auxiliary tasks:**
- **Images:** Predict rotation angle (0°, 90°, 180°, 270°)
- **Text:** Predict masked words (like BERT's MLM)
- **Audio:** Predict temporal order of shuffled clips
- **Tabular:** Predict which feature was randomly corrupted

---

### Real-Life Analogy

A chef trained in Italian cuisine moves to Japan.
- **Supervised adaptation:** The chef takes cooking classes with Japanese masters (expensive, time-consuming, requires teachers).
- **Unsupervised adaptation:** The chef walks through Japanese markets, tastes ingredients, and infers flavor principles from the raw materials. They notice that umami is central, that fish is handled differently than meat, and that rice texture matters. They adapt their techniques without any explicit instruction.

The chef uses the STRUCTURE of the new environment (ingredient combinations, cooking smells, market organization) to infer how to adapt. No labels needed.

---

### Tiny Numeric Example

**Model trained to classify MNIST digits.**

**Test input:** A digit rotated 45° (unseen during training).

**Frozen model:** Predicts confidently but WRONG because it never saw rotations.

**Unsupervised adaptation:**
```
Auxiliary task: predict rotation angle of the test image
Test image at 45° -> auxiliary label = 45°
Run 3 gradient steps on auxiliary task
Model updates its feature extractors to become rotation-aware
```

**Adapted model on same test image:**
```
Prediction: correct digit
```

The model did not need the true digit label. It adapted using only the self-supervised rotation task.

---

### Common Confusion

1. **"Unsupervised adaptation is just data augmentation."** Data augmentation happens during training. Unsupervised adaptation happens at test time on the actual test input.

2. **"If there are no labels, how do you know it worked?"** You evaluate on a separate held-out test set. The adaptation happens on the training portion of the test distribution.

3. **"Unsupervised adaptation fixes any distribution shift."** No. If the test distribution is completely different (e.g., audio vs. images), adaptation cannot bridge the gap.

4. **"All auxiliary tasks work equally well."** The best auxiliary task depends on the domain. Rotation prediction works for images but not for text.

5. **"Unsupervised adaptation is slower than inference."** It adds 1-10 forward/backward passes. For latency-critical applications, you might adapt offline on a batch of test data.

---

### Where It Is Used in Our Code

`src/phase48/phase48_test_time_training.py` — We implement rotation prediction as an auxiliary task. At test time, the model predicts the rotation angle of the test image, adapts its weights for a few steps, and then classifies the image more accurately.
