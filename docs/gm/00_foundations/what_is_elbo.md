# What Is the ELBO?

**The Problem:** You want to train a generative model $p_\theta(x)$ of a complex distribution (e.g., the distribution of natural images). The training objective is to maximize $\log p_\theta(x)$ — the log-probability of the data under the model. But you can't compute this directly, because computing $p_\theta(x)$ requires an intractable integral over latent variables. The ELBO is a *lower bound* on $\log p_\theta(x)$ that you can compute and optimize.

**Definition:** The *Evidence Lower Bound (ELBO)* is:

$$\text{ELBO}(x; \theta, \phi) = \mathbb{E}_{z \sim q_\phi(z | x)} [\log p_\theta(x | z)] - D_{KL}(q_\phi(z | x) \| p(z))$$

where:
- $x$ is the data
- $z$ is a latent variable
- $p_\theta(x | z)$ is the decoder (likelihood)
- $q_\phi(z | x)$ is the encoder (approximate posterior)
- $p(z)$ is the prior on the latent

The ELBO is a lower bound on $\log p_\theta(x)$:
$$\log p_\theta(x) \geq \text{ELBO}(x; \theta, \phi)$$

with equality iff $q_\phi(z | x) = p_\theta(z | x)$ (the approximate posterior matches the true posterior).

**How It Works (Step-by-Step):**

1. **The model**: $p_\theta(x, z) = p_\theta(x | z) p(z)$. We have data $x$ and latent $z$. We want to compute $\log p_\theta(x) = \log \int p_\theta(x, z) dz$.

2. **The problem**: The integral $\int p_\theta(x, z) dz$ is intractable for high-dimensional $z$. We can't compute $\log p_\theta(x)$ directly.

3. **The trick**: Introduce an approximate posterior $q_\phi(z | x)$. Then:
   $$\log p_\theta(x) = \log \int q_\phi(z | x) \frac{p_\theta(x, z)}{q_\phi(z | x)} dz \geq \int q_\phi(z | x) \log \frac{p_\theta(x, z)}{q_\phi(z | x)} dz = \text{ELBO}$$

   The inequality is *Jensen's inequality* ($\log$ is concave).

4. **Decompose the ELBO**:
   $$\text{ELBO} = \underbrace{\mathbb{E}_{q_\phi(z | x)} [\log p_\theta(x | z)]}_{\text{reconstruction}} - \underbrace{D_{KL}(q_\phi(z | x) \| p(z))}_{\text{regularization}}$$

   The first term encourages the decoder to reconstruct $x$ from $z$ (high likelihood). The second term encourages the encoder to be close to the prior (regularization).

5. **Train by maximizing the ELBO**: $\max_{\theta, \phi} \text{ELBO}$. This is equivalent to $\min_{\theta, \phi} D_{KL}(q_\phi(z | x) \| p_\theta(z | x))$ — minimizing the divergence between the approximate and true posterior.

**Why it works:**

- The ELBO is a *tractable* lower bound. It can be computed (assuming we can sample from $q_\phi$ and evaluate $p_\theta$ and $p$).
- Maximizing the ELBO is a *surrogate* for maximizing $\log p_\theta(x)$. As the bound tightens (when $q_\phi$ matches $p_\theta(z | x)$), the surrogate becomes exact.
- Tightening the bound is itself a learning signal: better $q_\phi$ → tighter bound → better $p_\theta$.

**Real-life analogy:** The ELBO is like a *probabilistic ledger*. You want to know the total "value" of $x$ under the model. You can't compute it directly, so you estimate it by sampling from an approximation. The approximation is biased low (the bound), but the bias is the divergence between the approximation and the truth. As the approximation improves, the bound tightens and the estimate gets closer to the truth.

**Tiny numeric example:** 1D Gaussian example.

Let $p_\theta(x | z) = \mathcal{N}(x; z, 1)$ and $p(z) = \mathcal{N}(0, 1)$. Let $q_\phi(z | x) = \mathcal{N}(z; x, 1)$.

The true posterior is $p_\theta(z | x) = \mathcal{N}(z; x/2, 1/2)$.

The KL divergence $D_{KL}(q_\phi(z | x) \| p_\theta(z | x)) = D_{KL}(\mathcal{N}(x, 1) \| \mathcal{N}(x/2, 1/2))$.

For $x = 1$:
- $D_{KL} = \frac{1}{2} \log \frac{1/2}{1} + \frac{(1 - 1/2)^2}{2 \cdot 1/2} - \frac{1}{2} + 1 = \frac{1}{2} \log(0.5) + 0.25 - 0.5 + 1 \approx 0.097$

The ELBO is:
- Reconstruction: $\mathbb{E}_{z \sim \mathcal{N}(1, 1)}[\log \mathcal{N}(1; z, 1)] = \mathbb{E}[-\frac{1}{2}(1-z)^2 - \frac{1}{2} \log(2\pi)] = -\frac{1}{2} \text{Var}(z) - \frac{1}{2} \log(2\pi) = -\frac{1}{2} - 0.919 = -1.419$
- KL: $D_{KL}(\mathcal{N}(1, 1) \| \mathcal{N}(0, 1)) = \frac{1}{2}(1^2 + 0 - 1 + 0) = 0.5$
- ELBO: $-1.419 - 0.5 = -1.919$

True log-likelihood: $\log p_\theta(1) = \log \int \mathcal{N}(1; z, 1) \mathcal{N}(z; 0, 1) dz = \log \mathcal{N}(1; 0, 2) = -\frac{1}{2} \cdot \frac{1}{4} - \frac{1}{2} \log(4\pi) \approx -1.919$

So the bound is tight (within rounding) when $q_\phi$ is the true posterior. Good.

**Common confusion:**

- "ELBO is a magical lower bound." No, it's a mathematical fact (Jensen's inequality). It always holds, and it is always a lower bound. The trick is choosing $q_\phi$ well.
- "Maximizing the ELBO maximizes the data likelihood." Yes, approximately. The gap is the KL divergence between $q_\phi$ and the true posterior. If $q_\phi$ is good, the gap is small.
- "The ELBO requires choosing $q_\phi$." Yes, this is a design choice. Common choices: mean-field, normalizing flow, encoder network (in VAE).
- "ELBO is the only lower bound." No. The ELBO is the *evidence* lower bound. There are tighter bounds (e.g., IWAE, alpha-divergence, f-divergence). Each trades off tightness, variance, and computational cost.
- "The two terms of the ELBO are independent." No, they are coupled through the choice of $q_\phi$. A flexible $q_\phi$ (e.g., normalizing flow) gives better reconstruction *and* better matching to the prior, but is more expensive.
- "ELBO is just a loss function." Yes, but a *principled* one. It comes from a clear probabilistic interpretation. Many "loss functions" in ML don't.

**Key properties:**

- **Lower bound**: $\log p_\theta(x) \geq \text{ELBO}(x; \theta, \phi)$ for any $q_\phi$.
- **Tight when accurate**: equality iff $q_\phi(z | x) = p_\theta(z | x)$.
- **Two interpretations**: (a) reconstruction - KL, (b) expected log-joint - entropy of $q$.
- **Tractable**: can be estimated by sampling $z \sim q_\phi$ and Monte Carlo.
- **Differentiable w.r.t. $\theta$ and $\phi$** (with reparameterization for $\phi$).

**Tech comparison:**

| Bound | Tightness | Variance | Cost |
|---|---|---|---|
| ELBO | Loose | Low | 1 sample |
| IWAE | Tighter | Higher | K samples |
| Alpha-divergence | Family | Tunable | Variable |
| f-divergence | Family | Tunable | Variable |

**Connection to generative models:** The ELBO is the training objective of the *Variational Autoencoder (VAE)* (Part 1). The same idea generalizes: any model with latent variables and intractable likelihoods can be trained by maximizing the ELBO. The score function (Part 0.5) is closely related: the gradient of the ELBO with respect to $\theta$ is an estimate of the score.
