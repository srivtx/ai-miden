## What Is Domain Adaptation?

---

### The Problem

A general-purpose language model knows a little about everything — medicine, law, coding, cooking, history. But when a hospital tries to use it for radiology reports, the model speaks like a Wikipedia article instead of a doctor. It uses wrong terminology, misses clinical nuances, and recommends treatments that are outdated. The model was trained on the broad internet, not on the specific distribution of medical text. How do you make it speak the language of a specific domain?

---

### Definition

**Domain Adaptation** is the process of adapting a pre-trained model to a specialized field (medical, legal, coding, finance) so it performs better on domain-specific tasks while retaining general knowledge. It bridges the gap between the general data the model was originally trained on and the narrow, technical data it needs to handle in production.

**How it works:**
```
Base model: trained on 10T tokens of general internet text
Domain corpus: 1B tokens of legal contracts, case law, and court filings
Domain-adapted model: base + further training on domain corpus
Result: model speaks like a lawyer, not like a blogger
```

**Key techniques:**
- **Continual pre-training:** further pre-training on unlabeled domain text
- **Task-specific fine-tuning:** supervised training on labeled domain tasks
- **Adapter layers:** small trainable modules that shift behavior without changing base weights

**Why this matters:**
- A general model scores 45% on the medical board exam; a domain-adapted one scores 82%
- Legal document review requires understanding jurisdiction-specific language
- Code completion needs to know your company's internal API conventions

---

### Real-Life Analogy

A general practitioner vs. a specialist doctor.
- **Base model:** A family doctor who knows a little about every body system. They can treat a cold, set a bone, and recognize basic symptoms. But if you have a rare neurological condition, they will refer you out.
- **Domain-adapted model:** A neurologist who spent ten extra years reading only neurology journals, attending brain conferences, and examining thousands of MRI scans. They still remember general medicine, but they can diagnose a complex seizure disorder in minutes.
- **The trade-off:** The neurologist might be slightly worse at treating skin rashes than the family doctor because their focus shifted. Domain adaptation is choosing specialization over generalism.

---

### Tiny Numeric Example

**Base model logits for the prompt "The patient presented with dyspnea and...":**
```
Next-token probabilities:
  "chest"    → 0.12
  "a"        → 0.10
  "severe"   → 0.08
  "was"      → 0.07
```

**After domain adaptation on 100K medical case notes:**
```
Next-token probabilities:
  "tachypnea" → 0.18   (medical term, more likely)
  "chest"     → 0.14
  "acute"     → 0.11
  "was"       → 0.03   (general word, less likely)
```

**Accuracy comparison on a 100-question medical quiz:**
```
Base model:          45/100 correct (45%)
Domain-adapted:      78/100 correct (78%)
General trivia quiz:
  Base model:        82/100 correct (82%)
  Domain-adapted:    79/100 correct (79%)  ← slight drop
```

**The shift:** The model redistributed its probability mass from general words toward domain-specific terms. It gained 33 points on medical tasks and lost 3 points on general knowledge.

---

### Common Confusion

1. **"Domain adaptation is the same as fine-tuning."** Fine-tuning is the mechanism. Domain adaptation is the goal — shifting the model's distribution toward a specific field. You can fine-tune without domain adaptation (e.g., teaching a general model to be more helpful).

2. **"Domain adaptation makes the model forget everything else."** Only if you over-train. With proper learning rates, early stopping, and regularization, the model retains general knowledge while gaining domain expertise.

3. **"You need millions of domain examples."** Not necessarily. Even 10,000 high-quality medical notes can shift a model significantly. Quality and diversity matter more than raw count.

4. **"Domain adaptation fixes hallucinations."** No. It reduces hallucinations *in the domain* because the model knows the vocabulary better. But it can still make up facts. You still need retrieval and verification.

5. **"Continual pre-training and fine-tuning are the same thing."** Continual pre-training uses unlabeled text and teaches the model domain language. Fine-tuning uses labeled task data and teaches the model what to do. They are sequential steps, not alternatives.

6. **"One domain-adapted model works for every subdomain."** A model adapted on general medical text will still struggle with radiology-specific reports. Sub-specialization often requires further adaptation.

7. **"Domain adaptation only applies to text."** False. Vision models are adapted to medical imaging (X-rays, CT scans), satellite imagery, and industrial defect detection using the same principles.

---

### Where It Is Used in Our Code

`src/phase70/phase70_domain_adaptation.py` — We simulate a base model and domain-specific data, then show how fine-tuning shifts the model's output distribution toward the domain. We compare base vs. domain-adapted accuracy on domain and general tasks, and we plot the accuracy trade-off curve.
