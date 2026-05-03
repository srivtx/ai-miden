# What is KV Cache Management?

## Why it exists (THE PROBLEM first)

In transformer inference, computing attention for token N requires the key and value vectors for tokens 1 through N. Recomputing them from scratch every step would make generation impossibly slow. Storing them in a cache saves compute but consumes enormous amounts of high-bandwidth GPU memory. Poor management of that memory limits batch size and sequence length.

## Definition (very simple)

KV cache management is the set of techniques used to store, organize, and reuse key and value tensors during autoregressive generation while minimizing memory overhead and fragmentation.

## Real-life analogy

Reading a long novel, you keep notes on each chapter's characters and plot so you do not have to re-read earlier chapters to understand the current one. The notebook is your cache. Good management means organizing notes efficiently so the notebook does not fill up after chapter three.

## Tiny numeric example

A 1-billion-parameter model with 24 layers, hidden size 2048, and batch size 8 processing sequences of length 1024 stores roughly 8 * 1024 * 24 * 2048 * 2 (keys and values) * 2 bytes = 1.6 GB in the KV cache. Doubling batch size doubles this to 3.2 GB, which can exceed GPU memory if not managed carefully.

## Common confusion

- **The KV cache is not the model weights.** Weights are static and shared; the KV cache grows with every new token generated.
- **Management is not just allocation.** It also includes eviction, swapping to CPU memory, and sharing across beams.
- **A larger cache does not mean better quality.** It means faster generation; quality comes from the model weights.
- **KV cache management is not automatic in all frameworks.** Some require manual tuning of cache size and block allocation.
- **It is not only for decoding.** Prefix caching for prompt processing also uses KV cache management.

## Where it is used in our code

In `src/phase90/phase90_inference_serving.py`, we simulate sequences of varying lengths sharing a fixed total cache budget. We compare naive per-sequence allocation against paged block allocation, demonstrating that intelligent management directly determines how many concurrent requests can be served.
