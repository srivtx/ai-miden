# What Is Context Compression?

## Problem
Long contexts are expensive to attend over, and many tokens in a long document are redundant or irrelevant to the current task. Feeding the entire context wastes compute and memory.

## Definition
Context Compression is the process of distilling a long context into a shorter, dense representation while preserving relevant information. Methods include hierarchical attention, memory layers, prompt compression, and learned compression tokens.

## Analogy
Reading a 500-page textbook for a single fact is inefficient. Context compression is like having a detailed index: you still have the knowledge, but you only retrieve the relevant pages when needed.

## Example
In hierarchical attention, a document is chunked into paragraphs. A "coarse" attention layer reads paragraph summaries, and a "fine" layer reads only the selected paragraph in full. This avoids quadratic attention over the entire book.

## Common Confusion
Context compression is not the same as truncation. Truncation discards information; compression attempts to preserve it in a compact form. It is also distinct from retrieval-augmented generation, though the two can be combined.

## Code Location
See `src/phase97/phase97_long_context.py` for a discussion of context scaling strategies.
