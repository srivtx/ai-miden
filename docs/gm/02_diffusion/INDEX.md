# Part 2: Diffusion Models

> The forward process: slowly add noise to an image until it becomes pure Gaussian noise. The reverse process: learn to undo the noise, one small step at a time. After training, you can sample by starting from noise and following the reverse process. This is the most successful generative model architecture as of 2026.

---

## The four files in this part

| File | One-line summary |
|---|---|
| `what_is_diffusion.md` | The forward process. Slowly destroy an image by adding Gaussian noise. |
| `what_is_ddpm.md` | The reverse process. Learn to undo the destruction, one tiny step at a time. |
| `what_is_score_matching.md` | The training loss. Why it works. Why it's a denoising task. |
| `ddpm_mnist.py` | A runnable DDPM on procedural 8x8 digits, in NumPy. |
| `ddpm_mnist_colab.py` | The same DDPM in PyTorch, for Colab with MNIST. |

## Reading order

1. **`what_is_diffusion.md`**. The forward process. Why a closed-form exists.
2. **`what_is_ddpm.md`**. The reverse process. The U-Net. The noise schedule. The sampling loop.
3. **`what_is_score_matching.md`**. The training loss. Why predicting the noise is the same as learning the score.
4. **`ddpm_mnist.py`**. Run it. See the forward process destroy an image, the reverse process rebuild it.

## The synthesis

A diffusion model is two processes:
- **Forward**: $q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1 - \beta_t} x_{t-1}, \beta_t I)$. Slowly add Gaussian noise over $T$ steps, with a variance schedule $\beta_1, \ldots, \beta_T$.
- **Reverse**: $p_\theta(x_{t-1} | x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t), \Sigma_\theta(x_t, t))$. Learn a network that predicts the parameters of the denoising step.

After training:
- Sample by starting at $x_T \sim \mathcal{N}(0, I)$.
- Run the reverse process for $T$ steps.
- The result is a new image.

The math is straightforward. The trick is:
1. The forward process has a *closed form* $q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar\alpha_t} x_0, (1 - \bar\alpha_t) I)$, so we can sample $x_t$ for any $t$ in one step.
2. The training loss is a simple denoising objective: $\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon} [\| \epsilon - \epsilon_\theta(\sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t} \epsilon, t) \|^2]$ where $\epsilon$ is Gaussian noise and $\epsilon_\theta$ is the network that predicts the noise.
3. The reverse process uses the predicted noise to compute $\mu_\theta$ and $\Sigma_\theta$ in closed form.

## Why diffusion beats VAEs and GANs

- **VAE samples are blurry** because the KL term encourages a smooth latent, which limits sharpness.
- **GAN samples are sharp** but unstable to train (mode collapse, no convergence guarantee).
- **Diffusion samples are both sharp and stable** because the loss is a simple denoising MSE.

The catch: diffusion is *slow* at sampling (100-1000 steps). Modern variants (DDIM, latent diffusion, consistency models, flow matching) speed this up dramatically.

## Where this leads

After Part 2, you understand the core of modern image generation. Part 3 makes it practical by working in a compressed latent space (Stable Diffusion). Part 4 extends to time (video).
