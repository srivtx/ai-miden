# Research: Flow Matching & Diffusion Transformers

**Status:** Missing from course. Should be Phase 40, extension of Phase 31.
**Last Updated:** May 2026
**Sources:** Lipman et al. (2022), Stable Diffusion 3 (2024), Flux (2024), DiT (Peebles & Xie, 2023)

---

## 1. The Problem

DDPM diffusion (Phase 31) works but is slow and requires many sampling steps. The training objective (predicting noise) is indirect. Can we train generative models with a simpler, more direct objective that also allows faster sampling?

## 2. What It Is

**Flow Matching** is a reformulation of diffusion that trains a neural network to model a **probability flow** — a continuous path that transforms noise into data.

Instead of predicting noise, the model learns the **velocity field** that describes how to move from noise to data:
```
dx/dt = v(x_t, t)
```

**Key advantages over DDPM:**
- Simpler training objective (regression on a vector field)
- Faster sampling (can use ODE solvers with adaptive step sizes)
- More stable training
- Direct connection to optimal transport

**Diffusion Transformers (DiT)** replace the U-Net backbone with a Transformer. Instead of processing images through convolutions, DiT:
1. Patches the image into tokens (like ViT)
2. Processes tokens with a Transformer
3. Unpatches back to an image

This scales better to large models and achieves state-of-the-art results.

## 3. Real-Life Analogy

**DDPM (Phase 31):** A restorer removes dust from a photo by guessing how much dust is on it at each step. They iterate 1000 times.

**Flow Matching:** A sculptor starts with a block of marble (noise) and knows exactly what the statue should look like (data). Instead of chipping randomly and checking, they learn the optimal carving path — which direction to move each point at every moment. They can use a motorized tool (ODE solver) that adapts its speed to the complexity of each region.

**Diffusion Transformer:** Instead of a sculptor using hand tools (convolutions), they use a robotic arm that views the entire sculpture as a set of patches and plans globally using attention.

## 4. Key Technical Details

### Flow Matching Objective
```
L = E[||v_θ(x_t, t) - u_t(x_t)||²]
```
Where `u_t` is the true velocity that transports noise to data along a straight line (optimal transport).

For a data point x₀ and noise x₁:
```
x_t = (1-t) × x₀ + t × x₁     (linear interpolation)
u_t = x₁ - x₀                  (constant velocity)
```

The model learns to predict this velocity.

### Sampling
```
x_1 ~ N(0, I)          # start from noise
for t from 1 to 0:
    dx = v_θ(x_t, t) × dt
    x_{t-dt} = x_t - dx
```

With adaptive ODE solvers, you might need only 10-50 steps instead of 1000.

### DiT Architecture
```
Input image → Patchify → Add positional embeddings → Transformer blocks → Unpatchify → Output
```

Conditioning (class label, text) is injected through adaptive layer norm (adaLN).

## 5. Common Confusion

- **Flow matching is not a different model family.** It is a different way to train the same architectures. You can train a U-Net or Transformer with either DDPM or flow matching objectives.
- **Flow matching still uses diffusion.** It is a continuous generalization. The sampling process is still "gradual refinement from noise."
- **DiT does not mean no convolutions ever.** Some hybrid architectures use both. But pure Transformer backbones scale better.
- **Flow matching requires fewer steps but each step is similar cost.** The speedup comes from needing 20 steps instead of 1000, not from cheaper steps.
- **Not all flow matching uses straight lines.** Rectified Flow uses straight-line paths. General flow matching can use curved paths.

## 6. What We Would Build

A toy flow matching model where:
- 2D points are interpolated from noise to data
- A small MLP learns the velocity field
- We visualize the flow lines from noise to data
- Compare sampling steps: DDPM (many) vs. Flow Matching (few)

## 7. Why It Matters Now

- **Stable Diffusion 3** uses flow matching + DiT
- **Flux** (Black Forest Labs) is the leading open-source image model, using flow matching
- **Sora** (OpenAI) uses a DiT architecture for video generation
- Flow matching is becoming the default training objective for generative models

## 8. Connection to Existing Phases

- **Phase 31 (Diffusion):** Flow matching is the modern replacement for DDPM training
- **Phase 28 (ViT):** DiT applies the Vision Transformer idea to generative models
- **Phase 18 (Transformer):** DiT uses standard Transformer blocks with adaptive conditioning

---

## References

- Lipman et al. (2022): "Flow Matching for Generative Modeling"
- Liu et al. (2022): "Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow"
- Peebles & Xie (2023): "Scalable Diffusion Models with Transformers" (DiT)
- Esser et al. (2024): "Scaling Rectified Flow Transformers for High-Resolution Image Synthesis" (Stable Diffusion 3)
