## Why it exists (THE PROBLEM)

A dense transformer uses ALL its parameters for EVERY token. If you double the parameters, you double the inference cost. This creates an impossible trade-off: either your model is small (fast but dumb) or large (smart but expensive). There's no middle ground in a dense architecture.

The brain solved this differently. It has ~86 billion neurons but only 1-5% are active at any moment. Different tasks activate different subnetworks. The brain's "parameter count" is massive, but its "active computation" is small and task-specific.

**Mixture of Experts** (Shazeer et al., 2017; Jiang et al., 2024 with Mixtral) applies this insight to transformers. Instead of one FFN per layer, you have N FFN "experts" and a router that selects the top-K experts per token. You can have 8× more parameters (8 experts) at only 2× the inference cost (because only 2 experts are active per token). Capacity explodes, cost barely moves.

## Definition (very simple)

**MoE** replaces each dense FFN layer with N independent FFN experts plus a trainable router. For each input token:

1. Router computes a score for each expert: $s = W_g \cdot x$ (linear projection)
2. Top-K experts are selected: $\text{indices} = \text{argtopk}(s, k)$
3. Only those K experts compute their forward pass
4. Output is the weighted sum: $h = \sum_{i \in \text{top-k}} \text{softmax}(s)_i \cdot \text{Expert}_i(x)$

The key: N is large (8-128), K is small (1-2). 95% of experts do NOTHING per token. Their parameters consume memory but not compute. The router learns which experts handle which types of input.

In practice, MoE layers are placed in the FFN blocks of a transformer. Self-attention stays dense (it's already expensive). Only the FFN gets the MoE treatment because FFN is typically 2/3 of the parameters.

## Real-life analogy

**A dense model is a single general contractor for every job.** Need plumbing? Ask him. Need electrical? Ask him. Need drywall? Ask him. He's mediocre at everything because he can't specialize.

**MoE is a building project with specialists.** You have a plumber, an electrician, a drywaller, a painter, a roofer — 8 experts. For each task, you CALL ONLY the relevant expert. The plumber never touches the electrical. The drywaller never paints. Each expert is excellent at their specific job because they focus.

**A dense model is a hospital with one doctor who treats every patient.** She's exhausted, sees 100 patients, and gets worse at each. **MoE is a hospital with 10 specialists.** Each patient is routed to the right specialist. The cardiologist sees 10 heart patients and gets better at hearts. The neurologist sees 10 brain patients and gets better at brains. Total patients seen: 100. Total doctors working: 10. Active per patient: 1. Quality: much better.

## Relationship to the brain

The brain is the original MoE system. The cortex is divided into functional areas (visual, auditory, motor, language) that activate selectively based on the task. Within each area, only ~5% of neurons fire at any moment. The thalamus acts as a router (gating which cortical areas communicate). The basal ganglia select actions by routing activation to the most promising motor programs.

MoE in AI copies this: modular experts, selective activation, a learned router. The difference: the brain's routing is MORE sophisticated (neuromodulators, attention, working memory all modulate routing) and the brain's experts are MORE specialized (individual neurons vs entire FFN blocks).

## Tiny numeric example

Dense FFN (no MoE):
```python
x = [0.5, -0.2, 0.8, 0.1]  # 4-dim input
W1 = 4×8 matrix, W2 = 8×4 matrix
h = W2 @ GELU(W1 @ x)  # 4 → 8 → 4, all weights active
# 4×8 + 8×4 = 64 weights used
```

MoE FFN with 4 experts, top-K=2:
```python
x = [0.5, -0.2, 0.8, 0.1]  # same input

# Router: 4-dim linear → 4 expert scores
s = W_gate @ x = [1.2, -0.5, 3.1, 0.3]
top2_indices = argtop2(s) = [2, 0]  # experts 2 and 0
top2_weights = softmax([3.1, 1.2]) = [0.87, 0.13]

# Only experts 2 and 0 compute:
h2 = Expert_2(x)   # 4×8 + 8×4 = 64 weights (expert 2)
h0 = Expert_0(x)   # 4×8 + 8×4 = 64 weights (expert 0)

h = 0.87 * h2 + 0.13 * h0  # weighted sum

# Experts 1 and 3: DO NOTHING. Zero compute.

# Total parameters: 4 experts × 64 = 256 weights
# Active compute: 2 experts × 64 = 128 weights (2× dense)
# Parameters: 4× dense. Active compute: 2× dense.
```

Real Mixtral 8×7B: 8 experts per layer, top-2 active. Total: 47B params. Active per token: 13B. Same inference speed as a 13B dense model. Quality matches a ~30B dense model. Parameter efficiency: 47B / 13B = 3.6×. Quality efficiency: matches model 2.5× larger.

## Common confusion (5+ bullet points)

1. **"MoE makes training faster."** No. MoE makes INFERENCE more efficient per parameter, but TRAINING is similar speed or slower. During training, ALL experts must compute because backprop needs gradients for all weights. Training an 8-expert MoE takes roughly the same time as training an 8× larger dense model. The savings come at inference (only K experts forward). For a Colab T4, this means MoE training takes longer than dense training for the same number of tokens. The benefit is at deployment.

2. **"The router will collapse — all tokens go to one expert."** This IS a real problem and requires a load-balancing loss. The standard approach: add an auxiliary loss term $\lambda \cdot \mathcal{L}_{balance}$ that penalizes uneven expert usage. This pushes the router to distribute tokens evenly across experts. Without this, the router greedily sends all tokens to the "best" expert, and the other experts get zero gradient and die.

3. **"MoE is just an ensemble of smaller models."** Close, but the router is trained END-TO-END with the experts. It's not an ensemble (where each model is trained independently and then combined post-hoc). The router and experts co-adapt. The router learns which expert to pick BECAUSE the expert is learning to specialize. The expert learns to specialize BECAUSE the router is picking it for certain types of inputs. This co-evolution is what makes MoE work better than an ensemble.

4. **"More experts is always better."** There's a sweet spot. Mixtral 8×7B (8 experts) found that going from 8 to 16 experts didn't improve quality much but increased training instability. The optimal number depends on: (a) how diverse your training data is (more diverse → more experts help), (b) how many tokens per expert is "enough" to learn specialization, (c) memory constraints (more experts = more VRAM for training).

5. **"MoE requires a special training infrastructure."** For small models (10M-100M params), standard PyTorch works fine. For large models (7B+), expert parallelism (each expert on a different GPU) requires distributed training frameworks. Mixtral uses Megatron-LM with tensor parallelism AND expert parallelism. For a 10M model on a T4, you can just write a for loop over experts.

6. **"The router needs to be complex."** No. The simplest router is a single linear projection + softmax + top-K. Mixtral uses exactly this. More complex routers (hierarchical, learned prior, RL-based) have been tried but the linear router works surprisingly well. The simplicity is part of what makes MoE practical — the routing overhead is negligible (~0.1% of total compute).

## Key properties

| Property | Dense | MoE (8 experts, top-2) |
|---|---|---|
| Total params | P | ~4P |
| Active params per token | P | ~0.5P (2 experts = 2/8 × 4P = P... wait) |

Let me be precise: MoE replaces ONLY the FFN, which is typically 2/3 of total params. For Mixtral 8×7B:

| Component | Dense (Mistral 7B) | MoE (Mixtral 8×7B) |
|---|---|---|
| Attention params | 2.3B | 2.3B (unchanged) |
| FFN params per expert | 4.7B | 4.7B |
| Total FFN params | 4.7B × 1 = 4.7B | 4.7B × 8 = 37.6B |
| Total model params | 7B | 46.7B |
| Active FFN per token | 4.7B | 4.7B × 2 = 9.4B |
| Active total per token | 7B | 12.9B |
| Active / total ratio | 100% | 27.6% |
| Inference speed vs dense 7B | 1× | 1.8× (2× more FFN compute) |
| Quality | Baseline | Matches ~30B dense |

## Tech comparison: MoE vs alternatives

**Dense scaling** — when you have no training compute limits and inference latency is the only metric. Dense is simpler, more stable, easier to deploy.

**MoE** — when you want more capacity for the same inference latency. When your data has clear clusters/types (different codebases, different languages, different image types). When storage is cheap but compute is expensive.

**Ensembles** (multiple independent models) — when you need diversity (averaging predictions reduces variance), when you don't mind N× inference cost, when training each model independently is easier than coordinating a router.

**Structured sparsity** (static pruning) — when you know a priori which weights matter for which tasks. MoE is dynamic (tokens determine routing), structured sparsity is static (fixed masks). MoE is more flexible but has routing overhead.

## Connection to our projects

**cortexcode:** Replace the dense FFN in `MSPCHBlock` with an MoE FFN (8 experts, top-2). Total params: 10M → 40M. Active per token: 20M (2× increase). Training time: 2× longer (all experts compute gradients). Inference speed: 1.5× slower (2 experts vs 1 FFN, plus routing). The model learns specialization: one expert handles class definitions, another handles import statements, another handles argument parsing.

**logogen:** Less relevant — the U-Net's bottleneck and decoder already act like "experts" at different resolutions. MoE would add complexity without clear benefit for a 35M model on 128×128 images. MoE shines for 1B+ parameter models where dense scaling is prohibitive.

**MSPCH connection:** MoE IS the sparse-activation principle from neuroscience. The brain's cortical columns are MoE experts. The thalamus is the router. The neuromodulator system (DA, NE, ACh) modulates routing based on context. Our `MSPCHBlock` claims to be "brain-inspired" but uses dense FFN — MoE would make that claim real.

## Mathematical skeleton

**Standard FFN:**
$$h = \text{FFN}(x) = W_2 \cdot \text{GELU}(W_1 \cdot x)$$
where $W_1 \in \mathbb{R}^{d \times d_{ff}}$, $W_2 \in \mathbb{R}^{d_{ff} \times d}$

**MoE FFN:**
$$h = \sum_{i=1}^{N} g_i(x) \cdot \text{Expert}_i(x)$$
where each Expert$_i$ is a separate FFN with weights $W_1^{(i)}, W_2^{(i)}$.

**Router:**
$$g(x) = \text{softmax}(W_g \cdot x)$$
$$g_i(x) = \begin{cases} \frac{\exp(s_i)}{\sum_{j \in \text{top-k}} \exp(s_j)} & \text{if } i \in \text{top-k}(W_g \cdot x) \\ 0 & \text{otherwise} \end{cases}$$

**Load balancing loss:**
$$\mathcal{L}_{balance} = N \cdot \sum_{i=1}^{N} f_i \cdot P_i$$
where $f_i$ = fraction of tokens routed to expert $i$, $P_i$ = mean softmax probability for expert $i$.

$$\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda \cdot \mathcal{L}_{balance}$$

Typical $\lambda = 0.01-0.1$. If $\lambda$ is too high, the router over-distributes and experts can't specialize. If too low, routing collapses. Mixtral uses $\lambda = 0.02$.

**Why softmax is computed only over top-K:**
Computing softmax over all N experts for every token would require evaluating ALL expert scores, defeating the purpose of sparse routing. Instead:
1. Compute raw scores $s = W_g \cdot x$ (cheap: one linear projection)
2. Find top-K indices (cheap: O(N) with torch.topk)
3. Compute softmax ONLY over those K scores (K is small)
4. Only those K experts compute their forward pass (the expensive part)

**Capacity factor:** Each expert has a capacity limit per batch: how many tokens it can process. If more tokens are routed to an expert than its capacity, the overflow tokens are dropped (identity shortcut). Capacity factor = actual_capacity / (tokens_per_expert_under_uniform_routing). Capacity factor 1.25 means 25% over-provisioning. Dropped tokens = tokens that exceed per-expert capacity → passed through as identity → no gradient for those tokens on that expert.
