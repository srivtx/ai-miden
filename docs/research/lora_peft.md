# Research: LoRA and Parameter-Efficient Fine-Tuning (PEFT)

**Status:** Missing from course. Should be Phase 35 or extension of Phase 22.
**Last Updated:** May 2026
**Sources:** Hu et al. (2021), Hugging Face PEFT library, QLoRA (2023), DoRA (2024)

---

## 1. The Problem

Fine-tuning a 70B parameter model requires 280 GB of GPU memory just for the weights (FP32), plus optimizer states (another 560 GB for Adam). This is inaccessible to almost everyone. Even a 7B model needs 28 GB for weights + 56 GB for optimizer states = 84 GB total. We need a way to adapt large models without updating all parameters.

## 2. What It Is

**LoRA (Low-Rank Adaptation)** freezes the pre-trained model weights and injects trainable **rank-decomposition matrices** into each layer.

Instead of updating a weight matrix W (size d×d), LoRA learns:
```
W' = W + BA
```
Where:
- B is d×r
- A is r×d
- r << d (typically r = 8, 16, 32, 64)

For a 4096×4096 matrix:
- Full fine-tuning: 16.7M trainable parameters
- LoRA (r=16): 2 × 4096 × 16 = 131K parameters (0.8% of full!)

### Why Low-Rank Works

Pre-trained weights have a low "intrinsic dimension" — the meaningful changes needed for adaptation live in a low-dimensional subspace. LoRA finds that subspace rather than searching the full parameter space.

### Where to Apply LoRA

Typically applied to:
- **Query and Value projection matrices** in attention (best quality)
- All attention projection matrices (Q, K, V, O)
- FFN layers (more parameters, marginal quality gain)

### QLoRA (2023)

Extends LoRA with 4-bit quantization:
- Base model stored in 4-bit NormalFloat (NF4)
- LoRA adapters in 16-bit or 32-bit
- Double quantization of quantization constants
- Paged optimizers to handle GPU memory spikes

**Result:** Fine-tune a 65B model on a single 48GB GPU.

### DoRA (Weight-Decomposed Low-Rank Adaptation, 2024)

Decomposes weights into magnitude and direction:
```
W' = m · (W / ||W|| + BA)
```
- m = learned magnitude vector
- Direction is adapted via LoRA
- More stable training, especially at higher ranks

## 3. Real-World Analogy

A massive symphony orchestra (the pre-trained model) has been practicing a standard repertoire for years. Now they need to learn a jazz piece. Instead of retraining every musician (full fine-tuning), the conductor adds small sheet music inserts (LoRA adapters) that tell each section how to modify their playing style. The core skills remain unchanged; only the style adapter is new. And these inserts are tiny — a few pages versus reprinting the entire orchestral library.

## 4. Key Technical Details

### Scaling the LoRA Update
```
h = W_0x + (α/r) · BAx
```
- α is a scaling hyperparameter (usually α = 2r)
- When r changes, α/r keeps the update magnitude stable

### Initialization
- A is initialized with Gaussian random values
- B is initialized with zeros
- This ensures W' = W at the start of training (no disruption)

### Merging Adapters
At inference, BA can be merged into W:
```
W_merged = W + BA
```
This has zero inference overhead compared to the base model.

### Multi-Adapter Inference
Multiple LoRA adapters can be loaded and switched at runtime:
- Base model: shared
- Adapter 1: chat style
- Adapter 2: coding style
- Adapter 3: medical domain

This enables "model personality switching" without loading multiple full models.

## 5. Common Confusion

- **LoRA is not just for LLMs.** It works for diffusion models (Stable Diffusion fine-tuning), vision transformers, and any model with linear layers.
- **Higher rank is not always better.** r=64 often matches or exceeds r=256 because low-rank acts as regularization.
- **LoRA does not reduce inference memory.** Unless you merge adapters, the model still loads base weights + adapters. QLoRA reduces training memory, not inference.
- **Not all layers need LoRA.** Applying LoRA only to attention layers often gives 90% of the quality with 50% of the parameters.
- **Full fine-tuning can still be better.** For tasks that require changing the model's core knowledge (not just style), full fine-tuning may be necessary.

## 6. What We Would Build

A toy linear regression where:
- Base model: y = Wx (frozen)
- LoRA adapter: y = Wx + BAx (only B and A trained)
- Show that a tiny r=2 adapter can adapt the model to new data
- Compare trainable parameters: full (100%) vs. LoRA (2%)

## 7. Why It Matters Now

- **Democratizes fine-tuning:** Anyone with a consumer GPU can fine-tune 70B models
- **Adapter marketplace:** Hugging Face has thousands of LoRA adapters for popular models
- **Multi-tenancy:** One base model serves thousands of customized adapters
- **Deployment efficiency:** Adapters are 3–100 MB vs. models that are 10–100 GB

## 8. Connection to Existing Phases

- **Phase 22 (SFT):** LoRA makes SFT accessible on consumer hardware
- **Phase 23 (RLHF):** QLoRA enables RLHF on single GPUs
- **Phase 29–31 (Generation):** LoRA is the dominant way to customize diffusion models
- **Phase 32 (Foundation Models):** PEFT is how most people interact with foundation models

---

## References

- Hu et al. (2021): "LoRA: Low-Rank Adaptation of Large Language Models"
- Dettmers et al. (2023): "QLoRA: Efficient Finetuning of Quantized LLMs"
- Liu et al. (2024): "DoRA: Weight-Decomposed Low-Rank Adaptation"
