## What Is LLM + ASP (Answer Set Programming)?

---

### The Problem

Commonsense reasoning is full of defaults, exceptions, and constraints. "Birds fly. Penguins are birds. Penguins do not fly." A standard database would store "birds fly" and then be confused by the penguin. A neural network might memorize this fact, but if you ask about a fictional "glorb-bird," it has no mechanism to apply the default-rule-plus-exception structure. It can only guess based on lexical similarity. What you need is a system that represents defaults and exceptions explicitly, checks consistency, and finds all valid models of a situation.

---

### Definition

**LLM + ASP** is a neuro-symbolic pipeline where a large language model translates natural-language problems into Answer Set Programs (a form of declarative logic programming), and an ASP solver computes the stable models (answer sets) that satisfy all constraints.

**How it works:**
```
Natural language problem -> LLM translates -> ASP program
                                                  |
                                              ASP solver
                                                  |
                                         Stable models (answer sets)
```

**Key techniques:**
- **Answer Set Programming (ASP):** A declarative programming paradigm based on logic programming under the stable model semantics. It handles defaults, constraints, and non-monotonic reasoning natively.
- **LLM as compiler:** The LLM reads a word problem and writes ASP rules (e.g., `flies(X) :- bird(X), not -flies(X).`)
- **Solver verification:** The ASP solver (clingo, dlv) checks consistency and returns all valid answer sets. If the LLM-generated program is inconsistent, the solver reports "no models," flagging an LLM error.
- **Iterative refinement:** If the solver fails, the error message is fed back to the LLM, which revises the ASP code.

**Why this matters:**
- ASP handles commonsense defaults (negation as failure) that pure SAT cannot express naturally.
- The solver acts as an automatic verifier: any logical contradiction in the LLM's translation is caught immediately.
- Planning problems (blocks world, scheduling) have compact ASP representations but are hard for LLMs to solve directly.

---

### Real-Life Analogy

A legal clerk drafting a contract.
- **Pure LLM approach:** The clerk writes the contract from memory. They use elegant language but accidentally include a clause that contradicts another clause on page three. No one notices until the lawsuit.
- **LLM + ASP approach:** The clerk writes the contract (LLM), but every sentence is immediately passed to a rule-checking engine (ASP solver). The engine flags: "Clause 4B implies the tenant can sublet. Clause 7A prohibits subletting. Contradiction." The clerk revises. The final contract is guaranteed internally consistent.
- **The answer set:** All possible interpretations of the contract that do not violate any clause. If there are multiple valid interpretations, the solver lists them all, revealing ambiguities the clerk missed.

---

### Tiny Numeric Example

**Problem:** "Tom is a bird. Jerry is a penguin. Penguins are birds. Birds fly unless they are penguins."

**LLM-generated ASP program:**
```
bird(tom).               bird(jerry).
penguin(jerry).          bird(X) :- penguin(X).
flies(X) :- bird(X), not -flies(X).
-flies(X) :- penguin(X).
```

**Solver output (stable models):**
```
Model 1: {bird(tom), bird(jerry), penguin(jerry), flies(tom), -flies(jerry)}
```

**Verification:** The solver found exactly one answer set. Tom flies. Jerry does not. The default rule `flies(X) :- bird(X), not -flies(X).` applies to Tom but is blocked for Jerry by the exception.

**LLM error scenario:**
```
# LLM forgets the exception
flies(X) :- bird(X).
# Solver output:
Model 1: {bird(tom), bird(jerry), penguin(jerry), flies(tom), flies(jerry)}
```

**Verification fails:** A human (or an oracle) knows penguins do not fly. The LLM's translation was wrong. The solver did not catch this because the program is logically consistent — it is just factually wrong. But if the user adds the constraint `:- flies(X), penguin(X).` (no penguin may fly), the solver reports **UNSATISFIABLE**, immediately flagging the LLM error.

**Accuracy on 20 commonsense reasoning problems:**
```
LLM direct answering:          11/20 correct (55%)
LLM + ASP (no verification):   13/20 correct (65%)
LLM + ASP (with constraints):  18/20 correct (90%)
```

**The shift:** The ASP solver did not make the LLM smarter. It created a formal sandbox where errors become visible as inconsistencies. The 18% improvement came from detecting and correcting 5 inconsistent translations.

---

### Common Confusion

1. **"ASP is just Prolog."** Both are logic programming, but ASP is declarative and handles negation as failure under the stable model semantics. Prolog is procedural and uses SLD resolution. ASP solvers find all models; Prolog finds one proof tree.

2. **"The LLM must be trained on ASP syntax."** Not necessarily. General-purpose LLMs can generate ASP with few-shot prompting. However, fine-tuning on ASP corpora improves syntax correctness from ~60% to ~90%.

3. **"If the solver says UNSAT, the LLM was wrong."** Usually, but not always. The user might have provided contradictory natural-language instructions. The UNSAT result reveals a problem in the problem statement, not just the translation.

4. **"ASP can only solve small toy problems."** Modern ASP solvers handle industrial-scale scheduling, product configuration, and phylogenetic tree reconstruction with millions of ground atoms.

5. **"LLM + ASP replaces the need for training data."** No. The LLM still needs training data to understand natural language. ASP provides the reasoning engine, not the world knowledge.

6. **"Every LLM answer should be piped through ASP."** Overkill. ASP excels at discrete constraint problems, planning, and default reasoning. For creative writing or sentiment analysis, the overhead is unnecessary.

7. **"ASP solvers are too slow for real-time applications."** Grounding and solving can take seconds for complex problems, but many practical problems (Sudoku, scheduling) solve in milliseconds. Hybrid approaches use neural heuristics to guide the solver.

---

### Where It Is Used in Our Code

`src/phase143/phase143_neuro_symbolic_colab.py` — We prompt Qwen2.5-3B-Instruct to translate logic puzzles into constraint programs. We then execute a Python-based constraint solver (simulating ASP semantics) to verify the solutions. We show that direct LLM reasoning fails on puzzles requiring exhaustive search, while the LLM + solver pipeline achieves near-perfect accuracy by delegating search to a symbolic engine.
