## Why it exists (THE PROBLEM)

A 70B model is expensive to serve. Every inference costs money. But you don't need 70B parameters for most tasks — you need the KNOWLEDGE, not the size. A distilled 7B model trained to imitate the 70B model's outputs can achieve 90% of the quality at 10% of the cost.

**Knowledge distillation** compresses a large "teacher" model into a small "student" model. The student doesn't just learn from ground-truth labels — it learns from the teacher's SOFT predictions (the full probability distribution, not just the argmax). This transfers the teacher's uncertainty, its "maybe this is answer A but B is also possible" knowledge.

## Definition (very simple)

**Standard training:** Student learns from hard labels: `target = [0, 0, 1, 0]` (correct answer is class 2).

**Distillation:** Student learns from teacher's soft labels: `teacher_output = [0.05, 0.02, 0.85, 0.08]` (teacher is 85% sure it's class 2, but thinks class 3 has 8% chance). The student learns: "this example looks similar to class 3" — knowledge that hard labels don't provide.

**The loss:** `L = alpha * L_hard(pred, label) + (1-alpha) * L_soft(pred/T, teacher/T)`. Where T (temperature) > 1 softens the teacher's predictions, making the distribution smoother. Higher T = more weight on the teacher's "almost-right" answers.

## Tiny numeric example

Teacher model (70B) predicts for code completion `def add(a, b):\n    `:
```
"return"  : 0.45
"result"  : 0.20  
"a"       : 0.15
"answer"  : 0.08
"out"     : 0.05
...       : 0.07
```

**Hard label:** `"return"` (highest probability). Student learns: "the answer is `return`."

**Soft label (T=2):** `"return": 0.35, "result": 0.22, "a": 0.18, ...`. Student learns: "the answer is probably `return`, but `result` and `a` are also reasonable in this context." This is DARK KNOWLEDGE — the teacher knows which wrong answers are "close" to right, and the student absorbs this.

The student trained with soft labels generalizes better because it understands the RELATIONSHIPS between tokens, not just the correct answer.

## Key recipe (for cortexcode)

Given a large teacher model (e.g., a fine-tuned CodeLlama 7B) and a small student (cortexcode 10M):

1. Collect 10,000 prompts from the target codebase
2. For each prompt: teacher generates probability distribution over next token (soft labels)
3. Store (prompt, teacher_logits) pairs
4. Train student on: `loss = 0.5 * cross_entropy(student_logits, ground_truth) + 0.5 * KL_div(student_logits/T, teacher_logits/T) * T^2`
5. Student learns 90% of teacher quality at 10M params

The magic: the 10M student trained with distillation outperforms a 10M student trained from scratch on the same data. It's not about more data — it's about richer supervision.

## Key properties

| | From scratch | Distilled |
|---|---|---|
| Data efficiency | 100% of data needed | 30-50% (teacher provides richer signal) |
| Generalization | Limited by model size | Improved (teacher transfers patterns) |
| Training time | Same | Same (one extra forward pass on teacher per batch) |
| Model size | Student only | Teacher + student (teacher discarded after) |
| Quality at small scale | Low | Medium (matches teacher's quality curve) |

## Common confusion

1. **"Distillation is just compression."** It's richer than compression. Compression (quantization, pruning) reduces model size AFTER training. Distillation trains a NEW model that learns the teacher's REASONING patterns. A 7B compressed to 7B INT4 is 7B params in 4-bit. A 7B distilled to 1B is 1B params. Different approach, same goal, but distillation preserves more nuance.

2. **"Temperature T just makes things softer."** T controls what the student learns. Low T (1-2): student focuses on the teacher's most confident predictions (like hard labels). High T (5-20): student learns the teacher's uncertainty and relationships between classes. T=1 is standard softmax. Non-intuitive: the loss includes a T^2 scaling factor to keep gradient magnitudes comparable.

3. **"The teacher must be much larger."** The teacher needs to be BETTER, not necessarily BIGGER. An ensemble of 5 small models can be a teacher for 1 small model. A teacher trained on more data can be a teacher for a student trained on less. The key is that the teacher has knowledge the student doesn't.

## Connection to cortexcode

Use distillation to improve the 10M model's quality. Train a larger model (100M) on the same data (rich + jc + cpython → maybe 2-3 hours on T4). Use it as teacher. Distill to the 10M student. The 10M student now transfers the 100M teacher's knowledge patterns, achieving higher quality at the same inference cost. This is how Copilot's tiny autocomplete model (350M) matches Codex's larger model — distillation.
