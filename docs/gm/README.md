# The Generative Models Curriculum

> A from-first-principles curriculum on how to build image and video generation models — from basic probability to latent diffusion to text-to-video. No shortcuts, no pretrained weights, no magic. Just the math, the intuition, and the code.

> **This curriculum is part of `ai-miden`. It lives at `ai-miden/docs/gm/`.**

---

## What this is

This is a **6-part, code-first curriculum** that teaches you how modern image and video generation works, by building it from scratch. Every concept is paired with a runnable prototype: a NumPy version that runs anywhere, and a PyTorch version for Colab.

By the end, you will understand:
- How a VAE compresses images into a continuous latent space and samples from it
- How DDPM (Denoising Diffusion Probabilistic Models) reverses a noise process to generate images
- How latent diffusion (Stable Diffusion) makes this efficient by working in a compressed space
- How video diffusion extends the same idea to time
- How text conditioning ties everything together
- How to read the latest papers (DiT, Sora, Veo, etc.)

The arc is **bottom-up**: probability → VAE → diffusion → latent diffusion → video → text conditioning. Each part builds on the last.

---

## The part index

| Part | Topic | What you'll build |
|---|---|---|
| **00** | **Foundations** | Probability, sampling, KL divergence, ELBO, score functions |
| **01** | **Autoencoders and VAEs** | A working VAE on MNIST from scratch |
| **02** | **Diffusion models** | DDPM from scratch (forward + reverse process, noise schedule, sampling) |
| **03** | **Latent diffusion** | Stable Diffusion architecture (autoencoder + U-Net + text encoder) |
| **04** | **Video diffusion** | Temporal attention, 3D U-Net, latent video diffusion |
| **05** | **Implementations** | All code in one place, with tests and benchmarks |

---

## How to read this curriculum

**If you are new to generative models**: read in order. Part 0 (foundations) → Part 1 (VAE) → Part 2 (DDPM) → Part 3 (latent) → Part 4 (video).

**If you just want Stable Diffusion**: read Part 0 (especially `what_is_kl_divergence.md` and `what_is_score_function.md`) → Part 1 (the autoencoder) → Part 2 (the diffusion math) → Part 3 (the architecture).

**If you just want video gen**: read Part 0 → Part 2 → Part 4.

**If you are a researcher**: skim the foundations, then read the papers in the bibliography. Use the code as a reference implementation.

---

## How to use the code

Each concept has a `*.py` file. Following `ai-miden` AGENTS.md conventions:
- Local scripts use only **NumPy**. They run on any laptop.
- Colab scripts use **PyTorch + CUDA**. Run them in Colab with a T4 GPU.
- All plots use `matplotlib.use('Agg')` and save to `plots/`.

```bash
# Local NumPy version
python docs/gm/02_diffusion/ddpm_mnist.py

# Colab PyTorch version
!python docs/gm/02_diffusion/ddpm_mnist_colab.py
```

---

## Why "from scratch"

Most tutorials on diffusion models start with a pretrained checkpoint and a `pipeline.generate(prompt)` call. That hides the actual math.

This curriculum starts with: "given a noise-corrupted image, what is the gradient of the log-probability of the original image?" From that, you derive the loss function. From the loss function, you build the training loop. From the training loop, you build the sampler. From the sampler, you get a generative model.

If you can implement DDPM from scratch in 200 lines of NumPy, you understand it. If you only know how to call a pipeline, you don't.

---

## The deepest lesson

Modern image and video generation is not magic. It is:
1. A way to **sample** from a probability distribution (images are samples from p(image))
2. A way to **estimate** the score (gradient of log p) at any point
3. A way to **condition** the distribution on text (classifier-free guidance)

The math is the same across VAEs, GANs, normalizing flows, autoregressive models, and diffusion. The implementations differ. The math is one.

---

## Status

This curriculum is under construction. The foundations, VAE, DDPM, and latent diffusion parts are complete. The video diffusion and text conditioning parts are in progress.

| Part | Status | Files |
|---|---|---|
| 00 | Drafted | Probability, sampling, KL, ELBO, score function |
| 01 | Drafted | Autoencoder, VAE, code prototype |
| 02 | Drafted | Forward/reverse process, DDPM, score matching, code prototype |
| 03 | Drafted | Latent diffusion, U-Net, text encoder, code prototype |
| 04 | Stub | Temporal attention, 3D U-Net, video diffusion |
| 05 | Stub | Aggregated implementations |

---

## Companion resources

- `ai-miden/docs/phaseX/` — The main AI curriculum (158 phases, from perceptron to GPT)
- `ai-miden/docs/nature/` — Neuroscience curriculum (Parts 0-12, 90K+ words)
- `ai-miden/docs/gm/` — This curriculum

---

Built: 2026.
