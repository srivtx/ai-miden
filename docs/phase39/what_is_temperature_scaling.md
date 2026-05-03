## What Is Temperature Scaling?

---

### The Problem

In knowledge distillation, the teacher's raw logits might be too sharp (e.g., [5.0, -2.0, -3.0] → [0.99, 0.005, 0.005]). The student cannot learn much from such extreme probabilities because the gradients for the incorrect classes are nearly zero. How do you make the teacher's distribution more informative?

---

### Definition

**Temperature scaling** divides logits by a temperature parameter T before applying softmax:
```
P(i) = exp(z_i / T) / Σ exp(z_j / T)
```

**Effect of T:**
- **T = 1:** Standard softmax (sharp distribution)
- **T > 1:** Softer distribution (more probability mass on incorrect classes)
- **T < 1:** Sharper distribution (more extreme, approaching one-hot)

**Why it helps distillation:**
When T > 1, the teacher reveals more about the relative probabilities of incorrect classes. The student gets meaningful gradients for all classes, not just the top one.

---

### Real-Life Analogy

A professor grading essays.
- **T = 1 (normal):** The professor gives clear As and Fs. Students learn what is perfect and what is failing, but miss the nuance between B+ and A- work.
- **T = 4 (high temperature):** The professor gives detailed rubrics showing exactly how close each essay was to the next grade level. A B+ essay was "almost an A- — just needed stronger thesis." An F essay was "not even close." Students learn the gradations between quality levels.

High temperature gives the student (apprentice) a richer signal about what matters.

---

### Tiny Numeric Example

**Logits:** z = [2.0, 0.5, -1.0]

**T = 1 (standard):**
```
exp = [7.389, 1.649, 0.368]
sum = 9.406
P = [0.786, 0.175, 0.039]
```

**T = 2:**
```
z/T = [1.0, 0.25, -0.5]
exp = [2.718, 1.284, 0.607]
sum = 4.609
P = [0.590, 0.279, 0.131]
```

**T = 4:**
```
z/T = [0.5, 0.125, -0.25]
exp = [1.649, 1.133, 0.779]
sum = 3.561
P = [0.463, 0.318, 0.219]
```

**Comparison:**

| T | Class 0 | Class 1 | Class 2 | Entropy |
|---|---|---|---|---|
| 1 | 0.786 | 0.175 | 0.039 | 0.68 |
| 2 | 0.590 | 0.279 | 0.131 | 1.30 |
| 4 | 0.463 | 0.318 | 0.219 | 1.56 |

As T increases, the distribution becomes more uniform (higher entropy), revealing more information about the relative ranking of all classes.

**Gradients:**
For a student with logits [1.5, 0.3, -0.8], the gradient from KL divergence is proportional to (P_teacher - P_student). At T=4, the gradient for class 2 is (0.219 - 0.170) = 0.049 — non-zero and meaningful. At T=1, it is (0.039 - 0.015) = 0.024 — much smaller.

---

### Common Confusion

1. **"Temperature changes the model's accuracy."** No. Temperature scaling is applied during distillation training only. At inference, T=1 is used. The teacher's accuracy is unchanged.

2. **"Higher temperature always helps."** Not beyond T=5-10. Very high temperature makes all probabilities nearly equal, destroying the signal. The student cannot learn which class is truly preferred.

3. **"Temperature is the same as confidence calibration."** Temperature scaling is also used for calibration (making model probabilities match true likelihoods), but in distillation its purpose is different: to create richer training targets.

4. **"Temperature must be the same for teacher and student."** Yes, during distillation both use the same T. But the student can be trained with additional hard-label loss at T=1.

5. **"T² scaling in the loss is optional."** It is mathematically necessary. When you divide logits by T, gradients scale by 1/T. Multiplying the distillation loss by T² restores the gradient magnitude.

---

### Where It Is Used in Our Code

`src/phase39/phase39_knowledge_distillation.py` — The `softmax_with_temperature()` function implements temperature scaling. We compare student training with T=1 vs. T=4 to show how softer labels improve learning.
