# What Is Hebbian Learning?

**The Problem:** If the brain is a network of neurons connected by synapses, how do the connections get stronger or weaker? There must be a rule — a physical law — that says "synapses that contribute to a useful output get stronger; synapses that don't, get weaker." In 1949, Donald Hebb proposed the simplest possible rule. It is still the foundation of all theories of biological learning.

**Definition:** *Hebbian learning* is the principle that a synapse is strengthened when the presynaptic neuron repeatedly contributes to the firing of the postsynaptic neuron. Hebb's original (1949) formulation: *"When an axon of cell A is near enough to excite a cell B and repeatedly or persistently takes part in firing it, some growth process or metabolic change takes place in one or both cells such that A's efficiency, as one of the cells firing B, is increased."*

**How It Works (Step-by-Step):**

1. **Baseline.** A synapse starts at some strength. Two neurons A (presynaptic) and B (postsynaptic) are weakly connected.
2. **Coincidence.** A fires, releasing neurotransmitter. B is depolarized. If A fires *just before* B fires, the synapse from A to B has contributed to B's firing.
3. **Strengthening.** This repeated co-activation triggers molecular changes in the synapse:
   - More AMPA receptors inserted into the postsynaptic density
   - Spine enlarges
   - Presynaptic release probability increases
   - More neurotransmitter packaged per vesicle
4. **Result.** The next time A fires alone, it has a much larger effect on B. The connection is now "wired" — A reliably contributes to B's firing.
5. **The two mnemonics:**
   - "Cells that fire together, wire together" (co-activation → strengthening)
   - "Out of sync, lose their link" (asynchronous firing → weakening)
6. **Mathematical form:** The simplest Hebbian rule is
   Δw = η · x_pre · x_post
   where w is the synaptic weight, η is the learning rate, x_pre is presynaptic activity, and x_post is postsynaptic activity.
7. **The problem with this rule:** It is *unstable*. If the rule is purely positive (only "fire together → strengthen"), then any two strongly-connected neurons will keep strengthening each other, leading to runaway positive feedback. This is a well-known mathematical problem.

**Real-life analogy:** Imagine two people in a conversation. If person A says something and person B is inspired to act on it, the next time A speaks, B will listen more carefully. They have formed a stronger conversational bond. But if A speaks and B ignores it, the connection weakens. The brain is doing this billions of times per second.

**Tiny numeric example:** Suppose neurons A and B both fire at 1 Hz. By chance, their spikes coincide 1% of the time. Over 1,000 spike pairs, ~10 coincidences strengthen the synapse by 1% each (η = 0.01). So after 1,000 pairs, the synapse is ~10% stronger. After 10,000 pairs, ~100% stronger (saturated). The same synapse, if A and B fire 100 ms apart, would *weaken* by the same mechanism (this is anti-Hebbian). The "stability" problem: if the rule were "fire together, always strengthen," then any two strongly connected neurons would strengthen each other without bound, leading to all neurons firing maximally — useless.

**Common confusion:**

- No. "Hebb invented spike-timing dependent plasticity." No. Hebb's rule is co-occurrence-based, not timing-based. STDP (see next file) is the modern timing-dependent refinement.
- No. "Hebbian learning is a complete theory." No. The pure Hebbian rule is mathematically unstable. Real brains have homeostatic plasticity, inhibitory constraints, and neuromodulation to keep it stable.
- No. "Hebb believed only strengthening happens." No. Hebb himself noted in his 1949 book that weakening must also occur, though he did not specify the mechanism. Modern understanding is that the rule is *biphasic* (see STDP, LTP/LTD).
- No. "Hebbian learning requires a teacher." It is *unsupervised*. It just depends on activity correlations. A supervised version would require a global "correctness" signal — that's backprop, not Hebbian.
- No. "Hebbian learning is a hypothesis." It is now a *measured phenomenon*. LTP (long-term potentiation) in the hippocampus, first discovered by Bliss and Lømo in 1973, is the molecular embodiment of Hebbian learning.
- No. "Hebbian learning is local." It is *local* — the rule can be implemented using only the activities of the pre- and postsynaptic neuron, with no global information. This is the property that makes it biologically plausible.

**Key properties:**

- **Locality:** Δw depends only on x_pre and x_post. No need for backpropagated error from distant layers.
- **Unsupervised:** The rule requires no external teacher or label.
- **Correlation-based:** Synapses become stronger when pre and post fire together; weaker when they don't.
- **Unstable alone:** Pure Hebbian rules diverge without stabilizing mechanisms.
- **Biphasic (in modern form):** Strengthening *and* weakening, depending on activity.

**Where it appears in technology:**

- **Oja's rule** (1982) and **PCA networks** are the simplest stabilizations of Hebbian learning. Oja's rule makes the weight vector converge to the first principal component of the input.
- **Sanger's rule** (1989) extends this to *all* principal components, giving a complete PCA network.
- **Slow feature analysis (SFA)** is a Hebbian-style rule that extracts the slowest features of the input stream.
- **Independent Component Analysis (ICA)** uses a related local rule.
- In deep learning, **contrastive Hebbian learning** is the closest biologically-plausible analog of backprop. Modern work (e.g., Contrastive Hebbian Learning, modern Predictive Coding) shows local Hebbian rules can match backprop on some tasks.
- **Hopfield networks** (1982) use pure Hebbian learning to store and recall memories as attractors. They are content-addressable memory.
- **Boltzmann machines** (Hinton & Sejnowski, 1985) are stochastic generalizations of Hopfield nets. They are essentially Hebbian + noise.

**Why it matters for the rest:** Hebbian learning is the *parent* of all biological learning rules. STDP, LTP, three-factor learning, BTSP — all are descendants of Hebb's principle. The key fact: **Hebbian learning is local.** This is why it is biologically plausible and why it is computationally interesting. It is also why it cannot do everything backprop can do — but it does a lot, with much less.

**Connection to next file:** Hebb's rule is correlation-based, not timing-based. The next file (`what_is_ltp_ltd.md`) shows what happens at the *molecular* level when a Hebbian coincidence occurs. The file after that (`what_is_stdp.md`) shows how *timing* — not just coincidence — refines the rule into something more powerful.
