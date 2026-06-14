# What Is Three-Factor Learning?

**The Problem:** A 1997 experiment in monkeys showed that dopamine neurons fire when a reward is *better than expected* — not when a reward is received. This was a complete reinterpretation of what dopamine does. The 2000s and 2010s revealed a deeper story: neuromodulators like dopamine, acetylcholine, and norepinephrine don't just signal reward; they *gate* whether and how synapses change. The brain has a third factor in every learning event.

**Definition:** *Three-factor learning* (or *neuromodulated plasticity*) is a learning rule where synaptic change depends on three signals: (1) presynaptic activity, (2) postsynaptic activity, and (3) a global neuromodulatory signal that gates whether plasticity occurs and what its sign is. The neuromodulator acts as a "permission slip" for plasticity.

**How It Works (Step-by-Step):**

1. **Two-factor rules (Hebbian, STDP) are blind to context.** A pre-post coincidence produces LTP. But that LTP is *inappropriate* if it doesn't help the animal achieve a goal. Hebbian learning doesn't know what the animal wants.

2. **The third factor comes from outside the synapse.** Neuromodulators (DA, ACh, NE, 5-HT) are released by specialized neurons with diffuse projections. They bathe large brain regions and signal global states: reward, surprise, attention, arousal.

3. **Dopamine is the reward prediction error.** The seminal finding by Wolfram Schultz and colleagues (1990s) was:
   - When an unexpected reward arrives → dopamine burst
   - When an expected reward arrives → no dopamine (it was already predicted)
   - When a predicted reward is *omitted* → dopamine dip (negative prediction error)
   - This is exactly the *temporal-difference (TD) error* used in reinforcement learning.

4. **Dopamine gates plasticity.** Brzosko, Schultz, Clopath, and Paulsen (2017, *eLife*) showed:
   - Acetylcholine release → enables LTD
   - Followed by a dopamine signal within ~1 second → LTD is converted to LTP
   - The pairing of ACh + DA effectively says: "this input was active *and* it was followed by reward — strengthen it."

5. **The neuromodulator acts locally, not globally.** Although dopamine is released broadly, it acts on specific synapses that are *eligible* — they were recently active and have the right receptors and signaling state. This is the "eligibility trace" concept.

6. **The eligibility trace.** When a pre-post coincidence occurs, the synapse doesn't immediately change. Instead, it enters a *transient eligible state* (~1-2 seconds in the striatum, longer elsewhere). During this window, if a neuromodulator arrives, the synapse is updated. Otherwise, the eligibility decays and nothing changes.

7. **The three-factor rule:**
   - Δw = η · x_pre · x_post · M
   - where M is the local concentration of the relevant neuromodulator.

8. **The math matches reinforcement learning.** The combination of (1) eligibility trace and (2) neuromodulator signal is mathematically equivalent to the actor-critic architecture in RL. The "actor" is the synapse's eligibility; the "critic" is the neuromodulator.

9. **Different neuromodulators, different rules:**
   - **Dopamine:** Reward prediction error. Gating for LTP vs. depression. Acts on D1 and D2 receptors.
   - **Acetylcholine:** Attention, learning state, arousal. Acts on muscarinic (M1-M5, slow, modulatory) and nicotinic (fast, ionotropic) receptors. High ACh = engaged, learning mode.
   - **Norepinephrine:** Arousal, surprise, novelty. Acts on α and β adrenergic receptors. Boosts LTP.
   - **Serotonin:** Mood, patience, behavioral flexibility. Modulates many targets; complex effects on plasticity.
   - **Acetylcholine in cortex:** Frémaux et al. (2016) show that ACh can convert a normally-depressing protocol into a potentiating one.

**Real-life analogy:** A teacher in a classroom. The student hears a lecture (presynaptic activity), takes notes (postsynaptic activity), and understands (coincidence). But the *strength* of the learning depends on the teacher (the neuromodulator): a great teacher inspires deep understanding; a boring teacher makes students forget. The teacher's mood (dopamine level) modulates how effectively the material is encoded. The student's attention (acetylcholine) determines whether the synapses are even eligible to learn.

**Tiny numeric example:** In the Brzosko et al. (2017) experiment, hippocampal synapses were given:
- A low-frequency pairing protocol → would normally produce LTD
- ACh application during the protocol → still produces LTD
- ACh *followed* by DA ~1s later → LTD is converted to LTP
- DA alone (without ACh) → no plasticity (no eligibility)
- ACh alone (without DA) → LTD

This is the cellular basis of "actions that lead to reward are remembered, while actions that don't are forgotten." Without the reward signal (DA), even an eligible synapse doesn't change.

**Common confusion:**

- No. "Dopamine is pleasure." No. Dopamine is *reward prediction error*. It fires when something is *better* than expected. Addictive drugs cause dopamine release not because they're pleasurable, but because they are *unexpectedly rewarding* (or because they directly hijack the dopamine system).
- No. "Dopamine is the only neuromodulator for learning." No. Acetylcholine, norepinephrine, and serotonin all gate plasticity. Each gates it differently.
- No. "The neuromodulator just adds itself to the Hebbian rule." The actual mechanism is more subtle: the neuromodulator modifies the *signaling state* of the synapse (via cAMP, PKA, MAPK) which changes how subsequent Ca²⁺ signals are interpreted.
- No. "Eligibility traces are long (seconds to minutes)." The trace length is region-specific. In the striatum, it's ~1 second. In the hippocampus, it can be longer. In cortical synapses, it can be 10s of seconds.
- No. "Three-factor learning is just RL on the brain." It is the *biological implementation* of actor-critic RL. The math is the same. The substrate is neuromodulators and synaptic eligibility.
- No. "Three-factor learning is just for reward learning." It's also for attention, arousal, behavioral state, and even consciousness. The same architecture, different neuromodulators, different functions.

**Key properties:**

- **Gated:** Plasticity only occurs when the third factor is present.
- **Time-limited:** The eligibility trace decays without the third factor.
- **Multiplicative:** The third factor scales the Hebbian update.
- **Region-specific:** The third factor's effect depends on receptor expression and downstream signaling in each region.
- **Bidirectional:** DA, NE, and 5-HT can both strengthen and weaken depending on receptor subtype (D1 vs D2 for dopamine, β vs α2 for norepinephrine, etc.).

**Where it appears in technology:**

- **Actor-critic reinforcement learning** is the direct mathematical analog. The "actor" is the policy (synaptic eligibility); the "critic" is the value function (neuromodulator).
- **Reward-modulated STDP** in spiking neural networks (e.g., Frémaux & Gerstner, 2016) implements three-factor learning in silicon. The third factor is a global reward signal that gates synaptic updates.
- **Neuromodulated plasticity in AI agents:** Modern agentic systems use a similar idea — a "global" reward signal modulating local learning rules. The "neuromodulator" is the policy gradient.
- **Distinguishing supervised, unsupervised, and reinforcement learning:** All three can be implemented with three-factor rules. The third factor is the *objective signal*:
  - Unsupervised: no third factor (or third factor is constant)
  - Supervised: third factor is the error signal
  - Reinforcement: third factor is the reward signal

**Connection to next file:** Three-factor learning adds a *context-gating* layer on top of Hebbian and STDP rules. But the brain also has *behavioral-timescale* plasticity — a rule that operates on the timescale of events, not spikes. The next file introduces this, the most recent and arguably the most important discovery in biological learning.
