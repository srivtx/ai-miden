# What Is a Replay Buffer?

## 1. Why it exists (THE PROBLEM first)

Catastrophic forgetting happens because the model never sees old data again. The simplest way to prevent forgetting? Just **show it old data again** while learning new things. But storing all old data is expensive and violates privacy. A replay buffer stores a small, fixed-size subset of old examples and interleaves them with new training data. It's the "brute force but smart" solution to continual learning.

## 2. Definition

A **replay buffer** is a memory store of examples from previously learned tasks. During training on a new task, a small batch of replay examples is mixed into each training minibatch, forcing the model to maintain performance on old tasks while learning the new one.

## 3. Real-life analogy

Imagine you're learning Spanish. Every day you learn 10 new vocabulary words (Task B). But you also review 2 flashcards from last week (Task A). Just 2 cards out of 12 total keeps last week's words fresh. The 2 cards are your "replay buffer"—a tiny sample of old knowledge that prevents total forgetting without re-studying the entire old deck.

## 4. Tiny numeric example

Task A has 1000 examples. Task B has 1000 new examples.

Without replay:
- Training batch = 32 Task B examples only
- Model only optimizes for Task B
- Task A accuracy: 50% (forgotten)

With replay buffer (stores 100 Task A examples):
- Training batch = 28 Task B examples + 4 Task A examples
- Model optimizes for both simultaneously
- Task A accuracy: 85% (remembered!)

You only needed 4% of old data to preserve most of the old knowledge.

## 5. Common confusion

- **"Replay buffer means storing ALL old data."** No. The point is you store a **small, fixed** subset. Often just 1-5% of old data. It's not full retraining.
- **"It's just shuffling datasets together."** No. The buffer is typically fixed-size and uses strategies like reservoir sampling or prioritized replay. Old examples may be evicted as new ones arrive.
- **"Replay is cheating because you still have old data."** In continual learning, the constraint is usually "no access to the full old dataset," not "zero old examples." A small buffer is considered acceptable and biologically plausible (humans have memories).
- **"Replay fixes forgetting completely."** No. With a tiny buffer, you get ~80-90% of old performance back, but rarely 100%. The model still slightly drifts because the buffer doesn't cover the full old distribution.
- **"You can only replay raw images/text."** Replay can also mean replaying **features** or even **gradients** (gradient episodic memory). The concept generalizes beyond raw data.
- **"The buffer should contain the most recent old examples."** Not necessarily. Random sampling (reservoir sampling) often works better than keeping only the most recent, which may not cover the old task's distribution.

## 6. Where it is used in our code

In `src/phase81/phase81_continual_learning.py`, after training on Task A, we save 20 random examples into `replay_buffer`. During Task B training, every minibatch contains 24 Task B examples plus 8 replay examples (25% replay). The `train_with_replay()` function shuffles these together before the forward pass. We show that replay preserves Task A accuracy at ~85% compared to naive ~50%.

In `src/phase81/phase81_continual_learning_colab.py`, we implement a replay buffer for split MNIST. After training on digits 0-4, we store 200 random examples in the buffer. When training on digits 5-9, each batch contains a 4:1 ratio of new-to-old data. This dramatically reduces forgetting on digits 0-4 while still learning 5-9 effectively.