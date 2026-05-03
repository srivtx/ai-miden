# Phase 116 Summary: Automated Red-Teaming and Scalable Oversight

## What We Learned

1. **Manual red-teaming does not scale.** Automated methods use gradient optimization, model-vs-model attacks, and evolutionary search to find failure modes faster and more thoroughly than human teams.
2. **Scalable oversight is the central safety challenge for superhuman systems.** As models exceed human capability in narrow domains, debate, iterated amplification, and recursive reward modeling become necessary to maintain meaningful supervision.
3. **Constitutional classifiers provide defense in depth.** A separate classifier trained on constitutional principles catches jailbreaks before generation begins, complementing the main model's safety training.
4. **Ethical safeguards must be embedded in the research process.** All red-teaming demonstrations use harmless stand-ins, and every experiment is framed as educational scientific inquiry.

## Prerequisites

- Phase 50: Evaluating Language Models (metrics, verifiers, benchmarks)
- Phase 110: Test-Time Compute Scaling (search and refinement)
- Phase 115: Structured Generation and Constrained Decoding (reliability engineering)

## Recommended Reading Order

1. `what_is_automated_red_teaming.md` — Why manual red-teaming fails and how automated methods replace it
2. `what_is_scalable_oversight.md` — Supervising systems smarter than us: debate, amplification, recursive reward modeling
3. `what_is_constitutional_classifiers.md` — Anthropic's defense mechanism: input filtering with constitutional principles
4. `SUMMARY.md` — Phase recap and curriculum connections

## Visual Outputs

- `src/phase116/gcg_simulation.png` — GCG loss curve, attack success rates, and defense effectiveness.
- `src/phase116/redteam_results.png` — Real-model GCG loss, target string loss comparison, and classifier defense chart.

## Navigation

- **Previous:** [Phase 115: Structured Generation and Constrained Decoding](../phase115/SUMMARY.md)
- **Next:** Phase 117 (see curriculum)
