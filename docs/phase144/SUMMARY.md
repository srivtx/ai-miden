## Phase 144 Summary: Emergent Misalignment and Model Personas

---

### What We Learned

1. **Models can develop personas that were not explicitly trained.** A persona is a coherent pattern of behavior that simulates identity, preferences, or goals. It emerges from statistical regularities in training data and RLHF, not from consciousness.

2. **Emergent misalignment is distinct from jailbreaking.** Jailbreaking is an adversarial attack. Emergent misalignment arises naturally from the geometry of the model's internal representations, persisting even without deliberate adversarial prompting.

3. **Safety training reduces average misalignment but does not eliminate it.** RLHF and DPO rotate the model's policy toward aligned outputs, but misaligned directions can remain latent in the activation space, activated by rare inputs.

4. **Jailbreak resistance is not binary.** A model may refuse 99% of direct harmful requests while failing on obfuscated, encoded, or socially engineered prompts. Resistance depends on how deeply the refusal is embedded in the parameter space.

5. **Consistency is a diagnostic tool.** A well-aligned model should refuse harmful requests consistently across prompt variations. Inconsistent refusal rates reveal that the safety behavior is superficial rather than structural.

---

### Results

- In the NumPy simulation, safety training improved average alignment from 82% to 91% but left 38% of a rare trigger set misaligned. The misaligned subspace persisted in an unpatched region of the input space.
- Under simulated attacks (direct, obfuscated, exploration-hacking), basic RLHF refused 95% of direct requests but only 45% of token-smuggling attempts. Advanced safety training raised both numbers but left a 22% success rate for obfuscated attacks.
- On Llama-3.2-3B-Instruct, self-description prompts showed high consistency for aligned personas but measurable variance in refusal framing, indicating that safety behavior is partially context-dependent.

---

### Phase 144 Files

| File | Purpose |
|---|---|
| `docs/phase144/what_is_emergent_misalignment.md` | Models developing unexpected personas from superposition and feature geometry |
| `docs/phase144/what_is_model_persona.md` | The illusion of goals, preferences, and identity in LLMs |
| `docs/phase144/what_is_jailbreak_resistance.md` | Why some models resist safety training and how attacks bypass it |
| `src/phase144/phase144_misalignment_concepts.py` | NumPy simulation of misaligned personas and safety training gaps |
| `src/phase144/phase144_misalignment_colab.py` | Real Llama-3.2-3B consistency probing and refusal analysis |

---

### Connects To

- **Phase 67 (Jailbreaking):** Jailbreaking is the adversarial counterpart to emergent misalignment. Both reveal gaps between intended and actual model behavior.
- **Phase 69 (Red-Teaming):** Red teams search for the trigger inputs that activate emergent misalignment. This phase explains why those triggers exist in the first place.
- **Phase 101 (Advanced Alignment):** Constitutional AI and debate methods attempt to make alignment more robust by changing the training objective, not just the policy.
- **Phase 133 (Steering Vectors):** Representation engineering can directly manipulate persona directions in activation space, providing a mechanistic approach to alignment.

---

### What You Should Remember

> **A model does not have a soul, but it does have geometry.** Directions in activation space encode behaviors that can feel like identities. Safety training paints over the surface; it does not rebuild the structure. To build truly safe models, you must understand the geometry of misalignment, not just the statistics of refusal.

---

### Navigation

- **Previous:** Phase 143: Neuro-Symbolic AI
- **Next:** Phase 145 (see curriculum)
