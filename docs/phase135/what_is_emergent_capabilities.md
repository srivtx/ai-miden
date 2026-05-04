## What Is Emergent Capabilities?

---

### The Problem

Machine learning has always been gradual: add more data, get slightly better results. Engineers could train small models, observe the trend, and extrapolate to predict large-model performance. But around 2020, researchers noticed something strange. Certain abilities — chain-of-thought reasoning, arithmetic, translation between low-resource languages — were completely absent in 1B-parameter models, slightly present in 10B models, and suddenly excellent in 100B models. There was no smooth curve. The capability appeared almost overnight. This broke every forecasting tool in the field. If you cannot predict what a larger model will do, how do you plan research, allocate compute, or assess safety?

---

### Definition

**Emergent capabilities** are abilities that are not present in small models but appear suddenly and unpredictably once a model crosses a critical scale threshold. They are typically measured as discrete binary outcomes (pass/fail) rather than continuous metrics, which makes their emergence look like a phase transition.

**How it works:**
```
Model scale (parameters)
   1B:   Cannot do 3-digit multiplication
   3B:   Cannot do 3-digit multiplication
   7B:   Cannot do 3-digit multiplication
  13B:   Cannot do 3-digit multiplication
  30B:   Cannot do 3-digit multiplication
  70B:   Suddenly achieves 95% accuracy
```

**Key examples:**
- **Chain-of-thought reasoning:** Breaking a problem into steps and solving each one
- **Arithmetic:** Accurate multi-digit addition, subtraction, and multiplication
- **Translation:** Fluent translation between language pairs not seen in bilingual training data
- **In-context learning:** The ability itself emerges — small models cannot learn from prompt examples at all

**Why this matters:**
- Small models cannot be used to safety-test large models
- Product roadmaps based on smooth scaling assumptions fail
- Capabilities may appear before we have alignment techniques to control them

---

### Real-Life Analogy

Water freezing into ice.
- **Small model (liquid water):** At 4 degrees Celsius, water is still liquid. Lower it to 3, 2, 1 degrees — still liquid. The system appears continuous. You might predict it will never solidify.
- **Critical threshold:** At exactly 0 degrees, water suddenly becomes ice. The change is discontinuous. Nothing in the 1-degree behavior predicted the phase transition.
- **Large model (ice):** Once frozen, the material has entirely new properties — it holds shape, it cracks rather than flows, it floats. These properties were not "slightly present" at 0.5 degrees. They emerged at the threshold.
- **The forecasting failure:** If you only tested water at 10, 5, and 2 degrees, you would conclude water is always liquid. Emergent capabilities require testing across the full scale range because extrapolation from small models fails.

---

### Tiny Numeric Example

**Task: 3-digit multiplication (e.g., 123 x 456)**

**Accuracy by model size:**
```
Parameters    Accuracy
   100M          0%
   500M          0%
   1B            0%
   3B            0%
   7B            2%
  13B            5%
  30B           15%
  70B           92%   ← sudden jump
 100B           96%
```

**Perplexity (continuous metric) over the same range:**
```
Parameters    Perplexity
   100M        28.5
   500M        22.1
   1B          18.3
   3B          14.7
   7B          12.2
  13B          10.8
  30B           9.1
  70B           7.8
 100B           7.2
```

**The paradox:** Perplexity improves smoothly and predictably. Anyone looking at perplexity would draw a nice curve and predict 70B perplexity to be around 8.5. They would be right. But if they used that same curve to predict multiplication accuracy, they would predict 70B to score around 20%. Instead it scores 92%. The smooth metric does not predict the discrete jump.

---

### Common Confusion

1. **"Emergent capabilities are just better versions of small-model abilities."** No. They are qualitatively new. A small model cannot do chain-of-thought reasoning at all, even poorly. A large model does it fluently. It is not a difference of degree; it is a difference of kind.

2. **"Emergence is an illusion caused by using bad metrics."** This is partially true but misses the point. While binary pass/fail metrics make emergence look sharper, the underlying phenomenon is real. Even on continuous metrics, certain task-specific capabilities show sharp transitions that are not predicted by loss curves.

3. **"If we train longer, small models will develop the same capabilities."** Generally false. Emergent capabilities are linked to scale (parameters + data + compute), not just training time. A 1B model trained for 10x longer does not develop chain-of-thought reasoning. The capability is in the architecture-scale interaction.

4. **"Emergence means the model is conscious or understanding."** No. Emergence is a statistical phenomenon in high-dimensional function approximation. The model is still next-token prediction. The sudden capability comes from the combinatorial explosion of representable functions at scale, not from sentience.

5. **"All capabilities emerge."** False. Most capabilities improve smoothly with scale. Reading comprehension, basic syntax, and common-sense facts all get gradually better. Emergence is the exception, not the rule, but it is the exception that matters most for capabilities evaluation.

6. **"We can predict emergent capabilities from first principles."** Not yet. There is no formula that says "at N parameters, capability X will appear." Researchers can sometimes predict after seeing a few data points, but ex-ante prediction from small models alone remains unreliable.

7. **"Emergent capabilities only appear in language models."** False. Emergence has been observed in vision models (e.g., zero-shot classification suddenly working), protein folding models, and robotics policies. It is a general deep-learning phenomenon at scale.

---

### Where It Is Used in Our Code

`src/phase135/phase135_icl_concepts.py` — We simulate emergent capabilities by defining a task that requires a minimum model capacity. Below a critical hidden dimension, accuracy is near zero. Above it, accuracy jumps sharply. This reproduces the phase-transition behavior seen in real models.

`src/phase135/phase135_icl_colab.py` — We evaluate `meta-llama/Llama-3.2-3B-Instruct` on a task where smaller models (if available) would fail completely, while the 3B model succeeds when given enough in-context examples. The experiment demonstrates that ICL itself is an emergent capability.
