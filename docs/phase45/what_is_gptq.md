## What Is GPTQ?

---

### The Problem

Basic quantization rounds each weight independently. But weights are not independent — they interact in layers. Rounding one weight up and its neighbor down might cancel out. Can we quantize weights while considering how the error propagates through the network?

---

### Definition

**GPTQ (General-purpose Post-Training Quantization)** is an algorithm that quantizes weights one layer at a time, using the Hessian matrix (second derivatives) to optimally compensate for quantization error.

**How GPTQ works:**
1. **Process layers sequentially:** Start with the first layer, quantize it, then move to the next.
2. **Optimal Brain Quantization:** For each weight being quantized, compute how much it affects the layer output.
3. **Error compensation:** When you round weight w_i to the nearest quantized value, the error `δ_i = w_i - quantized(w_i)` is distributed to the remaining unquantized weights to cancel it out.
4. **Update remaining weights:** `W_remaining -= δ_i × H^(-1)[:, i]` where H is the Hessian.

**Why GPTQ is powerful:**
- It quantizes to INT4 with near-INT8 quality
- It processes a 175B model in a few hours on a single GPU
- It is the standard for open-source LLM quantization (llama.cpp, AutoGPTQ)

**Key formula:**
```
For each weight w_i in layer:
    q_i = round(w_i / scale) × scale
    error = w_i - q_i
    w_j -= error × H^(-1)[j, i] / H^(-1)[i, i]  for all unquantized j
```

---

### Real-Life Analogy

A team of 100 people carrying a giant sculpture.
- **Basic quantization:** Each person independently adjusts their grip by rounding to the nearest inch. The sculpture tilts and wobbles because no one coordinated.
- **GPTQ:** One person at a time adjusts their grip. When Alice moves her hand an inch left, the team leader tells Bob and Carol to shift right by exactly the right amount to compensate. The sculpture stays balanced.

GPTQ treats quantization as a sequential optimization problem where each decision is propagated to the remaining weights. The result is a globally better solution than independent rounding.

---

### Tiny Numeric Example

**Layer with 3 weights:**
```
W = [0.34, -0.87, 1.23]
Scale = 0.5, so quantized values are multiples of 0.5: {-1.0, -0.5, 0.0, 0.5, 1.0, 1.5}
```

**Basic quantization (independent rounding):**
```
q = [0.5, -1.0, 1.0]
Error = [0.16, -0.13, -0.23]
```

**GPTQ (sequential with compensation):**
```
Step 1: Quantize w_0 = 0.34 -> 0.5, error = -0.16
        Compensate w_1 and w_2 using Hessian inverse:
        w_1 = -0.87 - (-0.16) × 0.3 = -0.82
        w_2 = 1.23 - (-0.16) × 0.2 = 1.26

Step 2: Quantize w_1 = -0.82 -> -1.0, error = 0.18
        Compensate w_2:
        w_2 = 1.26 - 0.18 × 0.4 = 1.19

Step 3: Quantize w_2 = 1.19 -> 1.0, error = 0.19
        No remaining weights to compensate.

Final quantized: [0.5, -1.0, 1.0]
But the weights were adjusted to minimize global error.
```

The quantized values look the same, but the path to get there optimized the layer output error, not just individual weight error.

---

### Common Confusion

1. **"GPTQ requires training data."** Yes, it needs a small calibration dataset (usually 128-256 samples) to compute the Hessian. But it does not retrain the model.

2. **"GPTQ is only for LLMs."** It was designed for LLMs but works for any neural network. The algorithm is general.

3. **"GPTQ produces the same result every time."** No. The quantization order matters. GPTQ processes weights in a fixed order (usually column by column), but different orderings give slightly different results.

4. **"GPTQ is slow."** It is slow compared to basic rounding, but fast compared to training. A 7B model quantizes in minutes. A 70B model in hours.

5. **"GPTQ needs the Hessian exactly."** No. It uses an approximate Hessian computed from activation statistics, which is much cheaper than exact second derivatives.

---

### Where It Is Used in Our Code

`src/phase45/phase45_quantization.py` — We implement a simplified layer-wise quantization with error compensation (the core idea of GPTQ) and compare it against independent rounding on a small neural network.
