## What Is Curriculum Learning?

---

### The Problem

Training a model on the hardest examples from day one is like teaching calculus to a student who has not learned algebra. Gradients are noisy, loss spikes, and convergence stalls. At the same time, training only on easy data forever leaves the model unable to solve complex tasks. How do you schedule difficulty so the model learns efficiently without collapsing?

---

### Definition

**Curriculum learning** is a training strategy that presents examples in order of increasing difficulty. The model first masters simple patterns, building stable representations, before tackling harder data that requires those foundations.

**How it works:**
```
1. Define a difficulty score for each example (e.g., loss under a small model, length, entropy, human label).
2. Start training with only the easiest subset.
3. Gradually increase the difficulty threshold according to a schedule.
4. By the final stage, the model trains on the full distribution.
5. Result: faster convergence and better final performance than random mixing.
```

**Key techniques:**
- **Predetermined schedules:** linear, exponential, or step-function increase in difficulty.
- **Self-paced learning:** the model itself decides when it is ready for harder data based on its own loss or confidence.
- **Catastrophic forgetting guard:** retain a small percentage of easy data throughout training to prevent skill decay.

**Why this matters:**
- Early training on easy data provides low-variance gradients that stabilize the optimization landscape.
- Hard data introduced too late is also harmful; a smooth transition prevents sudden loss spikes.
- Curriculum learning can reduce total training time by 20-30% while improving final accuracy.

---

### Real-Life Analogy

Learning to play the piano. A beginner who starts with a simple scale builds finger memory and rhythm. After a month, they move to short songs with both hands. After six months, they tackle complex concertos. If the beginner started with the concerto, they would develop bad habits to compensate for missing technique, and those habits would be hard to unlearn. Conversely, if they played only scales for a year, they would never learn to read music or perform. The trade-off is pacing: too fast causes injury and frustration; too slow causes boredom and plateau. Curriculum learning finds the pace where each new challenge is just slightly beyond current ability.

---

### Tiny Numeric Example

**Random mixing (all difficulties from step 1):**
```
Step 0-100:   loss oscillates between 2.0 and 4.0
Step 100-200: loss slowly settles to 2.2
Step 200-300: final loss = 1.9
```

**Curriculum learning (easy → medium → hard):**
```
Step 0-100:   easy only, loss drops smoothly from 3.0 to 1.2
Step 100-200: medium added, loss rises to 2.0 then drops to 1.5
Step 200-300: hard added, loss rises to 2.3 then drops to 1.3
Final loss = 1.3
```

**The shift:** Curriculum learning starts lower, experiences controlled rises when difficulty increases, and finishes 32% lower than random mixing. The plateau at step 100 and step 200 is expected; it signals that the model has encountered its next challenge.

---

### Common Confusion

1. **"Curriculum learning is just sorting data by sequence length."** Length is one proxy for difficulty, but true difficulty can be measured by model loss, human ratings, or syntactic complexity.

2. **"It only works for computer vision."** Curriculum learning improves NLP pretraining, code generation, and reinforcement learning alike.

3. **"Easy data causes catastrophic forgetting of hard tasks."** This only happens if hard data is never introduced. A proper curriculum phases hard data in gradually and retains easy data at low weight.

4. **"Curriculum is slower because it delays hard data."** Although hard data arrives later, total convergence time is usually shorter because the model wastes fewer steps on unstable gradients early on.

5. **"Defining difficulty requires expensive human annotation."** Automatic difficulty metrics—such as the loss of a small reference model or the entropy of the target distribution—are cheap and effective.

6. **"Curriculum learning and data mixing are the same thing."** Mixing controls proportions at every step. Curriculum controls the sequence of subsets over time. You can combine both.

7. **"Once hard data is introduced, easy data should be removed."** Retaining a small fraction of easy data prevents forgetting and acts as a regularizer.

---

### Where It Is Used in Our Code

`src/phase117/phase117_mixing_concepts.py` — We simulate three difficulty levels and show how a curriculum schedule (easy first, then medium, then hard) produces smoother loss curves and better final performance than uniform random sampling.
