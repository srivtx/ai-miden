## What Is Model Staleness?

---

### The Problem

You deploy a state-of-the-art language model on January 1st. It aces every benchmark. By December, users are asking about elections that happened in March, treaties signed in June, and products released in September. The model answers with pre-January assumptions. It describes the old government, the old trade deal, and the old software version. It does not know it is wrong because its training data never contained the new reality. The model is not broken; it is **stale**. Its internal map of the world is frozen at the training cutoff. In domains where facts change quickly — news, medicine, law, technology — staleness is not a minor bug. It is a fundamental decay function.

---

### Definition

**Model Staleness** is the degradation of a model's accuracy over time as the real world diverges from the distribution of its training data. It is driven by **temporal drift**: new events, new language, new concepts, and shifting relationships that the model has never seen.

**How it works:**
```
Training cutoff: June 2023

Evaluation in January 2024:
  Question: "Who is the current Speaker of the House?"
  Model answer (based on June 2023): "Kevin McCarthy"
  Correct answer (January 2024): "Mike Johnson"
  -> Staleness error

Evaluation in January 2025:
  Question: "What is the latest version of Python?"
  Model answer: "Python 3.11"
  Correct answer: "Python 3.13"
  -> Staleness error

The gap between training data and reality grows monotonically with time.
```

**Key drivers of staleness:**
- **Event drift:** new facts (elections, acquisitions, discoveries)
- **Concept drift:** new terminology ("generative AI" exploding post-2022)
- **Relationship drift:** shifting associations (company CEOs, geopolitical alliances)
- **Language drift:** new slang, memes, and communication patterns

**Why this matters:**
- A model that scored 90% on current-events QA in 2023 scores 60% in 2025 without updates
- Staleness creates silent failures: the model is confident and wrong
- Users lose trust when a model is obviously behind the times

---

### Real-Life Analogy

An expired medicine cabinet.
- **Fresh model:** You open the cabinet in January. Every bottle is labeled, sealed, and effective. The antibiotics cure the infection, the painkiller works, the antihistamine stops the rash. You trust the cabinet.
- **Stale model:** You open the cabinet two years later. The bottles look identical. The labels are crisp. But the antibiotics have lost potency, the painkiller now causes side effects that were discovered after manufacture, and the antihistamine has been recalled. You take the pills and get worse. The cabinet did not break; its contents silently decayed.
- **The danger:** Staleness is invisible until it causes harm. A model does not raise an error when it answers with outdated facts. It simply answers wrong with full confidence.

---

### Tiny Numeric Example

**A model evaluated on a "current events" quiz each quarter:**
```
Training cutoff: Q2 2023

Quiz questions about events from the last 6 months:

Q3 2023 evaluation:
  Model accuracy: 78% (some events in training overlap)

Q4 2023 evaluation:
  Model accuracy: 71%

Q1 2024 evaluation:
  Model accuracy: 64%

Q2 2024 evaluation:
  Model accuracy: 58%

Q3 2024 evaluation:
  Model accuracy: 52%
```

**Accuracy decay rate:**
```
Roughly -4 to -6 percentage points per quarter on time-sensitive facts
After 5 quarters: 78% -> 52%, a 26-point drop
```

**Contrast with static knowledge:**
```
Quiz on "basic geometry" over the same period:
  Q3 2023: 91%
  Q2 2024: 90%   <- virtually no decay
```

**The shift:** Staleness is not uniform. It attacks fast-moving domains (politics, tech, medicine) while leaving stable domains (math, history, physics) intact. A single accuracy number hides this divergence.

---

### Common Confusion

1. **"Bigger models are less stale."** False. A 70B model trained in 2023 knows more 2023 facts than a 7B model, but both stop at the same cutoff. Scale does not buy time travel.

2. **"Retrieval augmentation fixes staleness."** It helps. A RAG system can fetch current documents and answer with up-to-date information. But the base model itself is still stale. If the retriever fails or the question requires internalized reasoning, the stale model hurts performance.

3. **"Model staleness is the same as model drift."** Model drift usually refers to the model's predictions drifting away from ground truth because the input distribution changed (e.g., users start asking different questions). Staleness is about the world changing while the model stays frozen. They are related but distinct.

4. **"You can just filter old data and the model stays fresh."** Filtering does not help if the model is already trained. And training only on recent data makes the model forget older but still-relevant facts. Freshness and retention are in tension.

5. **"Staleness only affects question answering."** It affects everything: code generation (new API versions), translation (new loanwords), recommendation (new products), and safety (new social engineering tactics).

6. **"Users notice staleness immediately."** They do not. Users often accept confident wrong answers unless the fact is obviously time-sensitive. Staleness is a silent credibility killer.

7. **"Continual pretraining eliminates staleness."** It reduces it, but continual pretraining has its own lag (data collection, training time, evaluation). There is always a window of staleness between the latest event and the next model update.

---

### Where It Is Used in Our Code

`src/phase146/phase146_continual_concepts.py` — We simulate a model's accuracy on time-sensitive tasks decaying over simulated quarters, contrast it with stable-task accuracy, and visualize the divergence between fast-moving and static knowledge.

`src/phase146/phase146_continual_colab.py` — We evaluate `Qwen/Qwen2.5-3B-Instruct` on pre-2024 facts versus post-2024 facts to measure the model's built-in staleness, then show how fine-tuning on new data updates the model but introduces catastrophic forgetting on old facts.

(End of file)
