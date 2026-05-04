## Phase 143 Summary: Neuro-Symbolic AI (LLMs + Symbolic Reasoning)

---

### What We Learned

1. **Neural networks excel at perception but fail at precise reasoning.** Pattern matching over training data cannot guarantee logical consistency. A model that answers 92% of math word problems correctly still fails catastrophically on the remaining 8% with no warning.

2. **Symbolic solvers provide correctness guarantees but require crisp inputs.** Answer Set Programming, SAT solvers, and theorem provers can verify constraints exhaustively, but they break when the input is noisy or unstructured.

3. **Neuro-symbolic integration combines the strengths of both paradigms.** The neural module handles the messy real world (natural language, images, noise). The symbolic module handles structured inference (logic, constraints, planning). The result is more robust than either alone.

4. **LLMs can act as translators between natural language and formal languages.** A general-purpose LLM, prompted correctly, can generate ASP rules, Python constraint programs, or theorem-prover scripts. The solver then verifies the translation, turning silent errors into detectable inconsistencies.

5. **Tool-augmented reasoning extends the LLM's capabilities beyond its training distribution.** Calculators, code interpreters, and search engines let the model reach outside its parameters for precise, up-to-date, or computationally expensive information.

---

### Results

- In the NumPy simulation, the neural-only module achieved 62% accuracy on noisy object classification. The symbolic-only module achieved 45% because it could not handle ambiguous inputs. The neuro-symbolic combination reached 89% by using the neural module for perception and the symbolic module for consistency checking.
- On real logic puzzles with Qwen2.5-3B-Instruct, direct LLM reasoning solved only 55% of Sudoku and constraint puzzles. The neuro-symbolic pipeline (LLM translates to constraints + Python solver) achieved 90% accuracy by delegating exhaustive search to a symbolic engine.
- Symbolic verification caught 5 inconsistent LLM translations in 20 test cases, enabling iterative refinement that pure generation could not provide.

---

### Phase 143 Files

| File | Purpose |
|---|---|
| `docs/phase143/what_is_neuro_symbolic_ai.md` | Core concept: combining neural perception with symbolic reasoning |
| `docs/phase143/what_is_llm_asp.md` | LLMs translating natural language to Answer Set Programming |
| `docs/phase143/what_is_tool_augmented_reasoning.md` | Delegating precise sub-tasks to external tools |
| `src/phase143/phase143_neuro_symbolic_concepts.py` | NumPy simulation of neural + symbolic integration |
| `src/phase143/phase143_neuro_symbolic_colab.py` | Real Qwen2.5-3B on logic puzzles with constraint verification |

---

### Connects To

- **Phase 27 (Agentic AI):** Tool-augmented reasoning is the engine behind agentic systems that use calculators, code interpreters, and search APIs.
- **Phase 69 (Red-Teaming):** Symbolic verification can be used to formally check whether a model's plan violates safety constraints.
- **Phase 100 (MechInterp):** Understanding how LLMs internally represent logical concepts helps design better LLM-to-symbolic translators.
- **Phase 115 (Constrained Decoding):** Both neuro-symbolic AI and constrained decoding impose structure on model outputs; the former uses external solvers, the latter uses grammar masks.

---

### What You Should Remember

> **A neural network is a pattern machine. A symbolic solver is a guarantee machine. Together, they are a reasoning machine.** Do not ask an LLM to do arithmetic, logic, or planning alone. Give it a solver, teach it to translate, and let the solver verify.

---

### Navigation

- **Previous:** Phase 142 (see curriculum)
- **Next:** Phase 144: Emergent Misalignment and Model Personas
