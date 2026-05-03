## What Is a Data Pipeline?

---

### The Problem

Training data does not come clean. It has duplicates, garbage, toxic content, personal information, and formatting inconsistencies. Feeding raw internet scrapes into a model produces a model that memorizes garbage, generates toxic outputs, and leaks private data. How do you clean and process data at scale?

---

### Definition

A **data pipeline** is the sequence of processing steps that transforms raw data into training-ready examples.

**Typical LLM data pipeline:**
```
Raw web crawl (Common Crawl, etc.)
  ↓
Deduplication (remove exact and near-duplicates)
  ↓
Quality filtering (remove garbled text, boilerplate, code errors)
  ↓
Toxicity filtering (remove hate speech, adult content)
  ↓
PII removal (remove emails, phone numbers, addresses)
  ↓
Language identification (keep only target language)
  ↓
Tokenization (BPE / SentencePiece)
  ↓
Shuffling and batching
  ↓
Training batches
```

**Why each step matters:**
- **Deduplication:** Prevents memorization. A model trained on 10 copies of the same article memorizes it.
- **Quality filtering:** Removes SEO spam, template text, and auto-generated garbage.
- **Toxicity filtering:** Reduces harmful outputs. Models learn what they are trained on.
- **PII removal:** Prevents privacy leaks. GPT-3 memorized some individuals' contact info.
- **Language ID:** Ensures the model learns the target language, not random multilingual noise.

**Scale:**
```
Raw crawl:     10 trillion tokens
After dedup:   5 trillion tokens
After quality: 2 trillion tokens
After toxicity: 1.5 trillion tokens
Final dataset: 1 trillion tokens
```

Data processing can take months and cost millions of dollars for frontier models.

---

### Real-Life Analogy

A gold mining operation.
- **Raw ore:** Rocks dug from the ground containing tiny gold flakes
- **Crushing:** Break rocks into smaller pieces (tokenization)
- **Washing:** Remove dirt and sand (quality filtering)
- **Chemical separation:** Extract gold from other metals (toxicity/PII removal)
- **Smelting:** Purify into gold bars (final dataset)
- **Waste:** 99% of raw material is discarded

The gold mine processes tons of rock to get ounces of gold. Similarly, data pipelines process petabytes of web data to get terabytes of clean training text.

---

### Tiny Numeric Example

**Raw text samples:**
```
Sample 1: "The cat sat on the mat. Buy cheap viagra now!!!"
Sample 2: "The cat sat on the mat. Buy cheap viagra now!!!" (duplicate)
Sample 3: "asdf qwer zxcv jkl;" (gibberish)
Sample 4: "Contact me at john@email.com for details."
Sample 5: "The quick brown fox jumps over the lazy dog."
```

**After pipeline:**
```
Deduplication:    Remove Sample 2
Quality filter:   Remove Sample 3
Toxicity filter:  Remove "Buy cheap viagra now!!!" from Sample 1
PII removal:      Sample 4 -> "Contact me at [EMAIL] for details."
Final dataset:    ["The cat sat on the mat.", "Contact me at [EMAIL] for details.", "The quick brown fox jumps over the lazy dog."]
```

**Result:** 5 samples → 3 clean samples. 40% of raw data discarded.

---

### Common Confusion

1. **"Data cleaning is optional."** No. GPT-3 trained on uncleaned data memorized credit card numbers and generated toxic text. Cleaning is essential.

2. **"More data is always better."** Quality matters more than quantity. 100B clean tokens often beats 1T dirty tokens.

3. **"Deduplication removes useful repetition."** Exact duplicates are never useful. Near-duplicates (paraphrases) are kept by modern deduplication.

4. **"The pipeline is the same for every model."** No. Medical models need different filtering than general chatbots. Code models need different quality heuristics.

5. **"Data pipelines are only for pre-training."** Fine-tuning datasets also need cleaning. Instruction datasets are heavily curated by human annotators.

---

### Where It Is Used in Our Code

`src/phase52/phase52_data_augmentation.py` — We implement a toy data pipeline: deduplication with MinHash, quality filtering by length, and PII detection with regex.
