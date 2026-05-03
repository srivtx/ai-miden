## What Is a Query Strategy?

---

### The Problem

You have a pool of 10,000 unlabeled examples and budget to label 100. Uncertainty sampling picks the 100 most uncertain examples. But what if all 100 are nearly identical points near the same decision boundary? You would learn a lot about that tiny region and nothing about the rest of the space. How do you balance uncertainty with diversity?

---

### Definition

A **query strategy** is the algorithm that decides which unlabeled examples to label next in active learning. It balances informativeness (how much the model would learn) with representativeness (how well the selection covers the data distribution).

**Common query strategies:**

**1. Uncertainty sampling:**
```
Score = uncertainty(x)
```
- Picks the most uncertain examples
- Fast but can be redundant

**2. Query-by-committee:**
```
Score = disagreement between multiple models
```
- Train an ensemble of models
- Pick examples where models disagree most
- Captures different "opinions" about the data

**3. Expected model change:**
```
Score = how much would the model parameters change if we labeled this example?
```
- Pick examples that would most change the model
- Theoretically optimal but computationally expensive

**4. Density-weighted:**
```
Score = uncertainty(x) × density(x)
```
- Weight uncertainty by how representative the example is
- Avoids outliers that are uncertain but irrelevant

**5. Diversity sampling:**
```
Score = uncertainty(x) + diversity_bonus(x, already_selected)
```
- Use clustering or distance to ensure selected examples are spread out
- Prevents redundant labeling of similar uncertain examples

**Why this matters:**
- A bad query strategy wastes labels on redundant or uninformative examples
- A good query strategy can reduce labeling costs by 50-90%
- The choice of strategy depends on the problem, model, and budget

---

### Real-Life Analogy

A traveler planning a trip to explore a new country.
- **Uncertainty sampling:** Visit the most confusing cities first. But all confusing cities might be in the same region (e.g., all in the north). You never see the south.
- **Diversity sampling:** Visit one confusing city in the north, one in the south, one in the east, one in the west. You learn about the whole country.
- **Density-weighted:** Skip the confusing city on a remote mountaintop (unrepresentative) and visit the confusing city near the capital (representative).
- **Query-by-committee:** Ask 5 travel guides where to go. If 4 say "visit Paris" and 1 says "visit Lyon," go to Lyon — that is where the experts disagree.

---

### Tiny Numeric Example

**Pool of 6 unlabeled examples:**
```
A: uncertainty=0.9, region=north
B: uncertainty=0.85, region=north
C: uncertainty=0.8, region=north
D: uncertainty=0.7, region=south
E: uncertainty=0.6, region=east
F: uncertainty=0.5, region=west
```

**Uncertainty sampling (pick top 3):**
```
Selected: A, B, C (all in the north!)
Result: Model learns north well, but knows nothing about south/east/west.
```

**Diversity-aware sampling (uncertainty + coverage):**
```
Step 1: Pick A (highest uncertainty, north)
Step 2: Pick D (highest uncertainty in a NEW region, south)
Step 3: Pick E (highest uncertainty in a NEW region, east)

Selected: A, D, E (spread across regions)
Result: Model learns about all regions.
```

Diversity prevents redundancy and ensures broad coverage.

---

### Common Confusion

1. **"Query strategy and sampling method are the same."** No. Sampling is how you select. Query strategy is the criterion for WHAT to select.

2. **"The best query strategy is problem-independent."** No. Image classification benefits from uncertainty. NLP benefits from diversity. Scientific discovery benefits from expected model change.

3. **"Query strategies only work with neural networks."** No. They work with any model that produces predictions or confidence scores.

4. **"More complex query strategies are always better."** Not always. A simple margin sampler often beats a complex diversity-weighted method on small budgets.

5. **"You need a large initial labeled set for active learning."** No. Even 5-10 labeled examples can start the loop. The model just needs enough to make any prediction at all.

---

### Where It Is Used in Our Code

`src/phase62/phase62_active_learning.py` — We compare uncertainty-only sampling vs. diversity-aware sampling, showing how the latter avoids redundant selections and achieves better coverage of the input space.
