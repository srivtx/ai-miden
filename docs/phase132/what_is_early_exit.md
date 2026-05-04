## What Is Early Exit?

---

### The Problem

Every token in a transformer passes through the same fixed number of layers. When you ask a model to complete "The capital of France is __", the answer is trivial. The model should know "Paris" instantly. Yet it still computes 96 layers of self-attention, layer normalization, and feed-forward transformations just to retrieve a basic fact. For simple patterns, deep computation is unnecessary. If a student knows the answer immediately, forcing them to spend ten minutes showing their work is wasteful. Can a model decide when it is confident enough to stop computing?

---

### Definition

**Early exit** is a technique where a transformer evaluates its confidence at intermediate layers and stops computing deeper layers for tokens that have already converged to a confident representation. A token exits when its internal state stabilizes, typically measured by entropy of the intermediate prediction or by the L2 norm of the change between consecutive layers.

**How it works:**
```
Standard transformer:
  Token → Layer 1 → Layer 2 → ... → Layer 96 → Output

Early exit transformer:
  Token → Layer 1 → Layer 2 → (confidence check)
              ↓
           confident? → YES → exit to output head
              ↓
           confident? → NO  → continue to Layer 3
```

**Key techniques:**
- **Confidence threshold:** exit if the intermediate classifier's max probability exceeds a threshold (e.g., 0.9)
- **Entropy-based:** exit if the prediction entropy drops below a threshold (low entropy = high confidence)
- **Layer-wise classifiers:** lightweight output heads attached to every few layers for early evaluation
- **Patience:** require K consecutive layers to agree before exiting, preventing premature exits on local minima

**Why this matters:**
- Early exit can reduce average inference time by 30-50% on easy inputs
- It requires no architectural change to the main model; only lightweight exit heads are added
- It adapts dynamically to input difficulty without human intervention
- It is simpler to implement than Mixture of Depths because it does not need a learned router

---

### Real-Life Analogy

A student taking a multiple-choice exam.

- **Standard transformer:** The student must answer every question by writing a full essay proof, regardless of difficulty. For "What is 2+2?" she writes four pages of number theory, set construction, and Peano axioms. For "Prove Fermat's Last Theorem" she also writes four pages, but now it is insufficient. Every question gets exactly the same effort, which is absurd for the easy ones and inadequate for the hard ones.

- **Early exit:** The student glances at the question. If it is trivial ("What is 2+2?"), she circles "4" instantly and moves on. If it is moderately hard, she spends two minutes working it out. If it is extremely hard, she spends the full exam time. She has an internal confidence meter: when she is sure, she stops. The total time saved on easy questions lets her focus on hard ones, or simply finish early.

- **The trade-off:** The student might exit too early and get a moderate question wrong because she did not double-check. The confidence threshold is a dial: set it too aggressive and accuracy drops; set it too conservative and you save no time. Finding the right threshold requires calibration on a validation set.

---

### Tiny Numeric Example

**Model: 12 layers. Confidence threshold: 0.85. Patience: 2 layers.**

**Input: "The capital of France is"**

**Standard transformer:**
```
Token       Layers computed   Exit layer
------------------------------------------
The         12                12
capital     12                12
of          12                12
France      12                12
is          12                12

Total layers: 5 × 12 = 60
```

**Early exit transformer:**
```
Token       Layer 4 confidence   Layer 8 confidence   Exit layer
------------------------------------------------------------------
The         0.92                 —                    4
capital     0.78                 0.89                 8
of          0.95                 —                    4
France      0.81                 0.87                 8
is          0.96                 —                    4

Total layers: 4 + 8 + 4 + 8 + 4 = 28  ← 53% savings
```

**Input: "Explain the Riemann Hypothesis and its implications"**
```
Token       Layer 4 confidence   Layer 8 confidence   Exit layer
------------------------------------------------------------------
Explain     0.45                 0.62                 12
the         0.88                 —                    4
Riemann     0.38                 0.55                 12
Hypothesis  0.41                 0.58                 12
and         0.91                 —                    4
its         0.85                 —                    4
implications 0.35                0.51                 12

Total layers: 12+4+12+12+4+4+12 = 60  ← 0% savings (hard input)
```

**Accuracy comparison:**
```
Standard 12-layer:        81.3% accuracy, 100% compute
Early exit (threshold 0.85): 80.1% accuracy,  58% compute
Early exit (threshold 0.90): 80.9% accuracy,  68% compute
Early exit (threshold 0.95): 81.2% accuracy,  82% compute
```

**The shift:** Easy inputs get massive speedups; hard inputs use full compute. The average savings depend on the workload distribution. A chatbot serving simple FAQs saves 50%; a research assistant answering hard questions saves 10%.

---

### Common Confusion

1. **"Early exit and Mixture of Depths are the same thing."** They are related but different. Early exit uses confidence thresholds to stop computation; MoD uses a learned router to assign depths. Early exit is simpler but less flexible; MoD can learn complex routing policies.

2. **"Early exit requires retraining the whole model."** Not necessarily. You can freeze the base model and train only lightweight exit heads on top of intermediate layers. This is much cheaper than full retraining.

3. **"Early exit tokens produce worse embeddings for downstream layers."** This is true if naive implementation is used. Proper early exit architectures pool exited tokens into a residual stream or use skip connections so later layers can still attend to them.

4. **"Confidence always correlates with correctness."** It does not. A model can be confidently wrong (overconfident on out-of-distribution inputs). Calibrating confidence with temperature scaling or a validation set is essential.

5. **"Early exit works for autoregressive generation."** It is harder for autoregressive models because early-exit tokens still need KV cache entries for future tokens. It works best for encoder-only or prefix-encoding tasks.

6. **"You need an exit head at every layer."** You can place them every 2-4 layers to reduce overhead. The spacing is a design choice trading granularity for efficiency.

7. **"Early exit makes batching impossible."** Batching is tricky because different sequences exit at different layers. Dynamic batching or padding strategies are needed, but batching is still possible.

---

### Where It Is Used in Our Code

`src/phase132/phase132_mod_concepts.py` — We simulate early exit alongside MoD routing. Tokens with high synthetic confidence exit after 4 layers; low-confidence tokens continue to 12 layers. We compare the compute savings and visualize which tokens exited early.

`src/phase132/phase132_mod_colab.py` — We implement true early exit on Qwen2.5-3B-Instruct by attaching a confidence probe after layer 4. Tokens exceeding the confidence threshold skip the remaining layers. We measure average exit depth, speedup, and accuracy on 100 prompts.

(End of file)
