## What Is Byte Pair Encoding?

---

### The Problem

Language models process tokens, not characters. English has ~50,000 words. But what about "neuroplasticity" or "Transformers" or names like "Cholmondeley"? You cannot have a vocabulary of every possible word. And what about languages like Chinese with tens of thousands of characters? How do you split text into pieces the model can handle?

---

### Definition

**Byte Pair Encoding (BPE)** is a subword tokenization algorithm that builds a vocabulary by iteratively merging the most frequent pairs of characters or subwords.

**How BPE works:**

**Step 1: Start with characters**
```
Vocabulary: {a, b, c, d, e, f, g, ...}
Corpus: "low lower lowest"
```

**Step 2: Count pairs**
```
"l o" appears 3 times
"o w" appears 3 times
"w e" appears 1 time
...
```

**Step 3: Merge most frequent pair**
```
Merge "l o" -> "lo"
New vocab: {a, b, c, ..., lo}
Corpus: "lo w lo w er lo w est"
```

**Step 4: Repeat**
```
"lo w" appears 3 times -> merge to "low"
"low e" appears 2 times -> merge to "lowe"
...
```

**Final vocabulary might include:**
```
{low, lower, lowest, er, est, ing, ed, ...}
```

**Why BPE is powerful:**
- Handles rare words by breaking them into known subwords
- "neuroplasticity" -> ["neuro", "plastic", "ity"]
- Keeps vocabulary size manageable (typically 32K-100K tokens)
- Works for any language
- GPT-2, GPT-3, Llama all use BPE

---

### Real-Life Analogy

Building with LEGO bricks.
- **Word-level tokenization:** You have pre-built LEGO models. A car is one piece. A house is one piece. But you cannot build a "spaceship-car" because you do not have that piece.
- **Character-level tokenization:** Every LEGO piece is a single 1×1 brick. You can build anything, but it takes millions of bricks to make a car.
- **BPE (subword):** You have common sub-assemblies: wheels, doors, windows, engines. You combine them to build cars, houses, and even spaceship-cars. You have flexibility without absurd granularity.

BPE finds the right balance between fixed words and single characters.

---

### Tiny Numeric Example

**Corpus:**
```
"hug hugging hugs"
```

**Initial characters:**
```
{h, u, g, i, n, s}
```

**After 1 merge (most frequent pair "u g"):**
```
{h, ug, i, n, s}
Corpus: "h ug h ug ging h ug s"
```

**After 2 merges ("h ug"):**
```
{hug, i, n, s}
Corpus: "hug hug ging hug s"
```

**After 3 merges ("hug g"):**
```
{hug, ging, s}
Corpus: "hug hug ging hug s"
```

**Tokenization of "hugging":**
```
"hug" + "ging" = [hug, ging]
```

**Tokenization of "hugged" (unseen word):**
```
"hug" + "ged" = [hug, ged]  (if "ged" was merged in training)
```

The model never saw "hugged" but can represent it from subwords it knows.

---

### Common Confusion

1. **"BPE is a compression algorithm."** It was originally invented for compression, but in NLP it is used for tokenization. The merge rules are the vocabulary.

2. **"BPE vocabulary is fixed after training."** Yes. Once trained on a corpus, the merge rules are fixed. New text is tokenized using those rules.

3. **"BPE handles all out-of-vocabulary words."** Yes, by definition. Any word can be broken into characters if needed. But rare words might tokenize into many pieces, which hurts performance.

4. **"BPE is the only subword method."** No. WordPiece (used by BERT) and SentencePiece (used by T5, Llama) are alternatives. They have slightly different merge criteria.

5. **"Larger vocabulary is always better."** Not necessarily. Larger vocabularies reduce sequence length but increase embedding matrix size. 32K-100K is the typical sweet spot.

---

### Where It Is Used in Our Code

`src/phase52/phase52_data_augmentation.py` — We implement a simplified BPE algorithm on a tiny corpus, showing how frequent pairs merge into subword tokens.
