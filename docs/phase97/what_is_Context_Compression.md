## What Is Context Compression?

---

## The Problem

You are building a legal assistant that must read an entire 200-page contract and answer questions about clause 47b. A standard transformer with full self-attention would build a 100,000 × 100,000 attention score matrix, consuming terabytes of memory and making inference impossible on any existing GPU. Even if you somehow fit the matrix into memory, most of the 100,000 tokens are redundant boilerplate: headers, footers, signature blocks, and pages of definitions that have no bearing on clause 47b. You are paying quadratic compute costs to attend over information that is irrelevant. The challenge is to preserve the knowledge buried in the long document without paying the full price of quadratic attention.

---

## Definition

**Context Compression** is the process of distilling a long context into a shorter, dense representation while preserving relevant information. Methods include hierarchical attention, memory layers, prompt compression, and learned compression tokens. The goal is to reduce the effective sequence length that the model must attend over, cutting both memory and latency.

**How it works:**
```
Full context:         128,000 tokens of legal text
Hierarchical chunking:
  Level 1:  128 chunks of 1,000 tokens each
  Level 2:  128 paragraph summaries (coarse attention)
  Level 3:  selected paragraphs expanded to full text (fine attention)
Effective attention:  128 summaries + 2 full paragraphs = ~4,000 tokens
Compression ratio:    128,000 / 4,000 = 32:1
```

**Key techniques:**
- **Hierarchical attention:** chunk the document, summarize each chunk, attend over summaries, then drill into selected chunks.
- **Memory layers:** external compressed memory banks that the model can read and write during inference.
- **Prompt compression:** learned models that compress a long prompt into a few dense vectors before the main model processes them.
- **Selective retrieval:** using an external index to fetch only relevant passages, then compressing those passages further.

**Why this matters:**
- Quadratic attention makes naive long-context processing impossible beyond ~16K tokens on consumer hardware.
- Most long documents are redundant; compression focuses compute on the subset that matters.
- Compression enables applications like book-length summarization, codebase-wide reasoning, and multi-document legal analysis.

---

## Real-Life Analogy

Imagine a lawyer preparing for a high-stakes trial. They have 50 boxes of documents: contracts, emails, deposition transcripts, and financial records. Reading every page for every question would take years. Instead, the lawyer's team creates a detailed index and a set of summary sheets. When a witness mentions "contract clause 7b," the lawyer does not open all 50 boxes. They look up "7b" in the index, retrieve the relevant 10 pages, and read those in full. The knowledge from the other 49 boxes is still available, but it is accessed selectively through the index rather than exhaustively.

**The trade-off:** Creating the index and summaries takes time and money. If the summary of a contract omits a critical amendment, the lawyer might miss a key argument. Compression trades upfront preparation cost for downstream query efficiency. In transformer terms, the compression step might require a separate forward pass, adding latency to the first query. But for subsequent queries, the compressed index makes retrieval nearly instantaneous.

**The nuance:** Some documents cannot be compressed without loss. A mathematical proof where every line depends on the previous one has no redundancy. A poetry anthology where every word carries meaning is similarly incompressible. Context compression works best on heterogeneous, redundant documents like legal contracts, technical manuals, and news archives. It works poorly on tightly structured, information-dense sequences.

---

## Tiny Numeric Example

**Processing a 128K-token legal document:**

| Method | Peak Memory | Time per Layer | Retrieval Accuracy | F1 on QA |
|---|---|---|---|---|
| Full attention | 256 GB | 120 ms | 97.0% | 0.87 |
| Hierarchical (32:1) | 2.1 GB | 8.2 ms | 94.2% | 0.84 |
| Memory layers | 1.8 GB | 6.5 ms | 91.5% | 0.81 |
| Prompt compression | 1.2 GB | 5.1 ms | 88.3% | 0.78 |
| Truncation (last 4K) | 0.5 GB | 3.8 ms | 62.0% | 0.55 |

**Breakdown of hierarchical compression:**
```
Input:               128,000 tokens
Chunk size:          1,024 tokens
Number of chunks:    125
Summary per chunk:   32 tokens
Coarse attention:    125 summaries = 4,000 tokens
Selected chunks:     2 chunks expanded = 2,048 tokens
Total attended:      6,048 tokens
Compression ratio:   128,000 / 6,048 ≈ 21:1
Memory saved:        256 GB → 3.2 GB (98.8% reduction)
```

**Quality trade-off:**
```
Full context:        answers 97% of questions correctly
Hierarchical:        answers 94% correctly (misses 3% due to summary errors)
Truncation:          answers 55% correctly (misses 42% because relevant info was cut)
```

**The shift:** Context compression reduces memory by 98% and latency by 93% while sacrificing only 3% accuracy. Truncation achieves similar speed but destroys accuracy because it discards information rather than distilling it.

---

## Common Confusion

1. **"Context compression is the same as truncation."** Truncation discards information permanently; compression attempts to preserve it in a compact form. Truncation is fast but destructive; compression is slower but reversible.

2. **"Context compression eliminates the need for long-context models."** Compression handles redundancy, but some tasks require attending over every token. A model with native long-context support is still valuable for incompressible sequences.

3. **"Compression is lossless."** Most compression methods lose some information. The art is minimizing loss on the dimensions that matter for the downstream task.

4. **"Context compression is the same as retrieval-augmented generation."** RAG fetches relevant passages from an external store; compression distills a long passage into a shorter one. They are complementary: RAG selects what to read, compression shortens what is read.

5. **"Compression happens only at inference time."** Some methods pre-compress documents into memory banks during indexing, while others compress on the fly during the forward pass.

6. **"A higher compression ratio is always better."** Aggressive compression can destroy nuanced information. The optimal ratio depends on the task: summarization tolerates high compression; precise legal reasoning does not.

7. **"Context compression is only for text."** The same principles apply to long video sequences, audio waveforms, and time-series sensor data where only a fraction of the timeline is relevant to any given query.

---

## Where It Is Used in Our Code

`src/phase97/phase97_long_context.py` — We simulate a long sequence of tokens and apply hierarchical chunking with a coarse attention layer over chunk summaries and a fine attention layer over selected chunks. We measure the effective sequence length, compute the memory savings compared to full attention, and plot the accuracy versus compression ratio trade-off curve.
