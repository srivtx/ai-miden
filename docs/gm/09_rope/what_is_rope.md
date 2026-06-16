## Why it exists (THE PROBLEM)

Learned position embeddings (what cortexcode uses) are a dictionary: `pos_emb[0]`, `pos_emb[1]`, ..., `pos_emb[max_seq_len-1]`. If you train on sequences of length 256, the model literally has `pos_emb[256]` uninitialized. You cannot generate 257 tokens without either (a) retraining with a longer `max_seq_len`, (b) interpolation (approximate `pos_emb[300]` from `pos_emb[150]` with some scaling), or (c) accepting garbage.

The fundamental issue: learned position embeddings are ABSOLUTE. Position 47 is "slot 47 in the lookup table." The model must memorize what "position 47" means separately from what "position 46" means.

**Rotary Position Embedding** (RoPE, Su et al., 2021) makes positions RELATIVE. Instead of embedding "I am at position 47," the model embeds "I am 3 tokens away from the start of the function, 5 tokens before the colon, 12 tokens after the `def` keyword." The position information is encoded in the ANGLE between query and key vectors. The attention score between token $i$ and token $j$ depends only on $i - j$, the relative distance.

This means: if you train on 256-token sequences, you can run inference on 10,000-token sequences. The model has never seen position 9,999, but it knows what it means to be "3 tokens away" from something.

## Definition (very simple)

**RoPE** rotates query and key vectors by an angle proportional to their position. The angle is different for each pair of dimensions (each "frequency"). The rotation is:

$$(q_i, k_j) \rightarrow (R_i \cdot q_i, R_j \cdot k_j)$$

where $R_i$ is a rotation matrix that rotates by $i \cdot \theta$ in each 2D subspace. Because rotation is orthogonal, the dot product depends only on the relative angle:

$$(R_i \cdot q_i)^T \cdot (R_j \cdot k_j) = q_i^T \cdot R_{j-i} \cdot k_j$$

The attention score $q_i^T k_j$ becomes a function of $i - j$, the relative position. The model sees "how far apart are these tokens," not "what is the absolute position of each."

In code, RoPE is applied AFTER the $W_q$ and $W_k$ projections but BEFORE the attention score computation. No new learnable parameters. No lookup table. Pure rotation.

## Real-life analogy

**Learned position = assigned seating.** Everyone has a fixed seat number (1-256). If someone sits at seat 257, there's no chair there. You literally can't seat more than 256 people without expanding the room.

**Sinusoidal position (Transformer 2017) = seats spaced by a formula.** You can extrapolate: seat 257 is at approximately the right distance. But the formula was designed for the numbers it was trained on — it degrades gracefully but still degrades.

**RoPE = everyone has a relative sense of distance.** "I'm sitting 3 seats left of John and 5 seats right of Mary." It doesn't matter if there are 100 seats or 10,000 — the relative distances are the same. You can add more seats without anyone being confused about where they are relative to each other.

## Tiny numeric example

2D query and key at positions 0 and 3. Hidden dim = 2 (one frequency).

$$\theta_1 = 1.0 \text{ (base frequency, actually } 10000^{-2/2} = 1.0 \times 0.01 = 0.01 \text{ in practice)}$$

Let me use the actual RoPE formula. For dimension pair $(2m, 2m+1)$:
$$\theta_m = 10000^{-2m/d}$$

For $d=4$, we have 2 frequency pairs: $\theta_0 = 10000^0 = 1.0$, $\theta_1 = 10000^{-2/4} = 10000^{-0.5} \approx 0.01$.

**Token at position 3:**
```
q = [0.5, 0.3, -0.2, 0.8]   # (dim=4) after W_q projection

# Pair 0 (dim 0,1): rotate by 3 * θ_0 = 3 * 1.0 = 3.0 radians
cos(3.0) ≈ -0.99
sin(3.0) ≈ 0.14
q_rot[0] = 0.5 * (-0.99) - 0.3 * 0.14 = -0.537
q_rot[1] = 0.5 * 0.14 + 0.3 * (-0.99) = -0.257

# Pair 1 (dim 2,3): rotate by 3 * θ_1 = 3 * 0.01 = 0.03 radians (tiny!)
cos(0.03) ≈ 1.0
sin(0.03) ≈ 0.03
q_rot[2] = -0.2 * 1.0 - 0.8 * 0.03 ≈ -0.222
q_rot[3] = -0.2 * 0.03 + 0.8 * 1.0 ≈ 0.794
```

**Token at position 5 (2 positions later):**
Rotated by $5 \cdot \theta_0 = 5.0$ and $5 \cdot \theta_1 = 0.05$ — more rotation.

**Why this captures relative position:**
The dot product between the query at position 3 and a key at position 5 encodes the rotation difference $5 - 3 = 2$, not the absolute positions. The low-frequency dimensions (θ_1 = 0.01) barely rotate — they encode long-range structure. The high-frequency dimensions (θ_0 = 1.0) rotate rapidly — they encode local word order.

## Common confusion (5+ bullet points)

1. **"RoPE is just sinusoidal embeddings applied differently."** Close but wrong. Sinusoidal embeddings (Vaswani 2017) add positional information to the INPUT representation: $x = tok\_emb + sin\_pos\_emb$. The model sees this once and then processes it through all layers. RoPE injects positional information into the ATTENTION computation at EVERY layer: for each attention head, query and key are rotated by their position angle. RoPE is applied per-layer, per-head. Sinusoidal is applied once at the input.

2. **"RoPE only works for text, not images or audio."** RoPE has been extended to 2D (for images, position becomes (row, col)), 3D (for video, (t, h, w)), and continuous domains (for audio, time is continuous). The principle is the same: encode the relative separation between any two elements. For a 2D image, patches at (i, j) have separate row and column frequencies. The attention between patch (i, j) and (p, q) depends on (i-p, j-q).

3. **"Extrapolation to unseen lengths is perfect."** No. Extrapolation gracefully degrades. At 2× training length, RoPE is ~95% accurate. At 4×, ~85%. At 10×, ~60%. The degradation comes from the fact that very long relative distances were never seen during training — the model learned that "token 200 away" means something specific, and it doesn't know how to interpret "token 2000 away." Techniques like YaRN (extended RoPE) scale the frequencies to handle longer contexts.

4. **"Base frequency 10000 is always best."** No. The base frequency $\theta = 10000$ in the original paper was chosen empirically for sequences up to ~2048 tokens. For longer sequences, a higher base (100000, 500000, 1000000) gives better long-range modeling because the low-frequency terms stay more distinguishable at higher positions. Llama 2 uses 10000. Llama 3 uses 500000. Gemma uses 10000. The choice depends on your target sequence length.

5. **"RoPE adds complexity to the attention computation."** RoPE adds EXACTLY one element-wise multiplication (for the rotation) before the attention matrix computation. It's a handful of sin/cos evaluations per position, precomputed once. The overhead is negligible (<1% of attention compute). In practice, it's faster than learned position embeddings because you skip the embedding lookup.

6. **"RoPE prevents the model from learning absolute position."** The model CAN learn absolute position indirectly — through causal masking (token 0 sees nothing, token 100 sees 100 things), through the accumulation of many relative distances, and through any non-linearities in subsequent layers. But RoPE biases the model toward RELATIVE reasoning, which is what we want for extrapolation.

## Key properties

| Property | Learned pos emb | Sinusoidal | RoPE |
|---|---|---|---|
| Extrapolation | ✗ (hard limit) | ~ (degrades) | ✓ (graceful) |
| Relative encoding | ✗ | ✗ | ✓ |
| Extra params | `max_seq_len × d` | 0 | 0 |
| Per-layer application | No (once) | No (once) | Yes (every layer) |
| Training buffer size | Fixed | Fixed | Can extend |
| Long-context quality | ✗ | ~ | ✓ |
| Industry adoption | GPT-1, CTRL | Transformer (2017) | Llama, Mistral, Gemma, Qwen |

## Tech comparison: position encoding methods

**Learned** — simplest to implement, zero compute overhead, but absolute position only. Used in small models where extrapolation isn't needed.

**Sinusoidal** — deterministic, no learned params, CAN extrapolate but quality degrades. Pre-RoPE standard.

**RoPE** — relative encoding, no learned params, extrapolates well. Current standard for all new LLMs.

**ALiBi** (Press 2021) — adds a bias to attention scores based on distance. No position embedding at all. Used in BLOOM. Simpler than RoPE, better extrapolation than sinusoidal, worse quality than RoPE at training length.

**NoPE** (Kazemnejad 2023) — no explicit position encoding. The model learns position from the causal mask alone (token 5 sees more context than token 2). Surprisingly effective for short sequences, fails on long ones.

## Connection to our projects

**cortexcode:** The most immediate win. Replace `self.pos_emb = nn.Embedding(max_seq_len, dim)` with `apply_rotary_emb(q, k, positions)` in the attention layer. ~30 lines. Then remove `max_seq_len` as a model parameter and train on block_size=128 but serve completions at block_size=1024. The model can now reference code 500 tokens ago even though it only saw 128-token chunks during training.

**gm/ curriculum:** RoPE should be taught alongside attention mechanisms. The progression: learn attention → learn position encoding → learn why relative encoding matters → learn RoPE as the current best approach.

**MSPCH connection:** The hippocampus encodes RELATIVE position (place cells fire based on relative distance to landmarks, not absolute GPS coordinates). The cortex represents temporal sequences with relative timing (this happened before that, not this happened at 2:37:42 PM). RoPE is the ML equivalent of relative positional reasoning, which is closer to how the brain represents space and time than absolute position lookup tables.

## Mathematical skeleton

**RoPE applied to a single dimension pair (2m, 2m+1):**
For query $q$ at position $i$:
$$q_{2m}^{rot} = q_{2m} \cos(i \cdot \theta_m) - q_{2m+1} \sin(i \cdot \theta_m)$$
$$q_{2m+1}^{rot} = q_{2m} \sin(i \cdot \theta_m) + q_{2m+1} \cos(i \cdot \theta_m)$$

where $\theta_m = 10000^{-2m/d}$ and $d$ is the head dimension.

**Rotary matrix for position $i$:**
$$R_i = \bigoplus_{m=0}^{d/2 - 1} \begin{pmatrix} \cos(i \cdot \theta_m) & -\sin(i \cdot \theta_m) \\ \sin(i \cdot \theta_m) & \cos(i \cdot \theta_m) \end{pmatrix}$$

This is a block-diagonal matrix. Each 2×2 block rotates a pair of dimensions by an angle $i \cdot \theta_m$.

**Attention with RoPE:**
$$a_{ij} = \text{softmax}\left(\frac{(R_i \cdot q_i)^T \cdot (R_j \cdot k_j)}{\sqrt{d_k}}\right)$$

Because $R_i^T \cdot R_j = R_{j-i}$ (rotation matrices are orthogonal and compose additively):
$$(R_i \cdot q_i)^T \cdot (R_j \cdot k_j) = q_i^T \cdot R_i^T \cdot R_j \cdot k_j = q_i^T \cdot R_{j-i} \cdot k_j$$

The attention score depends ONLY on the relative position $j - i$, encoded as a rotation.

**Efficient implementation:**
Precompute $\cos(i \cdot \theta_m)$ and $\sin(i \cdot \theta_m)$ for all positions and frequencies. This is a $(max\_seq\_len \times d/2)$ lookup table. Then apply:

```python
def apply_rotary_emb(x, cos, sin):
    # x: (batch, n_heads, seq_len, head_dim)
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    x_rot = torch.cat([
        x_even * cos - x_odd * sin,
        x_even * sin + x_odd * cos
    ], dim=-1)
    return x_rot

q = apply_rotary_emb(q, cos[:T], sin[:T])
k = apply_rotary_emb(k, cos[:T], sin[:T])
# v is NOT rotated (RoPE only applies to q and k)
```

Note: values $v$ are NOT rotated. Only queries and keys. Because the relative position should affect the attention weights (which tokens to attend to), not the content of what's being attended to.
