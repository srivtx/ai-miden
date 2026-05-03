### 1. Why it exists (THE PROBLEM first)
During autoregressive generation, a Transformer computes attention over the entire prefix at every single step. When generating token 100, it recomputes keys and values for tokens 1 through 99 even though those vectors never changed. This wastes enormous compute and makes long sequences painfully slow.

### 2. Definition (very simple)
The KV Cache is a storage buffer that saves the Key and Value vectors for every token already processed. During generation, the model only computes K and V for the NEW token, then appends them to the cache. Attention is computed between the new Query and the cached Keys, avoiding all redundant work.

### 3. Real-life analogy
You are writing a 50-page essay. Without KV Cache, every time you write a new paragraph, you re-read the entire essay from page 1. With KV Cache, you keep your notes open on the desk; you only write the new paragraph and glance at the notes you already took.

### 4. Tiny numeric example
Sequence: ["The", "cat", "sat"]

Step 1 (generate "The"):
- Compute Q1, K1, V1 for "The"
- No cache yet. Output next token.

Step 2 (generate "cat"):
- **Without cache:** Recompute K1, V1 for "The", plus K2, V2 for "cat". Attention over 2 tokens.
- **With cache:** Load K1, V1 from cache. Only compute K2, V2 for "cat". Attention over 2 tokens using cached K1 + new K2.

Step 3 (generate "sat"):
- **Without cache:** Recompute K1, V1, K2, V2, K3, V3. Attention over 3 tokens.
- **With cache:** Load K1, V1, K2, V2. Only compute K3, V3. Attention over 3 tokens using cached K1, K2 + new K3.

At step N, without cache you do O(N^2) work. With cache you do O(N) work.

### 5. Common confusion
- **KV Cache does not store attention weights.** It stores the Key and Value vectors BEFORE they are multiplied into attention scores. Attention weights are still computed fresh each step.
- **It only helps during inference, not training.** During training, the whole sequence is known in parallel and the full attention matrix is needed for backpropagation.
- **It uses a lot of memory.** The cache grows with sequence length. For a 4096-token context with 32 layers and 128 hidden dims, the cache can be gigabytes.
- **It is not just for Transformers.** Any autoregressive model with key-value attention (like RNNs with attention) can use caching.

### 6. Where it is used in our code
`src/phase25/phase25_inference_optimization.py` demonstrates generation with and without KV Cache, measuring the compute savings at each step.
