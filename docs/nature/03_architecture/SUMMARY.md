# Part 3: Architecture — Summary

> The brain is not a single organ. It is a *collection* of specialized structures, each evolved for a different function, but all interconnected into a single integrated system. The architecture is the constraint that makes learning possible.

---

## The seven architectural elements

1. **Glia** (`what_is_glia.md`) — 50% of brain cells. Support, modulate, prune, myelinate. Active participants, not just glue.

2. **Cortex** (`what_is_cortex.md`) — 2-3 mm thick sheet, ~16-26 billion neurons, 6 layers, 4 lobes. The seat of perception, thought, language.

3. **Cortical column** (`what_is_cortical_column.md`) — ~300-500 µm vertical slab, the repeating functional unit. ~200 million minicolumns in human cortex. Same basic circuit everywhere.

4. **Thalamus** (`what_is_thalamus.md`) — Gateway to the cortex. ~50-60 nuclei, each gating a specific input. Reticular nucleus gates thalamocortical transmission.

5. **Hippocampus** (`what_is_hippocampus.md`) — Memory palace. Place cells, trisynaptic circuit, theta rhythm, sharp-wave ripples. Episodic memory and spatial navigation.

6. **Basal ganglia** (`what_is_basal_ganglia.md`) — Action selection. Direct and indirect pathways, dopamine-driven reinforcement learning, actor-critic architecture. Habits and reward.

7. **Cerebellum** (`what_is_cerebellum.md`) — Timing and motor learning. ~80% of brain neurons, mostly granule cells. Forward models, error correction, sub-millisecond precision.

---

## The macro-architecture: a quick map

```
                    CORTEX (perception, thought, planning)
                              ▲     ▲
                              │     │
        ┌─────────────────────┼─────┼─────────────────────┐
        │                     │     │                     │
   THALAMUS              HIPPOCAMPUS              BASAL GANGLIA
   (gating)              (memory, space)         (action, reward)
        ▲                                            ▲
        │                                            │
   SENSORY INPUT                              DOPAMINE
   (retina, cochlea,                          (VTA, SNc)
    skin, etc.)                                     │
        ▲                                            ▼
        │                                     CEREBELLUM
   BRAINSTEM                                (timing, motor
                                              correction)
```

The cortex is the "high-level" processor. The thalamus is its gateway. The hippocampus indexes the cortex for memory. The basal ganglia select actions. The cerebellum fine-tunes movements. The brainstem provides the life support and sensory relays.

---

## Five universal principles of brain architecture

1. **Hierarchy.** Most systems are layered: low-level (sensory, motor) → mid-level (associative) → high-level (prefrontal, integrative). Information flows up (perception) and down (prediction, control).

2. **Modularity with integration.** Distinct regions handle distinct functions. But every region is connected to many others. No region is an island.

3. **Recurrence.** Almost every cortical area has feedback connections. The brain is not a feedforward pipeline; it is a *recurrent* network with extensive top-down signaling.

4. **Uniformity.** Within the cortex, the same circuit is used everywhere. Specialization comes from inputs and outputs, not different hardware.

5. **Bilateral symmetry.** Most structures come in pairs. The two hemispheres have largely redundant functions, with some specialization (e.g., language usually in the left).

---

## The most important cross-cutting lesson: predictability and control

Each of these structures participates in a *prediction-correction* loop:

- **Cortex:** Generates predictions about the world.
- **Thalamus:** Delivers prediction errors to cortex.
- **Hippocampus:** Stores predictions about where/when events occur.
- **Basal ganglia:** Predicts the value of actions.
- **Cerebellum:** Predicts sensory outcomes of motor commands.

The brain is not just a feedforward system or a reactive system. It is a *predictive control system* — constantly making predictions, comparing them to reality, and updating its internal models. This is the core insight of *predictive coding* (see `04_systems/`).

---

## Where biological architecture beats modern AI

1. **Active gating.** The thalamus actively controls what reaches the cortex. AI systems typically receive all data equally.
2. **Specialized modules.** The brain has dedicated structures for memory (hippocampus), timing (cerebellum), action (basal ganglia), spatial cognition (entorhinal grid cells). Modern AI tends to have one general-purpose architecture.
3. **Re-entry and feedback.** The brain is recurrent, with massive top-down projections. Most ANNs are feedforward.
4. **Local computation in columns.** The cortex's basic unit is a column with rich internal computation. ANNs use simple "neurons" as units.
5. **Predictive control.** The brain is a prediction machine. ANNs are pattern matchers.

These are all architectural choices. Modern AI is starting to incorporate them (e.g., mixture of experts, recurrent transformers, retrieval-augmented memory), but it is still far from the brain's architecture.

---

## Connection to the next part

Architecture is the substrate. Now we explore the *systems* that emerge from these structures:

- `04_systems/what_is_visual_system.md` — A worked example of cortical hierarchy
- `04_systems/what_is_attention.md` — How the brain selects what to process
- `04_systems/what_is_sleep.md` — Offline consolidation and replay
- `04_systems/what_is_reward.md` — Dopamine and reinforcement learning
- `04_systems/what_is_predictive_coding.md` — The brain as a prediction machine

The transition from anatomy to function is the next step. The brain is not a static structure; it is a *process* running on an architecture. The next part explores that process.
