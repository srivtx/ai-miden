## What Is a Real Data Curation Pipeline?

**The Problem:**
You have access to the entire internet — trillions of words. But 80% of it is spam, duplicates, broken HTML, adult content, and low-quality filler. Training on raw web data makes your model worse, not better. How do you turn an ocean of noise into a clean, high-quality training corpus?

**Definition:**
A **data curation pipeline** is an automated workflow that ingests raw text, cleans it, filters it by quality metrics, removes duplicates, and exports a structured training corpus. It is the single most important system in modern AI training.

**Real-life analogy:**
A data curation pipeline is like a gold refinery. A gold mine produces tons of rock with tiny flecks of gold. The refinery crushes the rock (cleaning), dissolves it in acid to remove impurities (filtering), separates gold from other metals (deduplication), and casts pure gold bars (export corpus). The mine produces raw material. The refinery creates value. In AI, the internet is the mine. The data curation pipeline is the refinery.

**Tiny numeric example:**
Starting corpus: 10,000 Wikipedia articles
- After cleaning: 9,800 (remove empty, fix encoding)
- After quality filtering: 7,200 (remove short, repetitive, low-entropy text)
- After deduplication: 6,500 (remove near-duplicate articles)
- Final curated corpus: 6,500 high-quality, unique documents
- The pipeline removed 35% of raw data while improving average quality by 3x.

**Common confusion:**
- **"More data is always better."** No. Training on 10B tokens of high-quality data beats 100B tokens of low-quality data. Quality dominates quantity.
- **"Deduplication removes exact copies only."** Near-duplicate detection (MinHash, SimHash) removes articles that are 85%+ similar, not just identical. This catches mirrored content and template pages.
- **"Quality filtering is just length checks."** Length is one signal. Real pipelines use trained classifiers, perplexity scores, language detection, toxicity filters, and readability metrics.
- **"Data curation is a one-time job."** No. The internet changes. New data arrives. Old data becomes stale. Production pipelines run continuously.
- **"You can skip curation for small models."** Small models are even more sensitive to data quality. A 1B model trained on clean data outperforms a 7B model trained on dirty data.
- **"Data curation is only for pre-training."** Fine-tuning data also needs curation. Instruction datasets require diversity filtering, difficulty balancing, and format validation.

**Where it appears in our code:**
`src/phase155/phase155_data_curation.py` — Loads Wikipedia text, cleans HTML/URLs, filters by length and entropy, deduplicates with MinHash+LSH, and exports a curated corpus with full statistics.
