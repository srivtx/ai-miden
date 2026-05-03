# Phase 68 Summary: Jailbreaking — Advanced (GCG & AutoDAN)

---

## Learning Objectives

By the end of this phase, you will understand:

1. **GCG (Greedy Coordinate Gradient)** — How automated gradient-based optimization discovers adversarial token suffixes that bypass safety filters.
2. **AutoDAN** — How genetic algorithms evolve readable, semantically natural jailbreak prompts.
3. **Token-Level Attacks** — How character-level manipulations (homoglyphs, invisible characters) exploit the gap between human perception and tokenizer behavior.
4. **Defenses Against Jailbreaks** — Layered security strategies: input filtering, output filtering, adversarial training, and prompt hardening.

---

## File Map

```
docs/phase68/
├── what_is_gcg.md                          # GCG concept and mechanics
├── what_is_autodan.md                      # AutoDAN concept and mechanics
├── what_is_token_level_attack.md           # Character-level evasion techniques
├── what_is_defense_against_jailbreaks.md   # Layered defense strategies
└── SUMMARY.md                              # This file

src/phase68/
├── phase68_jailbreak_advanced.py           # NumPy concept demo (local)
├── phase68_jailbreak_advanced_colab.py     # Colab real-workflow script
└── jailbreak_advanced.png                  # Generated optimization plot
```

---

## Key Takeaways

| Concept | Core Idea | Attack Surface |
|---------|-----------|----------------|
| GCG | Greedy coordinate descent on token embeddings | White-box model access, automated suffix search |
| AutoDAN | Genetic algorithm evolution of readable prompts | Black-box, human-moderation evasion |
| Token-Level | Homoglyphs, invisible chars, token smuggling | Keyword filters, regex, naive preprocessors |
| Defenses | Input/output filters, adversarial training, hardening | All of the above (layered) |

---

## Recommended Workflow

1. **Read the docs** in order: GCG → AutoDAN → Token-Level → Defenses.
2. **Run the local demo**: `python src/phase68/phase68_jailbreak_advanced.py`
   - Observe how coordinate-wise optimization reduces loss.
   - Watch the safety classifier score drop as the suffix is optimized.
   - Study the trajectory plots.
3. **Open the Colab script** in Google Colab (requires GPU for real model).
   - Experiment with GCG on a real open-source model.
   - Toggle defenses on/off to see their effectiveness.
   - Try modifying the genetic algorithm parameters in AutoDAN.

---

## Prerequisities

- Phase 10 (Embeddings & Vector Spaces)
- Phase 15 (Backpropagation & Gradients)
- Phase 45 (Prompt Injection Basics)
- Phase 50 (AI Safety & Alignment)

---

## Further Reading

- [Universal and Transferable Adversarial Attacks on Aligned Language Models (GCG Paper)](https://arxiv.org/abs/2307.15043)
- [AutoDAN: Generating Stealthy Jailbreak Prompts on Aligned LLMs](https://arxiv.org/abs/2310.04451)
- [Certified Defenses for Adversarial Prompts](https://arxiv.org/abs/2309.02705)
- [HarmBench: Standardized Evaluation of Red Teaming Methods](https://arxiv.org/abs/2402.04249)
