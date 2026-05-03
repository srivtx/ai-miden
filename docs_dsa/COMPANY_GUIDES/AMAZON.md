# Amazon Interview Preparation Guide

> **Target level:** L4-L6 | **Focus:** Leadership Principles, practical problem solving, ownership

---

## Interview Process Overview

| Stage | Format | What Happens | Pass Rate |
|---|---|---|---|
| Online Assessment (OA) | 2 coding problems, timed | Automated; often includes debugging | ~50% |
| Phone Screen | 45 min video | 1-2 coding problems + LP probe | ~40% |
| Loop (Onsite / Virtual) | 4-5 rounds, 45-60 min each | Coding, system design, 2-3 LP-heavy rounds | ~25% |
| Bar Raiser | 1 round within the loop | Extra LP scrutiny, high bar for ownership | Can veto hire |
| Hiring Decision | HM + Bar Raiser + loop debrief | Consensus, BR has outsized influence | ~70% of loop passers |
| Offer | Call + email | Compensation, sign-on bonus focus | Most decisions |

**Key rule:** The Bar Raiser can single-handedly block an offer. Every round is behavioral, even the coding rounds.

---

## What Amazon Values: Leadership Principles

Amazon has 16 Leadership Principles (LPs). In practice, 8 are heavily tested:

| LP | What It Means | Interview Signal |
|---|---|---|
| Customer Obsession | Start with the customer and work backwards | You ask who the user is before designing |
| Ownership | You act on behalf of the entire company | You fixed something outside your job description |
| Invent and Simplify | Find easier ways; do not over-engineer | Your solution is elegant, not clever |
| Are Right, A Lot | Good judgment, strong instincts | You explain trade-offs with data |
| Learn and Be Curious | Always improving | You admit what you do not know and ask |
| Hire and Develop the Best | Raise the bar with every hire | You mentored someone to success |
| Insist on the Highest Standards | Deliver quality relentlessly | You caught a bug that would have cost users |
| Think Big | Create bold direction | You proposed a project that changed the team |
| Bias for Action | Speed matters in business | You shipped with 80% confidence, not 100% |
| Frugality | Accomplish more with less | You found a cheaper solution that worked |
| Earn Trust | Be vocally self-critical | You admitted failure before being asked |
| Dive Deep | Operate at all levels; audit details | You traced a bug to the root cause |
| Have Backbone; Disagree and Commit | Challenge decisions, then support them | You pushed back on a PM, then delivered |
| Deliver Results | Focus on key business inputs | Your project shipped and moved a metric |
| Strive to be Earth's Best Employer | Make work meaningful | You improved team morale or process |
| Success and Scale Bring Broad Responsibility | Be humble about impact | You considered downstream effects |

**In every answer, show at least 2 LPs.** The Bar Raiser will probe until they find the second.

---

## Curated Problem List: 30 Problems

Pulled from the NeetCode 150. Amazon tends toward practical, medium-difficulty problems. **Must-do** = solve with clean code; **Nice-to-have** = solve once.

### 01 Arrays & Hashing

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 1 | 217 | Contains Duplicate | Easy | 1.1 Existence |
| Must-do | 2 | 242 | Valid Anagram | Easy | 1.2 Frequency |
| Must-do | 3 | 1 | Two Sum | Easy | 1.3 Complement |
| Must-do | 4 | 49 | Group Anagrams | Medium | 1.4 Grouping |
| Must-do | 5 | 347 | Top K Frequent Elements | Medium | 1.2 + 8.1 |
| Must-do | 6 | 238 | Product of Array Except Self | Medium | 1.5 Prefix |
| Must-do | 8 | 271 | Encode and Decode Strings | Medium | 1.4 Grouping |
| Must-do | 9 | 380 | Insert Delete GetRandom O(1) | Medium | 1.6 Design |

### 02 Two Pointers

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 10 | 125 | Valid Palindrome | Easy | 2.4 Palindrome |
| Must-do | 11 | 15 | 3Sum | Medium | 2.1 Converging |
| Nice-to-have | 14 | 167 | Two Sum II | Medium | 2.1 Converging |

### 05 Sliding Window

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 30 | 3 | Longest Substring Without Repeating | Medium | 5.2 Variable |
| Must-do | 32 | 567 | Permutation in String | Medium | 5.2 Variable |
| Nice-to-have | 35 | 209 | Minimum Size Subarray Sum | Medium | 2.7 Window |

### 06 Linked List

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 36 | 206 | Reverse Linked List | Easy | 6.1 Reverse |
| Must-do | 37 | 21 | Merge Two Sorted Lists | Easy | 6.3 Merge |
| Must-do | 38 | 141 | Linked List Cycle | Easy | 6.2 Floyd |
| Must-do | 40 | 19 | Remove Nth From End | Medium | 6.6 Remove |
| Nice-to-have | 42 | 138 | Copy List with Random Pointer | Medium | 6.5 Copy |

### 07 Trees

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 43 | 104 | Maximum Depth | Easy | 7.1 Traversal |
| Must-do | 44 | 100 | Same Tree | Easy | 7.3 Validation |
| Must-do | 45 | 226 | Invert Binary Tree | Easy | 7.7 Modification |
| Must-do | 47 | 102 | Binary Tree Level Order | Medium | 7.1 BFS |
| Must-do | 51 | 98 | Validate BST | Medium | 7.3 Validation |
| Nice-to-have | 54 | 236 | LCA of Binary Tree | Medium | 7.4 LCA |

### 08 Heap

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 59 | 215 | Kth Largest Element | Medium | 8.1 Top K |
| Nice-to-have | 61 | 373 | Find K Pairs with Smallest Sums | Medium | 8.2 Merge K |

### 11 Graphs

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 71 | 200 | Number of Islands | Medium | 11.1 BFS |
| Must-do | 77 | 207 | Course Schedule | Medium | 11.3 Cycle |
| Nice-to-have | 75 | 994 | Rotting Oranges | Medium | 11.1 BFS |

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
| Easy | 11 | Bread and butter; must be automatic |
| Medium | 16 | Most common in the loop |
| Hard | 3 | Occasionally asked; do not prioritize |
| **Total** | **30** | 22 must-do, 8 nice-to-have |

---

## Focus Areas

### Arrays and Hash Maps (Pattern 01)
Amazon's OA and phone screen heavily favor array and hash map problems. Be able to:
- Build frequency maps in 30 seconds
- Use sets for deduplication
- Handle in-place modifications with O(1) extra space

Review: `docs_dsa/01_arrays_hashing/drills_part2.md` — aim to solve all core drills in one session.

### Graphs (Pattern 11)
Amazon asks practical graph problems:
- Grid BFS/DFS (islands, rotting oranges)
- Topological sort for dependency resolution
- Connected components

Review: `docs_dsa/11_graphs/pattern.md` and `drills_part2.md`.

### Object Design
Amazon often asks "design a class" or "design a data structure" questions:
- LRU Cache (though not in NC150, it is a classic Amazon problem)
- Design an iterator
- Design a rate limiter

Practice writing clean class APIs. Focus on encapsulation and testability.

---

## Bar Raiser Round: What It Is, How to Pass

The Bar Raiser (BR) is a specially trained interviewer whose job is to maintain hiring standards across the org. They can:

- Ask any type of question (coding, design, behavioral)
- Veto a hire even if everyone else said yes
- Probe deeper on any LP they feel was under-tested

**How to pass:**
- Treat the BR like any other round — do not get nervous
- Expect deeper follow-ups: "Why did you choose that? What if scale 10x?"
- Show ownership explicitly: "I took responsibility for..."
- Have at least one story that shows "Dive Deep" with technical detail

**Red flags for a BR:**
- Blaming others in behavioral answers
- Giving up on a hard problem without exploring alternatives
- Not asking clarifying questions

---

## LP Prep Framework: STAR Method with Coding Examples

Amazon expects every behavioral answer in STAR format:

| Letter | What to Include | Example |
|---|---|---|
| S — Situation | 1-2 sentences of context | "Our team was migrating a monolith to microservices" |
| T — Task | Your specific responsibility | "I owned the inventory service migration" |
| A — Action | What YOU did (not the team) | "I wrote the data migration script, tested it on a shadow DB, and rolled it back when I found a 0.1% mismatch" |
| R — Result | Quantified outcome | "Migration completed with zero downtime; query latency dropped 40%" |

### STAR + LPs in Coding Rounds

Even coding rounds at Amazon include LP probes. Be ready for:

- "Tell me about a time you had to optimize code under a deadline."
- "Tell me about a time you found a bug in production."
- "Tell me about a time you disagreed with a design decision."

For each, use STAR and name the LP explicitly: "This shows Ownership because..."

### Recommended Story Bank

Prepare 8-12 stories covering these angles:

1. **Customer Obsession + Ownership:** You fixed a customer-facing bug that was not your ticket.
2. **Dive Deep:** You traced a bug through 5 layers of the stack.
3. **Invent and Simplify:** You replaced a complex system with a simpler one.
4. **Deliver Results:** You shipped a feature that moved a metric.
5. **Have Backbone:** You pushed back on a product decision and were right.
6. **Learn and Be Curious:** You taught yourself a new technology to solve a problem.
7. **Hire and Develop:** You mentored a junior engineer to promotion.
8. **Bias for Action:** You shipped an MVP in a week to validate an idea.

---

## Amazon-Specific Behavioral Deep Dives

### Ownership
Amazon wants to hear that you treat the team's problems as your own.
- Good: "I noticed our deploy pipeline was flaky and spent a weekend fixing it."
- Bad: "I told the DevOps team and they fixed it."

### Customer Obsession
Every design answer should start with the customer.
- Good: "The customer here is a warehouse worker who needs real-time inventory."
- Bad: "We should use Kafka because it is scalable."

### Dive Deep
Be ready to go deep on technical details in behavioral answers.
- Good: "I traced the memory leak to a closure capturing a 10MB object in a polling loop."
- Bad: "There was a memory leak and I fixed it."

---

## Tips from the DSA System

1. **OA prep:** Use `docs_dsa/01_arrays_hashing/drills_part2.md` for speed. The OA timer is unforgiving.
2. **LP integration:** Practice saying your STAR stories out loud. Time them: 2-3 minutes each.
3. **Object design practice:** Write class skeletons for LRU Cache, Trie, and Min Stack without looking.
4. **Graph templates:** Amazon loves grid BFS. Write the 4-directional grid traversal template from memory.
5. **Mixed practice:** Do `docs_dsa/BLENDED_DRILLS.md` Set B — it has practical problems similar to Amazon's style.

---

## 2-Week Sprint Plan

| Day | Morning (2 hours) | Evening (1 hour) |
|---|---|---|
| Day 1 | Must-do Arrays & Hashing (8 problems) | Write 2 STAR stories |
| Day 2 | Must-do Linked List + Trees (9 problems) | Write 2 more STAR stories |
| Day 3 | Must-do Graphs + Intervals (5 problems) | Practice LP answers out loud |
| Day 4 | Must-do Sliding Window + Heap (4 problems) | Mock interview: 1 coding + 2 LP questions |
| Day 5 | Object design practice (LRU, Trie, Iterator) | Review `docs_dsa/QUICK_REFERENCE.md` |
| Day 6 | System design study (Amazon style: frugal, scalable) | Read an Amazon engineering blog post |
| Day 7 | REST DAY — light review only | Review STAR stories |
| Day 8 | Re-solve 5 hardest must-do problems without hints | Behavioral mock with a friend |
| Day 9 | Nice-to-have problems (4 problems) | Focus on clean class design |
| Day 10 | Mixed drill: 6 problems from random patterns | Time yourself. 25 minutes each. |
| Day 11 | INTERVIEW_SIMULATION.md Set A | Debrief: did you handle edge cases? |
| Day 12 | INTERVIEW_SIMULATION.md Set B | Practice "Dive Deep" stories with technical detail |
| Day 13 | Full mock loop (5 rounds if possible) | Include a Bar Raiser-style behavioral round |
| Day 14 | Light review: templates + STAR stories only | Sleep early. No new problems. |

---

## Final Checklist

- [ ] All 22 must-do problems solved twice, once without hints
- [ ] 8-12 STAR stories written, each tied to 2+ LPs
- [ ] Can explain "Dive Deep" and "Ownership" with specific technical examples
- [ ] Can design 1 scalable system with Amazon's frugality in mind
- [ ] Completed at least 1 full mock loop with behavioral rounds
- [ ] Grid BFS, topological sort, and hash map templates written from memory

---

*Reference the full NeetCode 150 at `docs_dsa/NEETCODE_150.md`. Track progress in `docs_dsa/PROGRESS_TRACKER.md`.*
