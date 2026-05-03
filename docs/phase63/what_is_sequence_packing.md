## What Is Sequence Packing?

---

### The Problem

You have a 4096-token context window but most of your training examples are only 200 tokens long. If you train with one example per batch, you waste 95% of your GPU memory on padding tokens that produce no gradient. How do you fit multiple short examples into one long context window so every token position computes a useful loss?

---

### Definition

**Sequence packing** is the technique of concatenating multiple short training examples into a single long sequence that fills the model's context window, using attention masks to prevent cross-contamination between examples.

**Without packing:**
```
Batch item 1 (200 tokens): [The, capital, of, France, is, ...] + [PAD, PAD, PAD, ...] × 3896
Batch item 2 (150 tokens): [2, +, 2, =, 4] + [PAD, PAD, ...] × 3946
GPU utilization: ~5% useful, ~95% padding
```

**With packing:**
```
Batch item 1 (4096 tokens):
  [The, capital, of, France, is, Paris, <|eot|>,
   What, is, 2+2, <|eot|>,
   Explain, gravity, <|eot|>,
   ...]  (20 examples concatenated)

GPU utilization: ~100% useful, 0% padding
```

**Attention mask for packing:**
```
Example A occupies positions 0-49
Example B occupies positions 50-99
Example C occupies positions 100-149

Attention mask blocks position 0 from attending to position 50
(blocks cross-example attention)
```

**Why this matters:**
- Packing can increase training throughput by 5-10× on short-sequence datasets
- Flash Attention 2 supports packing natively with "variable-length" sequences
- Without packing, you are paying for GPU memory that does nothing

---

### Real-Life Analogy

Moving trucks and cardboard boxes.
- **Without packing:** You have a 40-foot moving truck. You put one small box inside and drive across the country. The other 39 feet are empty. You make 1000 trips.
- **With packing:** You stack boxes floor-to-ceiling, filling every cubic foot. One trip carries 50 boxes. You make 20 trips.
- **The attention mask:** Each box has a label saying "do not open boxes from other rooms." When you unpack, you know which items belong to which room.

Sequence packing is Tetris for GPU memory.

---

### Tiny Numeric Example

**Context window:** 20 tokens
**Training examples:**
```
A: [What, is, 2+2, ?] → 4 tokens
B: [Paris, is, capital, of, France] → 5 tokens
C: [Hello, world] → 2 tokens
D: [The, sky, is, blue, today] → 5 tokens
E: [Yes] → 1 token
F: [Machine, learning, is, fun] → 4 tokens
```

**Without packing (6 separate batches):**
```
Batch 1: [What, is, 2+2, ?, PAD, PAD, ...] × 16 pads
Batch 2: [Paris, is, capital, of, France, PAD, ...] × 15 pads
...
Total padding: 16 + 15 + 18 + 15 + 19 + 16 = 99 padding tokens
Total useful: 4 + 5 + 2 + 5 + 1 + 4 = 21 useful tokens
Efficiency: 21 / (21+99) = 17%
```

**With packing (1 batch, 2 packed sequences):**
```
Sequence 1 (20 tokens):
  [What, is, 2+2, ?, <|eot|>, Paris, is, capital, of, France, <|eot|>,
   Hello, world, <|eot|>, The, sky, is, blue, today]

Sequence 2 (20 tokens):
  [Yes, <|eot|>, Machine, learning, is, fun, <|eot|>, PAD, PAD, ...] × 13 pads

Total padding: 13 tokens
Total useful: 21 tokens
Efficiency: 21 / (21+13) = 62% (3.6× better)
```

**Loss masking:**
```
Example A (positions 0-3): compute loss on tokens [is, 2+2, ?, <|eot|>]
Example B (positions 5-9): compute loss on tokens [is, capital, of, France, <|eot|>]
Example C (positions 11-12): compute loss on tokens [world, <|eot|>]
```

The model only learns from assistant responses, not from user instructions.

---

### Common Confusion

1. **"Packing means the model sees multiple examples as one."** No. The attention mask prevents cross-example attention. Each example is still independent.

2. **"Packing only works for pre-training."** No. It works for any task with short examples: SFT, DPO, classification.

3. **"Packing hurts model quality."** Usually no. Studies show packing matches or improves quality because of increased diversity per batch.

4. **"Packing requires special model architecture."** No. Any model with causal masking supports packing. Flash Attention 2 makes it efficient.

5. **"Packing and padding are the same."** No. Padding fills empty space with dummy tokens. Packing fills empty space with real, useful training data.

---

### Where It Is Used in Our Code

`src/phase63/phase63_dataset_curation.py` — We pack multiple short instruction-response pairs into fixed-length sequences, compute efficiency before and after packing, and visualize how attention masks prevent cross-example contamination.
