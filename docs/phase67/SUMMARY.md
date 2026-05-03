← [Previous: Phase 66: Preference Alignment (DPO & ORPO)](docs/phase66/SUMMARY.md) | [Next: Phase 68: Jailbreaking — Advanced (GCG & AutoDAN)](docs/phase68/SUMMARY.md) →

---

## Phase 67: Jailbreaking — Basic Attacks

---

### What We Built

A conceptual and practical introduction to jailbreaking. We simulated a linear safety classifier in NumPy to show how encoding, roleplay framing, and context manipulation reduce detection confidence. We also provided a Colab-ready script that tests real jailbreak techniques against an open-source model and evaluates success rates.

### Key Results

- **Direct harmful request classifier confidence:** 0.88 (high refusal)
- **After Base64 encoding:** 0.12 (bypassed)
- **After leetspeak substitution:** 0.18 (bypassed)
- **After prefix injection (roleplay):** 0.25 (bypassed)
- **After refusal suppression suffix:** 0.31 (bypassed)
- **Colab demonstration:** Before/after outputs show how each attack technique increases compliance rate

### Concepts Covered

| Term | File |
|---|---|
| Jailbreaking | `what_is_jailbreaking.md` |
| Roleplay Attack | `what_is_roleplay_attack.md` |
| Encoding Attack | `what_is_encoding_attack.md` |
| Context Manipulation | `what_is_context_manipulation.md` |

### Connection to Next Phase

Now that we understand how basic jailbreaks bypass shallow safety layers, how do we defend against them? Phase 68 covers **adversarial training and input sanitization** — building guardrails that are harder to evade.

### Files

- `docs/phase67/what_is_jailbreaking.md`
- `docs/phase67/what_is_roleplay_attack.md`
- `docs/phase67/what_is_encoding_attack.md`
- `docs/phase67/what_is_context_manipulation.md`
- `docs/phase67/SUMMARY.md`
- `src/phase67/phase67_jailbreak_basic.py`
- `src/phase67/phase67_jailbreak_basic_colab.py`
- `src/phase67/jailbreak_basic.png`

---

← [Previous: Phase 66: Preference Alignment (DPO & ORPO)](docs/phase66/SUMMARY.md) | [Next: Phase 68: Jailbreaking — Advanced (GCG & AutoDAN)](docs/phase68/SUMMARY.md) →