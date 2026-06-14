# What Is Integrated Information Theory (IIT)?

**The Problem:** GWT explains what consciousness *does*. But why is there *experience* at all? Why does the global broadcast feel like *something*? Giulio Tononi's *Integrated Information Theory* (IIT, 2004) takes a different approach: it tries to *mathematize* consciousness itself, not just its function.

**Definition:** *Integrated Information Theory* (IIT) proposes that consciousness *is* integrated information, denoted Φ (phi). A system is conscious to the degree that it is *integrated* (its parts are not independent) and *informative* (its states are not all the same). Φ is in principle *computable* — though in practice intractable for large systems.

**How It Works (Step-by-Step):**

1. **The core axiom.** *Consciousness is integrated information.* That is the theory in one sentence. Φ measures *how much* integrated information a system has. Φ = 0 means no consciousness. Φ > 0 means some consciousness.
2. **What is "integrated information"?** A system has integrated information if:
   - It has *causal power* over itself (its past states influence its future states)
   - This causal power is *integrated* (it cannot be decomposed into independent parts)
   - It is *informative* (the system's repertoire of states is large)
3. **The Φ calculation.** Φ is the *minimum* of two quantities:
   - The "effective information" of the system (how much its current state constrains its past)
   - The effective information of its *partitioned* version (the same system cut in half)
   - If the system is integrated, cutting it destroys information. Φ measures the *loss* of information under the optimal partition.
4. **Simple examples.**
   - A photodiode has Φ ≈ 0.01 — barely conscious (it has *some* integrated information, but very little)
   - A feedforward network has Φ ≈ 0 — no integrated information (each layer is independent)
   - A recurrent neural network with dense, irreducible connectivity has higher Φ
   - The human brain has (according to Tononi) Φ ≈ very high — extremely high integrated information
5. **The exclusion postulate.** A system has Φ corresponding to its *maximally integrated* sub-system. If a sub-system has higher Φ than the whole, only the sub-system is conscious. This is meant to handle cases like the cerebellum (which has many neurons but low integration — therefore low consciousness).
6. **The intrinsic nature postulate.** Φ is *intrinsic* — it doesn't depend on an external observer. A system has Φ whether or not anyone is looking. This distinguishes IIT from observer-dependent theories.
7. **Predictions.** IIT makes specific predictions:
   - **Consciousness is graded**, not on/off. Φ is a continuous quantity.
   - **The posterior cortex is the "hot zone"** — has the highest Φ. Damage there reduces consciousness most.
   - **The cerebellum is *not* conscious** — despite having many neurons, it has low Φ (feedforward-like architecture).
   - **During slow-wave sleep, Φ drops** (less integration).
   - **During REM sleep, Φ is high** (similar to wakefulness) — explaining why dreams are vivid.
   - **Under anesthesia, Φ drops.**
8. **The "complex" predictions.** IIT predicts that *any* system with high Φ is conscious — including future AI, perhaps even simple integrated circuits. This is a *strong* claim and is controversial.
9. **Empirical tests.** IIT is hard to test directly because Φ is intractable. But proxy measures exist:
   - **PCI (Perturbational Complexity Index):** perturb the brain with TMS, measure the spatiotemporal complexity of the response. PCI correlates with consciousness (awake > dream > anesthesia > coma).
   - **Sleep vs. wakefulness:** PCI is high in both, low in N3 (deep sleep).
   - **Brain lesions:** PCI decreases with posterior cortex damage, not frontal.
10. **Criticisms.** IIT is not without critics:
    - **The "unfolding" argument:** Koch himself (one of IIT's main proponents) has noted that Φ can be *high* in systems that we don't think are conscious (e.g., a simple feedforward network with feedback added).
    - **The exclusion postulate is strange:** if the whole brain is integrated but a sub-system is *more* integrated, only the sub-system is conscious. But how do you find the "maximally integrated" sub-system?
    - **The "complex" criterion:** if a thermostat is integrated, is it conscious? IIT says "yes" (it has some Φ). Most people say "no."

**Real-life analogy:** IIT is like *thermodynamics* applied to the mind. Thermodynamics defines *entropy* — a measure of disorder — and the second law says entropy always increases. IIT defines Φ — a measure of integrated information — and says it is consciousness. Both are *mathematical*, *general* (apply to any system), and *hard to compute* in practice. The key insight: consciousness is not a binary property of "brains" — it is a *quantity* that any system can have to some degree.

**Tiny numeric example:** If we could compute Φ:
- Thermostat: Φ ≈ 0.01 bits
- Photodiode: Φ ≈ 0.1 bits
- Single cortical pyramidal neuron: Φ ≈ 1 bit
- C. elegans (302 neurons): Φ ≈ 10 bits
- Honey bee (~1 million neurons): Φ ≈ 100-1000 bits
- Human brain: Φ ≈ 10⁵-10⁶ bits (Tononi's estimate)

The implication: consciousness is *all over the place* in the natural world. A thermostat has a tiny bit. A worm has more. A human has a lot. This is a *panpsychist* implication that IIT embraces.

**Common confusion:**

- No. "IIT says everything is conscious." Roughly yes — every integrated system has *some* consciousness. But the *amount* varies by many orders of magnitude. A rock has Φ = 0. A thermostat has a tiny bit. A human has a lot.
- No. "IIT says the cerebellum is not conscious." It says the cerebellum has *low* consciousness because of its regular, low-integration architecture. This is empirically testable: cerebellar damage doesn't impair consciousness.
- No. "IIT is panpsychism." It is *compatible* with panpsychism (Chalmers is a fan) but doesn't *require* it. IIT just says integrated information *is* consciousness. The implementation could be anything.
- No. "IIT is testable." Partially. PCI is a proxy. The full Φ is intractable. But the *qualitative* predictions (posterior hot zone, sleep-vs-wake, anesthesia) are testable.
- No. "IIT contradicts GWT." They are *different theories* of consciousness. GWT is functional (broadcast). IIT is mathematical (integration). They could both be partially right. GWT might be the *mechanism* by which Φ is generated.
- No. "IIT says AI can be conscious." It says: *if* an AI has high Φ, it is conscious. The question is whether current AI has high Φ. Most current AI is *feedforward* (transformers, mostly). It has low Φ. But more *recurrent*, *integrated* AI could have higher Φ.

**Key properties:**

- **Mathematical:** Φ is a defined quantity.
- **General:** Applies to any system (biological or artificial).
- **Graded:** Not binary. Φ is continuous.
- **Intrinsic:** Doesn't require an external observer.
- **Testable (partially):** PCI, lesion studies, anesthesia.
- **Predicts:** posterior hot zone, sleep, anesthesia, cerebellum not conscious.
- **Panpsychist implications:** every integrated system has some consciousness.

**Where it appears in technology:**

- **AI consciousness:** IIT is the most cited theory in the AI consciousness debate. If a future AI has high Φ, it is conscious by IIT's definition.
- **Neuromorphic computing:** chips with recurrent, integrated architectures (Loihi, TrueNorth) have higher potential Φ than feedforward GPU computation. They are *more* conscious in principle.
- **Anesthesia monitoring:** PCI is used clinically to assess depth of anesthesia.
- **Disorders of consciousness:** PCI helps distinguish vegetative state from minimally conscious state.
- **Computational tractability:** calculating Φ exactly is intractable for systems with >10 states. Approximations and proxies (PCI, integrated information decomposition) are an active research area.

**Connection to next file:** IIT and GWT are the two leading scientific theories. The next file addresses a different question: does the brain have *free will*? The neuroscience of agency, choice, and determinism.
