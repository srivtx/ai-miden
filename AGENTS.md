# Agent Instructions for `ai-miden`

## Project Overview

A phase-based AI course (0–32) built from scratch in Python/NumPy. Each phase teaches one concept with:
- `docs/phaseX/what_is_*.md` — per-term documentation (definition, analogy, numeric example, common confusion)
- `src/phaseX/phaseX_*.py` — local NumPy concept demonstration
- `src/phaseX/phaseX_*_colab.py` — PyTorch GPU script for Colab T4 (training-heavy phases only)
- `docs/phaseX/SUMMARY.md` — phase recap and curriculum connections

## Non-Obvious Conventions

### Two-Script Pattern
- **Local scripts** (`phaseX_*.py`) use only NumPy. They demonstrate concepts, not train real models.
- **Colab scripts** (`phaseX_*_colab.py`) use PyTorch + CUDA. Created for phases where raw NumPy training fails or is too slow (phases 15–21, 29–31).
- If a local script produces collapsed/blurry outputs, do not over-tune it. Write a Colab version instead.

### Code Style
- Every line must explain **WHY**, not just WHAT.
- All plotting code must begin with:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  ```
- Never use interactive plots (`plt.show()` without `Agg` backend blocks in scripts).
- Save plots to `src/phaseX/` with descriptive names.

### Documentation Style
Every `what_is_*.md` must follow this exact structure:
1. Why it exists (THE PROBLEM first)
2. Definition (very simple)
3. Real-life analogy
4. Tiny numeric example
5. Common confusion (5+ bullet points)
6. Where it is used in our code

### Phase Completion Checklist
When finishing a phase, update **all** of these in order:
1. Create docs in `docs/phaseX/`
2. Create code in `src/phaseX/`
3. Write `docs/phaseX/SUMMARY.md`
4. Add phase to `README.md`:
   - Project structure tree
   - Phase journey diagram (the `PHASE X: ... ↓ PHASE Y: ...` block)
   - Quick-start commands
   - Course stats table (docs / code files / terms)
   - Final message paragraph
5. Mark `(COMPLETED)` in `docs/MASTER_CURRICULUM.md`
6. Run the local script from project root:
   ```bash
   cd /Users/zen/Desktop/building-ai/ai-miden && python src/phaseX/phaseX_*.py
   ```

## Architecture

```
ai-miden/
├── docs/
│   ├── phase0/ ... phase32/    # Each phase: what_is_*.md docs + SUMMARY.md
│   ├── research/               # Legacy deep-dive docs (being phased out)
│   ├── MASTER_CURRICULUM.md    # 33-phase roadmap, mark COMPLETED as you go
│   └── ROADMAP*.md             # Older planning docs
├── src/
│   ├── phase0/ ... phase32/    # Each phase: local script + optional Colab script + plots
└── README.md                   # Living document; update stats and structure every phase
```

## Running Code

All scripts assume the project root as working directory:
```bash
# Correct
python src/phase4/phase4_neural_network.py

# Wrong (changes relative path behavior for plot saves)
cd src/phase4 && python phase4_neural_network.py
```

No test suite, no build system, no `requirements.txt`. Just Python + NumPy + Matplotlib. Colab scripts need PyTorch.

## Stats Table (copy this format into README)

```markdown
| Phase | Docs | Code Files | New Terms |
|---|---|---|---|
| Phase X | N | N | N |
| **Total** | **N** | **N** | **N** |
```

Update the total row when adding a phase.

## Git

- **Do not commit unless explicitly asked.**
- When asked, use `git add . && git commit -m "Phase X: ..."` (no push unless requested).
- If user asks to "commit after every phase," do so immediately after finishing the phase checklist above.

## Common Pitfalls

- **README final message** accumulates adjectives as phases grow. Update it to reflect the full journey (e.g., "Through thirty-two phases, you went from...").
- **Phase numbers > 21** may not appear in the old Quick Start block. Scroll down to verify.
- **MASTER_CURRICULUM.md** uses `(COMPLETED)` suffix on phase headers. Do not alter the table format.
- **Do not create new README files or documentation files** unless explicitly asked or they are part of the standard phase completion checklist.
- **No emojis** in any markdown files.
