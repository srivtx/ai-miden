# Agent Brain: How This Curriculum Was Built

> This document captures the methodology, patterns, and decision-making framework used to build the ai-miden curriculum. It is not about the content — it is about the *process*.

---

## 1. The Core Philosophy

### Why Over What
Every line of code must explain **WHY**, not just WHAT. This applies to:
- Comments (`// WHY: ` prefix mandatory)
- Documentation structure (Problem first, then definition)
- Architecture decisions (every step explains the reasoning)
- Git commits (explain the "why", not the "what")

### Progressive Disclosure
Never dump information. Build in layers:
1. **The Problem** — Why does this exist? What pain does it solve?
2. **The Analogy** — How does this work in everyday life?
3. **The Numbers** — Concrete example with actual math
4. **The Code** — Working implementation
5. **The Confusion** — What do people get wrong? (6 bullets, each starting with "No.")

### Connection-Based Learning
Every phase must answer: **"What does the student wonder AFTER finishing the previous phase?"**
- Phase N+1 is the natural next question from Phase N
- No arbitrary jumps. No "here are 5 unrelated topics"
- SUMMARY.md must have "Connection to Next Phase" section

---

## 2. The Agent Swarm Pattern

### When to Use Swarms
Use parallel agents when:
- **Evaluating** existing content (quality check across multiple files)
- **Building** independent phases that do not share state
- **Researching** multiple topics simultaneously
- **Fixing** unrelated files

### Swarm Size
- **Evaluation**: 12-15 agents (one per file/phase)
- **Building**: 8-12 agents (one per phase)
- **Research**: 3-5 agents (different angles)
- **DO NOT** use 100 agents — coordination overhead exceeds benefit

### Swarm Coordination
1. **Define boundaries** — Each agent gets exact file paths
2. **Shared structure** — Every agent uses the same doc template
3. **No mid-swarm changes** — Once launched, let agents finish
4. **Verify after** — Always run verification commands post-swarm

### Swarm Failure Handling
If an agent fails or returns empty:
- Check if the task was too large (split it)
- Check if file paths were wrong (verify with `ls`)
- For critical files, build directly instead of delegating
- Never assume "agent will handle it" — verify

---

## 3. The Build Decision Tree

### Concept Phase vs Real Project
```
Is this teaching a single concept?
├── YES → Concept Phase (what_is_*.md + simple demo)
│         └── 3 docs, 1 API, 1 SUMMARY
└── NO → Is this a production system?
    ├── YES → Real Project Phase
    │         └── ARCHITECTURE.md + multiple programs + API + tests
    └── NO → Concept Phase
```

### When to Rewrite vs Fix
```
Does the existing code have structural flaws?
├── YES (stubbed functions, fake security, broken math)
│   └── Create v2 phase (54v2, 55v2, etc.)
│   └── v2 must explicitly compare to v1 in SUMMARY.md
│   └── Explain: what changed, why changed, how changed
└── NO (minor bugs, missing steps)
    └── Fix in place
```

### Research Before Build
**Never** build without researching first:
1. What do professionals actually use? (Anchor vs native, Jupiter vs manual)
2. What is production-ready vs experimental? (Clockwork = dead, skip it)
3. What is the adoption data? (Token-2022 becoming default, SPL legacy)
4. What separates junior from senior? (CU optimization, LUTs, priority fees)

### The v2 Pattern
When rewriting a phase:
1. Keep original phase intact (do not delete)
2. Create `phaseNv2` directory
3. In v2 SUMMARY.md, add comparison table:
   | Aspect | Phase N | Phase Nv2 |
   |---|---|---|
   | Framework | Native Rust | Anchor v1.0 |
   | Token Standard | SPL | Token-2022 |
   | Signature Verification | Stubbed | Real Ed25519 |
4. Add deprecation note to original phase SUMMARY.md

---

## 4. Documentation Standards

### File Structure Per Phase
```
docs_web3/phaseX/
├── what_is_term_a.md      # First concept
├── what_is_term_b.md      # Second concept
├── what_is_term_c.md      # Third concept
├── SUMMARY.md             # Phase recap + connections
└── ARCHITECTURE.md        # Only for Real Project phases

src_web3/phaseX/
├── program_a/src/lib.rs   # On-chain program
├── program_a/Cargo.toml
├── program_b/src/lib.rs   # Second program (if needed)
├── program_b/Cargo.toml
├── api.ts                 # Express API
├── service.ts             # Standalone service (if needed)
└── deploy.sh              # Build + deploy script
```

### Doc Template (Mandatory)
Every `what_is_*.md` must have:
1. `## What Is [Term]?`
2. `**The Problem:**` — 2-3 sentences
3. `**Definition:**` — 1-2 sentences
4. `**How It Works (Step-by-Step):**` — 4-6 numbered steps
5. `**Real-life analogy:**` — Concrete everyday example
6. `**Tiny numeric example:**` — Specific numbers, actual math
7. `**Common confusion:**` — 6 bullets, each starts with "No."
8. `**Key properties:**` — 4-5 bullets
9. `**Where it appears in our code:**` — File reference

### Code Standards
- **Rust**: Anchor v1.0 for production phases, native Rust for concept phases
- **TypeScript**: `@coral-xyz/anchor` for Anchor clients, `@solana/web3.js` for raw
- **Every line**: `// WHY: ` comment explaining purpose
- **No emojis**: Anywhere in the codebase
- **No stubs**: If a function transfers tokens, it must be a real CPI call
- **Error handling**: Typed errors with `thiserror` (Rust), try/catch with logging (TS)

---

## 5. The Evaluation Loop

### Before Building: Evaluate Existing Content
1. Launch 12-15 evaluation agents in parallel
2. Each rates 7 criteria (1-10 scale):
   - Problem explanation clarity
   - Definition precision
   - Step-by-step depth
   - Analogy helpfulness
   - Numeric example concreteness
   - Common confusion coverage
   - Beginner-friendliness
3. Overall score < 8.0 = needs expansion
4. Empty sections (Key Properties, Step-by-Step) = automatic flag

### After Building: Verify Quality
```bash
# Check file counts per phase
for i in $(seq 51 58); do
  echo "phase$i: $(find docs_web3/phase$i -type f | wc -l) docs, $(find src_web3/phase$i -type f | wc -l) code"
done

# Check for missing SUMMARY.md
for d in docs_web3/phase*/; do
  [ ! -f "$d/SUMMARY.md" ] && echo "Missing: $d"
done

# Check for emojis (should be 0)
grep -r "emoji_pattern" docs_web3/ src_web3/ | wc -l
```

---

## 6. Curriculum Architecture

### The Three Tracks
```
Concept Phases (0-50)
    ↓ (student asks: "How do I build this for real?")
Real Project Phases (51-58)
    ↓ (student hits: "My transactions fail on mainnet")
Production Engineering Phases (59-66)
    ↓ (student asks: "How do I integrate everything?")
v2 Rewrites (54v2, 55v2, 56v2, 58v2)
    ↓ (student deploys to mainnet)
Capstone (67+)
```

### Connection Rules
- Phase N must answer a question raised by Phase N-1
- Phase N+1 must be the natural next step after Phase N
- If a phase feels "tacked on", it is in the wrong place
- Every SUMMARY.md must have "Connection to Next Phase"

---

## 7. Git Hygiene

### Commit Granularity
- One commit per logical batch (e.g., "Add phases 36-50")
- Never commit untested code
- Update README stats in the same commit as content additions
- Do not push until explicitly asked

### Commit Message Format
```
[Scope]: [What changed]

[Why it changed]
[Impact stats]
```

Example:
```
Add Web3 phases 36-50: Subscription payments through DePIN

75 files changed, 6207 insertions(+)
Covers subscriptions, vesting, DIDs, quadratic voting, bridges
```

---

## 8. Common Pitfalls (Learned the Hard Way)

### The "Stub Trap"
Agents often write stubbed functions with comments like "// In production, verify signature here". This is poison. Students copy-paste and deploy broken code.

**Fix**: Explicitly require "No stubs — all transfers must be real CPI calls"

### The "Mock API Trap"
Agents build Express APIs with in-memory `Map` storage instead of actual on-chain interaction. This creates a false sense of completion.

**Fix**: APIs must construct real transactions with `@solana/web3.js` or `@coral-xyz/anchor`

### The "Thin Doc Trap"
Agents generate 40-line docs when the standard is 80-120 lines. Step-by-step sections are often missing entirely.

**Fix**: Evaluate first. Flag thin docs. Require 5-6 step walkthroughs.

### The "Port Conflict Trap"
Multiple APIs on the same port cause silent failures.

**Fix**: Maintain a port registry. Phase 51 = 3055, Phase 52 = 3056, etc.

### The "Missing Cargo.toml Trap"
Agents create `src/lib.rs` but forget `Cargo.toml`. The code is unbuildable.

**Fix**: Verify `find src_web3/phaseX -name "Cargo.toml"` returns expected count

---

## 9. Port Registry

| Phase | Port | Service |
|-------|------|---------|
| 51 | 3055 | DEX API |
| 52 | 3056 | Lending API |
| 53 | 3057 | NFT Marketplace API |
| 54 | 3058 | DAO API (legacy) |
| 54v2 | 3063 | DAO API (Anchor) |
| 55 | 3059 | Yield Farm API (legacy) |
| 55v2 | 3064 | Yield Farm API (Anchor) |
| 56 | 3060 | Bridge API (legacy) |
| 56v2 | 3065 | Bridge API (Anchor) |
| 57 | 3061 | Prediction Market API |
| 58 | 3062 | Launchpad API (legacy) |
| 58v2 | 3066 | Launchpad API (Jupiter) |
| 59 | 3067 | Anchor Counter API |
| 60 | 3068 | Jupiter Swap API |
| 61 | 3069 | Infrastructure API |
| 62 | 3070 | Token-2022 API |
| 63 | 3071 | Blinks Server |
| 64 | 3072 | ZK Compression API |
| 65 | 3073 | Drift Keeper API |
| 66 | 3074 | Security Audit API |

---

## 10. Research Checklist

Before adding any new phase, verify:
- [ ] Is this technology production-ready? (Skip Clockwork, Steel alpha)
- [ ] Do professionals actually use this? (Anchor yes, Seahorse no)
- [ ] What is the adoption data? (Jupiter 75%+ of dApps)
- [ ] What did we miss in the previous phase? (Fix gaps first)
- [ ] Does this answer a natural student question?
- [ ] Can we build a runnable devnet demo?
- [ ] Are there real APIs/SDKs we can integrate?

---

## 11. The "Enough" Checklist

The curriculum is complete when:
- [ ] Every concept phase has 3 detailed docs + SUMMARY
- [ ] Every real project has ARCHITECTURE.md + multiple programs + API
- [ ] Every API constructs real transactions (no in-memory mocks)
- [ ] Every program has real CPI calls (no stubs)
- [ ] v2 phases exist for all broken original phases
- [ ] Production engineering phases cover: Anchor, Jupiter, Helius, Token-2022, Blinks, ZK, Drift, Security
- [ ] Curriculum document lists all phases with descriptions
- [ ] README has accurate stats and navigation
- [ ] AGENTS.md documents the build methodology
- [ ] Port registry is complete and conflict-free

---

## 12. Final Rule

> **Never build what you have not first understood. Never teach what you have not first built.**

Research → Evaluate → Plan → Build → Verify → Document → Commit
