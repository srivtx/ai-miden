## What Is Data Curation?

---

### The Problem

You have 10 million raw examples scraped from the internet. They contain duplicates, low-quality responses, toxic content, personal information, wrong answers, and inconsistent formatting. Feeding this raw sludge into a model produces a model that memorizes garbage, generates hate speech, and leaks private data. How do you clean, filter, and organize training data into something that produces a good model?

---

### Definition

**Data curation** is the process of cleaning, filtering, deduplicating, and organizing raw training data to maximize quality, diversity, and safety before it reaches the model.

**Key steps:**

**1. Deduplication:**
```
Near-duplicate removal:
  "The capital of France is Paris."  ← keep
  "The capital of France is Paris."  ← remove (exact duplicate)
  "Paris is the capital of France."  ← remove (near-duplicate, same meaning)
```

**2. Quality filtering:**
```
Remove examples where:
  - Response is too short ("I don't know")
  - Response is too long and rambling
  - Instruction and response are unrelated
  - Text is garbled or nonsensical
  - Contains excessive profanity or toxicity
```

**3. Format standardization:**
```
Before: {"prompt": "what is 2+2", "completion": "4"}
After:  {"instruction": "What is 2+2?", "input": "", "output": "4"}
```

**4. Safety filtering:**
```
Remove or flag examples containing:
  - Instructions for illegal acts
  - Hate speech or harassment
  - Personal identifiable information (PII)
  - Sexually explicit content
```

**Why this matters:**
- GPT-3 trained on uncleaned data memorized credit card numbers
- LLaMA 2's training data was filtered with toxicity classifiers
- Deduplication alone can reduce dataset size by 30-50% while improving model quality

---

### Real-Life Analogy

Cooking a gourmet meal from ingredients found in a dumpster.
- **Raw data:** The dumpster contains rotten tomatoes, moldy bread, perfectly good carrots, a dead rat, and some organic kale.
- **Deduplication:** You find 50 identical plastic bags of carrots. You keep one.
- **Quality filtering:** You throw out the rat, the moldy bread, and the rotten tomatoes.
- **Format standardization:** You chop everything to the same size so it cooks evenly.
- **Safety filtering:** You test for pesticides and contamination.
- **Result:** A clean, safe, high-quality ingredient set that produces a great meal.

Data curation is the difference between a Michelin-star restaurant and a dumpster fire.

---

### Tiny Numeric Example

**Raw dataset (10 examples):**
```
1. Instruction: "What is 2+2?"  Response: "4"
2. Instruction: "What is 2+2?"  Response: "4"          ← duplicate
3. Instruction: "What is 2+2?"  Response: "The answer is 4."  ← near-duplicate
4. Instruction: "How do I hack a bank?"  Response: "Step 1: find the IP..."  ← unsafe
5. Instruction: "What is France's capital?"  Response: "Paris is the capital."
6. Instruction: "Tell me a joke."  Response: ""         ← too short / empty
7. Instruction: "Explain quantum physics."  Response: "Quantum physics is a branch of physics that deals with physical phenomena at nanoscopic scales where the action is on the order of the Planck constant. It departs from classical mechanics..."  ← good
8. Instruction: "Hi"  Response: "Hello! How can I help you today?"  ← good
9. Instruction: "What is 2+2?"  Response: "fish"      ← wrong answer
10. Instruction: "Write a poem."  Response: "Roses are red, violets are blue..."  ← good
```

**After curation:**
```
Kept: 1, 5, 7, 8, 10  (5 examples)
Removed:
  - #2: exact duplicate
  - #3: near-duplicate
  - #4: unsafe content
  - #6: too short / empty
  - #9: incorrect response

Dataset reduced from 10 → 5 (50% reduction)
Quality increased significantly
```

**Quality score heuristic:**
```
score = length_penalty × format_validity × toxicity_filter × correctness_check
Example 1: 1.0 × 1.0 × 1.0 × 1.0 = 1.0 (keep)
Example 4: 1.0 × 1.0 × 0.0 × 0.0 = 0.0 (remove)
Example 6: 0.0 × 1.0 × 1.0 × 1.0 = 0.0 (remove)
```

---

### Common Confusion

1. **"Data curation is just removing duplicates."** No. It is quality filtering, format standardization, safety checks, diversity balancing, and more.

2. **"More data is always better."** No. 1 million clean examples beat 10 million dirty ones. Quality > quantity.

3. **"You can curate data after training."** No. The model has already memorized the garbage. Curation must happen BEFORE training.

4. **"Safety filtering makes the model useless."** No. It removes a tiny fraction of data (<5%) while preventing catastrophic failure modes.

5. **"Data curation is a one-time task."** No. As models evolve, curation standards evolve. What was acceptable for GPT-2 is not acceptable for GPT-4.

---

### Where It Is Used in Our Code

`src/phase63/phase63_dataset_curation.py` — We simulate a full data curation pipeline on a synthetic dataset: deduplication with MinHash, quality scoring, format validation, and safety filtering. We show before/after statistics and visualize the quality distribution.
