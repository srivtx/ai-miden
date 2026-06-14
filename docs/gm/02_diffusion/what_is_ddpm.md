# What Is DDPM (Denoising Diffusion Probabilistic Models)?

**The Problem:** The forward process (Part 2.1) destroys an image. To generate new images, you need to *reverse* this process: start from Gaussian noise and gradually denoise until a clean image emerges. The reverse process is unknown, but it can be *learned* if you assume the noise at each step is small enough that the reverse process is also Gaussian. This is DDPM (Ho et al. 2020), the paper that started the modern diffusion revolution.

**Definition:** *DDPM* is a generative model that learns to reverse a fixed forward diffusion process. The reverse process is parameterized as a Gaussian:

$$p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))$$

where $\mu_\theta$ and $\Sigma_\theta$ are outputs of a neural network (usually a U-Net). The training loss is:

$$\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| \epsilon - \epsilon_\theta(\sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon, t) \|^2 \right]$$

where $\epsilon_\theta(x_t, t)$ is the network's prediction of the noise $\epsilon$ that was added to produce $x_t$ from $x_0$.

**How It Works (Step-by-Step):**

1. **Architecture**: a U-Net. The input is $x_t$ (a noisy image) and a time embedding $t$. The output is $\epsilon_\theta(x_t, t)$, the network's prediction of the noise that was added.
   - The U-Net has down-sampling, bottleneck, up-sampling, and skip connections.
   - Time $t$ is embedded via sinusoidal positional encoding and added to feature maps at every layer.
   - Modern variants add cross-attention for conditioning (text, class labels).

2. **Training** (one step):
   - Sample a batch of $x_0 \sim p_{\text{data}}$.
   - Sample a random $t \sim \text{Uniform}(1, T)$.
   - Sample $\epsilon \sim \mathcal{N}(0, I)$.
   - Compute $x_t = \sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon$.
   - Predict $\hat\epsilon = \epsilon_\theta(x_t, t)$.
   - Loss: $\| \hat\epsilon - \epsilon \|^2$.
   - Backprop, update weights.

3. **Sampling** (one step):
   - Start with $x_T \sim \mathcal{N}(0, I)$.
   - For $t = T, T-1, \ldots, 1$:
     - Predict $\hat\epsilon = \epsilon_\theta(x_t, t)$.
     - Compute the predicted mean:
       $$\mu_\theta(x_t, t) = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{1 - \alpha_t}{\sqrt{1 - \bar\alpha_t}} \hat\epsilon \right)$$
     - Compute the predicted variance (in the simple version, $\Sigma_\theta = \beta_t I$).
     - Sample $x_{t-1} \sim \mathcal{N}(\mu_\theta, \Sigma_\theta)$ if $t > 1$, else $x_0 = \mu_\theta$.
   - Return $x_0$.

4. **Variance schedule**: $\beta_1, \ldots, \beta_T$. Common choices:
   - Linear: $\beta_t$ increases linearly from $\beta_1$ to $\beta_T$.
   - Cosine: more steps at low $\beta$, fewer at high $\beta$. Usually better.
   - For MNIST 8x8, $T = 100$ is enough. For high-resolution images, $T = 1000$.

5. **Loss reweighting**: variants like v-prediction, min-SNR, etc. reweight the loss for faster convergence.

**Key insight:** training DDPM is *just denoising*. You don't need to know the data distribution, the prior, or the score. Just predict the noise that was added. The network learns the *denoising* task, which implicitly learns the score (see `what_is_score_matching.md`).

**Real-life analogy:** DDPM is like *reverse-eroding a sculpture*. You start with a block of marble that has been eroded by water until it's a smooth pebble. To recover the sculpture, you (or the network) must guess, at each step, "what shape was here?" and add back the missing material. After many steps, the sculpture emerges. The network's job is to predict, given the current eroded state, what the *previous* state looked like.

**Tiny numeric example:**

Let $T = 2$, $\beta_1 = 0.1$, $\beta_2 = 0.2$. So $\bar\alpha_1 = 0.9$, $\bar\alpha_2 = 0.72$.

Forward:
- $x_1 = 0.95 x_0 + 0.32 \epsilon_1$
- $x_2 = 0.85 x_0 + 0.53 \epsilon_2$ (one-step) or $x_2 = 0.89 x_1 + 0.45 \epsilon_2$ (two-step)

Reverse (one step from $x_2$ to $x_1$):
- Predict $\hat\epsilon_2 = \epsilon_\theta(x_2, 2)$.
- Predicted mean: $\mu_1 = (x_2 - (1 - 0.2) / 0.53 \cdot \hat\epsilon_2) / \sqrt{0.8}$
- Sample $x_1 \sim \mathcal{N}(\mu_1, 0.2 I)$.

**Common confusion:**

- "DDPM requires $T = 1000$ steps." For high-res images, often. For 8x8, $T = 100$ is enough. Modern variants (DDIM, latent diffusion) reduce to 20-50.
- "The network predicts the denoised image." Often, but the standard formulation predicts the *noise*. Predicting the noise is mathematically equivalent and gives a better-conditioned loss.
- "DDPM is slow." Sampling is. Each step requires a full U-Net forward pass. DDIM removes the stochasticity, allowing 10-50x faster sampling. Latent diffusion compresses first, so each step is cheaper.
- "The reverse process is exactly Gaussian." Approximately. For small $\beta_t$, yes. The non-Gaussian corrections are small and can be ignored.
- "DDPM is the same as score-based." Almost. The connection is through denoising score matching. See `what_is_score_matching.md`.
- "You can train DDPM end-to-end." Yes, that's the whole point. The loss is a simple MSE.
- "The U-Net has attention." Modern versions do, for conditioning. The original DDPM did not (it was unconditional, on CIFAR-10).
- "DDPM works on text." It can, with discrete diffusion (e.g., D3PM). The continuous formulation in this file is for continuous data like images.

**Key properties:**

- **Simple loss**: MSE between predicted and true noise.
- **Fixed forward process**: only the reverse process is learned.
- **Stable training**: no adversarial dynamics, no mode collapse.
- **Sharp samples**: not blurry like VAEs.
- **Slow sampling**: 100s-1000s of network calls per image.
- **Tractable density** (in principle): the model can compute $p_\theta(x_0)$ via the ELBO.

**Tech comparison:**

| Method | Sharpness | Stability | Speed (train) | Speed (sample) |
|---|---|---|---|---|
| VAE | Blurry | High | Fast | Fast |
| GAN | Sharp | Low | Medium | Fast |
| DDPM | Sharp | High | Medium | Slow |
| DDIM | Sharp | High | Medium | Medium |
| Latent diffusion | Sharp | High | Medium | Medium |
| Consistency model | Sharp | High | Medium | Fast (1-4 steps) |

**Connection to generative models:** DDPM is the *baseline* of modern diffusion. Latent diffusion (Part 3) is DDPM in a compressed space. Video diffusion (Part 4) is DDPM over time. Flow matching is a continuous-time limit. Consistency models are DDPM distilled to few-step sampling. All of them are descendants of the same paper.
