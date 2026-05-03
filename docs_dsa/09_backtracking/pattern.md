# Pattern 09: Backtracking

> **Pattern Recognition:** When you see "all combinations", "permutations", "subsets", "find all", "ways to", "N-queens", "sudoku" — think backtracking.
>
> **Fundamental Insight:** Backtracking is DFS on a decision tree. At each step, you make a choice, recurse, and if it doesn't work, you undo the choice and try another. The key is the "undo" (backtrack).

---

## Archetype 9.1: Subsets

### Recognition Signal
Words: **"subsets", "power set", "all subsets", "subsequences"**

### Template
```python
def subsets(nums):
    result = []
    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result
```

### Problems
- Subsets (LeetCode 78)
- Subsets II (LeetCode 90) — with duplicates

---

## Archetype 9.2: Permutations

### Recognition Signal
Words: **"permutations", "all arrangements", "order matters"**

### Template
```python
def permute(nums):
    result = []
    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False
    backtrack([], [False] * len(nums))
    return result
```

### Problems
- Permutations (LeetCode 46)
- Permutations II (LeetCode 47) — with duplicates
- Next Permutation (LeetCode 31) — iterative

---

## Archetype 9.3: Combinations

### Recognition Signal
Words: **"combinations", "combination sum", "k elements", "sum to target"**

### Problems
- Combinations (LeetCode 77)
- Combination Sum (LeetCode 39) — reuse allowed
- Combination Sum II (LeetCode 40) — no reuse, duplicates
- Combination Sum III (LeetCode 216)

**Combination Sum template:**
```python
def combination_sum(candidates, target):
    result = []
    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return
        for i in range(start, len(candidates)):
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # i for reuse
            path.pop()
    backtrack(0, [], target)
    return result
```

---

## Archetype 9.4: N-Queens & Grid Placement

### Recognition Signal
Words: **"N-queens", "place", "board", "attack", "valid placement"**

### Problems
- N-Queens (LeetCode 51)
- N-Queens II (LeetCode 52)
- Sudoku Solver (LeetCode 37)

---

## Archetype 9.5: String / Expression Building

### Recognition Signal
Words: **"add operators", "parenthesize", "restore IP", "palindrome partition"**

### Problems
- Palindrome Partitioning (LeetCode 131)
- Restore IP Addresses (LeetCode 93)
- Expression Add Operators (LeetCode 282)
- Different Ways to Add Parentheses (LeetCode 241)

---

## Archetype 9.6: Word Break / Dictionary

### Recognition Signal
Words: **"word break", "concatenated", "dictionary", "sentence"**

### Problems
- Word Break (LeetCode 139) — DP
- Word Break II (LeetCode 140) — Backtracking + memoization
- Concatenated Words (LeetCode 472)

---

## Pruning Techniques

1. **Sort first** to skip duplicates
2. **Early termination** when sum exceeds target
3. **Memoization** for repeated states
4. **Constraint checking** before recursing

---

## Mastery Checklist
- [ ] Subsets: with and without duplicates
- [ ] Permutations: with and without duplicates
- [ ] Combinations: sum to target, with/without reuse
- [ ] N-Queens: row-by-row placement
- [ ] Sudoku: try 1-9, backtrack if invalid
- [ ] Palindrome partition: expand from center
- [ ] Word break: backtracking + memo

---

## The Backtracking Template

```python
def backtrack(candidate):
    if valid(candidate):
        output(candidate)
        return
    
    for next_candidate in candidates:
        if not valid(next_candidate):
            continue
        place(next_candidate)
        backtrack(next_candidate)
        remove(next_candidate)  # BACKTRACK
```

**Key insight:** The `remove()` step is what makes it backtracking. Without it, it's just DFS.

---

## Common Traps

**Trap:** Forgetting to copy path before adding to result.
- Fix: `result.append(path[:])` not `result.append(path)`

**Trap:** Modifying shared state without backtracking.
- Fix: Always undo changes after recursive call.

**Trap:** Infinite recursion from not advancing start index.
- Fix: Pass `i + 1` (no reuse) or `i` (reuse) correctly.

**Near Miss: DP vs Backtracking**
- "Count ways" → DP
- "List all ways" → Backtracking
