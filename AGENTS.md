# Agent Instructions for `ai-miden`

## Project Overview

A multi-track educational platform with three modules:

1. **AI Course (158 phases)** — Built from scratch in Python/NumPy + PyTorch
2. **Web3/Solana Course (36 phases)** — Built in Rust + TypeScript/Express
3. **DSA Interview Prep (18 patterns, 540 problems)** — Algorithm and system design practice

### AI Track
Each phase teaches one concept with:
- `docs/phaseX/what_is_*.md` — per-term documentation (definition, analogy, numeric example, common confusion)
- `src/phaseX/phaseX_*.py` — local NumPy concept demonstration
- `src/phaseX/phaseX_*_colab.py` — PyTorch GPU script for Colab T4 (training-heavy phases)
- `docs/phaseX/SUMMARY.md` — phase recap and curriculum connections

### Web3 Track
Each phase teaches one blockchain concept with:
- `docs_web3/phaseX/what_is_*.md` — per-term documentation (same structure as AI)
- `src_web3/phaseX/program_name/src/lib.rs` — Solana program in Rust (BPF)
- `src_web3/phaseX/*_api.ts` — TypeScript/Express API backend
- `docs_web3/phaseX/SUMMARY.md` — phase recap and connections

### DSA Module
- `docs_dsa/START_HERE.md` — Navigation and study plan
- `docs_dsa/01_arrays_hashing/` through `18_bit_manipulation/` — Pattern-based problem sets
- `docs_dsa/COMPANY_GUIDES/` — Google, Meta, Amazon specific prep
- `docs_dsa/FLASHCARDS.md` — 220 review cards

## Non-Obvious Conventions

### AI Two-Script Pattern
- **Local scripts** (`phaseX_*.py`) use only NumPy. They demonstrate concepts, not train real models.
- **Colab scripts** (`phaseX_*_colab.py`) use PyTorch + CUDA. Created for phases where raw NumPy training fails or is too slow.
- If a local script produces collapsed/blurry outputs, do not over-tune it. Write a Colab version instead.

### Web3 Dual-Track Pattern
- **Rust programs** (`src/lib.rs`) are on-chain Solana programs compiled to BPF bytecode.
- **TypeScript APIs** (`*_api.ts`) are Express servers that wrap on-chain operations or simulate them.
- Every phase has BOTH a Rust program and a TS API unless noted.

### Code Style (Both Tracks)
- Every line must explain **WHY**, not just WHAT.
- AI plotting code must begin with:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  ```
- Never use interactive plots (`plt.show()` without `Agg` backend blocks in scripts).
- Save plots to `src/phaseX/` with descriptive names.
- Web3 APIs run on dedicated ports (3000-3020) to avoid conflicts.

### Documentation Style (Both Tracks)
Every `what_is_*.md` must follow this exact structure:
1. Why it exists (THE PROBLEM first)
2. Definition (very simple)
3. Real-life analogy
4. Tiny numeric example
5. Common confusion (5+ bullet points)
6. Where it is used in our code

## Architecture

```
ai-miden/
├── docs/                           # AI Course (158 phases)
│   ├── phase0/ ... phase158/
│   ├── MASTER_CURRICULUM.md        # Full AI roadmap
│   └── AI_ROADMAP_FUTURE.md
├── src/                            # AI Code (158 phases)
│   ├── phase0/ ... phase158/
│   └── ...
├── docs_web3/                      # Web3 Course (36 phases)
│   ├── phase0/ ... phase35/
│   └── MASTER_CURRICULUM.md        # Full Web3 roadmap
├── src_web3/                       # Web3 Code (36 phases)
│   ├── phase0/ ... phase35/        # Rust + TypeScript
│   ├── package.json                # Node dependencies
│   └── tsconfig.json
├── docs_dsa/                       # DSA Interview Prep
│   ├── START_HERE.md
│   ├── 01_arrays_hashing/ ... 18_bit_manipulation/
│   ├── COMPANY_GUIDES/
│   ├── FLASHCARDS.md
│   └── ...
├── README.md                       # Main navigation (both tracks)
├── AGENTS.md                       # This file
└── .gitignore                      # Python + Rust + Node ignores
```

## Running Code

### AI Track
All scripts assume the project root as working directory:
```bash
# Correct
python src/phase4/phase4_neural_network.py

# Wrong (changes relative path behavior for plot saves)
cd src/phase4 && python phase4_neural_network.py
```

### Web3 Track
```bash
# Install Node dependencies
cd src_web3 && npm install

# Run TypeScript demos
npx ts-node src_web3/phase6/first_transaction.ts

# Start Express APIs
npx ts-node src_web3/phase13/vault_api.ts
npx ts-node src_web3/phase16/amm_api.ts

# Build Rust programs (requires Solana toolchain)
cd src_web3/phase8/hello_world && cargo build-bpf
```

## Phase Completion Checklist

When finishing a phase, update **all** of these in order:
1. Create docs in `docs/phaseX/` or `docs_web3/phaseX/`
2. Create code in `src/phaseX/` or `src_web3/phaseX/`
3. Write `SUMMARY.md`
4. Add phase to `README.md`:
   - Project structure tree
   - Phase journey diagram
   - Quick-start commands
   - Course stats table
5. Mark `(COMPLETED)` in `MASTER_CURRICULUM.md`
6. Run the local script to verify it works

## Git

- **Do not commit unless explicitly asked.**
- When asked, use `git add . && git commit -m "Phase X: ..."` (no push unless requested).
- Use `.gitignore` for `__pycache__/`, `.DS_Store`, `node_modules/`, Rust `target/`.

## Common Pitfalls

- **README final message** accumulates adjectives as phases grow. Update it to reflect the full journey.
- **Phase numbers > 21** may not appear in the old Quick Start block. Scroll down to verify.
- **MASTER_CURRICULUM.md** uses `(COMPLETED)` suffix on phase headers. Do not alter the table format.
- **Web3 APIs** need unique ports. Check what ports are already used before assigning a new one.
- **No emojis** in any markdown files.
- **Web3 Rust programs** need `Cargo.toml` in their project directory. Do not forget it.
