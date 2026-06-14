# What Is Sampling?

**The Problem:** You have a probability distribution p(x). You want to draw samples $x_1, x_2, \ldots, x_N$ from it. For simple distributions (Gaussian, uniform), this is easy. For high-dimensional distributions (the space of all natural images), it is *the* central challenge of generative modeling. Every diffusion model, every GAN, every VAE, is a different way to solve this problem.

**Definition:** *Sampling* is the process of generating instances from a probability distribution. Given p(x), the goal is to produce $x \sim p(x)$ — that is, x is a random draw such that the probability of x being in any region R equals $\int_R p(x') dx'$.

**How It Works (Step-by-Step):**

1. **Direct sampling** (only for simple distributions):
   - Uniform: $x \sim \text{Uniform}(0, 1)$ is just `random.random()`.
   - Gaussian: $x \sim \mathcal{N}(0, 1)$ via the *Box-Muller transform*: $x = \sqrt{-2 \log u_1} \cos(2\pi u_2)$ where $u_1, u_2 \sim \text{Uniform}(0, 1)$.
   - These are efficient: $O(1)$ per sample.

2. **Inverse transform sampling** (for univariate distributions with invertible CDF):
   - Compute the CDF $F(x) = \int_{-\infty}^x p(x') dx'$.
   - Invert: $x = F^{-1}(u)$ where $u \sim \text{Uniform}(0, 1)$.
   - Works for any univariate distribution. Doesn't extend to high dimensions.

3. **Rejection sampling** (for distributions we can evaluate but not sample from):
   - Sample $x$ from a proposal distribution $q(x)$.
   - Accept with probability $p(x) / (M q(x))$ where $M$ is a constant such that $M q(x) \geq p(x)$ for all $x$.
   - Inefficient in high dimensions: rejection rate grows exponentially with dimension.

4. **Markov Chain Monte Carlo (MCMC)**:
   - Construct a Markov chain whose stationary distribution is p(x).
   - Metropolis-Hastings: propose $x' \sim q(x' | x)$, accept with probability $\min(1, p(x') q(x | x') / (p(x) q(x' | x)))$.
   - Gibbs sampling: cycle through dimensions, sample each conditioned on the others.
   - Slow to converge in high dimensions.

5. **Variational sampling** (the modern approach):
   - Learn a network that maps a simple distribution (Gaussian noise) to p(x).
   - VAE: amortized variational inference, sampling via the reparameterization trick.
   - GAN: implicit distribution matching via a discriminator.
   - Flow: invertible network with tractable density.
   - Diffusion: learn the score $\nabla_x \log p(x)$, then sample by integrating a reverse-time SDE.

**Real-life analogy:** Sampling is like *rolling a weighted die* where the weights are not equal. For a 6-sided die with $p(1) = 0.5$ and $p(2) = p(3) = \ldots = p(6) = 0.1$, you need to find a way to roll 1 half the time. Direct sampling uses a lookup. Rejection sampling is rolling a fair die and only keeping some rolls. MCMC is rolling and adjusting the die after each roll based on the result. Variational sampling is *building* a die that has the right weights.

**Tiny numeric example:** Sample from a 1D Gaussian mixture $p(x) = 0.3 \cdot \mathcal{N}(x; -2, 1) + 0.7 \cdot \mathcal{N}(x; 3, 1)$.

```python
import numpy as np
# Rejection sampling with a wide proposal
def sample_gmm(n=1000):
    samples = []
    while len(samples) < n:
        # Propose from a wide uniform
        x = np.random.uniform(-10, 10)
        # Compute the density
        p = 0.3 * np.exp(-0.5 * (x + 2)**2) / np.sqrt(2 * np.pi)
        p += 0.7 * np.exp(-0.5 * (x - 3)**2) / np.sqrt(2 * np.pi)
        # Accept with probability p / M, where M is the max density
        if np.random.uniform() < p / 0.3:
            samples.append(x)
    return np.array(samples)

# Direct sampling (better)
def sample_gmm_direct(n=1000):
    # First, pick which component
    components = np.random.choice(2, size=n, p=[0.3, 0.7])
    # Then, sample from the chosen component
    means = np.array([-2, 3])
    return np.random.normal(means[components], 1)
```

**Common confusion:**

- "Sampling requires knowing p(x)." No, modern sampling (GAN, diffusion) only requires being able to *evaluate* a related quantity (the score, or the ratio). This is why we say GANs use *implicit* distributions.
- "Sampling is the same as optimization." No. Optimization finds a single optimum $x^* = \arg\max_x p(x)$. Sampling produces *many* $x$ values according to $p(x)$. They are different problems.
- "More samples = better." Yes, but only up to the *effective* sample size. If your samples are correlated (e.g., from a Markov chain), you need many more for the same statistical power.
- "All sampling methods are equally good." No. For high-dimensional distributions, MCMC and rejection sampling scale poorly. Variational methods (VAE, GAN, diffusion, flow) are designed for high dimensions.
- "Sampling from a neural network output is sampling from the data." No. The neural network output is a *function* of the input. The input is sampled from a simple distribution; the output has a complicated distribution.
- "Sampled images are real images." No. They are *samples* from a learned distribution. They look real because the model learned the distribution well, but they are not in the training set (usually).

**Key properties:**

- **Asymptotically exact** (MCMC, rejection): in the limit of infinite samples, the empirical distribution converges to p(x).
- **Biased** (variational): the samples are from an *approximation* of p(x), not p(x) itself.
- **Tractable density** (flow, autoregressive): the model can compute p(x) for any x.
- **Implicit density** (GAN, diffusion): the model can sample but not compute p(x) directly.
- **Trade-off**: tractable density is often expensive; cheap sampling is often biased.

**Tech comparison:**

| Method | Density | Quality | Speed | High-dim |
|---|---|---|---|---|
| Direct | Exact | Exact | Fast | Only low-dim |
| Rejection | Exact | Exact | Slow | Poor |
| MCMC | Exact | Exact | Slow | Poor |
| VAE | Tractable | Blurry | Fast | Good |
| GAN | Implicit | Sharp | Fast | Good |
| Flow | Tractable | Good | Fast | Good |
| Diffusion | Implicit (score) | Excellent | Slow | Good |

**Connection to generative models:** Sampling is the *use case* of every generative model. You train p_θ(x) to match p_data(x), then you sample from p_θ(x) to generate new data. The sampling method (ancestral, reparameterization, ODE, SDE) is one of the key design choices in each model family.
