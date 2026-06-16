## Why it exists (THE PROBLEM)

A 10M-parameter model trained on one codebase (say, jc) takes 10 minutes to train. If you want to fine-tune it on a new codebase (say, rich), you retrain all 10M parameters. Another 10 minutes. Another 10M-parameter file on disk. Now you have 5 codebases. That's 5 models, 5 training runs, 5 × 10M = 50M parameters on disk, 50 minutes of training. Each model is independent — no shared knowledge between them.

The problem compounds with scale. Fine-tuning a 7B-parameter model (Llama, Mistral) from scratch is $10K+. Fine-tuning all 10M parameters of a small model for every new task is wasteful because most of the weights encode generic knowledge that doesn't need to change. The WEIGHT UPDATE from fine-tuning is low-rank — it can be decomposed into two tiny matrices without losing accuracy.

**LoRA** (Low-Rank Adaptation, Hu et al., 2021) exploits this. Instead of updating $W \in \mathbb{R}^{d \times k}$ directly, you freeze $W$ and train $A \in \mathbb{R}^{d \times r}$ and $B \in \mathbb{R}^{r \times k}$ where $r \ll \min(d, k)$. The effective update is $\Delta W = A \times B$. For $r=4$, this is ~0.1% of the original parameters. During inference, $W + A \times B$ is pre-computed, so there's zero inference overhead.

## Definition (very simple)

**LoRA** freezes the pre-trained weights $W$ and adds a trainable low-rank decomposition $A \times B$ alongside every linear layer. Only $A$ and $B$ get updated during fine-tuning. At inference, you can either: (1) merge ($W_{new} = W + AB$, zero overhead) or (2) compute on-the-fly ($h = Wx + (AB)x$, keeps the base model intact).

The rank $r$ is typically 4-64. For a $d \times k$ matrix (e.g., 768 × 768 in a transformer), full fine-tuning trains 768 × 768 = 589,824 parameters. LoRA with $r=4$ trains (768 × 4) + (4 × 768) = 6,144 parameters — 96× fewer. The accuracy loss is typically <1%.

The intuition: when a neural network learns a new task, the weight update $\Delta W$ is not full-rank. Most of the learning happens in a low-dimensional subspace. LoRA is simply making that explicit rather than pretending $\Delta W$ can be anything.

## Real-life analogy

**Full fine-tuning is replacing every page of a textbook.** You wrote a textbook on "General Python." Now you want to add a chapter on "Rich library." Instead of editing every page (full fine-tune), you write a small insert booklet (LoRA adapter) that references pages in the original book. The original book stays on the shelf. The insert booklet costs $5 to print instead of reprinting the whole book for $500. Anyone who owns the original book just needs the insert.

**Full fine-tuning is repainting an entire wall.** You have a blue wall. You want one section to be green. LoRA is a small green sticker you place over that section. The blue wall is still blue underneath. If you want it blue again, remove the sticker.

## Tiny numeric example

Base model: a single linear layer $W x + b$ where $W$ is 4×4, trained on generic Python.

```python
W = [[0.5, 0.1, 0.3, -0.2],    # learned from jc+rich+cpython combined
     [0.1, 0.8, 0.0,  0.4],
     [-0.3, 0.2, 0.9, 0.1],
     [0.2, -0.1, 0.1, 0.7]]

# Full fine-tune on "requests" library: Update all 16 values.
# W_new = W + ΔW, where ΔW is 4×4 = 16 parameters
# File size: 16 × 4 bytes = 64 bytes per adapter

# LoRA fine-tune on "requests" library (r=2):
# Train A (4×2) and B (2×4) = 8 + 8 = 16 total, but the HYPOTHESIS
# is that r=2 captures most of the variance.

A = [[0.02, -0.01],     # (4×2) learned
     [0.00,  0.03],
     [-0.01, 0.01],
     [0.01,  0.00]]

B = [[0.5, 0.0, -0.2, 0.1],   # (2×4) learned
     [0.1, 0.3,  0.0, 0.2]]

ΔW = A × B = [[0.009, 0.003, -0.004, 0.000],
              [0.003, 0.009,  0.000, 0.006],
              [-0.004, 0.003,  0.002, 0.001],
              [0.005, 0.000, -0.002, 0.000]]

W_new = W + ΔW  # merge at inference, zero overhead

# For r=2, ΔW has rank ≤ 2. For r=4 (full rank), LoRA ≡ full fine-tune.
# In practice, r=4 IS enough for 10M-param models.
```

The key: $\Delta W$ is 4×4 = 16 numbers, but it only has 2 independent rows (rank 2). LoRA stores the 2 row-basis vectors in $A$ (4×2) and the 2 column-basis vectors in $B$ (2×4), total 16 numbers. When $r < \min(d, k)$, LoRA uses fewer parameters. When $r = \min(d, k)$, LoRA ≡ full fine-tune.

## Common confusion (5+ bullet points)

1. **"LoRA is just matrix factorization."** Yes, but the insight is that $\Delta W$ IS low-rank during fine-tuning, not that we're forcing it to be low-rank. The empirical finding is that fine-tuning a pre-trained model on a new task MOVES the weights in a low-rank subspace. LoRA doesn't compress — it matches the natural structure of the weight update. If $\Delta W$ were high-rank, LoRA would lose quality. In practice, it doesn't.

2. **"LoRA is only for LLMs."** No. LoRA works on ANY neural network with linear layers: transformers, CNNs, diffusion U-Nets, vision models. Stable Diffusion fine-tunes use LoRA extensively. The principle (weight updates during fine-tuning are low-rank) appears universal. It's been verified on image classification, segmentation, and audio processing.

3. **"r=4 is not enough for complex tasks."** For a 7B model on a 10-epoch fine-tune, r=4 is about 95% of full fine-tune quality. For a 10M model on a 30-second fine-tune, r=8-16 is safer. The optimal rank depends on: (a) the diversity of the base training data, (b) how different the new task is, (c) how many fine-tuning steps you run. More fine-tuning steps → ΔW can be higher rank → benefit from larger r.

4. **"Merging LoRA weights loses the ability to unmerge."** Merging is irreversible (W_new = W + AB, you lose A and B). If you want to keep them separate (for switching between adapters), don't merge — compute $h = Wx + (AB)x$ at inference. This adds a small overhead (one matmul per LoRA layer). Each adapter is tiny (100KB-1MB), so you can have dozens of project-specific adapters loaded simultaneously.

5. **"LoRA can't learn new concepts, only fine-tune existing ones."** This is partially true. LoRA adjusts existing representations but can't create entirely new neurons. For a code completion model, this means LoRA can teach the model "here's what the rich library's API looks like" (adjusting existing Python knowledge) but can't teach "here's how quantum computing works" if the base model never saw anything like it. For novel concepts, full fine-tune (or pre-train from scratch) is needed.

6. **"The α scaling factor matters a lot."** The LoRA equation is actually $h = Wx + (\alpha / r) \cdot (AB)x$. The scaling factor $\alpha$ controls how much the adapter influences the output. $\alpha = r$ means the adapter has 1× weight. $\alpha = 2r$ means 2×. This is a hyperparameter you tune. Typical: $\alpha = 16$ for $r=4$ (4× influence), $\alpha = 32$ for $r=8$.

## Key properties

| Property | Full fine-tune | LoRA |
|---|---|---|
| Parameters trained | 100% | ~0.1% (r=4) |
| Training time | Full | ~0.5-0.8× (less memory for optimizer) |
| Inference overhead | None | None (if merged) / ~5% (if on-the-fly) |
| Storage per adapter | Full model (50MB) | Adapter (100KB-1MB) |
| Swap adapters | No (need new model file) | Yes (swap A,B matrices) |
| Learning new concepts | Yes | Partial (depends on base knowledge) |
| Catastrophic forgetting | High (overwrites old knowledge) | Low (base model frozen) |

## Tech comparison: LoRA vs alternatives

**Full fine-tuning** — when the new task is very different from the base task, when you can afford the compute, when you only need one model.

**LoRA** — when you have multiple related tasks (different codebases, different styles), when storage is limited, when you need fast task switching.

**Prefix tuning / Prompt tuning** — when you can't modify the model at all (API-only access), when you prepend learnable tokens instead of modifying weights. Worse quality than LoRA, but works with any frozen model.

**Adapters** (Houlsby 2019, predecessor to LoRA) — similar idea but adds new layers between existing ones. More parameters, worse quality convergence, more inference overhead. LoRA is strictly better for linear layers.

## Connection to our projects

**cortexcode:** Train ONE base model on jc+rich+cpython combined (10M params, 30 min). Then for each new codebase, train a LoRA adapter (r=8) in 30 seconds. Each adapter is ~80KB. Deploy one adapter per project. The base model captures "how Python works generally." The adapter captures "this specific library's patterns."

**logogen:** Train ONE base model on 300 synthetic logos (35M params, 30 min). Then for each style you want (geometric, letter-only, minimalist, colorful), train a LoRA adapter on 50 curated logos in that style. Each adapter is ~100KB. Switch adapters to change style. No retraining the 35M-param base.

**gm/ curriculum:** LoRA should be taught AFTER VAE and diffusion but BEFORE MoE. The progression: learn to train a model → learn to fine-tune efficiently → learn to scale with sparse activation. LoRA is the bridge between "train once" and "deploy many."

## Mathematical skeleton

**Standard fine-tuning:**
$$\min_{\theta} \mathcal{L}(\theta_{pre} + \Delta \theta; D_{new})$$
$D_{new}$ = new task data. $\theta_{pre}$ = pre-trained weights. $\Delta \theta$ = full-rank update.

**LoRA fine-tuning:**
$$\min_{A, B} \mathcal{L}(\theta_{pre} + \Delta \theta_{approx}; D_{new})$$
where $\Delta \theta_{approx} = \bigoplus_{l \in \text{layers}} A_l \times B_l$ (concatenation across layers).

For a single linear layer $W \in \mathbb{R}^{d \times k}$:
$$h = Wx + \frac{\alpha}{r} \cdot (AB)x$$
$$A \in \mathbb{R}^{d \times r}, \quad B \in \mathbb{R}^{r \times k}$$

Rank $r$ controls the capacity of the adapter:
- $r=1$: the adapter can only shift weights in ONE direction (scalar multiple of one basis vector). Minimal capacity.
- $r=4$: 4 independent directions to modify. Enough for most fine-tuning tasks.
- $r=\min(d,k)$: the adapter has full rank. LoRA ≡ full fine-tune. No parameter savings.

**How to choose r:**
1. Start with $r=4$. Fine-tune, evaluate. 
2. If loss doesn't converge, try $r=8$ or $r=16$.
3. If $r=16$ doesn't converge, the task is too different from the base training → use full fine-tune or pre-train from scratch.

**Why LoRA prevents catastrophic forgetting:**
The base weights $W$ are frozen. The LoRA adapter $\Delta W = A \times B$ only adds information, never removes. The model retains everything it learned during pre-training because those weights never change. When you remove the adapter, the model is exactly the pre-trained model. This makes LoRA ideal for continual learning — each adapter is a non-destructive add-on.
