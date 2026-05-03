## What Is Continual Pre-training?

---

### The Problem

You have a base model trained on the entire internet. It knows English grammar, pop culture, and basic science. But when you feed it a legal brief, it stumbles over terms like "res ipsa loquitur" and "promissory estoppel." The vocabulary, style, and factual distribution of legal text are completely different from Reddit threads and news articles. Fine-tuning on a few labeled tasks cannot teach the model the *language* of the domain — it only teaches it the *task*. How do you make the model absorb the raw patterns of a new domain before you ever give it labeled tasks?

---

### Definition

**Continual Pre-training** is the process of further pre-training a base model on a large corpus of unlabeled domain-specific text. It teaches the model the vocabulary, syntax, facts, and reasoning patterns of a new field before any supervised fine-tuning happens.

**How it differs from original pre-training:**
```
Original pre-training:  predict next token on 10T general tokens
Continual pre-training: predict next token on 100B legal tokens
Supervised fine-tuning: learn (input, output) pairs for specific tasks
```

**Key insight:**
- Original pre-training learns *what language is*
- Continual pre-training learns *what legal language is*
- Supervised fine-tuning learns *how to answer legal questions*

**Why this matters:**
- A model that has seen 100B medical tokens will understand abbreviations, drug interactions, and diagnostic chains
- Task-specific fine-tuning on top of this produces much higher accuracy than fine-tuning on the base model alone
- It is the standard first step when building any serious domain assistant

---

### Real-Life Analogy

Moving to a foreign country and learning the local dialect by immersion.
- **Original pre-training:** You grew up speaking standard English. You can read newspapers, write emails, and hold conversations.
- **Continual pre-training:** You move to Scotland and spend a year reading Scottish newspapers, listening to local podcasts, and chatting in pubs. No one gives you vocabulary tests. You just absorb the accent, slang, and cultural references.
- **Supervised fine-tuning:** After immersion, you take a class on how to write formal Scottish legal documents. Now you know both the dialect AND the format.

Without the immersion year, the legal document class would be confusing. You would not understand the local terms, so you would memorize templates without comprehension.

---

### Tiny Numeric Example

**Vocabulary overlap between general corpus and medical corpus:**
```
General corpus top words: "the", "and", "said", "people", "time"
Medical corpus top words:  "the", "patient", "mg", "treatment", "mmHg"

Unique medical tokens not in general top-10K: 3,420
```

**Perplexity on medical text (lower is better):**
```
Base model:              perplexity = 28.4
After 1B medical tokens: perplexity = 14.2  (50% better)
After 10B medical tokens: perplexity = 9.8   (66% better)
```

**Downstream task accuracy after fine-tuning on 1K labeled examples:**
```
Base model + SFT:              62% accuracy
Continually pre-trained + SFT: 81% accuracy
```

**The numbers show:** Even without any labeled task data, continual pre-training halves the model's surprise at medical text. When you add even a small amount of labeled data, the gap grows to 19 percentage points.

---

### Common Confusion

1. **"Continual pre-training is just training longer on the same data."** No. It is training on *different* data from a new domain. The base model already saw general data; now it sees domain data.

2. **"Continual pre-training causes catastrophic forgetting."** It can, if done aggressively. But with low learning rates, short training, and mixing in some general data, the model retains broad knowledge while gaining domain knowledge.

3. **"You need as much domain data as the original pre-training corpus."** No. Even 1-10% of the original data size can shift the model significantly because the base model is already good at language; it just needs to learn the domain dialect.

4. **"Continual pre-training replaces fine-tuning."** No. They are sequential. Continual pre-training teaches domain language. Fine-tuning teaches domain tasks. You almost always need both.

5. **"Any model can be continually pre-trained."** In practice, yes, but smaller models benefit less. A 1B model may not have enough capacity to absorb a new domain without losing general knowledge. A 7B+ model is the practical minimum for serious domain adaptation.

6. **"Continual pre-training is only for language."** False. Vision models are continually pre-trained on medical images, satellite photos, and industrial sensor data. The principle is the same: absorb the raw distribution before task training.

7. **"The learning rate should be the same as original pre-training."** No. Continual pre-training uses much smaller learning rates (typically 1e-5 to 1e-4) because you are nudging an already-capable model, not training from scratch.

---

### Where It Is Used in Our Code

`src/phase70/phase70_domain_adaptation.py` — We simulate continual pre-training by updating a base model on domain-specific unlabeled data and measuring how the model's perplexity and task accuracy improve before any supervised labels are introduced.
