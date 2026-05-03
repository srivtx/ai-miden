### 1. Why it exists (THE PROBLEM first)
For decades, AI was a collection of narrow specialists: one model for speech recognition, another for chess, another for medical diagnosis. Each required custom datasets, custom architectures, and custom training. This was expensive, slow, and brittle. The breakthrough insight: train ONE enormous model on an enormous variety of data, and it becomes a generalist that can handle hundreds of tasks with minimal fine-tuning.

### 2. Definition (very simple)
A Foundation Model is a large-scale neural network trained on broad, diverse data (text, images, code, etc.) using self-supervision, such that it acquires general-purpose capabilities. It can then be adapted — via prompting, fine-tuning, or in-context learning — to specific downstream tasks without training from scratch.

### 3. Real-life analogy
A Swiss Army knife. Instead of carrying a separate knife, scissors, screwdriver, can opener, and corkscrew, you carry one compact tool. Each specialized tool is still there, folded into the handle. The Swiss Army knife is not the best at any single task compared to a dedicated tool, but it is good enough at almost everything — and far more convenient.

### 4. Tiny numeric example
Traditional AI pipeline:
- Task 1 (sentiment): Train model A on 10K labeled reviews. Cost: $100.
- Task 2 (translation): Train model B on 100K parallel sentences. Cost: $500.
- Task 3 (summarization): Train model C on 50K articles. Cost: $300.
- Total cost: $900. Three separate models to maintain.

Foundation model pipeline:
- Pre-train one GPT on 1 trillion tokens. Cost: $10M (one-time).
- Task 1: Prompt with "Classify sentiment: 'I loved it' →". Cost: $0.01.
- Task 2: Prompt with "Translate to French: 'Hello' →". Cost: $0.01.
- Task 3: Prompt with "Summarize: [article] →". Cost: $0.01.
- Total cost after pre-training: ~$0.03 per task. One model for everything.

The economics only work because the foundation model is reused millions of times across thousands of tasks, amortizing the pre-training cost.

### 5. Common confusion
- **Foundation models are not magic.** They are just large neural networks trained on lots of data. All the principles from Phases 0–31 still apply: gradients, backprop, attention, transformers.
- **"Foundation" does not mean "finished."** A foundation model is a starting point. It usually needs fine-tuning or prompting to perform well on a specific task.
- **Scale matters.** A 1-billion-parameter model is not a foundation model in the same sense as a 100-billion-parameter model. The emergent capabilities (reasoning, in-context learning) appear at scale.
- **They are expensive to train but cheap to use.** Pre-training GPT-4 cost an estimated $100M. But each API call costs fractions of a cent. This is the cloud computing model applied to AI.
- **Not all foundation models are LLMs.** BERT, GPT, CLIP, Stable Diffusion, and Whisper are all foundation models — they span text, vision, audio, and multimodal domains.

### 6. Where it is used in our code
`src/phase32/phase32_foundation_models.py` reflects on how our tiny GPT (from Phase 21) is a miniature foundation model: pre-trained on text, then adaptable to multiple tasks through prompting.
