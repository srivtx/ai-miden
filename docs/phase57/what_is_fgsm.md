## What Is FGSM?

---

### The Problem

You want to attack a neural network but computing a full optimization is slow. You need a fast, one-step method to create an adversarial example. How do you generate a perturbation in a single gradient computation?

---

### Definition

**FGSM (Fast Gradient Sign Method)** is a one-step adversarial attack that creates a perturbation by taking a small step in the direction of the gradient of the loss with respect to the input.

**The FGSM formula:**
```
x_adv = x + ε * sign(∇_x L(θ, x, y))
```

Where:
- `x` = original input
- `ε` = perturbation magnitude (how much noise to add)
- `∇_x L` = gradient of the loss with respect to the input
- `sign()` = element-wise sign function (+1, -1, or 0)
- `y` = true label (for targeted attacks, we use the target label)

**Why the sign function?**
- We want the maximum change per pixel with a bounded budget
- `sign(gradient)` tells us which direction to perturb each pixel
- ε controls the total perturbation size

**For a targeted attack (make the model predict a specific wrong class):**
```
x_adv = x - ε * sign(∇_x L(θ, x, y_target))
```

We step AWAY from the target class's loss (minimizing loss on the wrong class).

---

### Real-Life Analogy

Pushing someone off balance.
- **The model:** A person standing upright.
- **The gradient:** The direction they are most unstable (e.g., leaning slightly left).
- **FGSM:** Instead of analyzing their full posture, you just push them hard in the direction they are already leaning. One push is enough because you chose the optimal direction.
- **ε:** How hard you push. Too soft and they recover. Too hard and it is obvious you pushed them.

FGSM is the "one good push" attack.

---

### Tiny Numeric Example

**Model:** `logits = W @ x + b` where `W = [2.0, -1.0]`, `b = 0`
**Input:** `x = [1.0, 1.0]`, true label `y = 0` (positive class)
**Loss:** Cross-entropy

**Forward pass:**
```
z = 2.0*1.0 + (-1.0)*1.0 = 1.0
p = sigmoid(1.0) = 0.731
```

**Loss gradient w.r.t. input:**
```
dL/dz = p - y = 0.731 - 0 = 0.731
dz/dx = W = [2.0, -1.0]
dL/dx = dL/dz * dz/dx = 0.731 * [2.0, -1.0] = [1.462, -0.731]
```

**FGSM perturbation (ε = 0.1):**
```
sign(dL/dx) = [1, -1]
perturbation = ε * sign(dL/dx) = [0.1, -0.1]
x_adv = [1.0, 1.0] + [0.1, -0.1] = [1.1, 0.9]
```

**New prediction:**
```
z_adv = 2.0*1.1 + (-1.0)*0.9 = 2.2 - 0.9 = 1.3
p_adv = sigmoid(1.3) = 0.786
```

Still predicts class 0. Let us try ε = 0.5:
```
x_adv = [1.0, 1.0] + [0.5, -0.5] = [1.5, 0.5]
z_adv = 2.0*1.5 + (-1.0)*0.5 = 3.0 - 0.5 = 2.5
p_adv = sigmoid(2.5) = 0.924
```

FGSM on a linear model actually makes it MORE confident in the correct class. This is because the loss gradient points toward maximizing loss, but for a linear model, the sign method is too crude.

**For non-linear models (neural networks):** The gradient points to a local maximum of the loss landscape. A small step can cross a decision boundary because the boundary is highly non-linear in input space.

---

### Common Confusion

1. **"FGSM always works."** No. It is a weak attack. Modern defenses and robust models often resist FGSM. Stronger attacks use iterative methods (PGD).

2. **"FGSM adds random noise."** No. The noise is highly structured — it is the sign of the gradient.

3. **"ε must be large to work."** For images, ε = 8/255 (3% of pixel range) is often enough.

4. **"FGSM is only for images."** It works on any differentiable model: text (embeddings), audio, tabular data.

5. **"FGSM and PGD are the same."** FGSM is one-step. PGD is iterative FGSM — it takes multiple small steps and projects back to the valid region.

---

### Where It Is Used in Our Code

`src/phase57/phase57_adversarial_robustness.py` — We implement FGSM on a small neural network, showing how a single gradient step creates adversarial inputs that flip predictions.
