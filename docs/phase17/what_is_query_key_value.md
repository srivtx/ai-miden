### 1. Why it exists (THE PROBLEM first)

If attention is about computing "relevance," we still need a concrete, mathematical way to calculate that relevance. We cannot just say "this word is important" — we need a formula. The problem is: **how do we turn two vectors into a relevance score that we can learn with backpropagation?**

### 2. Definition (very simple)

Query/Key/Value is the mathematical machinery behind attention. Every token (or position) gets **three learned vectors**: a **Query** (what am I looking for?), a **Key** (what do I contain?), and a **Value** (what information should I pass on if I am selected?). Relevance is computed as the dot product between a Query and a Key. The output is a weighted sum of the Values, where the weights come from softmax-normalized dot products.

### 3. Real-life analogy

**A library search system.**

- **Query** = your search question typed into the catalog (e.g., *"books about cats"*).
- **Key** = the titles and descriptions on the library's index cards (e.g., *"The Cat in the Hat"*, *"Dog Training 101"*).
- **Relevance score** = how well the title/description matches your search query (high for the cat book, low for the dog book).
- **Value** = the actual contents of the books on the shelf.
- **Output** = a weighted average of the book contents. You read mostly from the cat book and almost nothing from the dog book, based on the match scores.

### 4. Tiny numeric example

- **Query (Q)** = `[1, 0, 0]`  → "I am looking for the first feature."
- **Key 1 (K1)** = `[1, 0, 0]` → "I have the first feature."
- **Key 2 (K2)** = `[0, 1, 0]` → "I have the second feature."

Compute dot products (raw scores):

- `Q · K1` = `(1*1) + (0*0) + (0*0)` = **1**
- `Q · K2` = `(1*0) + (0*1) + (0*0)` = **0**

After softmax, the attention weights become approximately **100%** on Value 1 and **0%** on Value 2. The final output is exactly Value 1 because the Query matched Key 1 perfectly and did not match Key 2 at all.

### 5. Common confusion

1. **Q, K, and V all come from the same input.** They are not three separate inputs from outside. They are three different linear projections (learned weight matrices multiplied by the same source vector).
2. **The Query is not a human-written question.** In self-attention, every token produces its own Query vector automatically from its embedding.
3. **The Key is not a database lookup table.** It is a learned vector representation of what that token "offers" to match against.
4. **The Value is not the raw input token.** It is another learned transformation of the input; it is the information that gets aggregated into the output.
5. **Dot product alone is not the final output.** The dot product only produces the mixing weights; the final result is the weighted sum of the Values.

### 6. Where it is used in our code

The Query, Key, and Value projections are used inside the multi-head self-attention block to compute the context-aware representations for each token in the sequence, allowing the model to relate distant words to one another.
