## What Is PGD?

---

### The Problem

FGSM is fast but often too weak. A model might resist a single-step attack but fall to a more persistent adversary. How do you create stronger adversarial examples by taking multiple small steps instead of one big step?

---

### Definition

**PGD (Projected Gradient Descent)** is an iterative adversarial attack that takes multiple small gradient steps to find the most adversarial point within a bounded region around the original input.

**The PGD algorithm:**
```
Initialize: x_0 = x + random noise (within ε-ball)
For t = 1 to T:
  1. Compute gradient: g = ∇_x L(θ, x_{t-1}, y)
  2. Take a step: x' = x_{t-1} + α * sign(g)
  3. Project back to ε-ball: x_t = clip(x', x-ε, x+ε)
  4. Clip to valid input range: x_t = clip(x_t, 0, 1)
Return x_T
```

Where:
- `T` = number of iterations (typically 20-40)
- `α` = step size (typically ε/4 or ε/10)
- `clip(x', x-ε, x+ε)` = ensure perturbation stays within ε of original
- `clip(x_t, 0, 1)` = ensure pixel values stay valid

**Why iterative steps help:**
- FGSM takes one large step and might overshoot the optimal perturbation
- PGD explores the loss landscape more carefully
- It is like hill-climbing: many small steps reach a higher peak than one big leap

**PGD as the "universal" attack:**
- If a model is robust to PGD, it is likely robust to most other attacks
- PGD is the standard benchmark for adversarial robustness

---

### Real-Life Analogy

Picking a lock.
- **FGSM:** You try to force the lock with one hard twist. Sometimes it works on cheap locks. Good locks resist it.
- **PGD:** You carefully probe the lock, feeling each pin. You make small adjustments, testing after each one. You stay within the lock's tolerance so you don't break your tools. After 20 careful probes, the lock opens.

PGD is the patient lockpicker. FGSM is the brute-force wrecker.

---

### Tiny Numeric Example

**Model:** Single hidden layer ReLU network
**Input:** `x = [0.5, 0.5]`, true label `y = 0`
**Parameters:** `W1 = [[1, -1], [-1, 1]]`, `b1 = [0, 0]`, `W2 = [1, 1]`, `b2 = 0`

**Forward pass:**
```
h = ReLU(W1 @ x + b1) = ReLU([0, 0]) = [0, 0]
logit = W2 @ h + b2 = 0
p = sigmoid(0) = 0.5 (uncertain)
```

**FGSM (ε=0.1, one step):**
```
x_adv = x + 0.1 * sign(gradient) = [0.6, 0.6]
h = ReLU([0, 0]) = [0, 0]  (still dead ReLUs!)
logit = 0 → still 0.5
```

FGSM fails because the gradient w.r.t. input is zero (dead ReLUs).

**PGD (ε=0.1, α=0.02, T=10):**
```
Step 1: x_1 = [0.5, 0.5] + small random noise = [0.52, 0.48]
h = ReLU([0.04, -0.04]) = [0.04, 0]
```

Now the first ReLU is active. The gradient flows. Subsequent steps exploit this.

After several steps, PGD finds a perturbation that activates different neurons and flips the prediction, even though FGSM failed completely.

---

### Common Confusion

1. **"PGD is just FGSM repeated."** Almost, but the projection step is crucial. Without it, perturbations grow unbounded.

2. **"More iterations always mean stronger attacks."** Diminishing returns. After ~50 steps, PGD usually plateaus.

3. **"PGD is too slow for real attacks."** It is slower than FGSM but still fast (milliseconds per image on a GPU). For critical security, the extra strength is worth it.

4. **"PGD adversarial training makes models invincible."** No. It improves robustness but does not eliminate vulnerability. Adaptive attacks can still break PGD-trained models.

5. **"PGD only works for L-infinity bounds."** Variants exist for L2 and L1 bounds (PGD-L2, PGD-L1).

---

### Where It Is Used in Our Code

`src/phase57/phase57_adversarial_robustness.py` — We implement iterative PGD on a neural network, comparing its success rate to FGSM and showing how multiple steps find stronger adversarial examples.
