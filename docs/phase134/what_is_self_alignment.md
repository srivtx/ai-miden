## What Is Self-Alignment?

---

### The Problem

Reinforcement Learning from Human Feedback (RLHF) requires thousands of expensive human labelers to rank model outputs. Constitutional AI reduces the human load by using a set of principles, but it still relies on a separate critic model trained with human data. What if you have no human labels at all, no pre-trained reward model, and no external judge? Can a model look in the mirror, spot its own flaws, fix them, and teach itself to be better?

---

### Definition

**Self-Alignment** is a training paradigm where a language model improves its own behavior without any human-provided labels after an initial setup. The model generates outputs, critiques them, revises them based on the critique, and then trains on the revised outputs. Repeating this loop causes the model to align with implicit quality standards it discovers through self-reflection.

**How it works:**
```
Round 1:
  Generate: model answers 100 prompts
  Critique: model reads each answer and lists what is wrong
  Revise: model writes improved answers using the critiques
  Train: model fine-tunes on the revised answers

Round 2:
  Generate: the improved model answers the same 100 prompts
  Critique: it finds new flaws that the first-round model missed
  Revise: it writes even better answers
  Train: fine-tune again

Result after N rounds: model quality increases, then plateaus
```

**Key components:**
- **Self-critique:** the model analyzes its own output for errors, bias, or incoherence
- **Self-revision:** the model produces a corrected version based on its own critique
- **Self-training:** the model fine-tunes on its revised data, absorbing the improvements

**Why this matters:**
- It removes the bottleneck of human labeling for alignment
- It enables recursive improvement: each round builds on the last
- It works for domains where human expertise is scarce (rare diseases, obscure programming languages)
- It proves that a model's internal knowledge can be unlocked by simply asking it to criticize itself

---

### Real-Life Analogy

A novelist editing their own manuscript across multiple drafts.
- **First draft:** The writer produces a rough manuscript. It has plot holes, flat characters, and grammatical errors. This is the initial model generation.
- **Self-critique:** The writer sets the manuscript aside for a week, then reads it with fresh eyes. They annotate every problem: "Chapter 3 contradicts Chapter 1," "This dialogue feels forced." This is the critique step.
- **Revision:** The writer rewrites sections based on their own annotations. No external editor touched the page. This is the revision step.
- **Training:** The act of rewriting teaches the writer patterns. In the next book, they avoid the same mistakes. This is the fine-tuning step.
- **The limit:** After ten drafts, the novel stops improving because the writer has reached the ceiling of their own skill. They cannot critique what they do not understand. This is the plateau.

---

### Tiny Numeric Example

**A toy model generates responses scored from 0 to 1, where 1 is perfect:**
```
Round 0 (baseline, no self-alignment):
  Mean quality score: 0.52

Round 1:
  Generate 100 responses → mean score 0.52
  Critique finds average 3.2 flaws per response
  Revise → mean score rises to 0.71
  Train on revised data → model improves

Round 2:
  Generate 100 responses → mean score 0.71
  Critique finds average 1.8 flaws per response
  Revise → mean score rises to 0.84
  Train on revised data → model improves further

Round 3:
  Generate 100 responses → mean score 0.84
  Critique finds average 0.9 flaws per response
  Revise → mean score rises to 0.89
  Train on revised data → model improves slightly

Round 4:
  Generate 100 responses → mean score 0.89
  Critique finds average 0.4 flaws per response
  Revise → mean score rises to 0.91
  Train on revised data → negligible improvement
```

**The shift:** The model gained 39 points in four rounds without a single human label. The improvement rate slowed each round because the model approached the limits of what it could critique and revise.

---

### Common Confusion

1. **"Self-alignment means the model trains itself from scratch."** No. The model starts from a pre-trained checkpoint. Self-alignment is the alignment phase, not pre-training. It assumes the model already possesses general knowledge and language ability.

2. **"Self-alignment produces an infinitely improving model."** It does not. The model plateaus when its critique ability matches its generation ability. It cannot fix errors it cannot detect, and it cannot detect errors beyond its own understanding.

3. **"Self-alignment is the same as Constitutional AI."** Constitutional AI uses a fixed list of principles and often still relies on a feedback model trained on human preferences. Self-alignment uses no principles list and no human feedback model. The model generates its own standards dynamically.

4. **"If the model critiques itself, it will just praise everything."** In practice, language models are surprisingly good at finding genuine flaws when explicitly prompted with "What is wrong with this answer?" The key is the prompt framing: asking for criticism rather than evaluation.

5. **"Self-alignment only works for large models."** While larger models have stronger critique abilities, small models (3B-7B) can still benefit from one or two rounds of self-alignment. The gains are smaller but measurable.

6. **"Training on revised outputs causes mode collapse."** There is a risk. If the model's revisions are too similar, the distribution collapses and diversity drops. The fix is to use a diverse prompt set and to mix original and revised data during training.

7. **"Self-alignment eliminates the need for safety monitoring."** Absolutely not. A model aligned to its own standards might still produce harmful content if its internal standards are flawed or biased. External evaluation and red-teaming remain essential.

---

### Where It Is Used in Our Code

`src/phase134/phase134_self_alignment_concepts.py` — We simulate iterative self-improvement in NumPy. A toy model generates vectors, critiques them by comparing to a hidden target, revises them, and updates its weights. We track quality over rounds and demonstrate the inevitable plateau.

`src/phase134/phase134_self_alignment_colab.py` — We use a real Qwen2.5-3B-Instruct model. It generates 100 responses, critiques each one, revises them, and we fine-tune the model on the revised data for 50 steps. We repeat for three rounds and plot quality scores and training loss.
