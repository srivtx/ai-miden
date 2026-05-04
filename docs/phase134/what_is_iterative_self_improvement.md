## What Is Iterative Self-Improvement?

---

### The Problem

One round of self-critique and revision helps, but does the improvement compound? If you let a model critique and revise itself five times in a row, will it become five times better, or will it hit a wall? Understanding the dynamics of repeated self-improvement is essential for estimating the ceiling of unsupervised alignment and for knowing when to stop burning GPU hours on a loop that has plateaued.

---

### Definition

**Iterative Self-Improvement** is the repetition of the generate-critique-revise-train loop for multiple rounds. Each round uses the model produced by the previous round as both the generator and the critic. The hope is that each cycle unlocks a slightly better version of the model, but in practice the gains diminish and eventually stop.

**How it works:**
```
Round 0: Base model M0
Round 1: M0 generates → critiques → revises → train → M1
Round 2: M1 generates → critiques → revises → train → M2
Round 3: M2 generates → critiques → revises → train → M3
...
Round N: Mn-1 generates → critiques → revises → train → Mn
```

**Convergence properties:**
- **Early rounds:** Large gains. The base model has obvious flaws that are easy to critique.
- **Middle rounds:** Diminishing returns. The model fixes low-hanging fruit and starts addressing subtle issues.
- **Late rounds:** Plateau. The model's critique ability equals its generation ability. It cannot find flaws that are beyond its own reasoning capacity.
- **Divergence risk:** If the training data becomes too homogeneous (all revisions look the same), the model may collapse into a narrow mode.

**When it plateaus:**
- The critique finds fewer and fewer genuine flaws per round
- The revised outputs become statistically indistinguishable from the generated outputs
- Training loss stops decreasing
- External evaluation scores flatten

---

### Real-Life Analogy

Practicing a musical instrument.
- **Week 1:** You learn the scales. Your fingers are clumsy. Every practice session yields massive improvement because the mistakes are obvious. This is round 1 of self-improvement.
- **Month 6:** You can play the piece cleanly, but your timing is slightly off and your dynamics are flat. You need a metronome and a recording of yourself to spot the flaws. Improvement is slower but still real. This is round 3.
- **Year 5:** You are a professional. Your teacher (critic) struggles to find errors. You spend months polishing a single phrase. The gains are microscopic. This is round 6.
- **The plateau:** After twenty years, you cannot become a better violinist by practicing alone. You need external input: a new genre, a new teacher, or a physiological breakthrough. The self-improvement loop has reached its ceiling.

---

### Tiny Numeric Example

**Quality score (0 to 1) across 5 rounds:**
```
Round 0 (base):     0.50
Round 1:            0.71   (+0.21)
Round 2:            0.84   (+0.13)
Round 3:            0.90   (+0.06)
Round 4:            0.93   (+0.03)
Round 5:            0.94   (+0.01)
```

**Flaws found per response:**
```
Round 0 critique:   3.8 flaws per response
Round 1 critique:   2.1 flaws per response
Round 2 critique:   1.0 flaws per response
Round 3 critique:   0.5 flaws per response
Round 4 critique:   0.2 flaws per response
Round 5 critique:   0.1 flaws per response
```

**Training loss on revised data:**
```
Round 1 loss:       1.85
Round 2 loss:       1.42
Round 3 loss:       1.21
Round 4 loss:       1.15
Round 5 loss:       1.13   (flat)
```

**The shift:** The first two rounds delivered 68% of the total improvement. By round 5, the model was polishing marginal details at significant compute cost. The optimal stopping point was round 3 or 4.

---

### Common Confusion

1. **"More rounds always means a better model."** No. After the plateau, additional rounds waste compute and can degrade the model by overfitting to its own revision style. The revision distribution becomes the training distribution, and diversity collapses.

2. **"Iterative self-improvement is guaranteed to converge."** It converges to a local maximum defined by the model's own capabilities. It does not converge to a global optimum or to human-level performance. It converges to the best version of itself that it can recognize.

3. **"You should use the same prompts every round."** Using the same prompts is fine for measuring convergence, but in practice you should expand the prompt set each round to prevent overfitting. New prompts expose new failure modes.

4. **"The plateau means the model is perfect."** The plateau means the model is as good as its own critic. It can still fail catastrophically on tasks it cannot evaluate. A model that cannot do advanced calculus cannot critique its own calculus errors, so the plateau hides blind spots.

5. **"Iterative self-improvement replaces pre-training."** Absolutely not. Pre-training gives the model knowledge. Self-improvement only organizes and surfaces that knowledge more reliably. You cannot self-improve a model into knowing facts it never saw during pre-training.

6. **"All model sizes benefit equally from many rounds."** Larger models benefit more from additional rounds because their stronger critique ability pushes the plateau higher. Small models plateau early because their critiques are shallow.

7. **"You need full fine-tuning between rounds."** LoRA or adapter-based fine-tuning works fine between rounds and is far more efficient. Full fine-tuning is unnecessary and risks catastrophic forgetting.

---

### Where It Is Used in Our Code

`src/phase134/phase134_self_alignment_concepts.py` — We simulate five rounds of iterative self-improvement in NumPy. We plot quality score, flaws found, and training loss per round to visualize the characteristic rapid-then-flat improvement curve.

`src/phase134/phase134_self_alignment_colab.py` — We run three rounds of real self-alignment on Qwen2.5-3B-Instruct. We measure response quality after each round, plot the per-round improvement, and compare sample outputs to show when the model stops getting noticeably better.
