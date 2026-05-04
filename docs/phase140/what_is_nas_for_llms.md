## What Is Neural Architecture Search for LLMs?

---

### The Problem

Every transformer you have ever used was designed by hand. A team of researchers sat in a room and decided: "12 layers, 768 hidden dimensions, 12 attention heads, 3072 FFN dimension." They arrived at these numbers through intuition, ablation studies, and hardware constraints. But human intuition is slow, expensive, and biased toward round numbers. A 9-layer model with 896 hidden dimensions might be faster and more accurate than the hand-tuned 12-layer baseline, yet no one ever tried it because it does not fit the standard grid. How do you escape the tyranny of human-chosen hyperparameters?

---

### Definition

**Neural Architecture Search (NAS) for LLMs** is the automated discovery of optimal transformer configurations — depth, width, number of attention heads, FFN expansion ratio, and activation functions — by treating architecture as a search variable rather than a design choice.

**How it works:**
```
Search space:   All valid combinations of {layers, hidden_dim, heads, ffn_ratio}
Objective:      Minimize validation loss subject to a FLOPs or latency budget
Search method:  Grid, random, evolutionary, or gradient-based search
Evaluation:     Train candidate architecture for few steps, measure quality
Output:         Pareto frontier of best architectures across efficiency metrics
```

**Key techniques:**
- **Grid search:** Exhaustively evaluate every combination. Guaranteed optimal within the space, but computationally infeasible for large spaces.
- **Random search:** Sample architectures uniformly. Surprisingly effective; often finds 90% of the quality of grid search with 10% of the compute.
- **Evolutionary search:** Maintain a population of architectures, mutate the best, and select for fitness. Works well because architectural choices are discrete and non-differentiable.
- **Weight-sharing NAS (supernet):** Train one giant model that contains all candidate architectures as subnets. Evaluate subnets by extracting their weights without retraining.

**Why this matters:**
- GPT-4's architecture was not found by NAS, but future frontier models may be. The search space is too large for manual tuning.
- Smaller models discovered by NAS (e.g., EfficientNet in vision) routinely outperform larger hand-designed models on mobile devices.
- NAS finds non-obvious trade-offs: reducing depth and increasing width can lower latency while maintaining accuracy on modern tensor cores.

---

### Real-Life Analogy

Building a custom racing bicycle.
- **Hand-designed architecture:** A frame builder uses tradition — 56cm frame, 700c wheels, aluminum tubes. It works well. But the builder never tests a 54cm frame with 650b wheels because it looks wrong.
- **NAS:** A wind tunnel tests 10,000 frame geometries automatically. It discovers that a slightly shorter frame with asymmetric tube diameters reduces drag by 8% while keeping weight identical. No human would have guessed this combination because it violates aesthetic norms.
- **The Pareto frontier:** Some frames are lighter but less stiff. Some are stiffer but heavier. The optimal frame depends on whether the race is uphill or flat. NAS does not give you one answer; it gives you the full menu of optimal trade-offs.

---

### Tiny Numeric Example

**Simulated search space (depth x width):**
```
Depth: [4, 6, 8, 10]
Width: [256, 384, 512, 640]
Ground-truth accuracy (simulated):
  acc(depth, width) = 0.5 + 0.3 * (1 - exp(-depth/8)) * (1 - exp(-width/400))
FLOPs = depth * width^2  (normalized)
```

**Best architecture found by each method (budget = 8 evaluations):**
```
Grid search (sampled 8 of 16):    depth=8, width=512 -> acc=0.742, FLOPs=2.0M
Random search (8 samples):        depth=6, width=640 -> acc=0.738, FLOPs=2.5M
Evolutionary (8 evaluations):     depth=10, width=384 -> acc=0.739, FLOPs=1.5M
```

**The insight:** Evolutionary search found the most accurate model *under the FLOPs budget* because it prioritized width early (fast gains) and then traded width for depth (better FLOPs efficiency). Grid search was forced into a coarse lattice. Random search got lucky on width but missed the depth sweet spot.

---

### Common Confusion

1. **"NAS replaces human engineers."** It does not. Humans define the search space, the objective, and the constraints. NAS optimizes within that box. A bad search space yields bad architectures no matter how smart the search algorithm is.

2. **"NAS is just hyperparameter tuning."** Hyperparameter tuning optimizes learning rate, batch size, and regularization for a fixed architecture. NAS optimizes the architecture itself — the number of layers, the dimension of each layer, and the connectivity pattern.

3. **"You need a supercomputer to run NAS."** Early NAS methods did. Modern weight-sharing approaches (supernets) and small proxy tasks (training for 100 steps on a subset) make NAS affordable on a single GPU.

4. **"The best architecture on a proxy task is the best on the full task."** Not always. A model that trains fast for 100 steps may plateau early. The correlation between proxy and final performance is strong but not perfect. Good NAS pipelines validate top candidates with full training.

5. **"Deeper is always better for LLMs."** NAS often discovers that widening the model or adjusting the FFN ratio yields better quality per FLOP than naively adding layers, especially when matrix-multiply dimensions align with hardware warp sizes.

6. **"NAS only searches over depth and width."** Modern NAS for LLMs also searches attention patterns (local vs. global), activation functions (SwiGLU vs. GELU), layer normalization placement (Pre-LN vs. Post-LN), and even training hyperparameters jointly.

7. **"Evolutionary search is obsolete because differentiable NAS exists."** Differentiable NAS (DARTS) works well for small vision models but struggles with the discrete, high-dimensional search spaces of Transformers. Evolutionary methods remain competitive for LLMs.

---

### Where It Is Used in Our Code

`src/phase140/phase140_nas_concepts.py` — We simulate a NAS search over depth and width with a synthetic accuracy surface. We compare grid search, random search, and evolutionary search, plotting the Pareto frontier of accuracy versus FLOPs and visualizing how each method explores the space.

`src/phase140/phase140_nas_colab.py` — We train 9 real small GPT-2 variants on wikitext-2, one for each configuration in a depth-by-width grid. We measure validation perplexity and parameter count, then compare exhaustive grid search, random sampling, and a short evolutionary run to show that simple configs often outperform naive scaling.

