## What Is a State Space Model (SSM)?

---

### The Problem

Transformers use self-attention, which requires comparing every token to every other token. For a sequence of length N, this costs O(N²) time and memory. A 100,000-token document creates a 10-billion-entry attention matrix. How do you process long sequences without this quadratic explosion?

---

### Definition

A **State Space Model (SSM)** is a sequence model that maintains a compressed internal **state** vector. At each timestep, it updates this state based on the current input and produces an output based on the state. The key equations are:

**Continuous form:**
```
h'(t) = A·h(t) + B·x(t)   (state evolves based on input)
y(t)  = C·h(t) + D·x(t)   (output is read from state)
```

**Discrete form (for digital sequences):**
```
h_t = Ā·h_{t-1} + B̄·x_t
y_t = C·h_t + D·x_t
```

Where:
- `h_t` is the hidden state (a compressed summary of all previous inputs)
- `x_t` is the input at time t
- `y_t` is the output at time t
- `A`, `B`, `C`, `D` are learned matrices

**Complexity:** Each step updates a fixed-size state. Processing N tokens costs O(N) time and O(1) memory per step. No KV cache. No attention matrix.

---

### Real-Life Analogy

A professional note-taker listening to a long lecture. Instead of transcribing every word (like attention), they maintain a running summary on a single sheet of paper. When the speaker says something important, they add it to the summary. When the speaker says something trivial, they ignore it. At any point, if you ask them a question, they consult their one-page summary — not the entire lecture transcript. The summary is small and fixed-size, no matter how long the lecture.

---

### Tiny Numeric Example

**Parameters:**
- State dimension: 2
- Input dimension: 1
- Output dimension: 1

```
A = [[0.9, 0.0],
     [0.0, 0.8]]

B = [0.5, 0.3]
C = [1.0, 0.5]
D = [0.1]
```

**Input sequence:** x = [2.0, 0.0, 1.0, 0.0]

**Step 0 (t=0):**
```
h_0 = [0, 0]  (initial state)
y_0 = C·h_0 + D·x_0 = 1.0·0 + 0.5·0 + 0.1·2.0 = 0.2
```

**Step 1 (t=1):**
```
h_1 = A·h_0 + B·x_1
    = [0.9·0 + 0.0·0, 0.0·0 + 0.8·0] + [0.5·0.0, 0.3·0.0]
    = [0, 0]
y_1 = C·h_1 + D·x_1 = 0 + 0.1·0.0 = 0.0
```

**Step 2 (t=2):**
```
h_2 = A·h_1 + B·x_2
    = [0.9·0, 0.8·0] + [0.5·1.0, 0.3·1.0]
    = [0.5, 0.3]
y_2 = C·h_2 + D·x_2
    = 1.0·0.5 + 0.5·0.3 + 0.1·1.0
    = 0.5 + 0.15 + 0.1 = 0.75
```

**Step 3 (t=3):**
```
h_3 = A·h_2 + B·x_3
    = [0.9·0.5, 0.8·0.3] + [0.5·0.0, 0.3·0.0]
    = [0.45, 0.24]
y_3 = C·h_3 + D·x_3
    = 1.0·0.45 + 0.5·0.24 + 0.1·0.0
    = 0.45 + 0.12 + 0.0 = 0.57
```

**Key observation:** The state `h_t` is a compressed summary. Even though the input at t=0 was 2.0, its influence on later outputs decays through A (0.9 and 0.8 are less than 1). The model "forgets" old inputs exponentially.

---

### Common Confusion

1. **"An SSM is just an RNN."** Almost, but not quite. A vanilla RNN has non-linear activations: `h_t = tanh(W·h_{t-1} + U·x_t)`. An SSM is linear: `h_t = A·h_{t-1} + B·x_t`. This linearity is what enables fast parallel training via convolution or scan algorithms.

2. **"SSMs cannot model complex patterns because they are linear."** The matrices A, B, C can be learned, and multiple SSM layers can be stacked with non-linearities between them. The linearity is only *within* one SSM step, not across the whole network.

3. **"SSMs have no memory limitations."** They do. The state is a fixed-size vector. If the state dimension is 16, the model can only retain 16 degrees of freedom worth of information. This is both the strength (constant memory) and weakness (compression loss) of SSMs.

4. **"All SSMs are the same."** Not at all. S4 uses a specific structured A matrix (HiPPO initialization). H3 adds multi-head gating. Mamba makes B, C input-dependent (selective). Each variant makes different trade-offs between speed, memory, and expressiveness.

5. **"SSMs replace Transformers completely."** Not yet. SSMs excel at long sequences but sometimes underperform Transformers on tasks requiring precise copying or retrieval of specific tokens from far away. Hybrid models (SSM + local attention) are currently the most promising.

---

### Where It Is Used in Our Code

`src/phase34/phase34_mamba.py` — Implements a simple selective SSM from scratch in NumPy. Shows how the state evolves, how selectivity controls what is remembered, and compares memory usage to a Transformer KV cache.
