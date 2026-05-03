## What Is SFT?

---

### The Problem

A pre-trained language model knows grammar, facts, and patterns from the internet. But it does not know how to follow instructions. Ask it "What is 2+2?" and it might respond with "The question 'What is 2+2?' is a common arithmetic query..." How do you teach it to answer directly, politely, and helpfully?

---

### Definition

**SFT (Supervised Fine-Tuning)** is the process of training a pre-trained model on a dataset of (instruction, response) pairs to teach it how to follow commands, answer questions, and behave as an assistant.

**How SFT works:**
```
1. Start with a pre-trained model (e.g., Llama-2, GPT-2)
2. Collect instruction-response pairs (e.g., Alpaca, ShareGPT)
3. Format each pair with a chat template
4. Train the model with next-token prediction on the responses
5. The instruction part is masked (loss only computed on the assistant's response)
```

**The loss function:**
```
Loss = -Σ log P(response_token | instruction + prior_response_tokens)
```

**Why this works:**
- The model already knows language from pre-training
- SFT only teaches it the assistant format and behavior
- It learns patterns like: after "<|assistant|>", I should give a direct answer

**SFT is the first step in building any chatbot:**
- GPT-3 → GPT-3.5: SFT on instruction data
- Llama-2 base → Llama-2 chat: SFT on synthetic instructions
- Every production assistant starts with SFT before RLHF/DPO

---

### Real-Life Analogy

Hiring a brilliant but socially awkward professor as a teaching assistant.
- **Pre-training:** The professor has read every book. They know everything.
- **SFT:** You give them 50,000 example office hours. Each example shows a student question and the ideal TA response. The professor practices answering in the TA format.
- **Result:** The professor still knows everything, but now they answer "x = 5" instead of launching into a 20-minute lecture on algebraic history.

---

### Tiny Numeric Example

**Training example:**
```
<|user|>
What is the capital of France?
<|assistant|>
The capital of France is Paris.
```

**Loss computation:**
```
Tokens: [<|user|>, What, is, the, capital, of, France, ?, <|assistant|>, The, capital, of, France, is, Paris, .]

Loss on "The":   -log P(The   | ... <|assistant|>)
Loss on "capital": -log P(capital | ... <|assistant|> The)
Loss on "of":     -log P(of     | ... <|assistant|> The capital)
...

User tokens are masked (loss = 0):
Loss on "What":   0 (masked)
Loss on "is":     0 (masked)
```

The model only learns to generate the assistant's response.

**After 10,000 such examples:**
- The model learns that after "<|assistant|>" it should answer directly
- It learns to be concise, helpful, and accurate
- It does not learn new facts (those come from pre-training)

---

### Common Confusion

1. **"SFT teaches new knowledge."** No. It teaches format and behavior. Facts come from pre-training.

2. **"SFT makes the model safe."** No. SFT teaches helpfulness, but models can still generate harmful content. Safety comes from RLHF/DPO.

3. **"SFT and instruction tuning are different."** They are the same thing. "Instruction tuning" is the concept; "SFT" is the implementation.

4. **"You need millions of examples for SFT."** No. 1,000-10,000 high-quality examples often suffice because the model already knows language.

5. **"SFT changes the model's personality."** Yes, if the training data has a consistent style. A formal dataset produces a formal assistant. A casual dataset produces a casual assistant.

---

### Where It Is Used in Our Code

`src/phase64/phase64_sft_lora_colab.py` — We load a pre-trained model, prepare instruction-response data with chat templates, and run supervised fine-tuning with LoRA adapters using the HuggingFace ecosystem.
