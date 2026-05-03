### 1. Why it exists (THE PROBLEM first)

Standard attention mechanisms (as used in encoder-decoder models) allow the **decoder** to attend to the **encoder's** output. This is great for translation: the decoder looks at the source sentence to produce each target word.

But what if words in the **same sentence** need to attend to each other?

For example, in the sentence "The cat sat on the mat because it was tired," the word **"it"** refers to **"cat."** To understand this, "it" needs to look at other words in the same sentence. Standard encoder-decoder attention doesn't help here because there is no separate encoder and decoder — it's all one sentence.

Self-attention solves this by letting each word attend to every other word **within the same input sequence**.

---

### 2. Definition (very simple)

Self-attention is a mechanism where each position in a sequence computes attention scores with every other position in the **same** sequence. The Query, Key, and Value vectors all come from the same input. Each word updates its representation by taking a weighted sum of all other words in the sentence, where the weights are determined by relevance.

---

### 3. Real-life analogy

Imagine a group discussion where everyone shares their initial opinion. Then, everyone updates their opinion based on what everyone else said.

- "I think X."
- "Everyone else thinks Y, Z, and W."
- "I update my view based on how relevant Y, Z, and W are to my position."

Each person listens to the whole group, not just the person next to them, and decides how much to weight each other's input.

---

### 4. Tiny numeric example

Sentence: **"The cat sat on the mat because it was tired."**

What does **"it"** refer to? Self-attention computes relevance scores between "it" and every other word:

| Word       | Relevance Score to "it" | Reasoning                          |
|------------|-------------------------|------------------------------------|
| The        | 0.05                    | Low relevance                      |
| cat        | **0.65**                | **High relevance — likely referent** |
| sat        | 0.05                    | Low relevance                      |
| on         | 0.02                    | Low relevance                      |
| the        | 0.02                    | Low relevance                      |
| mat        | 0.15                    | Moderate relevance (possible, but less likely) |
| because    | 0.03                    | Low relevance                      |
| it         | 0.00                    | Ignores itself                     |
| was        | 0.01                    | Low relevance                      |
| tired      | 0.02                    | Low relevance                      |

After self-attention, the representation for "it" becomes a weighted blend heavily influenced by "cat" (score 0.65) and slightly by "mat" (score 0.15). The model learns that "it" likely means "cat" because cats get tired, mats don't.

---

### 5. Common confusion

1. **"Self-attention is the same as standard attention."**
   - Standard attention connects two different sequences (e.g., decoder to encoder). Self-attention connects a sequence to itself. Query, Key, and Value all come from the same source.

2. **"Self-attention understands meaning like humans do."**
   - No. Self-attention computes statistical similarity between vector representations. It doesn't "understand" pronouns; it learns patterns from data that correlate "it" with nearby animate nouns.

3. **"Every word attends equally to all other words."**
   - The attention scores are weighted. After applying softmax, most weight goes to a few relevant words. Irrelevant words get near-zero attention.

4. **"Self-attention only looks at nearby words."**
   - Self-attention is global: every word can attend to every other word, regardless of distance. This is its advantage over RNNs, where distant words are harder to connect.

---

### 6. Where it is used in our code

In our codebase, self-attention is implemented within the Transformer encoder blocks. When we process an input sequence, each token's representation is updated by our self-attention module, allowing the model to resolve references and build contextualized embeddings before passing them to the feed-forward layers.
