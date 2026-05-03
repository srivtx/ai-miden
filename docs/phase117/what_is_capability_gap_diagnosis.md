## What Is Capability Gap Diagnosis?

---

### The Problem

A model scores 85% on general reasoning but fails at 40% on code debugging. The overall benchmark looks good, but a critical skill is broken. Blindly adding more pretraining data is expensive and might not fix the problem. How do you pinpoint exactly which data source is missing so you can target your collection budget?

---

### Definition

**Capability gap diagnosis** is the process of decomposing model performance into fine-grained skills, identifying which skills are underperforming, and tracing those deficits back to missing or underweighted data sources.

**How it works:**
```
1. Evaluate the model on a skill-specific benchmark (e.g., math, code, dialogue, reasoning).
2. Identify skills with large gaps versus human performance or a reference model.
3. Ablate data sources: train small models with and without specific domains.
4. Correlate data source presence with skill scores.
5. Collect or upsample the data sources that close the gap.
```

**Key techniques:**
- **Skill taxonomy evaluation:** break aggregate benchmarks into sub-skills (algebra, geometry, python, javascript, empathy, instruction following).
- **Data ablation studies:** measure the marginal contribution of each pretraining domain by removing it and observing score changes.
- **Targeted data collection:** after identifying the gap, curate high-quality data specifically for that skill.

**Why this matters:**
- A 1B model trained on the right 10M tokens can outperform a 7B model trained on generic data for a specific skill.
- Data collection is expensive; diagnosis ensures you collect the right data, not just more data.
- It reveals hidden correlations: improving reading comprehension data can unexpectedly boost coding performance because both require long-context reasoning.

---

### Real-Life Analogy

A restaurant receives mixed reviews. "The food is bad" is too vague to act on. A smart manager breaks reviews into categories: service, temperature, seasoning, presentation. They find that seasoning scores are low while service scores are high. Instead of retraining the entire kitchen staff, they investigate the spice supplier and discover a quality drop in the pepper shipment. They switch suppliers and seasoning scores recover within a week. Capability gap diagnosis is the same decomposition: instead of saying "the model is bad at code," you determine whether the gap is in syntax, debugging, algorithm design, or API knowledge. Then you trace it to the missing data—perhaps the pretraining corpus lacked stack traces and bug fixes.

---

### Tiny Numeric Example

**Model scores on three skills:**
```
Skill          | Score | Target | Gap
---------------|-------|--------|-----
Reasoning      | 45%   | 70%    | -25
Coding         | 80%   | 85%    | -5
Translation    | 60%   | 75%    | -15
```

**Data source ablation (small proxy model):**
```
Source removed | Reasoning drop | Coding drop | Translation drop
---------------|----------------|-------------|-----------------
Web (70%)      | -5             | -2          | -3
Code (20%)     | -2             | -50         | -1
Books (10%)    | -18            | -4          | -12
```

**Diagnosis:** Books are the critical driver of reasoning and translation. The gap is not total volume; it is the composition.

**Targeted fix:** Add 5B tokens of high-quality books and technical manuals.

**Result after retraining:**
```
Reasoning      | 62%   | +17
Translation    | 71%   | +11
Coding         | 81%   | +1   (unchanged, as expected)
```

---

### Common Confusion

1. **"Capability gaps are always fixed by more pretraining compute."** Often the gap is caused by missing data diversity, not insufficient steps. More compute on the wrong data deepens the gap.

2. **"A single aggregate benchmark score tells you the gap."** An overall score of 70% can hide a 95% in easy tasks and a 30% in hard tasks. You must disaggregate.

3. **"Data ablation means removing data from the production model."** Ablation studies train small, cheap models on subsets. They do not touch the production checkpoint.

4. **"Diagnosis is only useful after training finishes."** The best teams diagnose continuously during pretraining, adjusting the data mixture on the fly.

5. **"Targeted data collection is guaranteed to be high quality."** If you over-sample a narrow domain to close a gap, you can introduce bias or overfit the benchmark.

6. **"Capability gaps are independent."** Improving reasoning data often helps coding because both require structured logic. Gaps can be coupled.

7. **"Gap diagnosis requires teams of human experts."** Automated skill taxonomies and benchmark suites (e.g., MMLU categories, HumanEval) make diagnosis scalable without manual expert review for every skill.

---

### Where It Is Used in Our Code

`src/phase117/phase117_mixing_concepts.py` — We simulate three skills and three data sources, then show how ablating each source reveals which skill depends on which domain. We plot capability gaps before and after a targeted reweighting to demonstrate diagnosis-driven data collection.
