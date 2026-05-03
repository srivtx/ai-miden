# DSA Pedagogy: How to Actually Learn Patterns

> **This is not a problem list. This is a learning system.**
>
> **Core belief:** You do not learn patterns by reading about them. You learn them by solving 20 variations, getting each one wrong, and eventually feeling the pattern in your bones.

---

## The Learning Curve

```
Effort
   |
15 +                                          ****
   |                                     ****
10 +                                ****
   |                           ****
 5 +                      ****
   |                 ****
 2 +            ****
   |       ****
 0 +  ****
   +-----------------------------------------------
     Wk1  Wk2  Wk3  Wk4  Wk5  Wk6  Wk7  Wk8

     Phase 1          Phase 2          Phase 3
     Acquisition      Fluency          Mastery
```

**Phase 1: Acquisition (Weeks 1-2 per pattern)**
- You read the pattern doc
- You solve the canonical problem with the solution open
- You solve 5 warm-up problems
- You still need to look at the template
- **Feeling:** "I think I get it, but I couldn't do it alone"

**Phase 2: Fluency (Weeks 3-4 per pattern)**
- You solve 15 core drill problems
- You start recognizing the pattern in 30 seconds
- You make fewer syntax errors
- You can adapt the template to new situations
- **Feeling:** "Okay, I see this pattern everywhere now"

**Phase 3: Mastery (Weeks 5-6 per pattern)**
- You solve 10 near-miss and blend problems
- You can distinguish this pattern from similar ones
- You write solutions without looking at templates
- You can explain WHY the pattern fits
- **Feeling:** "This is obvious. Why was this ever hard?"

**The Dip:** Between Phase 1 and Phase 2, you will feel like you are not improving. This is normal. Push through.

---

## The 5-Phase Drill System

For EACH archetype, we provide 5 types of practice:

### Type 1: Warm-Up (3-5 problems)
**Purpose:** Build muscle memory for the template.

These are almost identical to the canonical problem. The story changes, but the code is 90% the same.

**Example for "Complement Lookup":**
- Canonical: Two Sum
- Warm-up 1: Two Sum with duplicates allowed
- Warm-up 2: Count pairs with sum < target
- Warm-up 3: Two Sum in BST (same logic, different structure)
- Warm-up 4: Find pair with difference K
- Warm-up 5: Count pairs with sum divisible by K

**How to study:** Look at the template. Solve it. Do NOT time yourself. Focus on correctness.

---

### Type 2: Core Drill (8-12 problems)
**Purpose:** Learn to adapt the template to new constraints.

These are the same archetype but with meaningful twists: different data types, additional constraints, optimization pressure.

**Example for "Complement Lookup":**
- Core 1: 3Sum (fix one, two-sum the rest)
- Core 2: 4Sum (same, more loops)
- Core 3: Two Sum II sorted (use two pointers instead)
- Core 4: Two Sum with BST iterator
- Core 5: Count pairs in two arrays with sum K
- Core 6: Find pair closest to target
- Core 7: Two sum less than K (maximize under constraint)
- Core 8: Two sum in linked list

**How to study:** Close the book. Solve from scratch. If stuck for 5 minutes, look at the archetype hint (not the solution). Time yourself.

---

### Type 3: Near Miss (3-5 problems)
**Purpose:** Learn what this archetype is NOT.

These problems LOOK like they fit the archetype but actually use a different one. This builds discrimination.

**Example for "Complement Lookup":**
- Near Miss 1: Subarray Sum Equals K (looks like pair sum, but needs prefix sums)
- Near Miss 2: 3Sum Closest (looks like 3Sum, but needs two pointers with tracking)
- Near Miss 3: Two Sum BST (can use hash map, but inorder + two pointers is better)
- Near Miss 4: Find Duplicate Number (array values as pointers — Floyd's cycle)
- Near Miss 5: Max Subarray (looks like sum-related, but needs Kadane's)

**How to study:** These are TRAPS. The interviewer will present these to test if you blindly apply patterns. For each near miss, write:
1. Why it LOOKS like the archetype
2. Why it ISN'T the archetype
3. What the correct archetype is

---

### Type 4: Pattern Blend (3-5 problems)
**Purpose:** Learn to combine patterns seamlessly.

These require two patterns working together.

**Example for "Complement Lookup":**
- Blend 1: Top K Frequent Elements (hash map + heap)
- Blend 2: Subarrays with K Different Integers (hash map + sliding window)
- Blend 3: Longest Consecutive Sequence (hash set + sequence building)
- Blend 4: Two Sum with sorted array and duplicates removed (two pointers + hash set)
- Blend 5: LRU Cache (hash map + linked list)

**How to study:** Identify both patterns BEFORE coding. Write the template for each. Then figure out how they connect.

---

### Type 5: Interview Simulation (3-5 problems)
**Purpose:** Practice under pressure.

These are presented WITHOUT archetype labels. You have 30 seconds to identify the pattern.

**Example:**
> "Design a system to track check-ins and check-outs at a subway station and calculate average travel time between stations."
>
> Answer: Two hash maps (in-progress trips and completed stats) — Archetype 1.6 Hash Map Design

**How to study:** Use the INTERVIEW_SIMULATION.md file. Time yourself. Track accuracy.

---

## The Repetition Schedule

Learning science says you need **spaced repetition** with **varied practice**.

### Week Structure

| Day | Activity | Time |
|---|---|---|
| Monday | Learn new archetype (read pattern doc) | 1 hour |
| Tuesday | Warm-ups (Type 1) — 5 problems | 2 hours |
| Wednesday | Core drills (Type 2) — 8 problems | 3 hours |
| Thursday | Near misses (Type 3) — 4 problems | 2 hours |
| Friday | Pattern blends (Type 4) — 4 problems | 2 hours |
| Saturday | Review ALL problems from this week | 2 hours |
| Sunday | Interview simulation + review previous patterns | 2 hours |

**Total: ~14 hours/week**

### Spaced Repetition

After learning a pattern, review it at these intervals:
- Day 1: Initial learning
- Day 3: First review (solve 3 problems)
- Day 7: Second review (solve 3 problems)
- Day 14: Third review (solve 2 problems)
- Day 30: Fourth review (solve 2 problems)

**This means:** You are always reviewing previous patterns WHILE learning new ones. By week 6, you might study one new pattern per week but review five previous patterns.

---

## The Fluency Threshold

You have "learned" an archetype when you can:

- [ ] Identify it in 10 seconds from a problem statement
- [ ] Write the template in 2 minutes without looking
- [ ] Solve a warm-up in 5 minutes
- [ ] Solve a core drill in 10-15 minutes
- [ ] Correctly reject a near miss (identify the real archetype)
- [ ] Explain WHY the archetype fits, not just HOW

**If you cannot do all 6, you have not learned it yet.** Keep drilling.

---

## The Discrimination Muscle

The hardest part of interviews is NOT solving problems. It is **identifying which archetype to use**.

We build this through:

1. **Explicit comparison:** For each archetype, we show 3 problems that look similar but use different archetypes.

2. **The confusion matrix:** A table of common misidentifications.

3. **Mixed drills:** Problem sets with no labels. You must identify before solving.

4. **The "why not" test:** For every solution, ask "why didn't I use [other pattern]?"

---

## Volume Targets

| Phase | Problems/Week | Cumulative | Archetypes |
|---|---|---|---|
| Month 1: Acquisition | 40 | 160 | 8 patterns |
| Month 2: Fluency | 50 | 360 | 16 patterns |
| Month 3: Mastery | 60 | 600 | 18 patterns |
| Month 4+: Maintenance | 30/week | 720+ | Review all |

**Target: 600-700 problems total.**

This is MORE than enough. Most competitive programmers interview-ready at 300-400. At 600+, you are elite.

---

## How We Built This System

### Each Pattern Folder Now Contains:

```
pattern/
├── pattern.md           # Core archetypes + templates + traps
├── problems.md          # Original 8-12 problems (Part 1)
├── drills_part2.md      # 15-20 warm-ups + core drills (Part 2)
├── drills_part3.md      # 15-20 near misses + blends (Part 3)
└── interview_sim.md     # 5 cold-start problems (Part 4)
```

**Total per pattern: ~40-50 problems**
**Total across 18 patterns: ~720-900 problems**

---

## Beginner vs Advanced Paths

### Beginner Path (12-16 weeks)
- Focus on Patterns 01-07 only
- 30 problems per pattern
- Spend 2 weeks per pattern
- Do ALL warm-ups before core drills
- Review every week

### Intermediate Path (8-10 weeks)
- Patterns 01-14
- 25 problems per pattern
- Spend 1 week per pattern
- Skip some warm-ups if easy
- Review every 2 weeks

### Advanced Path (6-8 weeks)
- All 18 patterns
- 20 problems per pattern
- Spend 3-4 days per pattern
- Focus on near misses and blends
- Daily review

---

## The Feeling

> "I don't think about patterns anymore. I just see the problem and my hands move."

That is the goal. It comes from:
- Solving 20+ variations of each archetype
- Getting problems wrong and understanding why
- Spaced repetition over 8+ weeks
- Mixed practice that forces discrimination

**This is not a sprint. This is a training program.**

---

## Next Step

1. Read the pattern doc for Pattern 01
2. Solve ALL warm-ups in `drills_part2.md`
3. Track your time and accuracy
4. Only move to core drills when warm-ups feel automatic
5. Follow the spaced repetition schedule

**Do not rush. Momentum > speed.**
