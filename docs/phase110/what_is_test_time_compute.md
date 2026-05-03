## What Is Test-Time Compute?

---

### The Problem

Scaling model size -- parameters, training data, compute -- is expensive and hits diminishing returns. Pre-training a 100B parameter model might cost tens of millions of dollars for a single-digit percentage gain. Yet at inference time, we often leave compute on the table, generating a single answer and hoping it is correct. A student who writes the first answer that comes to mind performs worse than one who checks their work. Can we trade inference-time computation for accuracy without making the model bigger?

---

### Definition

**Test-Time Compute** refers to spending additional computation during inference to improve output quality. Instead of generating a single greedy or sampled output, the model uses extra compute to search, verify, refine, or reason through multiple candidate solutions before returning an answer.

**How it works:**
```
Prompt → Generate 20 candidate answers → Verifier scores each
Select highest-scoring answer → Return
Alternative: Generate → Critique → Revise → Repeat
Result: better answers from the same model by using more inference compute
```

**Key techniques:**
- **Best-of-N sampling:** generate N outputs, pick the best via a verifier or reward model
- **Refinement loops:** iteratively critique and revise a single output over multiple passes
- **Search algorithms:** beam search, tree-of-thoughts, and Monte Carlo Tree Search over reasoning steps

**Why this matters:**
- It decouples model quality from model size, offering a path to better results without retraining
- It enables dynamic compute allocation: spend more computation on hard problems, less on easy ones
- It is the foundation of reasoning systems that use chain-of-thought search to solve complex problems

---

### Real-Life Analogy

Test-time compute is like a student taking a math test. A rushed student writes the first answer that comes to mind and moves on. A careful student spends extra time checking their work, trying alternate methods, and verifying the result. Both students have the same knowledge stored in their heads, but the careful one uses more time during the test to produce a better answer.

The trade-off is that the careful student finishes fewer questions in the same amount of time. Test-time compute improves quality but increases latency and cost per query proportionally to the extra compute used. A system that generates 128 candidates takes 128 times longer than a single-sample system. The benefit is accuracy; the cost is throughput.

---

### Tiny Numeric Example

**Model quality = 1.0, true value = 5.0**

**Baseline (single sample, 1000 trials):**
```
Mean absolute error: 0.892
```

**Best-of-N with strong verifier (verifier quality = 2.0):**
```
N=1:   error = 0.892
N=4:   error = 0.512
N=16:  error = 0.278
N=64:  error = 0.145
N=128: error = 0.103
```

**Best-of-N with weak verifier (verifier quality = 0.5):**
```
N=4:   error = 0.743
N=16:  error = 0.621
N=64:  error = 0.504
N=128: error = 0.491
```

**Compute cost is proportional to N.**
```
Strong verifier at N=128: 8.7x error reduction
Weak verifier at N=128:   1.8x error reduction
```

A strong verifier turns extra compute into meaningful gains. A weak verifier wastes compute because it cannot reliably distinguish good outputs from bad ones.

---

### Common Confusion

1. **"Test-time compute is the same as training longer."** Training longer updates model weights. Test-time compute only changes inference behavior without modifying weights or requiring any gradient computation.

2. **"More samples always improve accuracy."** Without a good verifier or scoring mechanism, increasing N yields diminishing returns because low-quality samples dilute the pool and the verifier cannot identify the best one.

3. **"Test-time compute is free."** It improves quality but increases latency and cost per query proportionally to the extra compute used; it is a trade-off, not a free lunch.

4. **"It only works for reasoning tasks."** It helps any task with a verifiable answer, including code generation, math, multiple-choice questions, and creative writing with a quality scorer.

5. **"Best-of-N requires training a separate verifier from scratch."** The verifier can be the same model with a different prompt, a smaller reward model, or even a simple rule-based checker or unit-test executor.

6. **"Test-time compute makes small models competitive with large ones."** It narrows the gap but does not close it; a small model with search still lags behind a large model with the same search strategy.

7. **"Test-time compute guarantees correctness."** It improves expected quality but can still fail on adversarial examples or when the verifier is systematically biased toward certain error patterns.

---

### Where It Is Used in Our Code

`src/phase110/phase110_test_time_compute.py` — We simulate a model that samples answers around a true value with noise inversely proportional to model quality. We implement a verifier that scores outputs with noise inversely proportional to verifier quality, then run best-of-N for N in [1, 2, 4, 8, 16, 32, 64, 128]. We compare strong and weak verifiers, plot accuracy versus N, and plot error reduction versus compute cost, saving both figures to `src/phase110/`.
