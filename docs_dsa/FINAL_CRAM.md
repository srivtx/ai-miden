# FINAL_CRAM.md — Last 48 Hours Before the Interview

> Read this once. Execute it. Do not deviate.

---

## 1. Mental Framework

### What to Tell Yourself
- You are not expected to solve every problem perfectly. You are expected to think clearly under pressure.
- The interviewer is not your enemy. They want to see how you reason, not just whether you reach the answer.
- If you have completed NEETCODE_150.md or similar structured prep, you already know more than 80% of candidates. Trust the reps.

### Anxiety Management
- Box breathing: 4 seconds in, 4 hold, 4 out, 4 hold. Do this for 2 minutes before any review session.
- If anxiety spikes during the interview, pause, breathe once, and restate the problem in your own words. It buys time and resets focus.
- Do not catastrophize one bad round. Most interview loops allow one mediocre round if the others are strong.

### Sleep Strategy
- T-48h to T-24h: Normal schedule. Light review only. No caffeine after 2 PM.
- T-24h to T-12h: Stop all screens 90 minutes before bed. Read paper notes if you must review.
- T-12h to T-0h: Aim for 7-8 hours. A tired brain cannot recurse.

---

## 2. The 48-Hour Schedule

| Time | Activity | Rule |
|---|---|---|
| T-48h | Light review of solved problems | Re-read 5 problems you have already solved. Do NOT write code. |
| T-42h | Pattern flashcards | Run through QUICK_REFERENCE.md trigger words. 30 minutes max. |
| T-36h | 3 easy warm-ups | Pick 3 Easy problems from NEETCODE_150.md. Time yourself: 10 minutes each. |
| T-30h | Stop studying | Eat a normal meal. Light exercise. No DSA. |
| T-24h | Final pattern review | Re-read the 10-Second Decision Tree in QUICK_REFERENCE.md. |
| T-18h | Sleep prep | No screens. Read COMPLEXITY_GUIDE.md tables on paper if needed. |
| T-12h | Sleep | Mandatory. Set two alarms. |
| T-6h | Final quick reference review | 20 minutes: complexity table, edge case checklist, one template per pattern. |
| T-4h | Arrival prep | Print or open FINAL_CRAM.md, QUICK_REFERENCE.md, and COMPLEXITY_GUIDE.md. |
| T-2h | Mental warmup | Re-solve Two Sum from memory. It builds momentum. |
| T-30min | Environment check | Virtual: see checklist below. In-person: ID, water, pen, paper. |
| During | Interview rounds | See Section 5 for time allocation and stuck protocol. |

---

## 3. What to Review (Ordered by ROI)

### 3.1 Pattern Recognition Cheat Sheet

See QUICK_REFERENCE.md for full templates. In the final 48 hours, memorize only the trigger words and the first 3 lines of each template.

| Pattern | Trigger Words | First 3 Lines of Template |
|---|---|---|
| Arrays & Hashing | find, count, duplicate | `seen = set()` / `for x in arr:` / `if x in seen:` |
| Two Pointers | sorted, pair sum, palindrome | `l, r = 0, len(arr)-1` / `while l < r:` / `if condition:` |
| Stack | valid parentheses, next greater | `stack = []` / `for i, x in enumerate(arr):` / `while stack and x > arr[stack[-1]]:` |
| Binary Search | sorted, O(log n) | `l, r = 0, len(arr)-1` / `while l <= r:` / `m = l + (r-l)//2` |
| Sliding Window | subarray, substring, consecutive | `l = 0` / `for r in range(len(s)):` / `window.add(s[r])` |
| Linked List | reverse, cycle, merge | `prev, curr = None, head` / `while curr:` / `nxt = curr.next` |
| Trees | root-to-leaf, LCA, level order | `def dfs(node):` / `if not node: return base_case` / `left = dfs(node.left)` |
| Heap | K largest/smallest, merge K | `heap = nums[:k]; heapify(heap)` / `for x in nums[k:]:` / `if x > heap[0]: heapreplace(heap, x)` |
| Backtracking | all combinations, permutations | `def backtrack(path, choices):` / `if valid(path): result.append(path[:])` / `for choice in choices:` |
| Graphs | connected, path, shortest, islands | `queue = [start]; visited = {start}` / `while queue:` / `node = queue.pop(0)` |
| 1-D DP | maximize, ways to reach | `dp = [0] * n; dp[0] = base` / `for i in range(1, n):` / `dp[i] = recurrence(...)` |
| Intervals | merge, overlap, meeting rooms | `intervals.sort(key=lambda x: x[1])` / `count, end = 0, -inf` / `for s, e in intervals:` |

### 3.2 The 15 Most Common Interview Problems

Memorize the pattern and the 3-step sketch. Do not write full code from scratch in your head.

| # | Problem | Pattern | Sketch |
|---|---|---|---|
| 1 | Two Sum | Hash Map | Complement map. `seen = {}`. If `target - x in seen`, return. Else `seen[x] = i`. |
| 2 | Valid Parentheses | Stack | Push opens. On close, pop and check match. If mismatch or stack empty, return False. |
| 3 | Merge Two Sorted Lists | Linked List | Dummy node. `while l1 and l2: pick smaller, advance`. Append remainder. |
| 4 | Best Time to Buy/Sell Stock | Greedy | Track `min_price` and `max_profit` in one pass. `profit = price - min_price`. |
| 5 | Valid Anagram | Hashing | Count chars in both strings. Compare frequency maps. Or sort and compare. |
| 6 | Maximum Subarray | 1-D DP / Kadane | `curr = max(x, curr + x)`. `best = max(best, curr)`. O(n) time, O(1) space. |
| 7 | Binary Search | Binary Search | `while l <= r`. `m = l + (r-l)//2`. Narrow left or right. Return -1 if absent. |
| 8 | Reverse Linked List | Linked List | `prev, curr = None, head`. Iterate: `nxt = curr.next`, `curr.next = prev`, shift pointers. |
| 9 | Longest Substring Without Repeating Characters | Sliding Window | `l = 0`. Expand `r`. If char in window, shrink `l` until valid. Track max length. |
| 10 | 3Sum | Two Pointers | Sort. Fix `i`. `l, r` converge. Skip duplicates on `i`, `l`, and `r`. |
| 11 | Number of Islands | Graph BFS/DFS | Grid DFS/BFS. Mark visited as `0`. Count calls from unvisited land cells. |
| 12 | Merge Intervals | Intervals | Sort by start. Iterate: if overlap (`curr[0] <= last[1]`), merge. Else append. |
| 13 | Climbing Stairs | 1-D DP | Fibonacci. `dp[i] = dp[i-1] + dp[i-2]`. Optimize to O(1) space with two variables. |
| 14 | Course Schedule | Graph + Topo Sort | Build adjacency list and in-degree. Kahn's BFS: queue nodes with in-degree 0. Reduce neighbors. |
| 15 | Container With Most Water | Two Pointers | `l, r` at ends. Area = `min(h[l], h[r]) * (r-l)`. Move shorter inward. Track max. |

### 3.3 Time/Space Complexity Quick Reference

See COMPLEXITY_GUIDE.md for full per-pattern tables. Memorize these rules of thumb:

| Scenario | Time | Space |
|---|---|---|
| Single pass with hash map | O(n) | O(n) |
| Sorted array + two pointers | O(n) | O(1) |
| Binary search on sorted data | O(log n) | O(1) |
| Tree/graph traversal | O(V+E) or O(n) | O(h) or O(w) |
| 1-D DP | O(n) | O(n) or O(1) |
| 2-D DP | O(mn) | O(min(m,n)) |
| Backtracking | Exponential | O(n) |

Sanity check: if your solution is worse than the table above, you missed an optimization.

### 3.4 Edge Case Checklist

Run this checklist on every problem before declaring done:

- [ ] Empty input (`[]`, `None`, `""`, `0`)
- [ ] Single element
- [ ] All elements identical
- [ ] All elements distinct
- [ ] Duplicates (if problem implies uniqueness)
- [ ] Negative numbers (if numeric)
- [ ] Integer overflow (use `long` or check bounds in languages with fixed-width ints)
- [ ] Target not found / no valid answer (what do you return?)
- [ ] Maximum input size (does your solution degrade?)

---

## 4. What to SKIP

Equally important. Violating any of these will hurt more than reviewing more will help.

| Do NOT | Why |
|---|---|
| Start new hard problems | You will learn failure, not pattern fluency. |
| Learn new patterns | 48 hours is not enough to build instinct. Trust what you know. |
| Deep dive system design | Unless your loop explicitly includes a system design round, it is a distraction. |
| Memorize solutions line-by-line | Interviewers detect rote recall. Memorize the pattern, not the syntax. |
| Stay up late cramming | Sleep deprivation destroys working memory and recursion depth. |
| Change your language | Use the language you practiced in. No exceptions. |

---

## 5. Interview Day Protocol

### 5.1 Virtual Setup Checklist

- [ ] Camera at eye level. Light in front of you, not behind.
- [ ] Second monitor or printed QUICK_REFERENCE.md available (only for your eyes, not visible on camera).
- [ ] IDE or whiteboard tool tested 24 hours prior.
- [ ] Headphones with working microphone. Test audio and video.
- [ ] Water nearby. Phone silenced. Door locked or Do Not Disturb sign posted.
- [ ] Backup internet (phone hotspot) ready.

### 5.2 How to Start Every Problem

Follow this sequence verbatim. It buys thinking time and signals professionalism.

1. **Clarify (1-2 min):** Restate the problem. Ask about input constraints, output format, and edge cases.
2. **Examples (1-2 min):** Write 2-3 examples. Include a trivial case and a non-trivial case.
3. **Brute Force (2-3 min):** State the obvious solution and its complexity. Do NOT apologize for it.
4. **Optimize (2-5 min):** Identify the bottleneck. Apply the 10-Second Decision Tree from QUICK_REFERENCE.md.
5. **Code (10-15 min):** Write clean code. Use helper functions if it improves readability.
6. **Test (3-5 min):** Walk through your code with one of the examples you wrote. Trace variable state line by line.

### 5.3 Time Allocation Per Problem (35-minute round)

| Phase | Minutes | Goal |
|---|---|---|
| Clarify + Examples | 5 | Zero ambiguity. Confirm constraints. |
| Brute Force | 10 | Get a working solution on the board. |
| Optimize + Code | 15 | Improve to optimal or near-optimal. |
| Test + Wrap-up | 5 | Trace an example. State complexity. |

If you solve optimally in 20 minutes, spend the remaining time on extra test cases and discussing trade-offs.

### 5.4 What to Do If Stuck — 3 Escalation Levels

**Level 1 — Verbalize the Block (30 seconds):**
State exactly where you are stuck. "I have the brute force, but I cannot see how to get below O(n^2)." This invites the interviewer to give a micro-hint without you asking.

**Level 2 — Ask a Specific Question (30 seconds):**
Do not say "I am stuck." Say: "Does the problem have sorted input, or can I sort it?" or "Is there a substructure here that suggests DP?"

**Level 3 — Request a Hint (last resort):**
"I feel like I am missing a pattern. Can you give me a small nudge toward the right data structure?"

Never stay silent for more than 60 seconds. Verbal silence is the only unrecoverable mistake.

### 5.5 When to Ask Hints

- If you have not made progress after 5 minutes of brute force.
- If you know the pattern family but cannot instantiate it.
- If the interviewer is already offering body-language cues (leaning forward, pointing).

Do NOT ask for a hint in the first 2 minutes unless the problem statement is genuinely ambiguous.

---

## 6. Post-Interview

### 6.1 What to Write Down Immediately

Within 30 minutes of the interview, document:

- Problem statements (paraphrased)
- Your approach and what you coded
- Where you got stuck and what hint you received
- Interviewer style (hands-off, collaborative, pressure-testing)
- Any behavioral questions asked and your answers
- Your self-assessment: strong round, average round, or weak round

Store this in a private doc. It is gold for future loops.

### 6.2 Follow-up Etiquette

- Send thank-you emails within 24 hours. Keep it under 5 sentences.
- Reference one specific part of the conversation to prove you were engaged.
- Do NOT ask about results in the thank-you note.
- If you were asked a question you could not answer, it is acceptable to include a brief follow-up with the correct answer in the thank-you email. Limit to one item.

### 6.3 Debrief Framework

For each round, score yourself 1-5:

| Dimension | 1 (Poor) | 3 (Average) | 5 (Strong) |
|---|---|---|---|
| Clarification | Jumped straight to code | Asked basic constraints | Probed deeply, found hidden constraints |
| Speed | Brute force only at 30 min | Optimal but rushed | Optimal with time to spare |
| Communication | Silent coding | Some narration | Constant, clear reasoning |
| Testing | None | One happy path | Edge cases + complexity stated |
| Code Quality | Messy, buggy | Readable, minor issues | Clean, modular, bug-free |

If your average is below 3 on any dimension, that is your target for the next prep cycle. See IMPROVEMENTS.md for targeted drills.

---

*This is a terminal document. Read it once, follow the schedule, and stop second-guessing. Good luck.*
