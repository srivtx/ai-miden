# What Is Score Matching?

**The Problem:** You want to learn the *score function* $\nabla_x \log p(x)$ of a distribution $p(x)$ (Part 0.5). The score is the central object of modern diffusion: once you have it, you can sample by Langevin dynamics or reverse SDE. But you don't have $p(x)$ as a closed form — you only have samples. How do you learn the score from samples?

**Definition:** *Score matching* is a training objective that learns the score $\nabla_x \log p(x)$ from samples of $p(x)$. The *denoising* version is what diffusion models use:

$$\mathcal{L}_{\text{DSM}} = \mathbb{E}_{x_0 \sim p_{\text{data}}, \sigma, \epsilon} \left[ \left\| s_\theta(x_0 + \sigma \epsilon, \sigma) + \frac{\epsilon}{\sigma} \right\|^2 \right]$$

where $\epsilon \sim \mathcal{N}(0, I)$, $\sigma$ is a noise level, and $s_\theta$ is a network that takes a noisy input and a noise level, and outputs the score.

**The Tweedie identity (the key insight):**

For Gaussian-perturbed data, the *best* denoising of $x = x_0 + \sigma \epsilon$ is the conditional mean $\mathbb{E}[x_0 | x]$. The optimal score is:
$$\nabla_x \log p_\sigma(x) = -\frac{x - \mathbb{E}[x_0 | x]}{\sigma^2}$$

This is the *Tweedie identity* (Efron 2011, applied to score matching by Hyvärinen 2005 and Vincent 2011). It says: if you can predict $\mathbb{E}[x_0 | x]$ (the denoised version of $x$), you have the score. So *denoising is the same as learning the score*.

**Why this matters for diffusion:**

- The network $s_\theta(x, t)$ predicts the score at noise level $t$.
- Equivalently, the network $\epsilon_\theta(x, t)$ predicts the noise $\epsilon$ that was added.
- The two are related: $s_\theta(x, t) = -\epsilon_\theta(x, t) / \sigma_t$ where $\sigma_t = \sqrt{(1 - \bar\alpha_t) / \bar\alpha_t}$.
- The training loss is the same: predict the noise (or equivalently, predict the score).

**How It Works (Step-by-Step):**

1. **Sample a data point** $x_0 \sim p_{\text{data}}$.
2. **Sample a noise level** $\sigma$ (or $t$).
3. **Sample noise** $\epsilon \sim \mathcal{N}(0, I)$.
4. **Compute noisy input** $x = x_0 + \sigma \epsilon$.
5. **Predict the noise** $\hat\epsilon = \epsilon_\theta(x, \sigma)$ (or the score $s_\theta = -\hat\epsilon / \sigma$).
6. **Compute loss** $\| \hat\epsilon - \epsilon \|^2$.
7. **Backprop** and update.

**Connection to DDPM:**

DDPM's training loss is exactly denoising score matching. The "noise" $\epsilon$ in DDPM is the same as the noise $\epsilon$ in DSM. The "denoising target" is the same. The network is learning the score, just parameterized differently.

**Why predicting noise is better than predicting the clean image:**

- Predicting the noise is *scale-invariant* (the noise always has unit variance).
- Predicting the clean image is scale-dependent (large images have larger pixel values).
- Empirically, predicting noise converges faster and gives better samples.

**Why multiple noise levels:**

- At small $\sigma$ (low noise), the score is dominated by the data distribution's local structure.
- At large $\sigma$ (high noise), the score approximates the prior.
- Training on multiple $\sigma$ levels lets the network learn a *multi-scale* representation.
- This is why diffusion works: the network learns to denoise at all noise levels.

**Real-life analogy:** Score matching is like learning a *map's contours* from elevation samples. You don't know the elevation function, but you have samples of (location, elevation). You fit a function that, at any point, gives the gradient of elevation — i.e., the slope. With the slope, you can navigate: walk uphill by following the gradient. With the score, you can sample: follow the score to find high-probability regions.

**Tiny numeric example:**

For $p(x) = \mathcal{N}(0, 1)$, the score is $\nabla_x \log p(x) = -x$. The DSM loss is:
$$\mathcal{L} = \mathbb{E}_{x_0, \sigma, \epsilon} \left[ \left( s_\theta(x_0 + \sigma\epsilon, \sigma) + \frac{\epsilon}{\sigma} \right)^2 \right]$$

The optimal $s_\theta$ is $-\frac{x_0 + \sigma\epsilon - 0}{\sigma^2} = -\frac{x}{\sigma}$ (Tweedie). With $s_\theta(x, \sigma) = -x / \sigma$, the loss is zero.

In practice, we parameterize $s_\theta$ as a neural network and minimize the loss. The network learns to output $-x / \sigma$ for the optimal case.

**Common confusion:**

- "Score matching requires the data distribution." No, it requires *samples* from the data distribution. The loss is a Monte Carlo estimate.
- "The score is the gradient of log p, not log q." Yes, but if $p = Z q$, they have the same score. So the score is independent of the (intractable) normalization constant.
- "Score matching and DDPM are different." No, DDPM is denoising score matching. The loss is identical (up to a constant).
- "Predicting noise and predicting the clean image are equivalent." Mathematically, yes. Empirically, predicting noise works better.
- "Score matching requires the network to be small." No, the loss is well-behaved for any architecture. Modern U-Nets work well.
- "The score is a vector field." Yes, it has the same shape as the input. For images, the score is an image (one value per pixel).

**Key properties:**

- **Score-free**: only requires samples, not the density.
- **Equivalent to denoising**: Tweedie identity connects the two.
- **Independent of normalization**: $\nabla_x \log p = \nabla_x \log (p/Z)$.
- **Multi-scale**: trained on multiple noise levels.
- **Tractable**: a simple MSE loss.
- **Connection to sampling**: with the score, you can sample via Langevin or reverse SDE.

**Tech comparison:**

| Method | Learns | Loss | Connects to |
|---|---|---|---|
| Score matching | Score | Fisher divergence | Score-based models |
| Denoising score matching | Score (via noise) | DSM loss | DDPM |
| Noise prediction | Noise | MSE | DDPM |
| Flow matching | Velocity | MSE | Continuous-time diffusion |
| Energy-based | Energy | Contrastive | EBMs |

**Connection to generative models:** Score matching is the *theoretical foundation* of modern diffusion. Every diffusion paper is, at its core, doing denoising score matching. The score is the central object. With it, you can:
- Sample (Langevin, reverse SDE).
- Compute log-likelihood (via the ELBO).
- Condition on text or other inputs (classifier-free guidance).
- Distill to a few-step model (consistency models).

If you understand score matching, you understand modern image generation.
