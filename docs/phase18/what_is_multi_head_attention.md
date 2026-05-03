### 1. Why it exists (THE PROBLEM first)

A single self-attention mechanism computes one set of attention weights for every word pair. But words in a sentence have many different types of relationships:

- **Syntactic:** Subject-verb agreement ("The cat **sits**", "The cats **sit**")
- **Semantic:** Synonymy or related meaning ("cat" and "feline")
- **Coreference:** Pronoun reference ("it" → "cat")
- **Positional:** Adjacency or word order patterns

One attention head can't capture all of these simultaneously. It has to compromise, learning an average of all relationship types, which dilutes its effectiveness.

We need a way to capture multiple types of relationships at the same time.

---

### 2. Definition (very simple)

Multi-Head Attention runs the self-attention mechanism multiple times in parallel using different learned linear projections. Each "head" produces its own attention output. These outputs are concatenated and projected again to produce the final result. Each head can specialize in capturing a different kind of relationship.

---

### 3. Real-life analogy

Imagine a jury of experts analyzing a court case:

- **Juror 1** focuses exclusively on motive.
- **Juror 2** focuses exclusively on physical evidence.
- **Juror 3** focuses exclusively on witness testimony.
- **Juror 4** focuses exclusively on legal precedent.

Each juror sees different aspects of the same case. Individually, each has a limited view. Together, by combining their perspectives, they reach a much better and more robust decision than any single juror could.

---

### 4. Tiny numeric example

Consider a Transformer with **8 attention heads** processing the sentence: **"The cat sat on the mat because it was tired."**

Each head learns to focus on different relationships:

| Head | What it learns | Example behavior |
|------|----------------|------------------|
| Head 1 | Subject-verb agreement | "cat" → "sat" (high score) |
| Head 2 | Pronoun reference | "it" → "cat" (high score) |
| Head 3 | Prepositional attachment | "sat" → "on" (high score) |
| Head 4 | Article-noun pairing | "the" → "mat" (high score) |
| Head 5 | Adjective-noun modification | "tired" → "it" (high score) |
| Head 6 | Semantic similarity | "cat" → "feline" (if in vocab) |
| Head 7 | Positional adjacency | "sat" → "on" (local focus) |
| Head 8 | Global sentence context | Attends broadly to content words |

For the word **"it"**, the 8 heads produce 8 different output vectors:

- Head 2 might output a vector heavily weighted toward "cat"
- Head 5 might output a vector heavily weighted toward "tired"
- Head 8 might output a broad context vector

These 8 vectors are concatenated into one long vector, then passed through a linear projection to produce the final, rich representation for "it."

---

### 5. Common confusion

1. **"More heads are always better."**
   - Not necessarily. More heads increase computation and memory. Research shows diminishing returns; 8-16 heads are common, but 64+ heads often don't help and can hurt if the model size doesn't scale with them.

2. **"Each head is manually assigned a role."**
   - No. The roles emerge from training. We don't tell Head 1 to learn syntax; it discovers that pattern on its own because it's useful for minimizing the loss.

3. **"Multi-head attention is 8x slower than single-head attention."**
   - In practice, the multiple heads are computed in parallel on the GPU. The cost is higher than one head, but not 8x because of parallelization and shared matrix operations.

4. **"All heads learn meaningful things."**
   - Some heads may learn redundant or uninterpretable patterns. It's common for a few heads to be much more important than others. Pruning less important heads is an active research area.

5. **"Concatenation is the only way to combine heads."**
   - Concatenation followed by a linear projection is standard, but averaging or other aggregation methods have been explored in some variants.

---

### 6. Where it is used in our code

In our Transformer implementation, multi-head attention is the core component of each encoder layer. We instantiate multiple attention heads with separate Query/Key/Value projections, run them in parallel, and concatenate their outputs before the final linear projection and residual connection.
