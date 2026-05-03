## What Is Technical Writing?

---

## The Problem

Six months ago, a graduate student wrote a training pipeline for a novel architecture. The variables were named `x`, `y`, and `z`. Comments read `# fix` and `# TODO`. There were no docstrings, no README, and no explanation of why certain hyperparameters were chosen. Now the student has graduated, and a new team member must reproduce the results. They spend two weeks reverse-engineering the code, only to discover that `z` was actually a custom learning-rate schedule that the paper failed to mention. The knowledge walked out the door with the original author. Research code without clear documentation decays into unreadable legacy within weeks, and the insights it contained are lost forever.

---

## Definition

**Technical writing** is the practice of communicating complex information clearly to a specific audience. In machine learning, this includes docstrings, README files, inline comments, experiment logs, papers, and blog posts that explain not just what was done, but why it was done and what the reader should do next.

**How it works:**
```
Before:  x = normalize(x)  # fix
After:   normalized_batch = batch_norm(
             input=image_batch,
             eps=1e-5,
             momentum=0.1
         )  # Stabilize activations; momentum chosen to balance
            # responsiveness to distribution shift vs. noise.
```

**Key techniques:**
- **Audience analysis:** writing differently for a collaborator, a reviewer, or a future self.
- **Precision over flair:** using exact terms like "L2-regularized cross-entropy" instead of "fancy loss."
- **Structure and navigation:** organizing documents with clear headings, tables of contents, and cross-references.
- **Runnable examples:** providing minimal reproducible snippets that a reader can execute immediately.

**Why this matters:**
- A well-written methods section can be reproduced; a vague one cannot.
- Clear variable names and comments reduce onboarding time from weeks to days.
- Papers with precise, well-structured writing are cited more often and rejected less frequently.

---

## Real-Life Analogy

Technical writing is like writing the manual for a nuclear power plant. A creative writer might describe the reactor's "majestic hum of boundless energy, a symphony of human ingenuity conquering the atom." That is beautiful, but it is useless to the engineer who needs to know the exact coolant flow rate, the pressure tolerance of the containment vessel, and the sequence for emergency shutdown.

**The trade-off:** Writing the manual takes months. Every valve, sensor, and protocol must be documented, verified, and updated when the plant is modified. But when a cooling pump fails at 2:00 AM, the on-call engineer does not have time to interpret poetry. They need a numbered list: step 1, close valve A; step 2, engage backup pump B; step 3, notify the control room. The manual's precision is what prevents a meltdown. In research, the meltdown is a retracted paper, a wasted GPU budget, or a product that fails in production because no one documented the data preprocessing pipeline.

**The nuance:** Technical writing is not devoid of narrative. A good paper still tells a story: here is the problem, here is why existing solutions fail, here is our insight, here is the evidence. But the narrative serves the facts, not the other way around. Every claim is anchored to an experiment, every experiment to a method, and every method to runnable code.

---

## Tiny Numeric Example

**Impact of documentation quality on research team productivity:**

| Metric | Poor Documentation | Good Documentation | Improvement |
|---|---|---|---|
| New member onboarding | 14 days | 4 days | 3.5x faster |
| Mean time to fix bug | 6 hours | 1.5 hours | 4x faster |
| Paper rejection rate | 65% | 35% | 46% lower |
| Reproduction success by external lab | 20% | 80% | 4x higher |

**Code readability comparison:**
```
Poor:
  def f(x, y):
      z = x @ y + 0.01
      return z / (1 + np.exp(-z))

Good:
  def attention_logits(query, key, temperature=0.01):
      """Compute scaled dot-product attention logits with temperature."""
      raw_scores = np.matmul(query, key.T)
      scaled_scores = raw_scores * temperature
      # Temperature < 1 sharpens the softmax distribution,
      # increasing focus on the most relevant tokens.
      return scaled_scores / (1 + np.exp(-scaled_scores))
```

**Documentation investment:**
```
Time to write code:           8 hours
Time to write good docs:      +3 hours
Time saved by next reader:    ~12 hours
Net return on documentation:  300%
```

**The shift:** Technical writing transforms code from a private mental model into a public asset. The three hours spent on documentation are repaid many times over by faster onboarding, fewer bugs, and higher reproducibility.

---

## Common Confusion

1. **"Technical writing is just adding comments."** Comments are one layer. Technical writing also includes architecture decisions, experiment logs, API documentation, tutorials, and peer-reviewed papers.

2. **"Technical writing is the same as creative blogging."** Blogging prioritizes engagement, narrative, and personality; technical writing prioritizes precision, reproducibility, and actionable instructions. Both are valuable, but they serve different goals.

3. **"Good code is self-documenting."** Code can express what it does, but it cannot express why a learning rate of 0.0003 was chosen, what alternatives were rejected, or what paper inspired the design. That context belongs in writing.

4. **"Documentation is written once and done."** Documentation is a living document. When the code changes, the docs must change. Stale documentation is often worse than no documentation because it misleads.

5. **"More documentation is always better."** Excessive documentation buries the signal in noise. Good technical writing is concise, structured, and targeted to the reader's needs.

6. **"Only junior researchers need to write docs."** Senior researchers write the most important docs: grant proposals, strategic roadmaps, and architectural decision records that shape the entire team's direction.

7. **"Writing well is a talent you are born with."** Writing is a craft that improves with practice, feedback, and revision. Every researcher can learn to write clearly by studying examples and rewriting their own work.

---

## Where It Is Used in Our Code

`src/phase95/phase95_research_communication.py` — We present a research script with cryptic variable names, missing docstrings, and unexplained magic numbers. We then rewrite it using technical writing principles: precise naming, detailed docstrings, inline explanations of design choices, and a README that documents assumptions and reproduction steps. We compare readability scores and plot the time-to-comprehension for both versions.
