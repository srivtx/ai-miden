## What Is Long Context Training?

---

### The Problem

You have successfully scaled the RoPE embeddings to handle 32K tokens. The model no longer crashes on long inputs. But when you actually feed it a 20,000-token legal document and ask a question about paragraph three, the model hallucinates or answers based on the conclusion instead. The position encodings work, but the model's attention layers have never learned to retrieve information from the distant past. The weights were trained on 4K sequences where every token is nearby. Long-context capability requires more than embedding tricks — it requires training the model to attend, reason, and remember across thousands of tokens. How do you prepare data and training infrastructure for this?

---

### Definition

**Long context training** is the process of continuing to train a pretrained language model on sequences longer than its original training context, using scaled position embeddings and specialized data formatting, so that the model learns to use the extended context window for retrieval, reasoning, and coherence across long documents.

**How it works:**
```
Standard training:
  Sequences: 4096 tokens
  Attention: every token attends to 4095 previous tokens
  What the model learns: local coherence, paragraph structure,
    short-range dependencies

Long context training:
  1. Scale RoPE (PI, NTK, or YaRN) to target length (e.g., 32K)
  2. Prepare long-sequence data:
     - Concatenate documents with separator tokens (packing)
     - Or pad single long documents to fixed length
  3. Continue pre-training or fine-tuning:
     - Learning rate: 10-100× smaller than pre-training
     - Steps: 100-1000 (much less than pre-training)
     - Batch size: small per device, large effective via gradient accumulation
  4. Evaluate with long-context benchmarks:
     - Perplexity on long sequences
     - Needle-in-haystack: hide a fact, ask model to retrieve it
     - Long-document QA: answer questions about distant passages
```

**Key techniques:**
- **Packing:** concatenate multiple short documents into one long sequence, separated by EOS tokens. Maximizes token utilization but creates artificial boundaries.
- **Padding:** use single long documents, pad to fixed length. More natural but wastes compute on padding tokens.
- **Ring attention:** for extremely long sequences (100K+), split attention computation across multiple devices so no single GPU holds the full attention matrix. Each device computes a "ring" segment.
- **Gradient accumulation:** process small micro-batches that fit in GPU memory, accumulate gradients over many steps, then update weights. Simulates a large batch size without large memory.

**Why this matters:**
- Long-context models can process entire books, legal contracts, code repositories, and multi-turn conversations
- Without training, scaled RoPE alone gives "functional" long context but not "useful" long context
- Training cost is 100-1000× cheaper than pre-training from scratch
- Needle-in-haystack accuracy improves from <10% to >90% after just 100 steps of fine-tuning

---

### Real-Life Analogy

Imagine a student who has only ever read short stories of 4 pages. You give them glasses that let them see 32 pages at once (scaled RoPE), but they have never practiced connecting ideas across 30 pages.

- **Without training:** The student reads a 30-page legal contract. They can see all the words, but when you ask "What was the penalty clause on page 5?" they guess based on the last page they read. They have the physical ability to see distant text but not the mental habit of retrieving it.
- **With long-context training:** You make the student read 100 long novels and answer detailed questions about early chapters. At first they fail. After practice, they learn to bookmark key facts, skip irrelevant sections, and connect distant passages. The glasses (scaled embeddings) enable vision; the practice (training) enables comprehension.
- **Packing vs padding:** Packing is like reading an anthology of short stories bound into one thick book — efficient use of paper, but the stories do not connect. Padding is like reading one long novel with blank pages inserted to make every book exactly 32 pages — natural when there is content, wasteful when there is not.

---

### Tiny Numeric Example

**Training configuration for extending 4K → 8K:**
```
Original model: trained on 4K sequences for 1 trillion tokens
Long-context fine-tuning:
  Target length: 8192 tokens (2× extension)
  RoPE scaling: YaRN with s=2.0, t=1.07
  Data: 50,000 book passages from Gutenberg
  Sequence packing: 4 short passages per 8K sequence
  
  Training hyperparameters:
    Batch size per device: 1 (8K tokens needs ~8GB just for activations)
    Gradient accumulation: 8 steps
    Effective batch size: 8
    Learning rate: 1e-5 (100× smaller than pre-training lr)
    Steps: 100
    Warmup: 10 steps
    
  Compute cost:
    ~800 forward/backward passes
    ~2 hours on a single T4 GPU
    vs. pre-training cost: ~$1,000,000 and 3 months
```

**Needle-in-haystack evaluation:**
```
Test: "The secret code is 7291. Remember this number."
  Hidden at position 500, 2000, 4000, 6000, 7500 in an 8K document
  
  Question: "What is the secret code?"

Results before fine-tuning (scaled RoPE only):
  Position 500:   85% accuracy (near beginning, model knows this)
  Position 2000:  60% accuracy
  Position 4000:  30% accuracy
  Position 6000:  10% accuracy
  Position 7500:   5% accuracy  (beyond training length, guessing)

Results after 100 steps fine-tuning:
  Position 500:   92% accuracy
  Position 2000:  88% accuracy
  Position 4000:  85% accuracy
  Position 6000:  82% accuracy
  Position 7500:  78% accuracy
  
  Improvement: from random guessing at 7500 to reliable retrieval
```

**Perplexity comparison:**
```
Perplexity on 8K book passages:
  Original 4K model (unscaled):      fails (OOM or >1000 PPL)
  Scaled RoPE, no fine-tuning:       PPL = 18.5
  After 50 steps fine-tuning:        PPL = 14.2
  After 100 steps fine-tuning:       PPL = 12.8
  After 500 steps fine-tuning:       PPL = 11.5 (diminishing returns)
  
Key insight: most gains happen in the first 100 steps
```

---

### Common Confusion

1. **"Scaled RoPE is enough; training is unnecessary."** For very simple tasks, yes. For retrieval, reasoning, and coherent generation across long distances, training is essential. Scaled RoPE gives the model the *potential* for long context; training teaches it to *use* that potential.

2. **"Long context training requires millions of long documents."** No. Even 10,000-50,000 long sequences are sufficient for fine-tuning because the model already knows language. You are not teaching it English; you are teaching it to use its existing knowledge across longer spans. Quality matters more than quantity.

3. **"Ring attention is the same as flash attention."** Flash Attention optimizes the memory layout of attention on a single GPU. Ring Attention distributes attention computation across multiple GPUs so that no single device holds the full sequence. They solve different problems and can be combined.

4. **"Gradient accumulation increases memory usage."** No. Gradient accumulation keeps the *activation* memory the same (micro-batch size is small) while increasing the effective batch size by accumulating gradients in a buffer. The only extra memory is for the gradient buffer, which is tiny compared to activations.

5. **"Packing is always better than padding."** Packing is more compute-efficient (fewer padding tokens), but it creates artificial document boundaries within a sequence. The model may learn spurious cross-document attention. Padding is simpler and cleaner but wastes compute. Many implementations use a hybrid: pack related documents, pad single long ones.

6. **"Long context training hurts short-context performance."** Usually not, if done correctly with small learning rates and early stopping. The model retains its 4K capabilities while gaining 8K+ capabilities. In some cases, short-context perplexity actually improves because the model learns better global coherence.

7. **"You need a 80GB GPU to train 32K context."** With gradient checkpointing, Flash Attention, and small micro-batches, 16GB (T4) can handle 8K context for 3B models. 32K needs more memory or model parallelism, but 8K is accessible on consumer hardware.

---

### Where It Is Used in Our Code

`src/phase125/phase125_long_context_concepts.py` — We simulate the long-context training pipeline in NumPy: generating packed sequences, computing effective batch size via gradient accumulation, and showing how perplexity improves over training steps. We visualize the needle-in-haystack accuracy curve before and after simulated adaptation.

`src/phase125/phase125_long_context_colab.py` — We implement the full pipeline on a T4 GPU: loading LLaMA-3.2-3B, applying YaRN scaling, creating 8K-token training data from Gutenberg texts, fine-tuning with gradient accumulation for 100 steps, and evaluating with needle-in-haystack tests at multiple positions. We plot perplexity comparison, training loss, and needle accuracy versus position.
