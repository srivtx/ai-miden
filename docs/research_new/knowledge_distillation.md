# Research: Knowledge Distillation

**Status:** Missing from course. Should be Phase 39.
**Last Updated:** May 2026
**Sources:** Hinton et al. (2015), DistilBERT (2019), TinyLlama (2023), MiniCPM (2024)

---

## 1. The Problem

You trained a huge model (70B parameters) that works great but is too slow and memory-hungry for phones, edge devices, or low-latency APIs. You need a much smaller model (7B or even 0.5B) that behaves similarly. Fine-tuning the small model from scratch on the same data does not work — it lacks the "dark knowledge" the large model learned. How do you transfer the large model's capabilities to a tiny one?

## 2. What It Is

**Knowledge distillation** trains a small "student" model to mimic a large "teacher" model. Instead of training on ground-truth labels, the student learns from the teacher's soft probability distributions.

**Key insight:** The teacher's probabilities contain rich information. If the teacher outputs:
```
cat: 0.70, dog: 0.25, fox: 0.05
```
The ground truth label is just "cat." But the teacher's distribution tells the student that "dog" is much more similar to "cat" than "fox" is. This is "dark knowledge" that helps the student generalize.

**Loss function:**
```
L = α × CE(student_logits, teacher_soft_labels) + (1-α) × CE(student_logits, hard_labels)
```

**Temperature scaling:** Both teacher and student logits are divided by temperature T before softmax. Higher T (e.g., T=4) produces softer distributions with more information in the relative probabilities of incorrect classes.

## 3. Real-World Analogy

A master chef (teacher) and an apprentice (student).
- **Standard training:** The apprentice reads recipe books (ground-truth labels). They learn basic techniques but miss the nuances.
- **Distillation:** The apprentice watches the master cook and tastes the master's dishes. The master might say: "This sauce is 70% French, 25% Italian, 5% Asian." The apprentice learns not just what the dish is, but what it is similar to. They internalize the master's intuition.

The temperature T controls how much the master explains their reasoning. High T = detailed explanations of why alternatives were rejected. Low T = just the final answer.

## 4. Key Technical Details

### Soft Targets
```
teacher_soft = softmax(teacher_logits / T)
student_soft = softmax(student_logits / T)
loss_distill = KL_divergence(student_soft, teacher_soft) × T²
```

The T² scaling compensates for the fact that gradients shrink by 1/T² when using high temperature.

### DistilBERT
- 40% smaller than BERT, 60% faster
- Retains 97% of BERT's language understanding
- Trained with triple loss: distillation + masked language modeling + cosine embedding loss

### TinyLlama
- 1.1B parameters, trained on 3 trillion tokens
- Distilled from larger Llama models during pre-training
- Outperforms much larger models on reasoning tasks

### Logit Matching vs. Hidden-State Matching
- **Logit matching:** Student mimics teacher's output probabilities (classic distillation)
- **Hidden-state matching:** Student mimics teacher's intermediate layer representations (used in MiniLM, MobileBERT)
- **Attention matching:** Student mimics teacher's attention maps

## 5. Common Confusion

- **Distillation is not pruning.** Pruning removes weights from the same model. Distillation trains a completely new, smaller model.
- **Distillation is not quantization.** Quantization uses fewer bits for the same model. Distillation creates a smaller architecture.
- **The teacher does not need to be perfect.** A slightly wrong teacher can still transfer useful structure. But a very wrong teacher teaches bad habits.
- **Temperature matters.** T=1 is usually suboptimal. T=2-5 is common. The best T depends on the task.
- **Distillation works best when the student is not too small.** Distilling 70B → 7B works well. 70B → 100M often fails because the student lacks capacity.

## 6. What We Would Build

A toy demonstration where:
- A large teacher network classifies points into 3 categories
- A small student is trained on hard labels only (baseline)
- Another student is trained with distillation from the teacher
- The distilled student outperforms the baseline

## 7. Why It Matters Now

- **Edge AI:** Phones and IoT devices need tiny models
- **API cost:** Smaller models are 10-100× cheaper to serve
- **Real-time:** Latency-critical applications need fast inference
- **Environmental:** Smaller models use less energy
- **DistilBERT, TinyLlama, Phi, MiniCPM** all use distillation

## 8. Connection to Existing Phases

- **Phase 25 (Inference Optimization):** Distillation creates smaller models that are faster to run
- **Phase 35 (LoRA):** Distillation and LoRA are complementary — distill once, then LoRA-adapt
- **Phase 38 (Scaling Laws):** Distillation is how we get small models with large-model quality

---

## References

- Hinton et al. (2015): "Distilling the Knowledge in a Neural Network"
- Sanh et al. (2019): "DistilBERT, a distilled version of BERT"
- Zhang et al. (2024): "MiniCPM: Unveiling the Potential of Small Language Models"
