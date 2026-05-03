## What Is TIES-Merging?

---

### The Problem

When you merge multiple fine-tuned models, most parameter changes are tiny noise. And when two models disagree on the direction of a weight change (one increases it, one decreases it), simple averaging cancels them out or produces a weak compromise. How do you merge only the meaningful changes and resolve conflicts intelligently?

---

### Definition

**TIES-Merging** (Trim, Elect, Sign, and Merge) is a model merging technique that:
1. **Trims** away small-magnitude parameter changes (noise reduction)
2. **Elects** the majority sign for each parameter across models (conflict resolution)
3. **Merges** only the elected changes by averaging them

**Step 1: Trim**
```
For each parameter change δ = W_finetuned - W_base:
    If |δ| < threshold: set δ = 0
```
This removes 50-90% of changes that are just noise from stochastic training.

**Step 2: Elect**
```
For each parameter position:
    Count how many models increased it (+) vs. decreased it (-)
    Keep only changes with the majority sign
    Discard minority-sign changes
```
If 3 out of 4 models increased a weight, the decreasing model's change is discarded.

**Step 3: Merge**
```
Average the remaining (trimmed and elected) changes
Add to base model
```

---

### Real-Life Analogy

Five architects each modified the same building blueprint.
- Most changes are tiny: "Move this outlet 2 inches left" (noise)
- Some changes conflict: Architect A says "Make the window bigger," Architect B says "Make the window smaller"

**TIES-Merging is like a senior architect reviewing all proposals:**
1. **Trim:** Ignore all changes smaller than 6 inches. They are just measurement noise.
2. **Elect:** For each wall, if 4 out of 5 architects agree it should move north, go with north. Ignore the one dissenting architect.
3. **Merge:** Average the magnitudes of the architects who agree. If they said "move 10ft", "move 12ft", "move 8ft", average to 10ft.

The result is a clean blueprint that reflects genuine consensus, not noise or conflict.

---

### Tiny Numeric Example

**Base model parameter:** `W_base[0] = 2.0`

**Changes from 4 fine-tuned models:**
```
Model A: δ_A = +0.01   (tiny noise)
Model B: δ_B = +0.50   (meaningful increase)
Model C: δ_C = -0.40   (meaningful decrease — conflicts with B)
Model D: δ_D = +0.60   (meaningful increase)
```

**Simple average merge:**
```
δ_avg = (0.01 + 0.50 - 0.40 + 0.60) / 4 = 0.71 / 4 = 0.18
W_merged = 2.0 + 0.18 = 2.18
```
The conflict between B/D (+) and C (-) dilutes the signal.

**TIES-Merging:**
1. **Trim** (threshold = 0.05): δ_A = 0.0 (removed as noise)
2. **Elect:** For this parameter, 2 models say + (B, D), 1 says - (C). Majority is +.
   Discard δ_C = -0.40.
3. **Merge:** Average remaining deltas: (0.0 + 0.50 + 0.60) / 3 = 0.37
   `W_merged = 2.0 + 0.37 = 2.37`

**Result:** TIES produces a stronger, cleaner update because it resolved the conflict and removed noise.

---

### Common Confusion

1. **"TIES-Merging is just trimming + averaging."** The "elect" step is crucial. Without sign election, conflicting changes cancel each other out.

2. **"Trimming loses important information."** Surprisingly, experiments show that 50-90% of fine-tuning deltas are noise. DARE (Drop And REscale) randomly drops 90% of deltas and still merges successfully.

3. **"TIES only works for many models."** It works for 2+ models. With 2 models, election is trivial: keep the larger-magnitude sign.

4. **"TIES prevents all task interference."** It reduces interference but cannot eliminate it entirely. If two tasks genuinely need opposite changes to the same parameter, one must lose.

5. **"TIES requires knowing the base model."** Yes. TIES computes deltas relative to the base model. Unlike simple averaging of fine-tuned weights, you need access to the original pre-trained weights.

---

### Where It Is Used in Our Code

`src/phase43/phase43_model_merging.py` — The `ties_merge()` function implements all three steps: trimming small deltas, electing the majority sign per parameter, and averaging the elected changes. We compare TIES against simple averaging and task arithmetic.
