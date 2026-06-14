# What Is Diffusion (the forward process)?

**The Problem:** You have a data distribution $p_{\text{data}}(x)$ of natural images. You want to learn a generative model that can sample from it. The space of images is high-dimensional (millions of pixels) and complex. You need a way to gradually transform this complex distribution into something simple (Gaussian noise) that you can sample from, and then learn to reverse the transformation. The *forward* process is the destruction. The *reverse* process (Part 2.2) is the creation.

**Definition:** The *forward diffusion process* is a Markov chain that gradually adds Gaussian noise to a data point over $T$ steps:

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1 - \beta_t} x_{t-1}, \beta_t I)$$

where:
- $x_0$ is the original data
- $x_t$ is the noisy version at step $t$
- $\beta_t$ is a variance schedule (typically small and increasing)
- $q(x_t | x_{t-1})$ is the conditional distribution

After $T$ steps, $x_T$ is approximately $\mathcal{N}(0, I)$ (pure Gaussian noise).

**The closed form (key insight):** because each step is Gaussian, the entire forward process has a *closed form*:

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar\alpha_t} x_0, (1 - \bar\alpha_t) I)$$

where $\alpha_t = 1 - \beta_t$ and $\bar\alpha_t = \prod_{s=1}^t \alpha_s$.

This means: **you can sample $x_t$ directly from $x_0$ in a single step**, without iterating. Just compute $\sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon$ for $\epsilon \sim \mathcal{N}(0, I)$. This is *the* key to making diffusion training tractable.

**How It Works (Step-by-Step):**

1. **Choose a schedule $\beta_1, \ldots, \beta_T$**. Common choices:
   - Linear: $\beta_t = \beta_1 + (t-1) (\beta_T - \beta_1) / (T-1)$
   - Cosine: $\beta_t = 1 - \bar\alpha_t / \bar\alpha_{t-1}$ where $\bar\alpha_t = \cos^2(t/T \cdot \pi/2)$
   - For MNIST, typical: $\beta_1 = 1e-4$, $\beta_T = 0.02$, $T = 1000$.

2. **Sample $x_t$ given $x_0$**: 
   - Compute $\bar\alpha_t = \prod_{s=1}^t (1 - \beta_s)$.
   - Sample $\epsilon \sim \mathcal{N}(0, I)$.
   - $x_t = \sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon$.
   - This works for *any* $t$ in $[1, T]$, no iteration needed.

3. **At $t = T$**: $x_T \approx \mathcal{N}(0, I)$. The original information is destroyed.

4. **At $t = 0$**: $x_0 = x_0$ (the original data).

The forward process is *fixed* (no learning). The reverse process (next file) is what we learn.

**Why this works for training:**

For training, we need pairs $(x_0, x_t)$ to teach the network. The closed form lets us generate $x_t$ from $x_0$ in one step, for any $t$. This makes training fast and simple:
- Sample a batch of $x_0 \sim p_{\text{data}}$.
- For each $x_0$, sample a random $t \sim \text{Uniform}(1, T)$.
- Compute $x_t = \sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon$.
- Train the network to predict $\epsilon$ from $x_t$ and $t$.

This is the *denoising score matching* loss. It is the foundation of modern diffusion.

**Real-life analogy:** The forward process is like *fading a photograph* into a uniform gray, then into pure white. The original information is gradually destroyed. At any point, you can show the photograph at a specific "fading level." The reverse process (Part 2.2) is the artist's job: from a blank canvas, gradually paint a recognizable image.

**Tiny numeric example:**

Let $T = 3$, $\beta_1 = 0.1$, $\beta_2 = 0.2$, $\beta_3 = 0.3$. So:
- $\alpha_1 = 0.9$, $\alpha_2 = 0.8$, $\alpha_3 = 0.7$
- $\bar\alpha_1 = 0.9$
- $\bar\alpha_2 = 0.9 \times 0.8 = 0.72$
- $\bar\alpha_3 = 0.72 \times 0.7 = 0.504$

For $x_0 = 1$ (a single pixel value), $x_t = \sqrt{\bar\alpha_t} \cdot 1 + \sqrt{1 - \bar\alpha_t} \cdot \epsilon$ where $\epsilon \sim \mathcal{N}(0, 1)$:
- $x_1 = 0.949 \cdot 1 + 0.316 \epsilon_1$
- $x_2 = 0.849 \cdot 1 + 0.529 \epsilon_2$
- $x_3 = 0.710 \cdot 1 + 0.704 \epsilon_3$

At each step, the signal ($\sqrt{\bar\alpha_t}$) shrinks and the noise ($\sqrt{1 - \bar\alpha_t}$) grows. After 3 steps, the signal is 71% of the original and the noise is 70% (already more noise than signal). The image is mostly noise.

**Common confusion:**

- "The forward process is learned." No, it is *fixed*. You choose the schedule; the data flows through it. The reverse process is learned.
- "Diffusion is slow." Training is fast (parallel across $t$). Sampling is slow (sequential through $T$ steps). Modern variants reduce $T$ to 20-50.
- "The schedule is the most important hyperparameter." Often true. A bad schedule (too aggressive early) makes the reverse process too hard to learn. Linear works but cosine is usually better.
- "Forward process must be Gaussian." For tractability, yes. But there are variants with non-Gaussian noise (e.g., discrete diffusion for text).
- "You can sample $x_t$ iteratively from $x_{t-1}$." Yes, but it's wasteful. The closed form is much faster.
- "The forward process destroys information." Yes, by design. The whole point is to map data to a tractable distribution (Gaussian), then learn to reverse the mapping.

**Key properties:**

- **Closed form**: $q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar\alpha_t} x_0, (1 - \bar\alpha_t) I)$.
- **Markov**: each step depends only on the previous.
- **Fixed**: no parameters.
- **Gaussian noise**: makes the math tractable.
- **Variance schedule**: $\beta_t$ can be linear, cosine, learned, etc.
- **Asymptotic**: $x_T \to \mathcal{N}(0, I)$ as $T \to \infty$ (or for a sufficiently spread $\beta_t$).

**Tech comparison:**

| Method | Forward process | Tractable? | Closed form? |
|---|---|---|---|
| Diffusion | Gaussian, $T$ steps | Yes | Yes |
| Normalizing flow | Invertible transform | Yes | Exact |
| VAE | Single step | Yes | Yes |
| GAN | None | N/A | N/A |
| EBM | None | No | No |

**Connection to generative models:** The forward process is the "easy" half of diffusion. The "hard" half is the *reverse* process: learning to undo the destruction. That is the subject of `what_is_ddpm.md`. The *training loss* that makes this possible is in `what_is_score_matching.md`.
