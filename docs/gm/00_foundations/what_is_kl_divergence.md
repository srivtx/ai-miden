# What Is KL Divergence?

**The Problem:** You have two probability distributions p(x) and q(x). You want to measure how *different* they are. This is the central question of generative modeling: how close is your model's distribution to the data distribution? KL divergence is the standard answer.

**Definition:** The *Kullback-Leibler (KL) divergence* from q to p is:

$$D_{KL}(p \| q) = \int p(x) \log \frac{p(x)}{q(x)} dx = \mathbb{E}_{x \sim p} \left[ \log \frac{p(x)}{q(x)} \right]$$

It is non-negative, $D_{KL}(p \| q) \geq 0$, with equality iff $p = q$. It is *not* a metric (not symmetric, doesn't satisfy the triangle inequality).

**How It Works (Step-by-Step):**

1. **Interpretation 1: information-theoretic.** $D_{KL}(p \| q)$ is the *extra number of bits* (or nats) needed to encode samples from p using a code optimized for q. If p = q, no extra bits. If p ≠ q, more bits.

2. **Interpretation 2: statistical.** $D_{KL}(p \| q)$ is the expected log-ratio of the densities. If p and q are very different at some x, the log-ratio is large.

3. **Discrete form**: for discrete distributions,
   $$D_{KL}(p \| q) = \sum_x p(x) \log \frac{p(x)}{q(x)}$$

4. **Forward vs reverse KL**:
   - $D_{KL}(p \| q)$ (forward): zero-forcing. If $q(x) = 0$ wherever $p(x) > 0$, then $D_{KL} = \infty$. Forces q to cover all of p.
   - $D_{KL}(q \| p)$ (reverse): mass-covering. Allows q to be zero in regions where p is small. Tends to make q over-disperse.

5. **Connection to maximum likelihood**: minimizing $D_{KL}(p_{\text{data}} \| p_\theta)$ is equivalent to maximum likelihood estimation of $\theta$. This is the most important fact in generative modeling.

**Derivation: maximum likelihood = KL minimization.**

The negative log-likelihood loss is:
$$L(\theta) = -\mathbb{E}_{x \sim p_{\text{data}}} [\log p_\theta(x)]$$

This is the same as:
$$L(\theta) = -\sum_x p_{\text{data}}(x) \log p_\theta(x) = -\sum_x p_{\text{data}}(x) [\log p_\theta(x) - \log p_{\text{data}}(x)] - H(p_{\text{data}})$$

The first term is $D_{KL}(p_{\text{data}} \| p_\theta)$. The second term $H(p_{\text{data}})$ is the entropy of the data, which doesn't depend on $\theta$. So minimizing the KL divergence is the same as minimizing the negative log-likelihood, which is the same as maximum likelihood.

**Real-life analogy:** KL divergence is like a *language confusion*. If you are an English speaker (q) listening to French (p), the "extra bits" you need to understand is $D_{KL}(\text{French} \| \text{English})$. If you are a French speaker listening to English, it's $D_{KL}(\text{English} \| \text{French})$. The two are different — the asymmetry reflects the asymmetry of which language you are more familiar with.

**Tiny numeric example:**

```python
import numpy as np

def kl_divergence(p, q):
    """Compute KL(p || q) for discrete distributions."""
    p = np.asarray(p, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64)
    # Avoid log(0)
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log(p[mask] / q[mask]))

# Two distributions
p = [0.5, 0.3, 0.2]
q = [0.4, 0.4, 0.2]

print(f"D_KL(p || q) = {kl_divergence(p, q):.4f}")  # 0.0252
print(f"D_KL(q || p) = {kl_divergence(q, p):.4f}")  # 0.0252 (here, symmetric)

# Asymmetric case
p = [0.99, 0.01]
q = [0.5, 0.5]
print(f"D_KL(p || q) = {kl_divergence(p, q):.4f}")  # 0.6531
print(f"D_KL(q || p) = {kl_divergence(q, p):.4f}")  # 0.0201
# D_KL(p || q) is large because p has 0.99 on index 0 but q has only 0.5
# D_KL(q || p) is small because q's mass is "covered" by p
```

**Common confusion:**

- "KL divergence is a distance." No, it is a *divergence*. It is not symmetric: $D_{KL}(p \| q) \neq D_{KL}(q \| p)$ in general. It also doesn't satisfy the triangle inequality.
- "Forward KL and reverse KL are the same." No, they have different properties. Forward KL is *zero-forcing* (q must cover all of p). Reverse KL is *mass-covering* (q can ignore parts of p). This affects variational inference.
- "Minimizing KL is the same as maximum likelihood." Yes, *forward* KL ($D_{KL}(p_{\text{data}} \| p_\theta)$) corresponds to maximum likelihood. Reverse KL is different.
- "KL divergence is bounded." No, it can be infinite (e.g., if p has support where q is zero).
- "KL divergence is differentiable." Yes, almost everywhere. It is not differentiable at points where either distribution is zero.
- "KL divergence is the only divergence." No. There are many: Jensen-Shannon, Wasserstein, total variation, f-divergences, chi-squared. Each has different properties. Wasserstein is popular in GANs because it is continuous even when distributions don't overlap.

**Key properties:**

- **Non-negative**: $D_{KL}(p \| q) \geq 0$.
- **Zero iff equal**: $D_{KL}(p \| q) = 0 \iff p = q$.
- **Asymmetric**: $D_{KL}(p \| q) \neq D_{KL}(q \| p)$ in general.
- **Additive for independent distributions**: $D_{KL}(p(x, y) \| q(x, q)) = D_{KL}(p(x) \| q(x)) + D_{KL}(p(y) \| q(y))$ if $p(x, y) = p(x) p(y)$ and $q(x, y) = q(x) q(y)$.
- **Not a metric**: fails symmetry and triangle inequality.

**Tech comparison:**

| Divergence | Symmetric | Differentiable | Use case |
|---|---|---|---|
| KL | No | Almost | Maximum likelihood, VAE |
| Reverse KL | No | Almost | Variational inference, recognition |
| Jensen-Shannon | Yes | Yes | GANs (with some tricks) |
| Wasserstein | Yes | Yes (under conditions) | Wasserstein GAN |
| Total variation | Yes | No | Hypothesis testing |

**Connection to generative models:** Training a generative model is *equivalent* to minimizing $D_{KL}(p_{\text{data}} \| p_\theta)$ over $\theta$. This is what "maximum likelihood" means. The catch is that you usually can't compute this KL directly (you don't know $p_{\text{data}}$ as a density, only as samples). The ELBO is a workaround (see `what_is_elbo.md`).
