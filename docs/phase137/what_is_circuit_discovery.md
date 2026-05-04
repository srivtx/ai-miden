## What Is Circuit Discovery?

---

### The Problem

You have a neural network with 7 billion parameters that can write essays, solve math problems, and translate languages. It is a black box. You know what goes in and what comes out, but you have no idea which neurons, layers, or connections are responsible for any specific behavior. If the model makes a biased hiring recommendation, you cannot point to the part of the network that caused it. If it correctly resolves a pronoun in a sentence, you cannot say which heads did the work. How do you open the black box and find the actual subnetwork — the circuit — that implements a specific task?

---

### Definition

**Circuit discovery** is the process of identifying a minimal subset of a neural network's components (nodes, edges, attention heads, MLP neurons) whose behavior is sufficient to reproduce the model's performance on a specific task. It answers the question: "Which parts of this model actually matter for this specific behavior?"

**How it works:**
```
Full model: 7B parameters, 32 layers, 32 heads per layer
Task: resolve "She" → "Mary" in "John threw the ball to Mary. She caught it."
Step 1: run the full model, record the output logit for "Mary"
Step 2: ablate (zero out) one attention head, measure the drop in "Mary" logit
Step 3: repeat for every head, rank them by impact
Step 4: keep only the top-k heads that preserve most of the task performance
Result: a circuit of ~20 heads that explains pronoun resolution
```

**Key techniques:**
- **Ablations:** remove a component and measure performance change. If removing head 17 in layer 14 drops the correct answer probability by 40%, that head is important.
- **Edge attribution (ACDC):** attribute the model's output to specific paths through the computation graph, then prune low-attribution edges.
- **Node attribution:** score individual neurons or heads by their contribution to the task, often using gradient-based methods or activation patching.
- **Automated circuit finding:** search algorithms (e.g., greedy pruning, evolutionary search) that iteratively remove components and check faithfulness.

**Why this matters:**
- Circuit discovery turns "the model is biased" into "heads 3, 7, and 12 in layer 8 amplify gender stereotypes through the Name Mover path"
- It enables targeted editing: disable a harmful circuit without retraining the whole model
- It validates safety claims: if you cannot find the circuit for a behavior, you do not understand it

---

### Real-Life Analogy

Diagnosing why a car will not start.
- **Full model:** The entire car — engine, battery, fuel system, electronics, 30,000 parts.
- **Task:** The car cranks but fails to start.
- **Circuit discovery:** You test one component at a time. You disconnect the fuel pump — still cranks, no start. You check the spark plugs — weak spark. You replace the ignition coil — it starts. The "circuit" for starting is: battery → starter → ignition coil → spark plugs → engine. You do not need the radio, the air conditioning, or the power windows to explain why the car starts.
- **The insight:** A car has 30,000 parts, but only ~20 are in the starting circuit. A 7B model has billions of parameters, but a specific behavior might depend on only a few hundred.

---

### Tiny Numeric Example

**Toy model:** 2 layers, 4 heads per layer, 8-dimensional residual stream.
**Task:** add two 4-bit numbers (A + B = C).

**Full model accuracy:** 98%

**Ablate head (Layer 1, Head 2):** accuracy drops to 45%
**Ablate head (Layer 1, Head 0):** accuracy drops to 97%  ← unimportant
**Ablate head (Layer 2, Head 3):** accuracy drops to 12%  ← critical

**Circuit found by greedy pruning:**
```
Keep: Layer 1 Heads {2, 3}
Keep: Layer 2 Heads {1, 3}
Keep: MLP in Layer 2
Drop: everything else
```

**Faithfulness test:**
```
Full model accuracy:    98%
Circuit accuracy:       96%   ← faithful (only 2% drop)
Random subset (same size): 51%  ← unfaithful
```

The circuit is 4 heads + 1 MLP out of 8 heads + 2 MLPs total. It is 50% of the model by component count but explains 96% of the task behavior.

---

### Common Confusion

1. **"Circuit discovery finds the only components that do anything."** No. It finds the components that matter for a specific task on specific inputs. A head that is critical for IOI might be irrelevant for arithmetic. Circuits are task-specific, not universal.

2. **"Ablating a head proves it is unnecessary."** Ablating one head can sometimes be compensated by others. If accuracy barely drops, the head might be redundant, not useless. You need to ablate combinations to detect redundancy.

3. **"Circuit discovery is the same as feature visualization."** Feature visualization shows what a single neuron responds to (e.g., curves, quotes). Circuit discovery shows how multiple components work together to implement a task. They are complementary, not the same.

4. **"Smaller circuits are always better."** A smaller circuit is more interpretable, but if it drops accuracy from 98% to 60%, it is not faithful. The goal is the smallest faithful circuit, not the smallest circuit at any cost.

5. **"Automated circuit finding is guaranteed to find the true circuit."** Greedy pruning can get stuck in local optima. The true minimal circuit might require removing components in a specific order that a greedy search misses. Faithfulness testing is essential but not foolproof.

6. **"Circuits are static across all inputs."** A circuit might change depending on sentence length, token position, or grammatical structure. Some heads only activate on long-range dependencies. Circuit discovery on a small dataset might miss context-dependent behavior.

7. **"If a circuit is faithful, it is complete."** Faithfulness means the circuit behaves like the full model. Completeness means it contains all necessary components. You can have a faithful circuit that is incomplete if the full model has redundant paths. Testing completeness requires checking that every component in the circuit is actually necessary.

---

### Where It Is Used in Our Code

`src/phase137/phase137_circuits_concepts.py` — We simulate a toy transformer, define a simple task (sequence copying with a twist), and run ablations on every attention head and MLP neuron. We rank components by impact, greedily prune unimportant ones, and visualize the resulting circuit graph. We also test faithfulness by comparing the circuit's accuracy against the full model and a random subset of the same size.

`src/phase137/phase137_circuits_colab.py` — We load `meta-llama/Llama-3.2-3B-Instruct` on a T4 GPU, construct Indirect Object Identification (IOI) prompts, and ablate attention heads one by one. We find the specific heads whose removal most hurts pronoun resolution, compare against random ablation, and attempt to steer the model by amplifying circuit heads.
