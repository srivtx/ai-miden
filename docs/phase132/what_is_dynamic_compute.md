## What Is Dynamic Compute?

---

### The Problem

Inference costs dominate the budget of production AI systems. A company serving a billion tokens per day spends hundreds of thousands of dollars on GPU compute. The vast majority of that compute is wasted on easy inputs. A user asking "What is 2+2?" consumes the same GPU cycles as a user asking "Write a legal brief analyzing the doctrine of equitable estoppel." Static architectures have no concept of "easy" versus "hard." They run every layer for every token, burning money on trivial queries and barely having enough depth for complex ones. If compute is your most expensive resource, why spend it uniformly?

---

### Definition

**Dynamic compute** is the principle of allocating computational resources unevenly across inputs, tokens, or layers based on real-time difficulty estimation. Instead of a fixed computational graph, dynamic compute systems adapt their depth, width, or precision to match the complexity of the current task. Mixture of Depths and early exit are two implementations of dynamic compute; the broader concept also includes adaptive precision, variable batch sizes, and speculative decoding.

**How it works:**
```
Static compute (wasteful):
  Input A (easy):    96 layers × 4096 dim = 100% compute
  Input B (hard):    96 layers × 4096 dim = 100% compute
  Input C (medium):  96 layers × 4096 dim = 100% compute

Dynamic compute (efficient):
  Input A (easy):    24 layers × 2048 dim = 12% compute
  Input B (hard):    96 layers × 4096 dim = 100% compute
  Input C (medium):  48 layers × 4096 dim = 25% compute
```

**Key techniques:**
- **Adaptive depth:** use fewer layers for easy inputs (early exit, MoD)
- **Adaptive width:** use narrower attention heads or smaller FFN dims for easy tokens
- **Mixed precision:** use FP16 for easy tokens and FP32 for hard tokens
- **Speculative decoding:** use a small draft model for easy sequences, verify with the large model
- **Input-dependent routing:** send short queries through a small model and long queries through a large model

**Why this matters:**
- Dynamic compute can cut inference costs by 30-60% without quality loss
- It aligns hardware utilization with actual problem difficulty
- It enables serving larger models to more users by reducing average load
- It is essential for edge deployment where battery and thermal constraints are strict

---

### Real-Life Analogy

A hospital emergency room.

- **Static compute:** Every patient gets the same full workup: blood tests, MRI, specialist consult, and overnight observation. A patient with a paper cut waits four hours and receives a $10,000 bill. A patient having a heart attack waits four hours too, because the system has no triage. Resources are distributed evenly, which means they are distributed poorly.

- **Dynamic compute:** A triage nurse assesses every patient in 30 seconds. Minor cases get a bandage and discharge. Moderate cases see a physician assistant and get basic labs. Critical cases bypass the waiting room and go straight to the trauma bay. The total staff and equipment are the same, but they are allocated based on need. The paper cut patient is out in 15 minutes; the heart attack patient gets immediate attention.

- **The trade-off:** Triage mistakes are costly. A patient with subtle symptoms might be sent home too early (a false negative in dynamic compute). The triage nurse herself takes time and training. If the triage is slower than the treatment, the system is worse, not better. Dynamic compute only wins when the difficulty assessment is fast and accurate relative to the compute it saves.

---

### Tiny Numeric Example

**Three inputs to a 96-layer, 4096-dim model:**

**Static compute (baseline):**
```
Input                  Layers   Width   Precision   Relative FLOPs
--------------------------------------------------------------------
"What is 2+2?"         96       4096    FP16        100%
"Explain quantum entanglement"
                       96       4096    FP16        100%
"Summarize this article"
                       96       4096    FP16        100%

Average: 100% FLOPs per input
```

**Dynamic compute (adaptive depth + width):**
```
Input                  Layers   Width   Precision   Relative FLOPs
--------------------------------------------------------------------
"What is 2+2?"         24       2048    FP16         12%
"Explain quantum entanglement"
                       96       4096    FP16        100%
"Summarize this article"
                       48       4096    FP16         50%

Average: 54% FLOPs per input  ← 46% savings
```

**Quality comparison on a benchmark suite:**
```
Static model (full):         100% FLOPs,  82.4% accuracy
Dynamic (aggressive):        45% FLOPs,  78.1% accuracy
Dynamic (balanced):          58% FLOPs,  81.2% accuracy
Dynamic (conservative):      72% FLOPs,  82.1% accuracy
```

**The shift:** Dynamic compute moves the Pareto frontier. The balanced configuration saves 42% of compute and loses only 1.2% accuracy. The conservative configuration saves 28% and loses only 0.3%. The right setting depends on whether the application values cost or accuracy more.

---

### Common Confusion

1. **"Dynamic compute always reduces quality."** Not if calibrated correctly. The conservative setting often matches static quality while saving 20-30% of compute. Quality loss only appears when the difficulty estimator is wrong.

2. **"Dynamic compute only applies to inference."** It is most common at inference, but training can also be dynamic: hard examples get more gradient steps, easy examples are subsampled. This is called curriculum learning or hard example mining.

3. **"Dynamic compute is the same as model compression."** Compression creates a smaller static model. Dynamic compute keeps the large model but uses less of it for easy inputs. Compression is permanent; dynamic compute is adaptive.

4. **"You need multiple models for dynamic compute."** Not necessarily. A single model with early exit heads or width adapters can provide dynamic compute internally. Multiple model sizes (cascades) are one approach, but not the only one.

5. **"Dynamic compute makes latency unpredictable."** Latency becomes variable, which complicates SLAs. But the *average* latency drops significantly, and tail latency can be managed with timeouts or fallback to full compute.

6. **"Dynamic compute is only for transformers."** The principle applies to any model. CNNs can use early exit, RNNs can truncate unrolling, and diffusion models can use fewer steps for easy images.

7. **"Dynamic compute saves memory."** It primarily saves FLOPs and latency. Memory savings are secondary unless combined with techniques like layer dropping or KV cache eviction.

---

### Where It Is Used in Our Code

`src/phase132/phase132_mod_concepts.py` — We simulate dynamic compute by assigning different depths to tokens based on synthetic difficulty scores. We compute total FLOPs saved versus a static baseline and show which positions in the sequence consumed more compute.

`src/phase132/phase132_mod_colab.py` — We implement dynamic compute on a real model by adding an early-exit confidence probe after layer 4 of Qwen2.5-3B-Instruct. We route easy tokens through 4 layers and hard tokens through all 36 layers, measuring the average depth per prompt, wall-clock speedup, and quality impact across 100 diverse prompts.

(End of file)
