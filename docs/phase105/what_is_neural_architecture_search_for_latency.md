## What Is Neural Architecture Search for Latency?

---

## The Problem

Standard Neural Architecture Search optimizes for validation accuracy, but edge devices operate under strict constraints. A 99%-accurate image classifier that takes 5 seconds per inference is useless for real-time mobile vision. A model that exceeds the phone's 4GB RAM limit cannot be installed. A model that drains the battery in an hour will be uninstalled by users. How do you search for architectures that sit on the Pareto frontier of accuracy versus real-world resource usage?

---

## Definition

**Neural Architecture Search for Latency** (Latency-Aware NAS) is a variant of NAS where the search objective is a multi-objective function combining accuracy and inference latency (or FLOPs, memory, or energy). The search algorithm explores architectures on a Pareto frontier, trading off accuracy for speed.

**How it works:**
```
Objective:  maximize  accuracy - lambda * latency

Search space: operations with known latency profiles on target hardware
              (e.g., depthwise separable conv = 2ms, standard 3x3 conv = 8ms)

Process:    1. Sample architecture
            2. Measure accuracy on validation set
            3. Measure latency on target device (or lookup table)
            4. Score = accuracy - lambda * latency
            5. Keep architectures on the Pareto frontier
```

**Key techniques:**
- **Hardware-aware search:** latency is measured on the actual target chip, not estimated from FLOPs
- **Multi-objective evolution:** maintain a population that spreads across the accuracy-latency plane
- **Platform-specific optimization:** a model optimized for a Pixel CPU may be suboptimal for an iPhone GPU

**Why this matters:**
- MobileNetV3 and EfficientNet-Lite were designed via latency-aware NAS
- Real-time AR, on-device translation, and autonomous navigation require millisecond-level inference
- FLOPs do not correlate perfectly with latency; memory access patterns and operator fusion matter

---

## Real-Life Analogy

A car designer is not trying to maximize top speed alone. They must also meet fuel efficiency standards, safety regulations, and emissions targets. A Formula 1 car is fast but illegal on public roads. A city bus is efficient but cannot win a race. Latency-aware NAS is like optimizing for both speed and mileage simultaneously. The algorithm generates thousands of car designs, tests each one for top speed and fuel economy, and keeps only the designs that are not dominated by another design in both dimensions. The result is a set of options: a fast but thirsty model, a slow but efficient model, and several balanced options in between.

But the car analogy misses a crucial detail. In NAS, the "road" is the target hardware. A design that is optimal for a highway (server GPU) may be terrible for a mountain trail (mobile CPU). The latency profile of an operation depends on whether the chip has fast matrix multipliers, large caches, or vector units. A depthwise separable convolution reduces FLOPs but may be memory-bound on some hardware, making it slower than a standard convolution with more FLOPs but better memory locality. Hardware-aware NAS measures latency on the actual device, not on paper.

The trade-off is between accuracy and deployability. A latency-aware search might discover that a slightly wider but shallower network is faster than a deeper one because it parallelizes better on the target chip. It might find that replacing a 5x5 convolution with two 3x3 convolutions reduces latency more than FLOPs suggest because of kernel launch overhead. These insights are invisible to accuracy-only NAS.

---

## Tiny Numeric Example

**A latency-aware search over 50 candidate architectures on a mobile CPU:**

| Architecture | Accuracy | Latency (ms) | FLOPs (M) | Score (acc - 0.01*lat) |
|--------------|----------|--------------|-----------|------------------------|
| Large CNN    | 94.2%    | 180          | 1,200     | 92.4                   |
| Medium CNN   | 92.8%    |  45          |   300     | 92.3                   |
| Small CNN    | 89.1%    |  12          |    80     | 88.0                   |
| NAS winner   | 93.5%    |  28          |   180     | 93.2                   |

**The NAS winner is not the most accurate, but it achieves the best balance.**

**Pareto frontier:**
```
Latency (ms)    Accuracy
  12            89.1%   ← fastest
  28            93.5%   ← best trade-off (selected)
  45            92.8%   ← dominated by winner
 180            94.2%   ← most accurate
```

**MobileNetV3-style search result:**
```
Baseline (hand-designed):    91.5% accuracy, 35ms latency
NAS-discovered:              93.1% accuracy, 22ms latency
Improvement:                 +1.6% accuracy, -37% latency
```

**The shift:** By incorporating latency directly into the search objective, latency-aware NAS found architectures that hand-tuned baselines missed, improving both accuracy and speed simultaneously.

---

## Common Confusion

1. **"Latency-aware NAS simply means picking the smallest model."** It searches the architecture space for unexpectedly efficient designs. Sometimes a slightly larger model with a better operation mix is faster than a smaller model with inefficient operations.

2. **"FLOPs are a good proxy for latency."** FLOPs ignore memory bandwidth, operator fusion, and kernel launch overhead. A model with fewer FLOPs can be slower if it is memory-bound or uses unfused operations.

3. **"You can optimize latency on a server and deploy on a phone."** Server GPUs and mobile CPUs have vastly different latency profiles. A model optimized for a V100 may be terrible on a Snapdragon chip.

4. **"Latency-aware NAS finds a single best architecture."** It finds a Pareto frontier of architectures. The final choice depends on the product's latency budget, which the search algorithm does not know.

5. **"Latency-aware NAS is only for vision models."** The same principle applies to NLP (searching for efficient attention patterns), speech (lightweight conformer variants), and any domain where inference speed matters.

6. **"The latency objective makes the search much harder."** Modern approaches use lookup tables and proxy tasks. Latency is evaluated without training, using precomputed profiles for each operation on the target hardware.

7. **"Once optimized, the latency never changes."** Software updates, OS changes, and competing processes on the device can shift latency. Periodic re-measurement and re-optimization are necessary in production.

---

## Where It Is Used in Our Code

`src/phase105/phase105_tiny_ml.py` — While the primary focus of our NumPy simulation is knowledge distillation, the Tiny ML pipeline as a whole represents the same accuracy-efficiency trade-off that latency-aware NAS optimizes. We compare student models trained with different objectives, demonstrating that the right training signal (soft targets) can produce a smaller model that retains more capability, which is the goal of latency-aware architecture search.
