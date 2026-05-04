## What Is Faithfulness and Completeness?

---

### The Problem

You run an ablation study and find a set of 15 attention heads that seem to implement the IOI task. You proudly call this "the IOI circuit." But then a colleague points out that if you ablate a 16th head — one you excluded — the task accuracy also drops by 20%. Your circuit is missing a critical component. Another colleague shows that a random subset of 15 heads achieves 85% of the full model's accuracy. Your circuit is not special; it is just large enough to approximate the task by chance. How do you prove that your discovered circuit is both accurate and actually contains the right parts?

---

### Definition

**Faithfulness** means the circuit's behavior on the task is statistically indistinguishable from the full model's behavior. If the full model gets 98% accuracy and your circuit gets 97%, it is faithful. If it gets 60%, it is unfaithful — you have removed too much.

**Completeness** means the circuit contains all components that are necessary for the task. If removing any component from the circuit causes a significant performance drop, the circuit is complete. If you can remove a head without consequence, the circuit is incomplete (it contains unnecessary parts) or redundant (the full model has backup paths).

**How they work together:**
```
Full model accuracy: 98%

Circuit A: 20 heads, accuracy 97%  → FAITHFUL
           Remove any head → accuracy drops to <90%  → COMPLETE
           This is a good circuit.

Circuit B: 20 heads, accuracy 65%  → UNFAITHFUL
           Too much was removed. The circuit is too small.

Circuit C: 100 heads, accuracy 97% → FAITHFUL
           Remove 10 random heads → still 97%  → INCOMPLETE
           The circuit is bloated; it contains unnecessary components.

Circuit D: 20 heads, accuracy 97%  → FAITHFUL
           Remove head X → accuracy stays 97%  → INCOMPLETE
           Head X is in the circuit but not necessary (redundancy).
```

**Why both matter:**
- A faithful but incomplete circuit is an over-approximation: it works, but you have not found the true mechanism.
- A complete but unfaithful circuit is an under-approximation: it contains the right parts, but misses others, so it does not actually explain the model's behavior.
- Only a circuit that is both faithful and complete earns the right to be called "the circuit" for a task.

---

### Real-Life Analogy

Diagnosing a broken production line.
- **Full model:** The entire factory with 100 machines.
- **Task:** Assemble a widget.
- **Faithfulness:** You build a mini-factory with 10 machines that also assembles widgets at the same speed and quality. Your mini-factory is faithful. If it produces defective widgets, it is unfaithful.
- **Completeness:** You try removing each machine from your mini-factory one at a time. If removing machine 3 stops widget production, machine 3 is necessary and your circuit is complete with respect to machine 3. If you can remove machine 7 with no effect, your circuit is incomplete — machine 7 was unnecessary.
- **The trap:** You might build a mini-factory with 50 machines that works perfectly (faithful) but contains 40 machines that do nothing (incomplete). Or you might build a mini-factory with 5 machines that almost works (unfaithful) because you left out the critical welding robot.

---

### Tiny Numeric Example

**Full model accuracy on 100 IOI prompts: 95/100 (95%)**

**Circuit candidate 1 (greedy pruning, 12 heads): 93/100 (93%)**
- Faithful? YES (only 2% drop)
- Completeness test: ablate each of the 12 heads individually
  - Head A: drops to 87%  ← necessary
  - Head B: drops to 84%  ← necessary
  - Head C: drops to 92%  ← small drop, borderline
  - Heads D-L: each drops below 90%  ← necessary
- Verdict: FAITHFUL and MOSTLY COMPLETE

**Circuit candidate 2 (random subset, 12 heads): 78/100 (78%)**
- Faithful? NO (17% drop)
- Verdict: UNFAITHFUL, discard.

**Circuit candidate 3 (conservative pruning, 40 heads): 94/100 (94%)**
- Faithful? YES
- Completeness test: ablate each head
  - 28 heads cause no drop when ablated individually  ← unnecessary
- Verdict: FAITHFUL but INCOMPLETE (bloated).

**Key insight:** Faithfulness is a global test (does the whole circuit work?). Completeness is a local test (is every part doing its job?). You need both.

---

### Common Confusion

1. **"Faithfulness and completeness are the same thing."** No. Faithfulness is about the circuit as a whole behaving like the model. Completeness is about whether every piece in the circuit is actually needed. A bloated circuit can be faithful but incomplete.

2. **"If the circuit is faithful, it must be complete."** Not true. A large random subset of components can be faithful because it contains the true circuit inside it, plus noise. Faithfulness does not guarantee that every component in your set is necessary.

3. **"If the circuit is complete, it must be faithful."** Not true. You might have identified all necessary components but missed some, so the circuit is too small to replicate the full model's performance. It is complete in what it contains, but unfaithful in what it produces.

4. **"A 1% accuracy drop means the circuit is unfaithful."** There is no universal threshold. In safety-critical settings, 1% might matter. In exploratory research, 5% might be acceptable. The standard is usually: "Does the circuit preserve the qualitative behavior and the ranking of outputs?"

5. **"Completeness requires testing every possible subset."** That would be exponential. In practice, researchers test completeness by ablating each component individually (linear cost). If no single ablation is harmless, the circuit is likely complete. If some are harmless, you can iteratively prune them.

6. **"Redundancy means the circuit is incomplete."** Redundancy in the full model means there are backup paths. If your circuit contains one path but the full model has two, your circuit might be complete (it contains all necessary components for one path) but the full model is robust to further damage. Distinguishing redundancy from bloat is subtle.

7. **"Faithfulness and completeness are binary."** They are spectra. A circuit can be mostly faithful and mostly complete. In practice, researchers report both metrics as continuous values (accuracy retained, percentage of components necessary) rather than yes/no judgments.

---

### Where It Is Used in Our Code

`src/phase137/phase137_circuits_concepts.py` — After greedily pruning a toy transformer to find a minimal circuit, we explicitly test faithfulness by comparing circuit accuracy against the full model. We then test completeness by ablating each remaining component one at a time and checking if the task performance drops. We report both metrics and visualize the trade-off between circuit size and faithfulness.

`src/phase137/phase137_circuits_colab.py` — We evaluate faithfulness by comparing the IOI accuracy of the full Llama-3B model against a circuit composed of the top-k most important heads. We then test completeness by removing each head in the circuit and measuring the impact on pronoun resolution accuracy.
