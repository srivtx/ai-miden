# What Is the Score Function?

**The Problem:** You have a probability distribution p(x). You want to draw samples from it. You don't know p(x) up to a constant (you can evaluate p(x) for any x, but the constant is unknown — this is the "unnormalized density" setting). You can't do MCMC easily (high dimensions, slow). What's the *fastest* way to sample? Modern diffusion models answer this question by learning the *score* $\nabla_x \log p(x)$ and then sampling by integrating a reverse-time SDE.

**Definition:** The *score function* of a distribution p(x) is the gradient of the log-probability density:

$$\mathbf{s}(x) = \nabla_x \log p(x) = \frac{\nabla_x p(x)}{p(x)}$$

It is a *vector field* on the space of x. It points in the direction of *highest increase* in log-probability.

**Why it matters:**

- The score tells you *which way* is "more probable." If you're at a low-probability x, the score points toward higher-probability regions.
- If you know the score, you can sample by *following* the score (or its noise-perturbed version) via Langevin dynamics or reverse SDE.
- Crucially, the score does not depend on the *normalization constant* of p. If p(x) = Z q(x), then $\nabla_x \log p(x) = \nabla_x \log q(x)$. So you can learn the score from an unnormalized density.

**How It Works (Step-by-Step):**

1. **For a Gaussian** $p(x) = \mathcal{N}(x; \mu, \Sigma)$:
   $$\log p(x) = -\frac{1}{2}(x - \mu)^T \Sigma^{-1} (x - \mu) - \frac{1}{2} \log \det(2\pi\Sigma)$$
   $$\nabla_x \log p(x) = -\Sigma^{-1}(x - \mu)$$
   
   The score points from $x$ toward $\mu$, scaled by the inverse covariance.

2. **For a mixture of Gaussians**: the score is a weighted average of the scores of each component, with weights proportional to the component responsibilities. Near a mode, the score points to that mode. Between modes, the score points away from the lower-density region.

3. **Langevin dynamics** (sampling with the score):
   $$x_{t+1} = x_t + \frac{\epsilon}{2} \nabla_x \log p(x_t) + \sqrt{\epsilon} z_t, \quad z_t \sim \mathcal{N}(0, I)$$
   
   This is *Langevin dynamics*. For small enough $\epsilon$, the distribution of $x_T$ converges to p(x). This is the simplest way to sample using the score.

4. **Denoising score matching** (learning the score):
   - You don't have $p(x)$ as a closed form. You have samples $x_i \sim p_{\text{data}}$.
   - For Gaussian-perturbed data, the score of the perturbed distribution is:
     $$\nabla_x \log p_\sigma(x) = -\frac{x - x_0}{\sigma^2}$$
     where $x_0 \sim p_{\text{data}}$ and $x = x_0 + \sigma z$, $z \sim \mathcal{N}(0, I)$.
   - This is the *Tweedie* identity. It lets you compute the score at a noisy data point.
   - Train a network $s_\theta(x, \sigma)$ to match this. The loss is:
     $$\mathcal{L} = \mathbb{E}_{x_0, \sigma, z} \left[ \| s_\theta(x_0 + \sigma z, \sigma) + z/\sigma \|^2 \right]$$
   - This is the loss used in DDPM and most modern diffusion models.

5. **Reverse SDE** (sampling with the score):
   - Start with $x_T \sim \mathcal{N}(0, I)$ (pure noise).
   - Integrate the *reverse-time SDE*:
     $$dx = [f(x, t) - g(t)^2 \nabla_x \log p_t(x)] dt + g(t) d\bar{w}$$
     where $f$ is the drift of the forward process, $g$ is the diffusion coefficient, and $d\bar{w}$ is a reverse-time Wiener process.
   - This requires the score $\nabla_x \log p_t(x)$ at every noise level $t$.
   - The network $s_\theta(x, t)$ learns this score. We get samples by integrating the reverse SDE.

**Real-life analogy:** The score is like a *hiking compass* that points uphill. If you're in a foggy mountain and want to find the peak, follow the compass. If you want to sample from a distribution, start at a random point and follow the score — you'll end up at high-probability regions. With noise (Langevin dynamics), you explore the whole distribution.

**Tiny numeric example:** For $p(x) = \mathcal{N}(0, 1)$, the score is $\nabla_x \log p(x) = -x$. So at $x = 2$, the score is $-2$, pointing toward $x = 0$ (the mean). At $x = -1$, the score is $+1$, pointing toward $x = 0$.

Langevin dynamics with $\epsilon = 0.1$:
- Start: $x_0 = 3$
- Step 1: $x_1 = 3 + 0.05 \cdot (-3) + \sqrt{0.1} \cdot z_1 = 3 - 0.15 + 0.316 z_1$
- Continue for 100 steps. The samples will be approximately distributed as $\mathcal{N}(0, 1)$.

**Common confusion:**

- "The score is the probability." No, the score is the *gradient* of log-probability. It is a vector, not a scalar.
- "Knowing the score is the same as knowing p(x)." No, the score does not determine p(x) up to a constant. If p_1(x) and p_2(x) differ by a constant, they have the same score. So the score is the *shape* of p, not its absolute value.
- "You can integrate the score to get log p(x)." No, not in general. The score is a gradient field, and integrating it requires it to be a *conservative* field. In high dimensions, this is often not the case.
- "Langevin dynamics is just gradient ascent." No, gradient ascent finds the *mode*. Langevin dynamics adds noise, which lets you sample from the *whole* distribution.
- "Score matching requires knowing p(x)." No, the *denoising* version uses the Tweedie identity to compute the score at noisy data points, without ever evaluating p(x).
- "The score is a learned function." Yes, in modern diffusion models. The network $s_\theta(x, t)$ approximates $\nabla_x \log p_t(x)$ for the perturbed distribution at noise level $t$.

**Key properties:**

- **Independent of normalization**: $\nabla_x \log p(x) = \nabla_x \log q(x)$ if $p = Z q$.
- **Vector field**: a function of $x$ that returns a vector of the same shape as $x$.
- **Points uphill in log-probability**: this is the direction of fastest increase in log p.
- **Denoising identity**: at noise level $\sigma$, the score of $p_\sigma$ at $x$ is $-\frac{x - \mathbb{E}[x_0 | x]}{\sigma^2}$ (Tweedie).
- **Tractable to learn**: via denoising score matching (no need for $p(x)$).
- **Tractable to sample from**: via Langevin dynamics or reverse SDE.

**Tech comparison:**

| Method | Learns | Samples via | Cost |
|---|---|---|---|
| VAE | Encoder + decoder | Ancestral | Fast (1 pass) |
| GAN | Generator | Implicit | Fast (1 pass) |
| Flow | Invertible net | Exact | Fast (1 pass) |
| Diffusion | Score | Reverse SDE | Slow (100s of steps) |
| Autoregressive | Conditional densities | Ancestral | Slow (1 step per token) |

**Connection to generative models:** The score is the central object of *modern* diffusion models (DDPM, score-based, latent diffusion). It is what the network learns. It is what makes the math work. Every paper in this family talks about "learning the score," "matching the score," or "denoising." If you understand the score, you understand diffusion.
