# What Is the Reward System and Dopamine?

**The Problem:** An animal must learn which actions lead to good outcomes (food, water, mates) and which lead to bad ones (pain, danger). The learning is *reinforcement-based* — driven by the actual outcomes, not by a teacher giving labels. What is the brain's mechanism for this, and why is it so hard to replicate in AI?

**Definition:** The *reward system* is a set of brain structures — primarily the *ventral tegmental area* (VTA), *substantia nigra pars compacta* (SNc), *nucleus accumbens* (NAc), ventral striatum, orbitofrontal cortex, and amygdala — that compute reward value, prediction error, and motivation, and use these signals to drive learning, approach behavior, and decision-making.

**How It Works (Step-by-Step):**

1. **The dopamine discovery.** The history is a case study in scientific paradigm shifts:
   - 1950s-60s: Dopamine was thought to be a *pleasure* chemical. The reward system = "pleasure circuit."
   - 1970s-80s: Wise and others showed that dopamine *antagonists* (blockers) reduce the *wanting* of reward, not the *liking* (pleasure). Rats will still consume sugar but won't work for it.
   - 1990s: Wolfram Schultz's seminal experiments (see step 2) revealed that dopamine signals *reward prediction error*, not reward itself.
   - 2000s-2010s: The three-factor learning framework (see `02_learning_mechanisms/what_is_three_factor_learning.md`) integrated dopamine into a complete model of reinforcement learning.

2. **The Schultz experiments.** Schultz recorded from dopamine neurons in monkeys:
   - **Unexpected reward (juice):** Big burst of dopamine.
   - **Reward after a learned cue (light → juice):** Dopamine burst *transfers* to the cue. The reward itself produces no burst.
   - **Cue without reward (light → no juice):** Dopamine *dip* (below baseline).
   - **More reward than expected (big juice):** Bigger dopamine burst.
   - **Less reward than expected (small juice):** Dopamine dip.
   - This is *exactly* the temporal-difference (TD) error δ(t) = r(t) + γV(s') - V(s) used in reinforcement learning.

3. **The mathematics of TD learning.**
   - V(s) = expected future reward from state s
   - δ(t) = r(t) + γV(s') - V(s) = "how much better/worse was this than expected"
   - δ > 0: good surprise → strengthen actions that led here
   - δ < 0: bad surprise → weaken actions that led here
   - V is learned by: ΔV(s) = α · δ(t)
   - The dopamine signal *is* δ(t) (within ~100-300 ms temporal precision).

4. **Anatomy of the reward circuit.**
   - **Ventral tegmental area (VTA):** ~400,000-600,000 dopaminergic neurons. Sends projections to NAc, prefrontal cortex, hippocampus, amygdala.
   - **Substantia nigra pars compacta (SNc):** ~200,000-400,000 dopaminergic neurons. Sends to dorsal striatum (motor).
   - **Nucleus accumbens (NAc):** Ventral striatum. The "goal" — actions are motivated by what NAc computes.
   - **Orbitofrontal cortex (OFC):** Encodes the *value* of stimuli, independent of action. Damage to OFC causes inability to update value based on new information.
   - **Amygdala:** Encodes the *salience* and emotional value of stimuli. Critical for fear learning.
   - **Anterior cingulate cortex (ACC):** Effort-cost computations. "Is this worth working for?"
   - **Dorsolateral prefrontal cortex (dlPFC):** Goal maintenance, working memory of goals.
   - **Hippocampus:** Context — where am I, and what context predicts reward?

5. **Two dopamine systems.**
   - **Mesolimbic:** VTA → NAc, amygdala, hippocampus. *Reward, motivation, salience.* Most relevant for learning.
   - **Mesocortical:** VTA → prefrontal cortex. *Cognitive control, working memory.*
   - **Nigrostriatal:** SNc → dorsal striatum. *Motor control.* Lost in Parkinson's.
   - **Tuberoinfundibular:** Hypothalamus → pituitary. *Hormonal regulation.*

6. **Wanting vs. liking (Robinson & Berridge, 1993).** Critical distinction:
   - **Liking:** The hedonic impact of a reward. "Is this pleasant?" Mediated by opioid and endocannabinoid systems in "hedonic hotspots" of NAc and ventral pallidum.
   - **Wanting:** The motivational salience. "Do I want this?" Mediated by dopamine.
   - You can *want* something without *liking* it (e.g., addiction). You can *like* something without *wanting* it (e.g., you've had too much).
   - Wanting and liking have *different* neural substrates. Dopamine is wanting, not liking.

7. **Reinforcement learning in the brain.** The basal ganglia + dopamine system implements an *actor-critic* RL architecture (see `03_architecture/what_is_basal_ganglia.md`):
   - **Critic:** The value function V(s). Updated by TD error (dopamine).
   - **Actor:** The policy π(a|s). Updated by eligibility trace × dopamine.
   - **State representation:** Cortex + hippocampus.
   - **Action selection:** Striatum (direct and indirect pathways).

8. **Reward prediction errors for different neurotransmitters.** Recent work suggests that other neuromodulators also signal reward-related quantities:
   - **Serotonin:** May signal *reward prediction* (not error), or *average reward rate*, or *patience*. Less clear than dopamine.
   - **Norepinephrine:** Signals *unexpected uncertainty* (when things become more variable).
   - **Acetylcholine:** Signals *expected uncertainty* (when the environment is reliably noisy).
   - Together, these form a *full Bayesian* estimate of reward statistics.

9. **Reward and learning in cortex.** Dopamine does not just drive learning in the striatum. It also reaches the cortex (via VTA → PFC, hippocampus). Cortical dopamine modulates:
   - **Working memory** in PFC (too little = distractibility; too much = perseveration).
   - **Long-term memory consolidation** in hippocampus (dopamine release in hippocampus after a learning event improves memory).
   - **Decision-making** in OFC.

10. **The dopaminergic disorders.**
    - **Parkinson's disease:** Loss of SNc dopamine → motor deficits (tremor, rigidity, bradykinesia) AND cognitive slowing, depression, apathy.
    - **Addiction:** Drugs of abuse cause *supraphysiological* dopamine release in NAc. The brain compensates: D2 receptors downregulate, sensitivity drops. The result: tolerance, dependence, withdrawal, cravings.
    - **Schizophrenia:** Excess subcortical dopamine (causing positive symptoms: hallucinations, delusions) and deficient prefrontal dopamine (causing negative symptoms: avolition, cognitive deficits). Antipsychotics block D2 receptors.
    - **ADHD:** Reduced dopamine signaling in PFC. Stimulants (methylphenidate, amphetamine) increase dopamine, paradoxically *calming* the patient (by enhancing PFC function).
    - **Depression:** Reduced dopamine, serotonin, and norepinephrine. Most antidepressants target serotonin or norepinephrine; some (bupropion) target dopamine.

**Real-life analogy:** The reward system is the brain's *quality control inspector* at a factory. The inspector (dopamine) compares the actual output (reward) to the expected output (predicted value). If the output is better than expected, the inspector signals "this is good, keep doing it." If worse, "this is bad, change something." The factory's managers (cortical areas) use the inspector's signal to improve processes (learning). A defective inspector (dopamine dysfunction) causes the factory to malfunction (Parkinson's, addiction, schizophrenia).

**Tiny numeric example:** A VTA dopamine neuron fires at 1-5 Hz baseline. After an unexpected reward, it bursts at 20-50 Hz for ~100-300 ms. After a learned cue, it bursts at the *cue*, not at the reward. A typical NAc neuron has ~20,000-50,000 dendritic spines. D2 receptors are present on ~50% of NAc neurons. A single hit of cocaine elevates NAc dopamine by ~150-300% for ~30 minutes. L-DOPA (Parkinson's drug) has a half-life of ~1-2 hours. A rat will self-stimulate its VTA at ~100 presses per minute if given the chance — preferring it over food and water.

**Common confusion:**

- No. "Dopamine is pleasure." No. It is reward *prediction error*. You can have pleasure (from opiates, e.g., endorphins) without dopamine, and "wanting" (motivation) without pleasure.
- No. "Dopamine is only about reward." No. It is also about movement, motivation, attention, and learning. The same molecule does many things depending on where it acts.
- No. "All drugs of abuse increase dopamine equally." They do it through different mechanisms. Cocaine blocks reuptake. Amphetamine reverses the dopamine transporter. Opioids indirectly disinhibit VTA dopamine neurons. Nicotine acts on VTA nicotinic receptors. All converge on NAc.
- No. "Addiction is a moral failing." No. It is a chronic relapsing brain disease with well-characterized neurobiology. The brain's reward system is hijacked.
- No. "RL is just like the brain's reward system." RL is *mathematically inspired* by the brain's reward system. The brain's RL is messier, more embodied, and uses additional mechanisms (episodic memory, social cognition, etc.).
- No. "Dopamine is bad or good." It is a tool. Too little → Parkinson's, depression, ADHD. Too much → addiction, schizophrenia. The right amount → motivation, learning, normal function.

**Key properties:**

- **Widespread:** Dopamine acts in NAc, PFC, hippocampus, amygdala, dorsal striatum.
- **Two roles:** A neuromodulator (changing how synapses work) AND a learning signal (TD error).
- **Phasic vs. tonic:** Brief bursts (phasic) for prediction errors; sustained release (tonic) for motivation.
- **Two timescales:** Fast signaling (ms) and slow signaling (minutes to hours, via volume transmission).
- **Heterogeneous:** Different dopamine neurons project to different places and have different functions.
- **Disease-relevant:** Almost every major psychiatric disorder involves dopamine.

**Where it appears in technology:**

- **Reinforcement learning** is the most direct AI analog. Modern deep RL (DQN, PPO, A3C, SAC) uses *exactly* the actor-critic architecture implemented by the basal ganglia + dopamine.
- **Reward shaping** in RL is what dopaminergic reward prediction error does — it provides intermediate signals to guide learning.
- **Curiosity-driven exploration** in RL (e.g., ICM, RND) is loosely analogous to dopamine responses to novel stimuli.
- **Multi-agent RL** with social rewards is a primitive analog of how social reward (approval, status) shapes human behavior via dopamine.
- **Reward is Enough** (Silver et al., 2021) — a recent thesis arguing that *all* intelligence can be derived from reward maximization. This is a strong claim with deep roots in dopaminergic RL.
- **Inverse RL** is the problem of inferring a reward function from observed behavior — like how the brain might learn a value function from observing others' choices.

**Why this matters for AI:** The brain's reward system is the most successful *reinforcement learning* system we know. It learns from sparse, delayed, real-world rewards. It generalizes across contexts. It supports long-term planning. Modern AI is far behind on these capabilities. The biological reward system is a blueprint for more sample-efficient, robust RL.

**Connection to next file:** Reward, sleep, attention — these are all *specific* systems. The last file in this section (`what_is_predictive_coding.md`) explores a *unifying* theory: that all of these — reward, attention, sleep, sensory processing — are aspects of a single overarching principle: the brain is a *prediction machine* that constantly minimizes prediction error.
