## What Is Continual Pretraining?

---

### The Problem

You deploy a large language model in January. It knows everything up to its training cutoff in mid-2023. By March, a new drug is approved, a new programming framework is released, and a geopolitical border shifts. The model still answers based on 2023 data. It prescribes the old drug, recommends the deprecated framework, and describes the old border. Fine-tuning on the new data helps, but after a few updates the model starts forgetting the old drug, the old framework, and the old border. Retraining from scratch costs millions of dollars and weeks of GPU time. How do you teach a model new knowledge without erasing the old?

---

### Definition

**Continual Pretraining** is the process of updating a pretrained model on new, unlabeled data over time without retraining from scratch. It aims to absorb new facts, language, and concepts while minimizing **catastrophic forgetting** — the tendency of neural networks to overwrite old knowledge when learning new tasks.

**How it works:**
```
Base model: trained on 10T tokens up to June 2023

Month 1 new corpus: 50B tokens of post-June 2023 web crawl
  Naive continual training: train on new corpus only
    Result: model knows 2024 politics but forgets 2020 politics

Month 2 new corpus: 50B tokens of medical journals
  With replay buffer: mix 20% old data + 80% new data
    Result: model learns medical terms and retains general knowledge
```

**Key techniques:**
- **Replay buffers:** mixing a sample of old training data with new data to prevent forgetting
- **Elastic weight consolidation (EWC):** penalizing changes to weights that were important for old tasks
- **Low-rank adapters (LoRA):** updating only small adapter matrices instead of full weights, preserving the base
- **Progressive networks:** adding new capacity (layers or parameters) for each new time period

**Why this matters:**
- The world changes daily; frozen models become stale within months
- Retraining from scratch is economically impossible for most organizations
- Production systems need models that learn continuously without human intervention

---

### Real-Life Analogy

A surgeon continuing medical education.
- **Base model:** A surgeon who graduated from medical school in 2010. They know anatomy, basic procedures, and classic pharmacology. They are competent for routine cases.
- **Naive fine-tuning:** The surgeon attends a weekend seminar on robotic surgery and nothing else. They become excellent with the robot but start forgetting how to perform open-heart surgery because those neural pathways were overwritten by robot controls. They gained a specialty and lost a foundation.
- **Continual pretraining with replay:** The surgeon reads new robotic-surgery journals every month but also reviews one classic anatomy paper per week. They master the robot and retain open-heart skills. The review acts as a replay buffer, reinforcing old knowledge while new knowledge is encoded.
- **The trade-off:** Without replay, the surgeon is a robot specialist who cannot handle emergencies. With replay, the surgeon is a generalist who also knows the latest techniques.

---

### Tiny Numeric Example

**A model evaluated on three tasks over time:**
```
Task A: 2020 world geography    (old knowledge)
Task B: 2023 programming APIs   (old knowledge)
Task C: 2024 medical guidelines (new knowledge)
```

**Naive fine-tuning on new data only:**
```
After training on Task C:
  Task A accuracy: 88% -> 52%  (catastrophic forgetting)
  Task B accuracy: 85% -> 48%  (catastrophic forgetting)
  Task C accuracy: 30% -> 91%  (new knowledge learned)
```

**Continual pretraining with a 25% replay buffer:**
```
After training on Task C with 25% old data mixed in:
  Task A accuracy: 88% -> 79%  (some forgetting, but tolerable)
  Task B accuracy: 85% -> 76%  (some forgetting, but tolerable)
  Task C accuracy: 30% -> 87%  (new knowledge learned, slightly less)
```

**Accuracy on all three tasks combined:**
```
Base model (frozen):           68% average
Naive fine-tuning:             64% average  <- worse than frozen
Continual with replay:         81% average  <- improvement without collapse
```

**The shift:** Continual pretraining with replay redistributes learning across old and new data. It sacrifices a small amount of new-task peak performance to preserve the foundation.

---

### Common Confusion

1. **"Continual pretraining is the same as fine-tuning."** Fine-tuning teaches a model a specific task. Continual pretraining teaches it new general knowledge. The data is unlabeled and broad, not labeled and narrow.

2. **"A replay buffer is just training on old data again."** It is not full retraining. A small random sample (5-25%) of old data is enough to anchor old knowledge. The buffer is curated for diversity, not volume.

3. **"Continual pretraining prevents all forgetting."** It does not. Some forgetting is inevitable. The goal is to reduce it from catastrophic (50+ point drop) to manageable (5-15 point drop).

4. **"Lower learning rates eliminate forgetting."** Lower rates help, but if you train long enough on new data, old knowledge still fades. You need lower rates plus replay or regularization.

5. **"This only matters for large language models."** Any neural system deployed in production faces this: recommendation engines forget old user preferences, vision models forget old object classes, fraud detectors forget old scam patterns.

6. **"You can continually pretrain forever without consequences."** False. Error accumulates. A model trained on January data, then February data, then March data compounds extraction noise and bias. Periodic full retraining is still necessary.

7. **"Adapters solve continual pretraining completely."** Adapters reduce forgetting by freezing base weights, but they have limited capacity. After many updates, adapter interference occurs and performance saturates.

---

### Where It Is Used in Our Code

`src/phase146/phase146_continual_concepts.py` — We simulate a sequence of three classification tasks, show how naive training on each new task destroys accuracy on old tasks, and demonstrate that a replay buffer preserves a much higher fraction of old knowledge.

`src/phase146/phase146_continual_colab.py` — We evaluate `Qwen/Qwen2.5-3B-Instruct` on old facts, fine-tune on new domain data, show catastrophic forgetting on old facts, and then apply a replay buffer to reduce forgetting while still learning the new domain.

(End of file)
