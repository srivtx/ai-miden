# DSA Navigation Map

> **How to navigate this system. Start here. Do not get lost.**

---

## The Master Folder Map

```
docs_dsa/
│
├── START_HERE.md              ← YOU ARE HERE (read this first)
├── README.md                  ← Overview & philosophy
├── ROADMAP.md                 ← Visual dependency graph
├── MASTER_PLAN.md             ← 108 archetype architecture
├── PEDAGOGY.md                ← How to actually learn
├── LEARNING_SCHEDULE.md       ← 16-week day-by-day plan
│
├── 01_arrays_hashing/         ← START: The foundation
│   ├── pattern_detailed.md    ← Theory: 8 archetypes explained
│   ├── archetypes_complete.md ← Deep dive with 40+ variations
│   ├── drills_part2.md        ← Practice: 15 warm-ups + core
│   └── drills_part3.md        ← Mastery: 15 near-misses + blends
│
├── 02_two_pointers/
│   ├── archetypes_complete.md ← 7 archetypes
│   ├── drills_part2.md        ← 15 practice problems
│   └── drills_part3.md        ← 15 advanced problems
│
├── 03_stack/
│   ├── archetypes_complete.md ← 6 archetypes
│   ├── drills_part2.md
│   └── drills_part3.md
│
├── 04_binary_search/
│   ├── archetypes_complete.md ← 7 archetypes
│   ├── drills_part2.md
│   └── drills_part3.md
│
├── 05_sliding_window/
│   ├── pattern.md             ← Theory (early format)
│   ├── problems.md            ← Original 8-12 problems
│   ├── drills_part2.md        ← 15 practice
│   └── drills_part3.md        ← 15 advanced
│
├── 06_linked_list/            ← Same structure as 05
├── 07_trees/
├── 08_heap/
├── 09_backtracking/
├── 10_tries/
├── 11_graphs/
├── 12_advanced_graphs/
├── 13_1d_dp/
├── 14_2d_dp/
├── 15_greedy/
├── 16_intervals/
├── 17_math_geometry/
├── 18_bit_manipulation/
│
├── BLENDED_DRILLS.md          ← Cross-pattern problems
├── INTERVIEW_SIMULATION.md    ← Cold-start timed practice
├── NEETCODE_150.md           ← Curated 150 problem list
├── PROGRESS_TRACKER.md        ← Checklist & weekly log
├── QUICK_REFERENCE.md         ← 1-page cheat sheet
├── COMPLEXITY_GUIDE.md        ← Time/space tables
└── IMPROVEMENTS.md            ← Future enhancements
```

---

## The Learning Path (Visual)

```
WEEK 1-2                    WEEK 3-4                    WEEK 5-6
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  01 Arrays  │            │  03 Stack   │            │  07 Trees   │
│   & Hashing │ ────────►  │  04 Binary  │ ────────►  │  09 Backt.  │
│             │            │    Search   │            │  10 Tries   │
└─────────────┘            └─────────────┘            └─────────────┘
       │                          │                          │
       ▼                          ▼                          ▼
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│  02 Two     │            │  05 Sliding │            │  08 Heap    │
│  Pointers   │            │   Window    │            │             │
└─────────────┘            └─────────────┘            └─────────────┘
       │                          │
       └──────────────┬───────────┘
                      ▼
               ┌─────────────┐
               │  06 Linked  │
               │    List     │
               └─────────────┘

WEEK 7-8                    WEEK 9-10                   WEEK 11-12
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│ 11 Graphs   │            │ 13 1-D DP   │            │ 15 Greedy   │
│ 12 Advanced │ ────────►  │ 14 2-D DP   │ ────────►  │ 16 Intervals│
│   Graphs    │            │             │            │             │
└─────────────┘            └─────────────┘            └─────────────┘

WEEK 13-14                  WEEK 15-16
┌─────────────┐            ┌─────────────┐
│ 17 Math &   │            │ Interview   │
│  Geometry   │ ────────►  │ Simulation  │
│ 18 Bit Man. │            │ Final Review│
└─────────────┘            └─────────────┘
```

**Arrows indicate prerequisites.** You can study vertically parallel tracks simultaneously.

---

## The File Reading Order (Within Each Pattern)

```
For EACH pattern folder, read in this EXACT order:

STEP 1: Read the THEORY
    ├── If folder has "pattern_detailed.md" → read that
    ├── If folder has "archetypes_complete.md" → read that
    └── If folder has "pattern.md" → read that
    
STEP 2: Read the ORIGINAL PROBLEMS (if exists)
    └── problems.md
    
STEP 3: Practice WARM-UPS
    └── drills_part2.md
    Read first 5 problems (Warm-Up section)
    Solve them WITH the theory doc open
    
STEP 4: Practice CORE DRILLS
    └── drills_part2.md
    Read last 10 problems (Core Drill section)
    Solve them WITHOUT looking at solutions
    
STEP 5: Practice NEAR MISSES
    └── drills_part3.md
    Read first 5 problems (Near Miss section)
    These are TRAPS — they look like the pattern but aren't
    
STEP 6: Practice BLENDS
    └── drills_part3.md
    Read middle 5 problems (Pattern Blend section)
    These combine 2 patterns
    
STEP 7: Practice INTERVIEW SIM
    └── drills_part3.md
    Read last 5 problems (Interview Simulation section)
    No labels given — identify the pattern yourself
```

---

## The Prerequisite Graph (Pattern Dependencies)

```
                    ┌─────────────────┐
                    │   01 Arrays     │
                    │    & Hashing    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ 02 Two        │   │ 03 Stack      │   │ 04 Binary     │
│ Pointers      │   │               │   │ Search        │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        │         ┌──────────┘                    │
        │         │                               │
        ▼         ▼                               ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ 05 Sliding    │   │ 06 Linked     │   │ 07 Trees      │
│ Window        │   │ List          │   │               │
└───────────────┘   └───────────────┘   └───────┬───────┘
                                                │
                          ┌─────────────────────┘
                          │
                          ▼
                ┌─────────────────┐
                │ 08 Heap         │
                │ 09 Backtracking │
                │ 10 Tries        │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ 11 Graphs       │
                │ 12 Adv Graphs   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ 13 1-D DP       │
                │ 14 2-D DP       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ 15 Greedy       │
                │ 16 Intervals    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ 17 Math         │
                │ 18 Bit Manip    │
                └─────────────────┘
```

**Rule:** Only move down when you can solve the previous level's problems without looking at the theory.

---

## The Quick Decision Map

```
"I want to start learning"
    └── Read: README.md → PEDAGOGY.md → ROADMAP.md
        └── Then go to 01_arrays_hashing/pattern_detailed.md

"I have an interview in 2 weeks"
    └── Read: QUICK_REFERENCE.md
    └── Do: NEETCODE_150.md (Patterns 01-08 only)
    └── Review: BLENDED_DRILLS.md Set A & B

"I want to track progress"
    └── Open: PROGRESS_TRACKER.md
    └── Check off problems as you solve them

"I keep confusing patterns"
    └── Read: ROADMAP.md "Pattern Confusion Matrix"
    └── Do: INTERVIEW_SIMULATION.md (no labels)

"I need a quick refresher"
    └── Read: QUICK_REFERENCE.md (1 page)
    └── Review: COMPLEXITY_GUIDE.md

"I want to know what's left to build"
    └── Read: IMPROVEMENTS.md
```

---

## The 5-Minute Start Guide

**If you only have 5 minutes right now:**

1. Open `docs_dsa/README.md` — read the first page (1 min)
2. Open `docs_dsa/01_arrays_hashing/pattern_detailed.md` — read "The Trigger" section (2 min)
3. Open `docs_dsa/01_arrays_hashing/drills_part2.md` — read Problem 1 (2 min)

**That's it.** You have started.

**Tomorrow, come back and solve Problem 1.**

---

## Cross-Reference Map

| If you're studying... | Also review... | Because... |
|---|---|---|
| 01 Arrays & Hashing | 05 Sliding Window | Hash map tracks window contents |
| 02 Two Pointers | 05 Sliding Window | Window uses two pointers |
| 03 Stack | 07 Trees | Iterative tree traversal uses stack |
| 04 Binary Search | 14 2-D DP | Answer-space search optimization |
| 07 Trees | 09 Backtracking | DFS is backtracking |
| 08 Heap | 12 Advanced Graphs | Dijkstra uses heap |
| 09 Backtracking | 13 1-D DP | Memoization = top-down DP |
| 10 Tries | 11 Graphs | Word Search II uses both |
| 11 Graphs | 12 Advanced Graphs | Natural progression |
| 13 1-D DP | 14 2-D DP | Same logic, +1 dimension |
| 15 Greedy | 16 Intervals | Scheduling problems |

---

## File Size Guide

| File Type | Typical Size | Reading Time |
|---|---|---|
| Theory (pattern/archetypes) | 300-800 lines | 20-30 min |
| Original problems | 150-300 lines | 15-20 min |
| drills_part2.md | 400-600 lines | Practice: 2-3 hours |
| drills_part3.md | 400-600 lines | Practice: 2-3 hours |
| Root docs (ROADMAP, etc.) | 100-300 lines | 10-15 min each |

---

## The "I'm Stuck" Flowchart

```
Stuck on a problem?
    │
    ├── Can you identify the archetype?
    │   └── NO → Re-read pattern.md "Recognition Signal"
    │
    ├── Can you write the template?
    │   └── NO → Re-read pattern.md "Template" section
    │
    ├── Can you solve a warm-up?
    │   └── NO → Look at the solution. Study it. Try again tomorrow.
    │
    ├── Can you explain WHY the pattern fits?
    │   └── NO → Read "The Core Insight" in pattern.md
    │
    └── Can you solve it in under 15 minutes?
        └── NO → More practice. Do 3 more warm-ups.
```

---

## Navigation by Goal

| Goal | Files to Open |
|---|---|
| **Learn pattern from scratch** | pattern.md → drills_part2.md (warm-ups) |
| **Practice for speed** | drills_part2.md (core drills) + timer |
| **Test pattern discrimination** | drills_part3.md (near misses) |
| **Practice combining patterns** | BLENDED_DRILLS.md |
| **Simulate real interview** | INTERVIEW_SIMULATION.md |
| **Track my progress** | PROGRESS_TRACKER.md |
| **Find a specific problem** | NEETCODE_150.md (alphabetical by number) |
| **Check time complexity** | COMPLEXITY_GUIDE.md |
| **Quick pre-interview review** | QUICK_REFERENCE.md |

---

## Color Coding (for printed version)

If you print these docs, use this color code:
- **YELLOW highlighter:** Theory files (pattern.md, archetypes_complete.md)
- **GREEN highlighter:** Practice files (drills_part2.md — solvable)
- **RED highlighter:** Challenge files (drills_part3.md — near misses)
- **BLUE highlighter:** Reference files (ROADMAP, QUICK_REFERENCE)
- **ORANGE highlighter:** Navigation files (this file, README)

---

*Start with 01_arrays_hashing. Follow the arrows. Trust the process.*
