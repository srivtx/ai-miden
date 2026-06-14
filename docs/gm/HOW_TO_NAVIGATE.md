# How to Navigate the Generative Models Curriculum

> Four reading paths depending on what you want to learn. Pick one and go.

---

## Path 1: The complete beginner (10-12 hours)

You have never built a generative model. You know basic ML and PyTorch. You want to understand image and video gen from the ground up.

1. `00_foundations/what_is_probability.md` — the language
2. `00_foundations/what_is_sampling.md` — how to draw from a distribution
3. `00_foundations/what_is_kl_divergence.md` — how to measure distance between distributions
4. `00_foundations/what_is_elbo.md` — the central training objective
5. `00_foundations/what_is_score_function.md` — the gradient of log p
6. `01_vae/what_is_autoencoder.md` — compressing images
7. `01_vae/what_is_variational_autoencoder.md` — sampling from a continuous latent
8. `01_vae/vae_mnist.py` — run it
9. `02_diffusion/what_is_diffusion.md` — the forward process
10. `02_diffusion/what_is_ddpm.md` — the reverse process
11. `02_diffusion/ddpm_mnist.py` — run it
12. `02_diffusion/what_is_score_matching.md` — the loss function
13. `03_latent_diffusion/what_is_latent_diffusion.md` — the Stable Diffusion architecture
14. `03_latent_diffusion/latent_diffusion.py` — run the architecture skeleton
15. `04_video_diffusion/what_is_video_diffusion.md` — extending to time

---

## Path 2: I just want Stable Diffusion (4-5 hours)

You have used Stable Diffusion. You want to understand how it actually works.

1. `00_foundations/what_is_kl_divergence.md`
2. `00_foundations/what_is_elbo.md`
3. `00_foundations/what_is_score_function.md`
4. `01_vae/what_is_variational_autoencoder.md`
5. `02_diffusion/what_is_diffusion.md`
6. `02_diffusion/what_is_ddpm.md`
7. `02_diffusion/what_is_score_matching.md`
8. `03_latent_diffusion/what_is_latent_diffusion.md`
9. `03_latent_diffusion/latent_diffusion.py`

---

## Path 3: I just want video gen (3-4 hours)

You want to understand Sora / Veo / Wan / etc.

1. `02_diffusion/what_is_ddpm.md` (you need this foundation)
2. `02_diffusion/what_is_score_matching.md`
3. `04_video_diffusion/what_is_video_diffusion.md`
4. `04_video_diffusion/what_is_temporal_attention.md`

---

## Path 4: I'm a researcher (1-2 hours)

You already know the field. You want the curriculum as a reference.

1. Skim the foundations
2. Read the bibliography at the end
3. Use the code as a reference implementation
4. Use `INDEX.md` in each part to find specific concepts

---

## The reading order within each part

Each part has an `INDEX.md` that lists the files. Read in this order:
1. The first `what_is_*.md` (the most fundamental concept)
2. The second `what_is_*.md` (the next building block)
3. ... and so on
4. The code prototypes (always last, after you understand the math)
5. The `what_is_*.md` files reference each other — when one says "see X", go read X

---

## The file naming convention

Following the project convention:
- `what_is_X.md` — concept file (problem-first, definition, analogy, numeric example, common confusions, where used in code)
- `X_mnist.py` — local NumPy prototype that runs anywhere
- `X_mnist_colab.py` — PyTorch + CUDA version for Colab
- `INDEX.md` — part navigation guide
- `SUMMARY.md` — part summary (for parts with code)

---

## Tips

- **Run the code while you read.** Don't just read the math.
- **Modify the code.** Change the noise schedule, change the network, see what happens.
- **Compare NumPy and PyTorch versions.** They teach different things.
- **Read the comments in the code.** Every line explains *why*, not just *what*.
- **When confused, go back to Part 0.** The foundations are the key.
