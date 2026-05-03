## What Is Variational Inference?

---

### The Problem

In Bayesian inference, you want to compute the posterior distribution over model weights given data: `p(w|data)`. But for neural networks with millions of weights, this posterior is intractable to compute exactly. How do you approximate it efficiently?

---

### Definition

**Variational Inference (VI)** is a method for approximating complex probability distributions (like the true Bayesian posterior) with simpler, tractable distributions. Instead of computing the true posterior, you find the closest simple distribution to it.

**The core idea:**
```
True posterior:    p(w|D) = p(D|w) * p(w) / p(D)  ← intractable
Variational approx: q(w|λ) ~ N(μ, σ²)             ← tractable

Find λ that minimizes: KL(q(w|λ) || p(w|D))
```

**KL divergence:** A measure of how different two distributions are.
```
KL(q || p) = E_q[log q(w) - log p(w|D)]
```

**Why minimize KL divergence:**
- When KL = 0, q is exactly the true posterior
- When KL is small, q is a good approximation
- We cannot compute KL directly (requires the true posterior), so we maximize the Evidence Lower BOund (ELBO) instead

**ELBO:**
```
ELBO = E_q[log p(D|w)] - KL(q(w) || p(w))

Maximizing ELBO:
  - First term: model should fit the data well (likelihood)
  - Second term: q should stay close to the prior (regularization)
```

**Why this matters:**
- VI scales Bayesian inference to large models
- It is the foundation of modern Bayesian deep learning
- It provides a principled way to approximate uncertainty

---

### Real-Life Analogy

Finding the closest parking spot to a crowded stadium.
- **True posterior:** The exact location of your friend's seat inside the stadium. It exists, but finding it requires walking through every row and column.
- **Variational approximation:** You look at the stadium map and guess they are in "Section B, lower level." This is close enough for practical purposes.
- **KL divergence:** The distance between your guess and the true seat. You want to minimize this distance without ever actually finding the true seat.
- **ELBO:** A shortcut. Instead of measuring distance directly, you maximize "how well your guess explains what you can observe" (can you see the field from Section B? yes) minus "how far your guess is from your prior assumption" (I assumed they would be in Section A).

---

### Tiny Numeric Example

**True posterior (unknown, intractable):** `p(w|D)`
**Variational approximation:** `q(w) = N(μ=2.0, σ=0.5)`

**Data:** `D = {3.0, 3.5, 4.0}`

**ELBO computation:**
```
E_q[log p(D|w)]:
  Sample w from q: w = 2.0 + 0.5*z where z ~ N(0,1)
  For w = 1.8: log p(D|w) = log N(D; mean=1.8, σ=1) = -5.2
  For w = 2.2: log p(D|w) = -3.1
  Average over samples: ≈ -4.0

KL(q || p):
  Prior p(w) = N(0, 1)
  KL = log(1/0.5) + (0.5² + (2.0-0)²)/(2*1) - 0.5
     = 0.693 + 2.125 - 0.5 = 2.318

ELBO = -4.0 - 2.318 = -6.318
```

**Optimizing μ and σ:**
```
Try μ=3.0, σ=0.3:
  E_q[log p(D|w)] ≈ -2.5 (better fit)
  KL ≈ 3.5 (further from prior)
  ELBO = -6.0 (improved!)
```

VI finds the best μ and σ by gradient ascent on the ELBO.

---

### Common Confusion

1. **"VI gives the exact posterior."** No. It gives the closest approximation within the chosen family (e.g., Gaussian).

2. **"VI is only for Bayesian NNs."** No. It is used throughout probabilistic ML: topic models, Gaussian processes, generative models.

3. **"Mean-field VI assumes all weights are independent."** Yes, that is the simplest form. Structured VI captures correlations between weights but is more complex.

4. **"ELBO maximization is the same as maximum likelihood."** No. ELBO adds a KL term that acts as regularization, preventing overfitting.

5. **"VI is always better than MCMC."** VI is faster but biased. MCMC is slower but asymptotically exact. Choose based on your needs.

---

### Where It Is Used in Our Code

`src/phase60/phase60_bayesian_neural_networks.py` — We implement a simple variational linear regression by optimizing the ELBO, showing how the approximate posterior q(w) converges toward the true posterior as more data is observed.
