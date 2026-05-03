# Meta Interview Preparation Guide

> **Target level:** E4-E6 | **Focus:** Speed, pragmatism, impact-first thinking

---

## Interview Process Overview

| Stage | Format | What Happens | Pass Rate |
|---|---|---|---|
| Recruiter Screen | 15-20 min call | Role fit, timeline, compensation alignment | High |
| Technical Phone Screen | 45 min video | 1-2 coding problems (CoderPad or similar) | ~35% |
| Onsite / Virtual Onsite | 4-5 rounds, 45 min each | 2 coding, 1 system or product design, 1 behavioral | ~25% |
| Post-Onsite Review | Hiring manager + calibrator | Consensus decision, no HC | Faster than Google |
| Offer | Call + email | Meta moves fast on offers | ~80% of onsite passers |

**Key rule:** Speed matters. You are expected to get to working code quickly. A brute-force that runs is better than a perfect solution you never finish.

---

## What Meta Values

Meta's internal culture is built on three principles that directly shape interviews:

1. **Move Fast**
   - Get a working solution on the board in 10 minutes
   - Optimize later, not first
   - Interviewers will nudge you forward if you over-theorize

2. **Be Bold**
   - Take the interview space; do not wait for permission
   - Propose approaches confidently, even if imperfect
   - Push back on weak hints if you have a better path

3. **Focus on Impact**
   - In design rounds, ask "what is the user impact?" early
   - In coding rounds, ask about scale and constraints
   - Behavioral stories must show measurable outcomes

**What separates pass from fail in coding:**
- You finished at least one solid solution
- You communicated while coding (thinking out loud)
- You showed you could iterate (brute force -> better)
- You handled edge cases without being asked

---

## Curated Problem List: 30 Problems

Pulled from the NeetCode 150. Meta interviews favor array manipulation, string problems, and fast pattern recognition. **Must-do** = solve under 20 minutes; **Nice-to-have** = solve once.

### 01 Arrays & Hashing (Heavy Emphasis)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 1 | 217 | Contains Duplicate | Easy | 1.1 Existence |
| Must-do | 2 | 242 | Valid Anagram | Easy | 1.2 Frequency |
| Must-do | 3 | 1 | Two Sum | Easy | 1.3 Complement |
| Must-do | 4 | 49 | Group Anagrams | Medium | 1.4 Grouping |
| Must-do | 5 | 347 | Top K Frequent Elements | Medium | 1.2 + 8.1 |
| Must-do | 6 | 238 | Product of Array Except Self | Medium | 1.5 Prefix |
| Must-do | 7 | 128 | Longest Consecutive Sequence | Medium | 1.8 Sequence |
| Must-do | 9 | 380 | Insert Delete GetRandom O(1) | Medium | 1.6 Design |

### 02 Two Pointers (Speed Matters)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 10 | 125 | Valid Palindrome | Easy | 2.4 Palindrome |
| Must-do | 11 | 15 | 3Sum | Medium | 2.1 Converging |
| Must-do | 12 | 11 | Container With Most Water | Medium | 2.5 Container |
| Nice-to-have | 14 | 167 | Two Sum II | Medium | 2.1 Converging |

### 03 Stack

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 16 | 20 | Valid Parentheses | Easy | 3.1 Matching |
| Nice-to-have | 20 | 739 | Daily Temperatures | Medium | 3.2 Monotonic |

### 05 Sliding Window (Meta Favorite)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 30 | 3 | Longest Substring Without Repeating | Medium | 5.2 Variable |
| Must-do | 31 | 424 | Longest Repeating Character Replacement | Medium | 5.2 Variable |
| Must-do | 32 | 567 | Permutation in String | Medium | 5.2 Variable |
| Nice-to-have | 35 | 209 | Minimum Size Subarray Sum | Medium | 2.7 Window |

### 06 Linked List

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 36 | 206 | Reverse Linked List | Easy | 6.1 Reverse |
| Must-do | 38 | 141 | Linked List Cycle | Easy | 6.2 Floyd |
| Nice-to-have | 42 | 138 | Copy List with Random Pointer | Medium | 6.5 Copy |

### 07 Trees

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 43 | 104 | Maximum Depth | Easy | 7.1 Traversal |
| Must-do | 45 | 226 | Invert Binary Tree | Easy | 7.7 Modification |
| Must-do | 47 | 102 | Binary Tree Level Order | Medium | 7.1 BFS |
| Nice-to-have | 51 | 98 | Validate BST | Medium | 7.3 Validation |

### 10 Tries (String Focus)

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 55 | 208 | Implement Trie | Medium | 10.1 Trie |
| Nice-to-have | 56 | 211 | Add and Search Word | Medium | 10.1 Trie |

### 11 Graphs

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 71 | 200 | Number of Islands | Medium | 11.1 BFS |
| Must-do | 77 | 207 | Course Schedule | Medium | 11.3 Cycle |
| Nice-to-have | 72 | 133 | Clone Graph | Medium | 11.1 BFS |

### 13 1-D DP

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 88 | 198 | House Robber | Medium | 13.1 Linear |
| Must-do | 91 | 322 | Coin Change | Medium | 14.5 Unbounded |
| Nice-to-have | 94 | 53 | Maximum Subarray | Medium | 13.1 Linear |

### 16 Intervals

| Priority | NC # | LC # | Title | Difficulty | Archetype |
|---|---|---|---|---|---|
| Must-do | 108 | 56 | Merge Intervals | Medium | 16.1 Merge |
| Nice-to-have | 112 | 253 | Meeting Rooms II | Medium | 16.2 Meeting |

---

## Difficulty Breakdown

| Difficulty | Count | Notes |
|---|---|---|
| Easy | 10 | Speed runs — solve in under 10 minutes |
| Medium | 17 | Core of the interview |
| Hard | 3 | Only if you finish medium early |
| **Total** | **30** | 22 must-do, 8 nice-to-have |

---

## Focus Areas

### String Manipulation
Meta asks more string problems than most companies. Be comfortable with:
- Character frequency maps
- Sliding window on strings
- Trie operations
- String builders and concatenation costs

Review: `docs_dsa/01_arrays_hashing/pattern_detailed.md` (frequency archetypes), `docs_dsa/05_sliding_window/pattern.md`, `docs_dsa/10_tries/pattern.md`

### Array Problems
Arrays are the most common Meta topic. Expect:
- In-place modification problems
- Multi-pass algorithms
- Sorting as a sub-step

Practice the entire `docs_dsa/01_arrays_hashing/drills_part2.md` for speed.

### System Design and Product Design
Meta sometimes asks product design instead of pure system design:
- "Design Facebook Groups"
- "Design Instagram Stories"
- "Design a content moderation system"

Frame everything around user impact. Ask:
- Who are the users?
- What is the core action?
- What is the worst experience we must prevent?

---

## Meta-Specific Interview Traits

### Faster Coding Expected
- You should produce runnable code within 15-20 minutes for mediums
- Do not spend 10 minutes on deep complexity analysis upfront
- State the brute force, ask if you should optimize, then code

### Less Theoretical Proof
- Google may ask you to prove correctness; Meta rarely does
- Focus on walking through examples, not formal induction
- If you say "this is optimal because...", one sentence is usually enough

### Behavioral Is a Filter
- Meta behavioral rounds are not soft. They probe for conflict, failure, and resilience
- Have 3-5 stories ready, each with a clear "what would you do differently" reflection

---

## Tips from the DSA System

1. **Speed drills:** Use `docs_dsa/01_arrays_hashing/drills_part2.md` and time yourself. Target 10 minutes per easy, 15 per medium.
2. **Sliding window fluency:** Meta loves this pattern. If you cannot write the variable-window template in 2 minutes, drill `docs_dsa/05_sliding_window/drills_part2.md` again.
3. **String practice:** Many Meta problems are string variants not in the standard list. Practice palindrome, anagram, and substring detection as a block.
4. **Interview simulation:** Use `docs_dsa/INTERVIEW_SIMULATION.md` but with a 25-minute timer, not 45.
5. **Mixed practice:** Do `docs_dsa/BLENDED_DRILLS.md` Set A for pattern-switching speed.

---

## 2-Week Sprint Plan

| Day | Morning (2 hours) | Evening (1 hour) |
|---|---|---|
| Day 1 | Must-do Arrays & Hashing (8 problems) | Time yourself. Target 15 min/medium. |
| Day 2 | Must-do Two Pointers + Sliding Window (7 problems) | Write templates from memory |
| Day 3 | Must-do Trees + Graphs (5 problems) | Review BFS/DFS templates |
| Day 4 | Must-do Stack + Linked List + DP (5 problems) | Mock interview: 1 medium, timed 30 min |
| Day 5 | Re-solve hardest must-do problems without hints | Behavioral story writing (3 stories) |
| Day 6 | System / Product design study | Review Meta engineering blog |
| Day 7 | REST DAY — light review only | Review `docs_dsa/QUICK_REFERENCE.md` |
| Day 8 | Nice-to-have problems (4 problems) | Focus on speed, not perfection |
| Day 9 | Mixed drill: 8 problems from random patterns | 20-minute timer per problem |
| Day 10 | String-focused practice (not in NC150) | Practice 5 string manipulation problems |
| Day 11 | INTERVIEW_SIMULATION.md Set A | Debrief: did you identify patterns in 10 seconds? |
| Day 12 | INTERVIEW_SIMULATION.md Set B | Behavioral mock with a friend |
| Day 13 | Full mock onsite (4 rounds if possible) | Debrief: where did you slow down? |
| Day 14 | Light review: templates only | Sleep early. No new problems. |

---

## Final Checklist

- [ ] All 22 must-do problems solved in under 20 minutes each
- [ ] Sliding window, two pointers, and hash map templates written from memory
- [ ] 3 behavioral stories with STAR format + "what I learned"
- [ ] Can whiteboard 1 Meta product design (user -> features -> trade-offs)
- [ ] Completed at least 1 full mock onsite under time pressure

---

*Reference the full NeetCode 150 at `docs_dsa/NEETCODE_150.md`. Track progress in `docs_dsa/PROGRESS_TRACKER.md`.*
