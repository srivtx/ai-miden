# Google Interview Preparation Guide

> **Target level:** L4-L6 | **Focus:** Depth over speed, optimal solutions, clean code

---

## Interview Process Overview

| Stage | Format | What Happens | Pass Rate |
|---|---|---|---|
| Recruiter Screen | 15-30 min call | Resume, motivation, basic fit | High |
| Phone Screen | 45 min video | 1 coding problem (shared editor) | ~30% |
| Onsite / Virtual Onsite | 4-5 rounds, 45 min each | 2 coding, 1 system design (L4+), 1 behavioral, 1 "Googlyness" | ~20% |
| Hiring Committee (HC) | Async packet review | Interviewers submit feedback; HC votes | ~70% of onsite passers |
| Offer | Call + email | Compensation negotiation | Most HC passers |

**Key rule:** One "no-hire" can kill the packet unless every other signal is exceptionally strong. You need consistency across all rounds.

---

## What Google Values

Google weights rounds in this approximate priority:

1. **Coding** (highest weight) — correctness, optimal complexity, clean code
2. **System Design** (L4+) — scalability, trade-offs, data model
3. **Behavioral / Googlyness** — not a free pass; a true filter

**What separates pass from fail in coding:**
- You produced an optimal solution (not just working)
- You analyzed time/space complexity correctly
- Your code was production-quality (meaningful names, edge cases handled)
- You navigated hints gracefully without needing rescue

---

## Googlyness Traits

Googlyness is not "being nice." It is specific behaviors:

| Trait | What It Means | How to Show It |
|---|---|---|
| Intellectual humility | You change your mind when evidence appears | "That's a good point — let me revise my approach" |
| Comfort with ambiguity | You can start without a perfect plan | Sketch a brute force, then optimize |
| Collaboration | You treat the interviewer as a peer | Ask for their input: "What constraints should I assume?" |
| User focus | You ask who the customer is | In design rounds, ask about user needs first |
| Courage | You defend a good idea, abandon a bad one | Push back on bad hints; admit when stuck |

---

## Curated Problem List: 30 Problems

Pulled from the NeetCode 150. **Must-do** = solve twice; **Nice-to-have** = solve once if time permits.

### 01 Arrays & Hashing

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 1 | 217 | Contains Duplicate | Easy | 1.1 Existence |
| Must-do | 4 | 49 | Group Anagrams | Medium | 1.4 Grouping |
| Must-do | 6 | 238 | Product of Array Except Self | Medium | 1.5 Prefix |
| Nice-to-have | 7 | 128 | Longest Consecutive Sequence | Medium | 1.8 Sequence |

### 02 Two Pointers

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 11 | 15 | 3Sum | Medium | 2.1 Converging |
| Nice-to-have | 13 | 42 | Trapping Rain Water | Hard | 2.5 Container |

### 04 Binary Search

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 25 | 33 | Search in Rotated Sorted Array | Medium | 4.2 Rotated |
| Nice-to-have | 27 | 4 | Median of Two Sorted Arrays | Hard | 4.7 Median |

### 05 Sliding Window

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 30 | 3 | Longest Substring Without Repeating | Medium | 5.2 Variable |
| Nice-to-have | 33 | 76 | Minimum Window Substring | Hard | 5.3 Minimum |

### 06 Linked List

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 36 | 206 | Reverse Linked List | Easy | 6.1 Reverse |
| Must-do | 38 | 141 | Linked List Cycle | Easy | 6.2 Floyd |
| Nice-to-have | 41 | 23 | Merge k Sorted Lists | Hard | 6.3 + 8.2 |

### 07 Trees (High Priority for Google)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 43 | 104 | Maximum Depth | Easy | 7.1 Traversal |
| Must-do | 46 | 124 | Binary Tree Maximum Path Sum | Hard | 7.8 Metrics |
| Must-do | 47 | 102 | Binary Tree Level Order | Medium | 7.1 BFS |
| Must-do | 48 | 297 | Serialize and Deserialize | Hard | 7.6 Serialization |
| Must-do | 50 | 105 | Construct from Preorder/Inorder | Medium | 7.6 Construction |
| Must-do | 51 | 98 | Validate BST | Medium | 7.3 Validation |
| Must-do | 54 | 236 | LCA of Binary Tree | Medium | 7.4 LCA |
| Nice-to-have | 52 | 230 | Kth Smallest Element | Medium | 7.1 DFS |

### 08 Heap

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 59 | 215 | Kth Largest Element | Medium | 8.1 Top K |
| Nice-to-have | 58 | 295 | Find Median from Data Stream | Hard | 8.4 Median |

### 09 Backtracking

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 62 | 78 | Subsets | Medium | 9.1 Subsets |
| Nice-to-have | 69 | 51 | N-Queens | Hard | 9.4 Grid |

### 11 Graphs (High Priority for Google)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 71 | 200 | Number of Islands | Medium | 11.1 BFS |
| Must-do | 72 | 133 | Clone Graph | Medium | 11.1 BFS |
| Must-do | 77 | 207 | Course Schedule | Medium | 11.3 Cycle |
| Must-do | 78 | 210 | Course Schedule II | Medium | 11.4 Topo Sort |
| Nice-to-have | 75 | 994 | Rotting Oranges | Medium | 11.1 BFS |

### 12 Advanced Graphs

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 81 | 743 | Network Delay Time | Medium | 12.1 Dijkstra |
| Nice-to-have | 84 | 684 | Redundant Connection | Medium | 12.5 Union-Find |

### 13 1-D DP (High Priority for Google)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 88 | 198 | House Robber | Medium | 13.1 Linear |
| Must-do | 91 | 322 | Coin Change | Medium | 14.5 Unbounded |
| Must-do | 92 | 300 | Longest Increasing Subsequence | Medium | 13.6 LIS |
| Must-do | 98 | 72 | Edit Distance | Hard | 14.2 Edit |
| Nice-to-have | 93 | 139 | Word Break | Medium | 13.3 Partition |

### 16 Intervals

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 108 | 56 | Merge Intervals | Medium | 16.1 Merge |
| Must-do | 112 | 253 | Meeting Rooms II | Medium | 16.2 Meeting |
| Nice-to-have | 113 | 986 | Interval List Intersections | Medium | 16.3 Intersection |

---

## Difficulty Breakdown

| Difficulty | Count | Notes |
|---|---|---|
| Easy | 5 | Warm-up / speed checks |
| Medium | 18 | The bulk of the interview |
| Hard | 7 | Differentiators for strong hire |
| **Total** | **30** | 20 must-do, 10 nice-to-have |

---

## Focus Areas

### Graphs (Patterns 11, 12)
Google loves graph problems. Be fluent in:
- BFS vs DFS trade-offs
- Topological sort (Kahn's algorithm + DFS-based)
- Dijkstra with a heap
- Union-Find for connected components

Review: `docs_dsa/11_graphs/pattern.md`, `docs_dsa/12_advanced_graphs/pattern.md`

### Trees (Pattern 07)
Google tree questions often go beyond LeetCode standard:
- Morris traversal (O(1) space)
- Threaded binary trees
- Serialization formats (JSON, compact binary)

Review: `docs_dsa/07_trees/pattern.md`, drills_part3 near-misses

### DP Optimization (Patterns 13, 14)
Google DP questions frequently ask for space optimization:
- 2-variable rolling window for 1D DP
- In-place matrix DP when permitted
- State machine DP (stock problems)

Review: `docs_dsa/13_1d_dp/archetypes_complete.md`, `docs_dsa/14_2d_dp/archetypes_complete.md`

### System Design (L4-L6 Expectations)

| Level | Expected Scope | Example Topics |
|---|---|---|
| L4 | Design + justify a scalable service | URL shortener, rate limiter, key-value store |
| L5 | Cross-system design with trade-offs | YouTube, Maps, Search indexing |
| L6 | Organizational / multi-team system | Ad serving, distributed storage |

Study: Google's published papers (Bigtable, MapReduce, Spanner, Borg). Know them at "I can explain the architecture" depth.

---

## Common Google-Specific Question Types

### Interval Merging
Google often asks interval problems with a twist:
- "Merge intervals with a rolling window"
- "Find free time across N calendars"
- "Schedule meetings with minimum rooms and track who is in each room"

Prep: Solve every problem in `docs_dsa/16_intervals/drills_part2.md` and `drills_part3.md`.

### Graph Traversal
Expect to write BFS/DFS from scratch without a library:
- Multi-source BFS
- BFS with level tracking
- DFS with cycle detection in directed graphs

### DP Optimization
Google interviewers will push you to optimize space:
- "Can you do it in O(1) extra space?"
- "Can you avoid the full table?"
- Practice explaining the recurrence before coding.

---

## Tips from the DSA System

1. **Use the 10-Second Decision Tree** in `docs_dsa/QUICK_REFERENCE.md` to identify patterns fast.
2. **Study near misses** in `docs_dsa/*/drills_part3.md`. Google interviewers love problems that look like one pattern but need another.
3. **Follow the Fluency Threshold** from `docs_dsa/PEDAGOGY.md`: if you cannot identify the archetype in 10 seconds, you are not ready.
4. **Practice writing code without autocomplete.** Google's shared editor is plain text.
5. **Do INTERVIEW_SIMULATION.md cold starts** 3 times per week in your final two weeks.

---

## 2-Week Sprint Plan

| Day | Morning (2 hours) | Evening (1 hour) |
|---|---|---|
| Day 1 | Must-do Trees (7 problems) | Review tree archetypes + near misses |
| Day 2 | Must-do Graphs (5 problems) | Write BFS/DFS templates from memory |
| Day 3 | Must-do DP (5 problems) | Practice space optimization on 2 problems |
| Day 4 | Must-do Arrays & Hashing (4 problems) | Review interval merging archetypes |
| Day 5 | Must-do Intervals + Heaps (3 problems) | Mock interview: 1 coding problem, timed |
| Day 6 | System design study (L4 target) | Read a Google engineering blog post |
| Day 7 | REST DAY — light review only | Review QUICK_REFERENCE.md |
| Day 8 | Re-solve 5 hardest must-do problems without hints | Behavioral prep: write 5 stories |
| Day 9 | Nice-to-have Hard problems (3 problems) | System design mock (if L4+) |
| Day 10 | Mixed drill: 5 problems from random patterns | Time yourself. No labels. |
| Day 11 | Review all graph + DP near misses | INTERVIEW_SIMULATION.md Set A |
| Day 12 | Review all tree + interval near misses | INTERVIEW_SIMULATION.md Set B |
| Day 13 | Full mock onsite (4 rounds if possible) | Debrief mistakes in a notebook |
| Day 14 | Light review: templates only | Sleep early. No new problems. |

---

## Final Checklist

- [ ] All 20 must-do problems solved twice, once without hints
- [ ] BFS, DFS, Dijkstra, and Union-Find templates written from memory
- [ ] System design: can whiteboard 1 scalable system end-to-end
- [ ] 5 behavioral stories using STAR format, with metrics
- [ ] Completed at least 2 full mock onsites

---

*Reference the full NeetCode 150 at `docs_dsa/NEETCODE_150.md`. Track progress in `docs_dsa/PROGRESS_TRACKER.md`.*
