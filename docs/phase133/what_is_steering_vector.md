## What Is a Steering Vector?

---

### The Problem

You have a model that sometimes lies, sometimes drifts into casual slang, or sometimes produces depressing outputs. You suspect there is a single "direction" inside its neural activations that controls this trait, but you do not know how to find it or how to use it. How do you isolate the axis of "honesty" or "happiness" inside a 4096-dimensional vector space?

---

### Definition

A **steering vector** (also called a control vector or concept vector) is the normalized difference between the mean activations of a neural network on inputs that exhibit a target concept and inputs that exhibit the opposite or absence of that concept.

**Mathematical definition:**
```
Let A_positive be the set of hidden-state vectors h_i at layer L
for inputs that contain the concept (e.g., happy sentences).

Let A_negative be the same hidden-state vectors for inputs that
contain the opposite concept (e.g., sad sentences).

Steering vector v = mean(A_positive) - mean(A_negative)
```

**How it is applied:**
```
During inference, at layer L:
  h_steered = h_original + coefficient * v

Coefficient > 0 amplifies the concept.
Coefficient < 0 suppresses or reverses the concept.
Coefficient = 0 is the baseline.
```

**Layer selection:**
- Early layers (0-30%): syntax, token morphology
- Middle layers (40-60%): concepts, sentiment, style, reasoning
- Late layers (70-100%): next-token distribution, output formatting
- **Best practice:** target middle layers for high-level behavioral steering.

**Why this works:**
Neural networks tend to represent concepts as linear directions in activation space. This property, called linear representation, means that moving along the vector v reliably increases or decreases the presence of the concept in the model's output.

---

### Real-Life Analogy

Wind direction in meteorology.
- **The concept:** You want to know which way the wind blows. You cannot see the wind directly.
- **Positive examples:** You release 50 helium balloons on a calm day and track their drift northeast.
- **Negative examples:** You release 50 weighted flags and track their drift southwest.
- **Steering vector:** The average difference between the balloon trajectories and the flag trajectories gives you the prevailing wind vector.
- **Application:** Once you know the wind vector, a pilot can add it to the airplane's heading to stay on course. Without it, every flight drifts off target.

---

### Tiny Numeric Example

**A transformer block has a residual stream of dimension 4. We collect activations at layer 10:**

**Positive class ("happy"):**
```
  [2.0, 0.5, -1.0, 1.5]
  [1.8, 0.6, -0.9, 1.4]
  [2.2, 0.4, -1.1, 1.6]
  Mean: [2.00, 0.50, -1.00, 1.50]
```

**Negative class ("sad"):**
```
  [-0.5, 1.0, 2.0, -1.0]
  [-0.4, 0.9, 1.9, -0.9]
  [-0.6, 1.1, 2.1, -1.1]
  Mean: [-0.50, 1.00, 2.00, -1.00]
```

**Steering vector:**
```
v = [2.00, 0.50, -1.00, 1.50] - [-0.50, 1.00, 2.00, -1.00]
  = [2.50, -0.50, -3.00, 2.50]
```

**Normalize (optional but recommended):**
```
||v|| = sqrt(2.50^2 + (-0.50)^2 + (-3.00)^2 + 2.50^2) = 4.53
v_norm = [0.55, -0.11, -0.66, 0.55]
```

**Steer a new activation h = [0.2, 0.3, 0.1, -0.2] with coefficient 3:**
```
h_steered = [0.2, 0.3, 0.1, -0.2] + 3 * [0.55, -0.11, -0.66, 0.55]
          = [1.85, -0.03, -1.88, 1.45]
```

**Result:** The third dimension (strongly negative in v) is pushed far negative, while the first and fourth dimensions are pushed positive. The model's next-token sampler now strongly prefers tokens associated with the positive class.

---

### Common Confusion

1. **"The steering vector must be orthogonal to everything else."** No. The vector is simply the mean difference. It almost certainly overlaps with other concepts. That is why steering can have side effects: pushing "honesty" might accidentally push "formality" if the two concepts are correlated in the training data.

2. **"You should normalize the steering vector to unit length."** Sometimes yes, sometimes no. Normalization makes the coefficient interpretable as a distance in standard deviations. However, raw magnitudes encode the strength of the concept separation, so unnormalized vectors can be more effective.

3. **"Steering vectors only work on the last token of a sequence."** You can average activations across all token positions, or you can use only the final token. Averaging often yields a cleaner vector because it reduces position-specific noise, but the last token can be sharper for sentence-level concepts.

4. **"A steering vector extracted from layer L must be applied at layer L."** Generally yes. Each layer has its own residual stream geometry. A vector from layer 10 will not align with the concept direction at layer 20. You extract and apply at the same layer.

5. **"Steering is the same as adding a bias term to the layer."** A bias is added to the pre-activation (before the nonlinearity). A steering vector is added to the hidden state or residual stream (after the nonlinearity). They live in different spaces and have different effects.

6. **"One global steering vector works for every prompt."** The vector is prompt-dependent in magnitude. A coefficient of +3 might be subtle for one prompt and overwhelming for another. In practice you tune the coefficient per use case.

7. **"Steering vectors are always additive."** Addition is the most common method, but researchers have also used multiplicative scaling, clamping specific neurons, and replacing entire activation subspaces. Additive steering is the simplest and most robust starting point.

---

### Where It Is Used in Our Code

`src/phase133/phase133_steering_concepts.py` — We build contrastive datasets in NumPy, compute mean activations for positive and negative classes, derive the steering vector, and show that adding it to middle-layer activations shifts the model's outputs in the intended direction.

`src/phase133/phase133_steering_colab.py` — We extract a real steering vector from Llama-3.2-3B-Instruct by feeding happy and sad sentences through the model, capturing layer-15 activations with a forward hook, and testing generation at coefficients -3, 0, and +3.
