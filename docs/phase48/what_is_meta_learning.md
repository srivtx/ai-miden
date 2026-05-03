## What Is Meta-Learning?

---

### The Problem

Humans can learn a new concept from just a few examples. Show a child three photos of a giraffe and they recognize giraffes forever. Neural networks need thousands of examples. How do you train a model to learn quickly from minimal new data?

---

### Definition

**Meta-learning** ("learning to learn") is training a model on many related tasks so that it can adapt to a new task with very few examples.

**The core idea:**
- Instead of learning ONE task, the model learns a good initialization that works for MANY tasks
- Given a new task, a few gradient steps from this initialization produce a good solution
- The model learns WHAT to learn — which features transfer across tasks

**MAML (Model-Agnostic Meta-Learning):**
```
1. Sample a task T_i from the task distribution
2. Take K gradient steps on T_i's training data -> adapted parameters θ'_i
3. Evaluate θ'_i on T_i's test data -> loss L_i
4. Update the ORIGINAL parameters θ to minimize L_i across all tasks
5. Repeat
```

**Result:**
- The initialization θ is "task-agnostic" but "adaptation-friendly"
- From θ, any new task requires only 1-10 gradient steps
- This is few-shot learning

---

### Real-Life Analogy

Learning to ride different vehicles.
- **Standard learning:** You spend months learning to ride a bicycle. Then months learning to ride a motorcycle. Then months learning to ride a scooter. Each is learned from scratch.
- **Meta-learning:** You first learn the COMMON skills: balancing, steering, braking, throttle control. Then learning a new vehicle takes hours instead of months because you already have the transferable foundation.

Meta-learning discovers the transferable foundation across all tasks.

---

### Tiny Numeric Example

**Task distribution:** Classify points by different linear boundaries.
- Task A: separate points where x + y > 0
- Task B: separate points where x - y > 0
- Task C: separate points where 2x + y > 0
- Task D: separate points where x + 2y > 0

**Standard training:**
```
Train on Task A with 1000 examples -> good at Task A
Test on Task B with 5 examples -> fails (needs retraining)
```

**Meta-learning:**
```
Train on Tasks A, B, C with 20 examples each
Learn initialization θ that works for all linear boundaries

Test on Task D with 5 examples:
  Step 1: θ predicts with 55% accuracy
  Step 2: 1 gradient step on 5 examples -> 72% accuracy
  Step 3: 5 gradient steps -> 89% accuracy
```

The meta-learned initialization adapts in 5 steps what standard training needs 1000 examples for.

---

### Common Confusion

1. **"Meta-learning is just transfer learning."** Transfer learning reuses a pre-trained model on a new task. Meta-learning explicitly trains the model to be good at adapting to new tasks.

2. **"Meta-learning requires a specific architecture."** MAML works with ANY architecture. It only modifies the training loop, not the model structure.

3. **"Meta-learning eliminates the need for training data."** No. It reduces the need for NEW task data. You still need many tasks for meta-training.

4. **"Meta-learning is only for classification."** It works for regression, reinforcement learning, and any task with a trainable loss.

5. **"Meta-learning and test-time training are the same."** Meta-learning happens during the TRAINING phase. Test-time training happens during the INFERENCE phase. They complement each other.

---

### Where It Is Used in Our Code

`src/phase48/phase48_test_time_training.py` — We implement a simplified meta-learning loop where the model trains on multiple related tasks (different linear boundaries) and learns an initialization that adapts quickly to new tasks with just a few examples.
