### 1. Why it exists (THE PROBLEM first)
Multi-head attention uses many parallel attention heads, each with its own Key and Value projections. For a model with 32 heads, the KV Cache stores 32 separate Key and Value tensors per token. As sequences get longer, this cache dominates memory usage and limits batch size. We want to shrink the cache without losing much quality.

### 2. Definition (very simple)
Grouped Query Attention (GQA) shares a single set of Key and Value heads among multiple Query heads. Instead of every Query head having its own K and V, a group of Query heads all looks up the same K and V. This reduces the KV Cache size proportionally to the group size.

### 3. Real-life analogy
Imagine a restaurant with 8 waiters (Query heads) and 8 separate copies of the menu (Key/Value heads). Every waiter carries their own heavy menu book. GQA says: let 4 waiters share 1 menu book. Now you only need 2 menu books total. The waiters still serve customers independently, but they all read from the shared book.

### 4. Tiny numeric example
Multi-Head Attention (MHA):
- 8 heads
- Each token stores 8 Keys and 8 Values
- KV Cache per token = 8 K + 8 V = 16 vectors

Grouped Query Attention (GQA, group size 4):
- 8 Query heads
- 2 Key heads (8 / 4 = 2)
- 2 Value heads (8 / 4 = 2)
- KV Cache per token = 2 K + 2 V = 4 vectors
- **Memory saved: 75%**

Multi-Query Attention (MQA, extreme case where group size = all heads):
- 8 Query heads
- 1 Key head, 1 Value head
- KV Cache per token = 2 vectors
- **Memory saved: 87.5%**

### 5. Common confusion
- **GQA is not the same as MQA.** MQA uses exactly 1 K and 1 V head for ALL Query heads. GQA is a middle ground: a few shared K/V heads, not just one.
- **Quality does not drop much.** Because attention heads often learn redundant patterns, sharing K/V across a small group barely hurts performance. Llama 2 and later models use GQA successfully.
- **It only affects inference memory, not training FLOPs.** During training, the full K and V are computed anyway. The savings come from the KV Cache during autoregressive generation.
- **The Query heads remain independent.** Only Keys and Values are shared. Each Query head still computes its own attention scores against the shared K/V.

### 6. Where it is used in our code
`src/phase25/phase25_inference_optimization.py` compares memory usage between standard multi-head attention, grouped query attention, and multi-query attention for a long sequence.
