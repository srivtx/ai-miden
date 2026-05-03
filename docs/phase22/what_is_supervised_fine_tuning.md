### 1. Why it exists (THE PROBLEM first)
A pre-trained GPT can generate fluent text, but it does not answer questions helpfully. If you ask "What is the capital of France?" it might ramble: "Paris is a beautiful city with many landmarks..." instead of simply answering "Paris." The model knows language, but it has not learned the *format* of being a useful assistant.

### 2. Definition (very simple)
Supervised Fine-Tuning (SFT) is the process of taking a pre-trained language model and continuing to train it on a curated dataset of (instruction, response) pairs so that it learns to follow conversational structure and produce helpful, on-topic answers.

### 3. Real-life analogy
Imagine a novelist who can write beautiful prose but has never done a job interview. You hand them a long list of common questions and concise, polite answers. After studying these pairs, the novelist learns not just *what* to say, but *how* to answer—directly, helpfully, and in the right tone.

### 4. Tiny numeric example
Training data:
```
[("What is 2+2?", "4"),
 ("Explain gravity.", "Gravity is a force that attracts objects with mass toward each other.")]
```
During SFT, the model sees the prompt "What is 2+2?" and is trained to maximize the probability of generating the token sequence "4". It learns the pattern: after a user question, provide a concise answer.

### 5. Common confusion
- **SFT does not teach the model new world facts.** It mainly teaches *style* and *format*; the knowledge usually comes from the earlier pre-training phase.
- **SFT is not the same as pre-training.** Pre-training uses billions of raw web pages; SFT uses thousands or millions of curated Q&A pairs.
- **SFT is not reinforcement learning.** There is no reward model or policy gradient; it is ordinary supervised next-token prediction.
- **More data is not always better.** Low-quality SFT data can teach the model to ramble or hallucinate, so curation matters more than scale.
- **SFT alone does not guarantee safety.** A model can still produce harmful outputs after SFT because it has only learned form, not human values.

### 6. Where it is used in our code
Brief mention: SFT is typically the second stage of our training pipeline, applied right after pre-training to adapt the base model into an instruction-following assistant.
