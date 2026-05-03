## What Is Interleaved Pretraining?

---

### The Problem

Most vision-language datasets are pairs: one image with one caption. A model trained on millions of pairs learns to describe images, but it never learns to reason about images embedded inside long documents. It cannot follow a tutorial that says "as shown in Figure 3," refer back to an image from three paragraphs ago, or generate a document that alternates between text and diagrams. How do you train a model to treat images as native elements of long-form content?

---

### Definition

**Interleaved pretraining** is a multimodal training regime in which text and images are mixed together in a single token sequence, mimicking the layout of real-world documents. The model is trained with standard next-token prediction on this mixed sequence, learning to refer to, describe, and generate images in context.

**How it works:**
```
Document:
  "The equation is shown below:"
  [image of equation]
  "where x represents time."
  [image of graph]
  "Figure 2 shows the result..."

Token sequence:
  ["The", "equation", "is", "shown", "below", ":",
   <image_start>, 502, 17, ..., 8991, <image_end>,
   "where", "x", "represents", "time", ".",
   <image_start>, 301, 12, ..., 44, <image_end>,
   "Figure", "2", "shows", "the", "result", "..."]
  → Next-token prediction on the entire sequence
```

**Key techniques:**
- **Document-level scraping:** extract web pages, textbooks, and scientific papers with inline images.
- **Special boundary tokens:** `<image_start>` and `<image_end>` delimit visual regions in the sequence.
- **Balanced sampling:** ensure the ratio of image tokens to text tokens stays within a stable range to prevent gradient spikes.

**Why this matters:**
- Paired captioning data teaches shallow associations. Interleaved data teaches deep reasoning: referring, comparing, and summarizing visual information across long contexts.
- Models trained on interleaved data transfer better to document understanding, user interfaces, and scientific literature.
- It is the only viable way to train native multimodal models that generate both text and images in one stream.

---

### Real-Life Analogy

Learning from flashcards versus learning from a textbook. A flashcard shows one picture with one caption on the front and back. You learn that this picture maps to that sentence, but you never learn how the picture fits into a larger argument. A textbook interleaves paragraphs, equations, figures, and tables. To understand the chapter, you must connect the text on page 10 to the diagram on page 14 and the table on page 20. Interleaved pretraining is the textbook. The model learns to maintain attention across modalities over long distances. The trade-off is that textbook data is harder to curate than flashcards; you need high-quality documents with meaningful image placement, not random memes inserted into spam text.

---

### Tiny Numeric Example

**Captioning sequence (paired data):**
```
Length: 256 image tokens + 4 text tokens = 260 tokens
Attention pattern: image tokens attend locally to each other; text tokens attend to all image tokens.
Context: single image, single sentence.
```

**Interleaved sequence (document data):**
```
Length: 20 text tokens + 256 image tokens + 10 text tokens + 256 image tokens + 15 text tokens
Total: ~557 tokens
Attention pattern: text token "Figure 2" attends to second image block;
                  text token "equation" attends to first image block.
Context: multiple images referenced by text at varying distances.
```

**Training stability:**
```
Captioning batch gradient norm: 1.2
Interleaved batch gradient norm: 3.8 (higher due to image token density)
Solution: gradient clipping at 1.0 and image-token weight decay.
```

---

### Common Confusion

1. **"Interleaved data is just more captioning pairs pasted together."** No. The images and text are part of a single coherent document, not independent pairs concatenated arbitrarily.

2. **"It requires special position embeddings for images."** Yes. Flattened image tokens need 2D-aware position encodings or explicit coordinate tags to retain spatial structure.

3. **"Training is less stable because images dominate gradients."** True. Image patches are dense and can produce larger gradient norms than sparse text tokens. Clipping and domain balancing are essential.

4. **"Interleaved pretraining is only for multimodal models."** It also benefits document understanding, web-agent training, and any task where visual layout matters.

5. **"Any scraped webpage works as interleaved data."** Most web pages are low-quality. You need filtering for coherent documents where images are genuinely referenced by the surrounding text.

6. **"Models trained on interleaved data are worse at pure text."** If text-only data is underrepresented, yes. A healthy mix retains text competence while adding visual reasoning.

7. **"Interleaved means alternating every single token."** It means mixing at the document level: paragraphs of text interspersed with blocks of image tokens, not a strict text-image-text-image alternation.

---

### Where It Is Used in Our Code

`src/phase118/phase118_multimodal_concepts.py` — We build an interleaved token sequence from simulated text and image tokens, then visualize the sequence structure and show how a single attention layer can connect text tokens to distant image tokens. We contrast this with paired captioning data where the context window is shallow.
