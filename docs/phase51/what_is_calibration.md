## What Is Calibration?

---

### The Problem

Your model says it is 90% confident that the image is a cat. But when you test 100 images where the model said "90% confident cat," only 70 of them are actually cats. The model is overconfident. How do you measure whether a model's confidence matches its actual accuracy?

---

### Definition

**Calibration** measures whether a model's predicted probabilities reflect true likelihoods. A perfectly calibrated model that says "80% confident" should be correct exactly 80% of the time.

**Expected Calibration Error (ECE):**
```
1. Group predictions into bins by confidence (e.g., 0-10%, 10-20%, ..., 90-100%)
2. For each bin:
   accuracy = fraction of correct predictions in bin
   confidence = average predicted probability in bin
   gap = |confidence - accuracy|
3. ECE = weighted average of gaps, weighted by bin size
```

**Example:**
```
Bin 80-90%: 100 predictions, average confidence = 85%, accuracy = 70%
  gap = 15%, weight = 100/total

Bin 90-100%: 50 predictions, average confidence = 95%, accuracy = 80%
  gap = 15%, weight = 50/total

ECE = (100/150) × 15% + (50/150) × 15% = 15%
```

An ECE of 15% means the model is systematically overconfident by 15 percentage points.

**Why calibration matters:**
- In medical diagnosis, a calibrated "90% cancer" means doctors can trust the number
- In autonomous driving, calibrated uncertainty triggers human takeover at the right times
- In weather forecasting, calibration means "30% rain" actually rains 30% of the time

---

### Real-Life Analogy

A weather forecast.
- **Well-calibrated:** The station says "30% chance of rain" on 100 days. It rains on exactly 30 of those days. You can trust their numbers.
- **Overconfident:** The station says "90% chance of rain" on 100 days. It only rains on 60 of those days. Their numbers are inflated.
- **Underconfident:** The station says "50% chance of rain" on 100 days. It rains on 80 of those days. They are too cautious.

A calibrated model is like a trustworthy weather station. You can act on its probabilities.

---

### Tiny Numeric Example

**Model predictions on 10 examples:**
```
Confidences: [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50]
Correct:     [1,    1,    0,    1,    0,    1,    0,    0,    1,    0   ]
```

**Bins:**
```
Bin 50-70%: confidences [0.70, 0.65, 0.60, 0.55, 0.50], correct [1, 0, 0, 1, 0]
  avg confidence = 0.60, accuracy = 2/5 = 0.40, gap = 0.20

Bin 70-90%: confidences [0.90, 0.85, 0.80, 0.75], correct [1, 0, 1, 0]
  avg confidence = 0.825, accuracy = 2/4 = 0.50, gap = 0.325

Bin 90-100%: confidence [0.95], correct [1]
  avg confidence = 0.95, accuracy = 1/1 = 1.0, gap = 0.0
```

**ECE:**
```
ECE = (5/10) × 0.20 + (4/10) × 0.325 + (1/10) × 0.0
    = 0.10 + 0.13 + 0.0
    = 0.23 (23%)
```

The model is poorly calibrated, especially in the 70-90% bin where it is correct only 50% of the time despite 82.5% average confidence.

---

### Common Confusion

1. **"High accuracy means good calibration."** No. A model can have 99% accuracy and terrible calibration (always predicting 99% confidence, even when wrong).

2. **"Calibration fixes model accuracy."** No. Calibration only fixes the probabilities. A model can be perfectly calibrated but still inaccurate.

3. **"Temperature scaling is the only way to calibrate."** No. Platt scaling, isotonic regression, and label smoothing also help.

4. **"Calibration is only for classification."** Regression models can be calibrated too (e.g., checking if 80% confidence intervals contain 80% of true values).

5. **"LLMs are well-calibrated."** Often not. LLMs can be overconfident on questions outside their training distribution.

---

### Where It Is Used in Our Code

`src/phase51/phase51_evaluation_metrics.py` — We compute ECE on a set of probabilistic predictions, showing how to measure and visualize calibration gaps.
