## What Is Self-Play Generation?

---

### The Problem

Some of the most valuable capabilities — strategic reasoning, mathematical proof, competitive programming, and scientific discovery — have almost no human-written training data. There are not millions of recorded grandmaster chess games annotated with reasoning traces. There are not billions of step-by-step mathematical proofs written in a format a model can learn from. Human experts are too slow and too few. How do you train a model to do something when no one has written down how to do it?

---

### Definition

**Self-Play Generation** is a technique where a model generates its own training data by interacting with itself or with a simulated environment. The model produces an action, receives feedback (win/loss, correct/incorrect, reward/punishment), and the game trace or reasoning chain becomes a new training example. Over thousands of rounds, the model bootstraps expertise from nothing but rules and a score function.

**How it works:**
```
Round 1:  Model plays both sides of a game randomly → record moves → train
Round 2:  Slightly better model plays itself → better moves → train
...       
Round N:  Model is now an expert → its self-play traces are expert training data
```

**Key techniques:**
- **Opponent sampling:** the model plays against older versions of itself to maintain a curriculum of difficulty
- **Monte Carlo Tree Search (MCTS):** exploring many possible move sequences before selecting the best one
- **Outcome-based filtering:** keeping only game traces that ended in a win or a correct proof
- **Process reward models:** scoring each intermediate step, not just the final result

**Why this matters:**
- AlphaGo became the world's best Go player by playing millions of games against itself
- Reasoning models learn multi-step logic by generating chains of thought and verifying the final answer
- Self-play creates an unlimited supply of hard, diverse training examples tailored to the model's current skill level
- It is the only scalable way to generate expert-level data for tasks where human experts are scarce

---

### Real-Life Analogy

A tennis player with a ball machine.
- **Traditional training:** The player reads books about tennis technique and watches professional matches. This is like training on human-written data. It helps, but it is passive and limited by how much expert footage exists.
- **Self-play:** The player sets up a ball machine that adapts to their skill level. It serves harder as the player improves. The player practices 10,000 serves per day, getting instant feedback on whether each shot landed in bounds. The machine is not a coach; it is an environment that generates practice data.
- **The key insight:** The player is not learning from a teacher. They are learning from the structure of the game itself — the rules, the scoring, and the physical feedback loop. The model invents its own curriculum.

---

### Tiny Numeric Example

**Scenario:** Training a model to play a simple number game: start at 0, add 1, 2, or 3 each turn, and try to reach exactly 20. If you go over 20, you lose.

**Initial model (random play):**
```
Win rate: 48% (barely better than a coin flip)
Average game length: 7 moves
```

**After 1,000 rounds of self-play:**
```
Model plays itself, records winning traces, trains on them
Win rate: 67%
Average game length: 8.5 moves (learning to control the pace)
```

**After 10,000 rounds of self-play:**
```
Win rate: 94%
Average game length: 9.2 moves (discovering endgame strategy)
Key discovery: reaching 16 guarantees a win, because whatever the opponent
adds (1, 2, or 3), you can add the complement to reach 20.
```

**Training data growth:**
```
Human experts who wrote down optimal strategies: 0 examples
Self-play generated expert traces: 10,000 examples
Model learned a provably optimal strategy from zero human demonstrations.
```

---

### Common Confusion

1. **"Self-play is just reinforcement learning."** Self-play is a *data generation* strategy within reinforcement learning. RL tells you to optimize a reward; self-play tells you where the training data comes from — the model's own games. Not all RL uses self-play, and not all self-play uses RL (some use supervised learning on winning traces).

2. **"The model is teaching itself from scratch."** It is bootstrapping from the rules and a verifier, not from nothing. Without a correct scoring function or environment simulator, self-play collapses into nonsense. The rules and verifier are the curriculum designer.

3. **"Self-play only works for games."** It works for any task with a verifiable outcome: math proofs (checkable by a proof assistant), code (runnable and testable), chemistry (simulable), and logic puzzles. Any domain where you can automatically say "this output is correct" is a candidate.

4. **"The best model always plays the most recent version of itself."** Playing only the current champion causes overfitting to a single style. Strong systems like AlphaZero maintain a pool of past versions and sample opponents from it. Diversity of opponents creates diversity of training data.

5. **"Self-play eliminates the need for human data."** Human data is still valuable for initialization. A model that starts from random weights will take far longer to bootstrap than one pre-trained on general text. Self-play is the specialization phase, not the foundation.

6. **"Self-play traces are always high quality."** The model generates many losing games, dead-end proofs, and incorrect code. The quality comes from filtering: keep only wins, only correct proofs, only passing tests. Without filtering, self-play data is mostly mistakes.

7. **"Self-play creates truly novel knowledge."** It discovers strategies that are novel *to the model*, not necessarily to humanity. AlphaGo found moves humans had not prioritized, but the rules of Go were fixed. Self-play explores a known space efficiently; it does not invent new rules.

---

### Where It Is Used in Our Code

`src/phase147/phase147_synthetic_concepts.py` — We simulate self-play for a simple arithmetic reasoning task. The model generates chains of thought, a verifier checks the final answer, and we keep only correct traces for training. We show how the accuracy of generated reasoning chains improves over self-play rounds, even though no human ever wrote a reasoning trace.

`src/phase147/phase147_synthetic_colab.py` — We use an instruction-tuned model to generate multiple candidate responses to the same prompt, score them with a heuristic verifier, and treat the highest-scoring responses as synthetic training data. This mimics the core self-play loop: generate, verify, filter, train.

(End of file)
