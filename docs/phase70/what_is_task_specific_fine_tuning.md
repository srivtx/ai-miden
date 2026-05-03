## What Is Task-Specific Fine-Tuning?

---

### The Problem

Your model has absorbed a domain's language through continual pre-training. It understands medical abbreviations and legal terminology. But when a doctor asks it to "summarize this patient's history in three sentences," the model rambles for ten paragraphs. Knowing the language is not the same as knowing what to do with it. The model needs to learn the *format* of tasks: how to summarize, how to classify, how to answer multiple-choice questions, how to generate structured output. How do you teach it these specific skills?

---

### Definition

**Task-Specific Fine-Tuning** (also called Supervised Fine-Tuning or SFT) is training a model on labeled examples of the exact tasks you want it to perform. Each example is an (input, output) pair showing the model what correct behavior looks like.

**How it works:**
```
Input:  "Summarize: The patient is a 67-year-old male with a history of..."
Output: "67-year-old male with hypertension and new-onset dyspnea."

Loss:   model's predicted output is compared to the true output
Update: weights are adjusted to make the model more likely to produce the true output
```

**Common task formats:**
- **Classification:** input = text, output = label ("positive", "negative")
- **Summarization:** input = long document, output = short summary
- **Question answering:** input = context + question, output = answer span
- **Code generation:** input = docstring, output = function implementation

**Why this matters:**
- A model that knows medical language but has never seen a summarization example will produce unstructured walls of text
- Just 1,000 high-quality task examples can transform a domain-aware model into a useful assistant
- Task-specific fine-tuning is what turns a "language model" into a "product"

---

### Real-Life Analogy

Learning to drive after studying the traffic code.
- **Continual pre-training:** You read the entire driver's manual. You know what a yield sign means, what double yellow lines mean, and how to parallel park in theory.
- **Task-specific fine-tuning:** You get behind the wheel with a driving instructor. They say "turn left here" and you do it. They say "merge onto the highway" and you practice. Each instruction is a labeled (situation, action) pair.
- **The result:** After enough practice, you can drive without the instructor. You have learned the *task* of driving, not just the *language* of traffic laws.

Reading the manual alone does not make you a driver. You need supervised practice on real tasks.

---

### Tiny Numeric Example

**Task: Classify patient notes as "urgent" or "routine"**

**Training data (5 examples):**
```
Input:  "Patient reports chest pain radiating to left arm."
Output: "urgent"

Input:  "Annual physical, no complaints, vitals stable."
Output: "routine"

Input:  "Fever 39C, confusion, neck stiffness."
Output: "urgent"

Input:  "Follow-up for hypertension medication refill."
Output: "routine"

Input:  "Sudden vision loss in right eye."
Output: "urgent"
```

**Model behavior before task-specific fine-tuning:**
```
Input:  "Severe abdominal pain, vomiting blood."
Output: "The patient may have gastrointestinal bleeding..."  ← rambling, wrong format
Accuracy: 0% (does not output the required label)
```

**Model behavior after fine-tuning on 1,000 examples:**
```
Input:  "Severe abdominal pain, vomiting blood."
Output: "urgent"
Accuracy: 94/100 correct (94%)
```

**Loss curve during fine-tuning:**
```
Epoch 1: cross-entropy loss = 1.85
Epoch 5: cross-entropy loss = 0.42
Epoch 10: cross-entropy loss = 0.18
```

The model learns to map inputs to the exact output format required by the task.

---

### Common Confusion

1. **"Task-specific fine-tuning is the same as prompt engineering."** No. Prompt engineering changes the input text to elicit better outputs without changing model weights. Fine-tuning changes the weights so the model naturally produces better outputs.

2. **"More task data always means better results."** Not if the data is low quality. Fifty perfectly labeled examples often beat five thousand noisy ones. Data quality dominates quantity in fine-tuning.

3. **"Fine-tuning fixes factual errors."** No. Fine-tuning teaches format and style. If the model never saw a specific drug interaction in pre-training, fine-tuning cannot invent it. You need retrieval or continual pre-training for facts.

4. **"You should fine-tune on one task at a time."** Multi-task fine-tuning (mixing summarization, QA, and classification examples) often produces better generalization than single-task training because the model learns shared reasoning patterns.

5. **"Fine-tuning requires a powerful GPU cluster."** With LoRA or QLoRA, you can fine-tune a 7B model on a single consumer GPU with 16GB VRAM. Full fine-tuning is expensive; parameter-efficient fine-tuning is not.

6. **"Fine-tuning makes the model overfit to the training examples."** It can, if you train too long. But early stopping, dropout, and diverse training data prevent memorization. A well-tuned model generalizes to new inputs.

7. **"Task-specific fine-tuning is only for NLP."** False. Vision models are fine-tuned for object detection, segmentation, and medical diagnosis. Speech models are fine-tuned for speaker identification and transcription. The principle is universal.

---

### Where It Is Used in Our Code

`src/phase70/phase70_domain_adaptation.py` — We simulate task-specific fine-tuning by training a base model on labeled domain task examples and measuring accuracy before and after. We compare the domain-adapted model against the base model on both domain-specific and general-purpose test sets.
