## What Is Adversarial Training?

---

### The Problem

Your model is vulnerable to adversarial examples. You can generate attacks, but how do you make the model itself resist them? Simply detecting attacks is not enough — you need to change the model so that small perturbations do not flip its predictions.

---

### Definition

**Adversarial training** is the process of training a model on a mixture of clean and adversarially perturbed examples so that the model learns to be robust against small input perturbations.

**Standard training objective:**
```
minimize E[ L(f(x), y) ]
```

**Adversarial training objective:**
```
minimize E[ max_{||δ||≤ε} L(f(x + δ), y) ]
```

This is a min-max game:
- **Inner maximization:** Find the worst perturbation δ within budget ε
- **Outer minimization:** Train the model to resist that worst-case perturbation

**How it works in practice:**
```
For each batch:
  1. Generate adversarial examples using FGSM or PGD
  2. Train on MIX of clean + adversarial examples (usually 50/50)
  3. Backpropagate loss on both
```

**Why this works:**
- The model sees hard examples during training
- It learns smoother decision boundaries
- Features become less brittle and more human-aligned

**Trade-offs:**
- Clean accuracy drops slightly (2-10%)
- Training is 2-10× slower (must generate adversarial examples each batch)
- Robustness is specific to the attack type trained against

---

### Real-Life Analogy

Vaccination.
- **Standard training:** A person grows up in a sterile environment. They are healthy — until they encounter a virus. Their immune system panics.
- **Adversarial training (vaccination):** The person is exposed to weakened viruses (adversarial examples). Their immune system learns to recognize and fight them. When the real virus comes, they are prepared.
- **The trade-off:** Vaccinated people might have slightly more tired immune systems (lower clean accuracy), but they do not die from the flu (robust to attacks).

Adversarial training is vaccination for neural networks.

---

### Tiny Numeric Example

**Linear model:** `f(x) = sign(w @ x)` where `w = [1.0, 0.1]`

**Standard training** on clean data learns a boundary nearly vertical.

**Adversarial training** with ε = 0.5:
```
The worst perturbation is δ = [-0.5, 0] (reduce the dominant feature).

Adversarial example: x_adv = x + [-0.5, 0]

The model must classify x_adv correctly too.
To do this, it learns to weight both features more equally:
  w = [0.6, 0.6] instead of [1.0, 0.1]

Now perturbing one feature by 0.5 is less devastating
because the other feature still contributes.
```

**Result:**
```
Clean accuracy: drops from 98% to 92%
Adversarial accuracy (ε=0.5): rises from 15% to 75%
```

The model becomes less sensitive to any single feature — a more robust decision boundary.

---

### Common Confusion

1. **"Adversarial training makes models perfectly robust."** No. It improves robustness but models can still be attacked with larger perturbations or adaptive methods.

2. **"You just add noise to training data."** No. Random noise does not help. The noise must be adversarial — computed to maximize loss.

3. **"Adversarial training hurts clean accuracy too much."** Modern methods (TRADES, MART) trade off less clean accuracy for robustness.

4. **"Adversarial training is only for images."** Works for text (adversarial word substitutions), audio, and any differentiable model.

5. **"If I train on FGSM, I am safe from PGD."** No. FGSM-trained models are often still vulnerable to PGD. You must train on the strongest attack you expect to face.

---

### Where It Is Used in Our Code

`src/phase57/phase57_adversarial_robustness.py` — We train a neural network on a mix of clean and adversarial examples, then compare its robustness to a standard-trained model under FGSM and PGD attacks.
