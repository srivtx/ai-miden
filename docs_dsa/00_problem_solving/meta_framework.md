# Pattern 00: The Problem-Solving Meta-Framework

> **This is not a pattern. This is HOW you find the pattern.**
>
> **Every other pattern doc tells you what to do AFTER you know the archetype. This doc tells you what to do when you have NO idea.**

---

## The Universal 10-Minute Framework

When you see a problem, your brain has 10 minutes to identify the archetype. Here is the exact sequence:

```
MINUTE 0-1: READ & PARAPHRASE
    └── Restate the problem in your own words. If you cannot, you do not understand it.

MINUTE 1-2: IDENTIFY THE OUTPUT
    └── What exactly are we returning? A number? A list? A boolean? The structure of the answer often hints at the pattern.

MINUTE 2-3: IDENTIFY THE INPUT CONSTRAINTS
    └── How big is n? What is the range? This tells you what time complexity is acceptable.
    └── n <= 20 → backtracking or exponential DP
    └── n <= 100 → O(n^3) DP might work
    └── n <= 10^5 → O(n log n) or O(n)
    └── n <= 10^6 → O(n) only

MINUTE 3-4: BRUTE FORCE
    └── Can I solve this with nested loops? What would the complexity be?
    └── If brute force is O(n^2) and n = 10^5, you need something faster.

MINUTE 4-5: FIND THE TRIGGER WORDS
    └── Scan the problem for the trigger words from each pattern.
    └── "sorted" → two pointers or binary search
    └── "subarray" → sliding window or prefix sums
    └── "all combinations" → backtracking
    └── "shortest path" → BFS or Dijkstra

MINUTE 5-6: TRY THE MOST LIKELY PATTERN
    └── Write the template for that pattern.
    └── Does it fit? Does the data support it?
    └── If yes → proceed.
    └── If no → try the next most likely pattern.

MINUTE 6-8: SOLVE WITH THE TEMPLATE
    └── Fill in the template. Adapt it to the problem.
    └── Do not optimize yet. Get it working first.

MINUTE 8-9: TEST ON EXAMPLES
    └── Walk through your code with the provided examples.
    └── Do not skip this. Most bugs are found here.

MINUTE 9-10: OPTIMIZE & STATE COMPLEXITY
    └── Can you reduce space? Can you avoid redundant work?
    └── State time and space complexity clearly.
```

---

## The Trigger Word Scanner

Your first reflex when reading a problem should be to scan for these words. They are the fastest way to narrow down the pattern.

### Arrays & Hashing Triggers
| Word | Archetype |
|---|---|
| "find two numbers" | Complement lookup |
| "count how many" | Frequency counting |
| "contains duplicate" | Existence checking |
| "group" / "anagram" | Grouping by signature |
| "subarray sum" | Prefix aggregate |
| "design a data structure" | Hash map design |
| "valid" / "satisfy rules" | Constraint satisfaction |
| "longest consecutive" | Sequence building |

### Two Pointers Triggers
| Word | Archetype |
|---|---|
| "sorted array" | Converging pointers |
| "in-place" / "remove duplicates" | Same-direction pointers |
| "partition" | Partitioning |
| "palindrome" | Palindrome check |
| "container" / "area" / "water" | Container/area |
| "merge two sorted" | Merge sorted |

### Stack Triggers
| Word | Archetype |
|---|---|
| "valid parentheses" | Matching |
| "next greater" / "daily temperatures" | Monotonic stack |
| "RPN" / "calculator" | Expression evaluation |
| "history" / "undo" | History/undo |
| "tree traversal without recursion" | DFS simulation |
| "remove adjacent duplicates" | String processing |

### Binary Search Triggers
| Word | Archetype |
|---|---|
| "sorted" + "find" | Classic search |
| "rotated" / "pivot" | Search space reduction |
| "first occurrence" / "last occurrence" | Boundary detection |
| "peak" / "mountain" | Condition-based search |
| "minimum speed" / "Koko" / "ship packages" | Answer space search |
| "search 2D matrix" | 2D matrix search |
| "median of two sorted" | Median |

### Sliding Window Triggers
| Word | Archetype |
|---|---|
| "window of size k" / "every consecutive k" | Fixed-size window |
| "longest substring with at most k" | Variable-size window |
| "minimum window substring" | Minimum window |
| "count subarrays with exactly k" | Count-based window |
| "sliding window maximum" | Monotonic queue |

### Linked List Triggers
| Word | Archetype |
|---|---|
| "reverse linked list" | Traversal & modification |
| "detect cycle" / "find middle" | Fast & slow pointers |
| "merge sorted lists" | Merge operations |
| "reorder" / "odd even" | Reordering |
| "copy list with random pointer" | Copy/deep copy |
| "remove nth from end" | Remove operations |

### Trees Triggers
| Word | Archetype |
|---|---|
| "inorder" / "preorder" / "level order" | Traversals |
| "root-to-leaf" / "path sum" | Path problems |
| "validate BST" / "symmetric" | Validation |
| "lowest common ancestor" | LCA |
| "right side view" | Views |
| "serialize" / "build from traversals" | Serialization |
| "invert" / "flatten" | Modification |
| "diameter" / "max path sum" | Metrics |

### Heap Triggers
| Word | Archetype |
|---|---|
| "k largest" / "k smallest" / "kth" | Top K |
| "merge k sorted" | Merge K |
| "meeting rooms" / "task scheduler" | Scheduling |
| "running median" / "data stream" | Median finder |
| "top k frequent" | Frequency-based |

### Backtracking Triggers
| Word | Archetype |
|---|---|
| "all subsets" / "power set" | Subsets |
| "all permutations" | Permutations |
| "combination sum" | Combinations |
| "N-queens" | Grid placement |
| "restore IP" / "palindrome partition" | String building |
| "word break" / "dictionary" | Word break |

### Graphs Triggers
| Word | Archetype |
|---|---|
| "level order" / "shortest path unweighted" | BFS |
| "connected components" / "all paths" | DFS |
| "course schedule" / "prerequisites" | Cycle detection |
| "order" / "sequence" / "dependencies" | Topological sort |
| "bipartite" / "two groups" | Bipartite check |
| "number of provinces" | Connected components |
| "word ladder" | Word ladder |

### Advanced Graphs Triggers
| Word | Archetype |
|---|---|
| "shortest path weighted" / "network delay" | Dijkstra |
| "negative weights" | Bellman-Ford |
| "all pairs shortest" | Floyd-Warshall |
| "minimum spanning tree" / "connect all points" | MST |
| "connected components" (fast) | Union-Find |
| "critical connections" / "bridges" | Tarjan |

### DP Triggers
| Word | Archetype |
|---|---|
| "maximize" / "minimize" on a line | 1D linear choice |
| "ways to reach" / "climbing stairs" | Climbing/jump |
| "word break" / "minimum cuts" | Partition |
| "stock" / "buy sell" | Stock problems |
| "count ways" / "tiling" | Counting ways |
| "longest increasing subsequence" | LIS |
| "grid" / "unique paths" | Grid path |
| "edit distance" | Edit distance |
| "LCS" / "uncrossed lines" | LCS |
| "subset sum" / "partition" | Knapsack 0/1 |
| "coin change" | Knapsack unbounded |
| "burst balloons" | Interval DP |
| "regex matching" | String matching |

### Greedy Triggers
| Word | Archetype |
|---|---|
| "non-overlapping" / "erase overlaps" | Interval scheduling |
| "jump" / "reach end" | Jump game |
| "partition labels" / "gas station" | Partition |
| "unlimited stock" | Two-choice greedy |
| "queue reconstruction" | Queue/line |

### Intervals Triggers
| Word | Archetype |
|---|---|
| "merge intervals" | Merge overlapping |
| "meeting rooms" | Meeting rooms |
| "interval intersection" | Intersection |
| "remove intervals" / "max non-overlapping" | Remove/select |

---

## The Pattern Identification Decision Tree

```
START: Read the problem
    │
    ├── Is there a hierarchical / parent-child structure?
    │   └── YES → Trees (Pattern 07)
    │
    ├── Are there nodes connected by edges?
    │   └── YES → Graphs (Pattern 11) or Advanced Graphs (12)
    │       ├── Unweighted / shortest path in unweighted → BFS (11.1)
    │       ├── Weighted / shortest path → Dijkstra (12.1)
    │       └── Negative weights → Bellman-Ford (12.2)
    │
    ├── Is the array SORTED?
    │   └── YES → Two Pointers (02) or Binary Search (04)
    │       ├── Need pair / container / palindrome → Two Pointers (02)
    │       └── Need find / search / minimum where condition changes → Binary Search (04)
    │
    ├── Need contiguous subarray / substring?
    │   └── YES → Sliding Window (05)
    │       ├── Fixed size → 5.1
    │       ├── Variable size (at most K) → 5.2
    │       └── Minimum window → 5.3
    │
    ├── Need to explore all possibilities?
    │   └── YES → Backtracking (09)
    │
    ├── Need optimal substructure (maximize/minimize/ways)?
    │   └── YES → DP (13 or 14)
    │       ├── One dimension / linear → 1D DP (13)
    │       ├── Grid / two strings → 2D DP (14)
    │       └── Can pick local optimum → Greedy (15)
    │
    ├── Need prefix-based string operations?
    │   └── YES → Tries (10)
    │
    ├── Need K largest/smallest/median/merge K?
    │   └── YES → Heap (08)
    │
    ├── Working with linked nodes (no random access)?
    │   └── YES → Linked List (06)
    │
    ├── Need LIFO processing / nesting / undo?
    │   └── YES → Stack (03)
    │
    ├── Need to merge / check overlap of intervals?
    │   └── YES → Intervals (16)
    │
    ├── Number theory / geometry / matrix operations?
    │   └── YES → Math & Geometry (17)
    │
    ├── Operating at bit level / XOR / power of 2?
    │   └── YES → Bit Manipulation (18)
    │
    └── DEFAULT → Arrays & Hashing (01)
        └── Most problems start here. Check existence, frequency, complement.
```

---

## The "I Have No Idea" Protocol

When the decision tree fails you, do this in order:

### Step 1: Solve the Brute Force (5 minutes)
Write the naive solution. Do not worry about efficiency. Just get something that works.

Why? Because:
- It proves you understand the problem
- It gives you test cases to verify later optimizations
- It often reveals the pattern naturally

### Step 2: Analyze the Brute Force (2 minutes)
What is its time complexity? What is the bottleneck?

- Nested loop checking all pairs → O(n^2). Can you reduce to O(n) with hashing?
- Recursive exploration → exponential. Can you memoize (DP)?
- Repeated minimum lookups → O(n) per lookup. Can you use a heap?

### Step 3: Find the Redundancy (2 minutes)
What work is being done repeatedly?

- Computing the same subproblem → DP
- Checking the same element multiple times → Two pointers or sliding window
- Searching in a sorted structure → Binary search
- Maintaining a running extreme → Heap or monotonic stack

### Step 4: Match to Pattern (1 minute)
Now that you know the bottleneck, which pattern solves that exact bottleneck?

---

## Clarifying Questions to Ask the Interviewer

Asking questions shows you think deeply. Here are the best ones:

### About Input
- "What is the range of n?" (tells you acceptable complexity)
- "Can the array be empty?" (edge case)
- "Are all elements positive?" (sliding window only works with positives)
- "Can there be duplicates?" (affects hashing and two pointers)

### About Output
- "If there are multiple valid answers, can I return any?" (simplifies problem)
- "What should I return if no solution exists?" (edge case)
- "Do you want all solutions or just one?" (backtracking vs greedy)

### About Constraints
- "Can I modify the input array?" (in-place vs extra space)
- "Is memory more constrained than time, or vice versa?" (guides tradeoff)
- "Do elements fit in standard integer types?" (overflow concerns)

---

## The Verbal Testing Technique

Before you write a single line of code, explain your solution out loud using a concrete example.

**Template:**
```
"Let me walk through Example 1 with my approach.

The input is [2, 7, 11, 15], target = 9.

My algorithm does [X].
At step 1, [this happens].
At step 2, [this happens].
At step 3, [this happens].

So the output is [2, 7], which matches the example.

Let me also check an edge case: empty array.
If the array is empty, my algorithm returns [empty result], which makes sense."
```

**Why this works:**
- It catches logic errors before you code them
- It shows the interviewer you think systematically
- It buys you time to think while talking
- It demonstrates communication skills

---

## Common Interview Traps & How to Avoid Them

### Trap 1: Starting to Code Immediately
**Symptom:** You read the problem and start typing in 30 seconds.
**Fix:** Spend at least 2 minutes understanding and 2 minutes planning. The interviewer cares more about your thought process than your typing speed.

### Trap 2: Optimizing Too Early
**Symptom:** You reject the O(n^2) solution because it is "too slow" and spend 5 minutes stuck trying to find O(n).
**Fix:** Write the brute force first. Then optimize. A working O(n^2) solution is better than no solution.

### Trap 3: Ignoring Edge Cases
**Symptom:** Your solution works for the example but fails on empty input, single element, or duplicates.
**Fix:** After writing code, explicitly test: empty, single element, all same, all different, maximum values.

### Trap 4: Not Stating Complexity
**Symptom:** You finish coding and wait for the interviewer to ask about complexity.
**Fix:** State time and space complexity immediately after finishing. It shows confidence and completeness.

### Trap 5: Getting Stuck in One Pattern
**Symptom:** You are convinced the problem is a sliding window problem and spend 10 minutes forcing it to work.
**Fix:** If a pattern does not fit after 3 minutes, abandon it. Try the next most likely pattern.

---

## The "5-Second Gut Check"

Before committing to a pattern, ask yourself:

1. **Does the input structure support this pattern?**
   - Binary search needs sorted data or sorted answer space.
   - Two pointers need sorted data or the ability to sort.
   - Sliding window needs a contiguous subarray constraint.

2. **Does the output structure match this pattern?**
   - Backtracking returns all combinations.
   - DP returns an optimal value or count.
   - Greedy returns a single optimal choice.

3. **Does the constraint size allow this pattern?**
   - n <= 20: exponential (backtracking) is okay.
   - n <= 10^5: must be O(n) or O(n log n).

If any answer is "no," your pattern is wrong. Pivot.

---

## The Confidence Checklist

Before saying "I am done," verify:

- [ ] I can explain the problem back to the interviewer
- [ ] I have identified the correct archetype
- [ ] I have written the template for that archetype
- [ ] I have walked through at least one example verbally
- [ ] My code handles all edge cases
- [ ] I have stated time and space complexity
- [ ] I can explain WHY this pattern fits and not another

---

## Practice Drills for Meta-Skills

### Drill 1: Speed Identification (5 minutes)
Pick 5 problems from NEETCODE_150.md. Cover the archetype column. Identify each in 60 seconds. Check your answers. Repeat until you get 5/5.

### Drill 2: The Pivot (10 minutes)
Pick a problem. Commit to the WRONG pattern for 2 minutes. Realize it does not fit. Pivot to the correct pattern. Solve it. This trains your "abandon ship" reflex.

### Drill 3: Verbal Walkthrough (5 minutes)
Pick a solved problem. Explain it to an imaginary interviewer using the verbal testing template. Record yourself. Listen for "um," "uh," and unclear explanations.

### Drill 4: Edge Case Stress Test (5 minutes)
Pick a solved problem. List 5 edge cases. Modify your code to handle each. This prevents interview surprises.

---

## Summary

| Step | Time | What to Do |
|---|---|---|
| Read & paraphrase | 1 min | Understand the problem |
| Identify output | 1 min | Know what you are returning |
| Check constraints | 1 min | Determine acceptable complexity |
| Brute force | 1 min | Write naive solution mentally |
| Scan triggers | 1 min | Match keywords to patterns |
| Try template | 2 min | Write pattern template |
| Solve | 2 min | Fill in the template |
| Test | 1 min | Walk through example |
| Optimize | 1 min | Reduce space or time |

**Total: 10 minutes to go from "I have no idea" to a working solution.**

---

*Master this framework first. Then learn the 18 patterns. Without this, the patterns are just memorized solutions. With this, the patterns are tools you know when to use.*
