# Research: Scaling Laws and Compute-Optimal Training

**Status:** Missing from course. Should be Phase 37 or early foundational phase.
**Last Updated:** May 2026
**Sources:** Kaplan et al. (2020), Hoffmann et al. (2022) — Chinchilla, various follow-ups

---

## 1. The Problem

Training large models costs millions of dollars. If you have a fixed compute budget, should you train a bigger model for fewer steps, or a smaller model for more steps? The answer was wrong for years — and the correction (Chinchilla, 2022) changed how every major lab trains models.

## 2. What It Is

**Scaling Laws** are empirical relationships that predict model performance (loss) as a function of:
- N = number of model parameters
- D = number of training tokens
- C = compute budget (measured in FLOPs)

### Kaplan Scaling Laws (OpenAI, 2020)

OpenAI's original finding:
```
Loss ∝ N^(-0.073)  and  Loss ∝ D^(-0.095)
```

This suggested that **model size matters more than data**. For a fixed compute budget, you should train a larger model for fewer steps. This led to models like GPT-3 (175B params, 300B tokens) being "undertrained" relative to their size.

### Chinchilla Scaling Laws (DeepMind, 2022)

DeepMind revisited the analysis with more careful experiments and found:
```
Loss ∝ N^(-0.34)  and  Loss ∝ D^(-0.28)
```

These exponents are much closer to each other. The optimal balance is:
```
D_optimal ≈ 20 × N
```

For a 70B parameter model, you need **1.4 trillion tokens** for compute-optimal training. GPT-3 was trained on only 300B tokens — it was severely undertrained!

### The Chinchilla Rule

For a given compute budget C, the optimal model size and data size are:
```
N_optimal ∝ C^0.50
D_optimal ∝ C^0.50
```

Model size and data size should scale **equally** with compute. Not model-heavy, not data-heavy — balanced.

## 3. Real-World Analogy

Building a library (model) and filling it with books (data):

**Kaplan approach:** Build a massive empty library with millions of shelves, but only fill 10% of them. The shelves are impressive, but most are empty. The library looks big but isn't very useful.

**Chinchilla approach:** Build a library sized exactly for your book collection. Every shelf is full. The library is smaller in square footage but more useful because every shelf has books.

**The twist:** The second approach turns out to be cheaper AND better. A smaller, full library costs less to build and maintain than a massive empty one.

## 4. Key Implications

### For Model Training
- **Llama 2 70B** was trained on 2T tokens ( compute-optimal!)
- **Llama 3 70B** was trained on 15T tokens (over-trained, but quality keeps improving)
- **GPT-4** is believed to have been trained on ~13T tokens (massive over-training for quality)

### For Smaller Models
Chinchilla also means small models can be surprisingly good if trained on enough data:
- **Chinchilla 70B** (trained on 1.4T tokens) outperforms **Gopher 280B** (trained on 300B tokens)
- **Llama 3 8B** (trained on 15T tokens) outperforms much larger models from 2022

### The Data Wall
There are only ~10T tokens of high-quality text on the internet. Once we hit this wall, we need:
- Synthetic data generation
- Multi-epoch training (repeating data)
- Better data curation (quality over quantity)

## 5. Common Confusion

- **Chinchilla is about compute-optimal, not quality-optimal.** If you have infinite compute, bigger models + more data always win. Chinchilla tells you the best trade-off for a FIXED budget.
- **Over-training is often worth it.** Llama 3 trains on 15T tokens for an 8B model (D/N ≈ 1875, vs. Chinchilla's 20). This is massively over-trained by Chinchilla standards, but the quality keeps improving.
- **The constants matter.** D ≈ 20N is approximate. Recent work suggests D ≈ 100N for very small models and D ≈ 10N for very large ones.
- **Not all tokens are equal.** 1T tokens of filtered, deduplicated, high-quality data beats 10T tokens of raw web crawl.
- **Scaling laws are empirical, not theoretical.** They are curve fits to experimental data. They might break at extreme scales.

## 6. What We Would Build

A toy experiment where:
- Train 3 tiny models: small/short, medium/medium, large/short
- Plot loss vs. parameters and loss vs. tokens
- Show that the medium model trained longer outperforms the large model trained briefly
- Fit a simple power law to the data

## 7. Why It Matters Now

- **Every training run** at frontier labs now uses Chinchilla-optimal or over-trained schedules
- **Smaller, longer-trained models** (Llama 3, Qwen 2) are replacing larger, under-trained ones
- **Data curation** has become as important as architecture
- **The data wall** is the central challenge for the next generation of models

## 8. Connection to Existing Phases

- **Phase 3 (Gradient Descent):** Scaling laws determine how long to train
- **Phase 21 (Tiny GPT):** We trained on tiny data; scaling laws explain why real models need trillions of tokens
- **Phase 32 (Foundation Models):** Scaling laws are the engineering principle behind all foundation model training decisions

---

## References

- Kaplan et al. (2020): "Scaling Laws for Neural Language Models"
- Hoffmann et al. (2022): "Training Compute-Optimal Large Language Models" (Chinchilla)
- Muennighoff et al. (2023): "Scaling Data-Constrained Language Models"
