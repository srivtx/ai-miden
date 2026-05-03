# Backtracking: Drills Part 3 — Near Misses + Pattern Blends + Interview Simulation

---

### Problem 16. 491. Non-decreasing Subsequences
**Archetype:** 9.1 Subsets
**Type:** Near Miss
**Statement:** Given an integer array nums, return all the different possible non-decreasing subsequences of the given array with at least two elements.
**Why it fits:** It uses the same include/exclude backtracking as subsets, but adds a monotonic constraint (non-decreasing). It also introduces a `used` set at the current recursion level to avoid duplicate subsequences without sorting the input.
**The Twist:** You cannot sort the input because the relative order defines the subsequence. Duplicates are avoided by tracking which values have been used at the current level in a hash set.
**Code Skeleton:**
```python
from typing import List

def findSubsequences(nums: List[int]) -> List[List[int]]:
    result = []

    def backtrack(start, path):
        if len(path) >= 2:
            result.append(path[:])
        used = set()
        for i in range(start, len(nums)):
            if nums[i] in used:
                continue
            if not path or nums[i] >= path[-1]:
                used.add(nums[i])
                path.append(nums[i])
                backtrack(i + 1, path)
                path.pop()

    backtrack(0, [])
    return result
```

---

### Problem 17. 526. Beautiful Arrangement
**Archetype:** 9.2 Permutations
**Type:** Near Miss
**Statement:** Suppose you have n integers labeled 1 through n. A permutation of those n integers is considered a beautiful arrangement if for every i (1 <= i <= n), either perm[i] is divisible by i or i is divisible by perm[i]. Return the number of beautiful arrangements.
**Why it fits:** It is a constrained permutation problem. Instead of generating all permutations and filtering, you prune branches where the divisibility condition fails at the current position.
**The Twist:** The constraint is checked at every position during the build, not at the end. This aggressive pruning makes a seemingly exponential problem feasible for n <= 15.
**Code Skeleton:**
```python
from typing import List

def countArrangement(n: int) -> int:
    count = 0
    used = [False] * (n + 1)

    def backtrack(pos):
        nonlocal count
        if pos > n:
            count += 1
            return
        for num in range(1, n + 1):
            if not used[num] and (num % pos == 0 or pos % num == 0):
                used[num] = True
                backtrack(pos + 1)
                used[num] = False

    backtrack(1)
    return count
```

---

### Problem 18. 216. Combination Sum III
**Archetype:** 9.3 Combinations
**Type:** Near Miss
**Statement:** Find all valid combinations of k numbers that sum up to n such that the following conditions are true: only numbers 1 through 9 are used, each number is used at most once.
**Why it fits:** A constrained variant of Combination Sum. The candidate set is fixed (1-9), numbers cannot be reused, and there are exactly two tight constraints: k elements and target sum n.
**The Twist:** The termination condition is a combination of `len(path) == k` AND `remaining == 0`. Pruning is very effective because the search space (1-9) is tiny.
**Code Skeleton:**
```python
from typing import List

def combinationSum3(k: int, n: int) -> List[List[int]]:
    result = []

    def backtrack(start, path, remaining):
        if len(path) == k:
            if remaining == 0:
                result.append(path[:])
            return
        for i in range(start, 10):
            if i > remaining:
                break
            path.append(i)
            backtrack(i + 1, path, remaining - i)
            path.pop()

    backtrack(1, [], n)
    return result
```

---

### Problem 19. 52. N-Queens II
**Archetype:** 9.4 N-Queens & Grid
**Type:** Near Miss
**Statement:** The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other. Return the number of distinct solutions.
**Why it fits:** It is structurally identical to N-Queens I, but instead of building board configurations, you only count valid placements. This removes the overhead of constructing output strings and focuses purely on constraint validation.
**The Twist:** No board representation is needed. Just count valid column placements per row. It is a pure constraint-satisfaction counting problem.
**Code Skeleton:**
```python
def totalNQueens(n: int) -> int:
    count = 0
    cols = set()
    diag1 = set()
    diag2 = set()

    def backtrack(r):
        nonlocal count
        if r == n:
            count += 1
            return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue
            cols.add(c)
            diag1.add(r - c)
            diag2.add(r + c)
            backtrack(r + 1)
            cols.remove(c)
            diag1.remove(r - c)
            diag2.remove(r + c)

    backtrack(0)
    return count
```

---

### Problem 20. 282. Expression Add Operators
**Archetype:** 9.5 String/Expression Building
**Type:** Near Miss
**Statement:** Given a string num that contains only digits and an integer target, return all possibilities to insert the binary operators '+', '-', and/or '*' between the digits of num so that the resultant expression evaluates to the target value.
**Why it fits:** A hard string-building problem where the decisions are where to place operators and what operands to form. It requires evaluating the expression on the fly to handle operator precedence correctly.
**The Twist:** Multiplication requires careful state tracking. You cannot simply accumulate a running sum; you must track the last operand so you can reverse it and apply multiplication (e.g., `1+2*3` requires knowing the last operand was `2`).
**Code Skeleton:**
```python
from typing import List

def addOperators(num: str, target: int) -> List[str]:
    result = []

    def backtrack(index, path, eval_val, last_operand):
        if index == len(num):
            if eval_val == target:
                result.append(path)
            return
        for i in range(index, len(num)):
            if i > index and num[index] == '0':
                break  # No leading zeros
            curr_str = num[index:i + 1]
            curr = int(curr_str)
            if index == 0:
                backtrack(i + 1, curr_str, curr, curr)
            else:
                backtrack(i + 1, path + '+' + curr_str, eval_val + curr, curr)
                backtrack(i + 1, path + '-' + curr_str, eval_val - curr, -curr)
                backtrack(i + 1, path + '*' + curr_str,
                          eval_val - last_operand + last_operand * curr,
                          last_operand * curr)

    backtrack(0, "", 0, 0)
    return result
```

---

### Problem 21. 140. Word Break II
**Archetype:** 9.6 Word Break/Dictionary (Blended with DP/Hashing)
**Type:** Pattern Blend
**Statement:** Given a string s and a dictionary of strings wordDict, add spaces in s to construct a sentence where each word is a valid dictionary word. Return all such possible sentences in any order.
**Why it fits:** It blends backtracking with memoization (DP). A naive backtracking solution is exponential, but caching whether a suffix can be broken prevents redundant exploration.
**The Twist:** The dictionary can be large, and the string can be long. Memoization of the suffix results (list of sentences) turns this into a classic DP + backtracking hybrid.
**Code Skeleton:**
```python
from typing import List

def wordBreak(s: str, wordDict: List[str]) -> List[str]:
    word_set = set(wordDict)
    memo = {}

    def backtrack(start):
        if start in memo:
            return memo[start]
        if start == len(s):
            return [""]
        result = []
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                for sub in backtrack(end):
                    if sub:
                        result.append(word + " " + sub)
                    else:
                        result.append(word)
        memo[start] = result
        return result

    return backtrack(0)
```

---

### Problem 22. 698. Partition to K Equal Sum Subsets
**Archetype:** 9.1 Subsets (Blended with DP/Bitmask)
**Type:** Pattern Blend
**Statement:** Given an integer array nums and an integer k, return true if it is possible to divide this array into k non-empty subsets whose sums are all equal.
**Why it fits:** It is a subset-partitioning problem that requires grouping elements into buckets of equal sum. Backtracking with pruning (sorting descending, early exit on bucket overflow) is the standard approach, but it can also be solved with DP over bitmasks.
**The Twist:** The search space is huge. Pruning heuristics are essential: sort descending to place large numbers first (fail fast), and skip duplicate numbers at the same bucket position.
**Code Skeleton:**
```python
from typing import List

def canPartitionKSubsets(nums: List[int], k: int) -> bool:
    total = sum(nums)
    if total % k != 0:
        return False
    target = total // k
    nums.sort(reverse=True)
    buckets = [0] * k

    def backtrack(index):
        if index == len(nums):
            return all(b == target for b in buckets)
        for i in range(k):
            if buckets[i] + nums[index] <= target:
                buckets[i] += nums[index]
                if backtrack(index + 1):
                    return True
                buckets[i] -= nums[index]
            if buckets[i] == 0:
                break  # Pruning: empty bucket failed
        return False

    return backtrack(0)
```

---

### Problem 23. 37. Sudoku Solver
**Archetype:** 9.4 N-Queens & Grid (Blended with Constraint Propagation)
**Type:** Pattern Blend
**Statement:** Write a program to solve a Sudoku puzzle by filling the empty cells.
**Why it fits:** The ultimate grid backtracking problem. It requires checking row, column, and 3x3 box constraints at every step. It demonstrates how backtracking can solve constraint satisfaction problems.
**The Twist:** Empty cells ('.') can be filled with any digit 1-9 that does not violate constraints. Finding the next empty cell and checking constraints efficiently (using bitmasks or hash sets) is the key to passing large test sets.
**Code Skeleton:**
```python
from typing import List

def solveSudoku(board: List[List[str]]) -> None:
    def is_valid(r, c, num):
        for i in range(9):
            if board[r][i] == num or board[i][c] == num:
                return False
        box_r, box_c = 3 * (r // 3), 3 * (c // 3)
        for i in range(box_r, box_r + 3):
            for j in range(box_c, box_c + 3):
                if board[i][j] == num:
                    return False
        return True

    def solve():
        for r in range(9):
            for c in range(9):
                if board[r][c] == '.':
                    for num in map(str, range(1, 10)):
                        if is_valid(r, c, num):
                            board[r][c] = num
                            if solve():
                                return True
                            board[r][c] = '.'
                    return False
        return True

    solve()
```

---

### Problem 24. 301. Remove Invalid Parentheses
**Archetype:** 9.5 String/Expression Building (Blended with BFS)
**Type:** Pattern Blend
**Statement:** Given a string s that contains parentheses and letters, remove the minimum number of invalid parentheses to make the input string valid. Return all possible results.
**Why it fits:** It blends backtracking with BFS-level pruning. Instead of exploring all deletion combinations, you can track how many left/right parentheses need removal and prune branches that require more deletions than allowed.
**The Twist:** The minimum removal constraint means you must first count how many left and right parentheses are invalid, then use backtracking to generate strings with exactly that many deletions.
**Code Skeleton:**
```python
from typing import List

def removeInvalidParentheses(s: str) -> List[str]:
    result = []

    def backtrack(index, left_count, right_count, left_rem, right_rem, expr):
        if index == len(s):
            if left_rem == 0 and right_rem == 0:
                result.append("".join(expr))
            return
        char = s[index]
        if char == '(' and left_rem > 0:
            backtrack(index + 1, left_count, right_count, left_rem - 1, right_rem, expr)
        elif char == ')' and right_rem > 0:
            backtrack(index + 1, left_count, right_count, left_rem, right_rem - 1, expr)

        expr.append(char)
        if char != '(' and char != ')':
            backtrack(index + 1, left_count, right_count, left_rem, right_rem, expr)
        elif char == '(':
            backtrack(index + 1, left_count + 1, right_count, left_rem, right_rem, expr)
        elif right_count < left_count:
            backtrack(index + 1, left_count, right_count + 1, left_rem, right_rem, expr)
        expr.pop()

    # Calculate minimum removals needed
    left_rem = right_rem = 0
    for char in s:
        if char == '(':
            left_rem += 1
        elif char == ')':
            if left_rem > 0:
                left_rem -= 1
            else:
                right_rem += 1

    backtrack(0, 0, 0, left_rem, right_rem, [])
    return list(set(result))
```

---

### Problem 25. 1239. Maximum Length of a Concatenated String with Unique Characters
**Archetype:** 9.1 Subsets (Blended with Bitmasks)
**Type:** Pattern Blend
**Statement:** You are given an array of strings arr. A string s is formed by the concatenation of a subsequence of arr that has unique characters. Return the maximum possible length of s.
**Why it fits:** It is a subset-selection problem where the constraint is character uniqueness. Backtracking over the array is natural, but bitmasks can speed up the uniqueness check by representing each string's character set as an integer.
**The Twist:** Many strings in arr may themselves contain duplicate characters and can be discarded immediately. For valid strings, a bitmask representation allows O(1) collision detection using bitwise AND.
**Code Skeleton:**
```python
from typing import List

def maxLength(arr: List[str]) -> int:
    masks = []
    for s in arr:
        mask = 0
        for ch in s:
            bit = 1 << (ord(ch) - ord('a'))
            if mask & bit:
                mask = 0
                break
            mask |= bit
        if mask > 0:
            masks.append(mask)

    max_len = 0

    def backtrack(index, current_mask, current_len):
        nonlocal max_len
        max_len = max(max_len, current_len)
        for i in range(index, len(masks)):
            if current_mask & masks[i] == 0:
                backtrack(i + 1, current_mask | masks[i],
                          current_len + bin(masks[i]).count('1'))

    backtrack(0, 0, 0)
    return max_len
```

---

### Problem 26. 1219. Path with Maximum Gold
**Archetype:** 9.4 N-Queens & Grid (Blended with DP)
**Type:** Interview Sim
**Statement:** In a gold mine grid of size m x n, each cell has an integer representing the amount of gold in that cell, 0 if empty. Return the maximum amount of gold you can collect.
**Why it fits:** A grid backtracking problem that asks for a maximum rather than a list of solutions. It requires exploring all valid paths from every non-zero cell and tracking the maximum sum encountered.
**The Twist:** Because you cannot revisit cells, the standard backtracking mark/unmark pattern applies. The path can start and end at any non-zero cell; there is no fixed start or target.
**Code Skeleton:**
```python
from typing import List

def getMaximumGold(grid: List[List[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    max_gold = 0

    def backtrack(r, c, curr):
        nonlocal max_gold
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == 0:
            return
        gold = grid[r][c]
        curr += gold
        max_gold = max(max_gold, curr)
        grid[r][c] = 0  # Mark as visited
        backtrack(r + 1, c, curr)
        backtrack(r - 1, c, curr)
        backtrack(r, c + 1, curr)
        backtrack(r, c - 1, curr)
        grid[r][c] = gold  # Unmark

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                backtrack(r, c, 0)
    return max_gold
```

---

### Problem 27. 1593. Split a String Into the Max Number of Unique Substrings
**Archetype:** 9.1 Subsets / 9.5 String/Expression Building
**Type:** Interview Sim
**Statement:** Given a string s, return the maximum number of unique substrings that the given string can be split into.
**Why it fits:** A backtracking optimization problem where the goal is to maximize the count of unique parts. It teaches using a set to enforce uniqueness and pruning when the remaining length cannot beat the current best.
**The Twist:** The decision at each step is "where to cut." Because you want to maximize the number of pieces, greedily cutting early seems appealing, but backtracking is needed to verify optimality due to uniqueness constraints.
**Code Skeleton:**
```python
from typing import List

def maxUniqueSplit(s: str) -> int:
    max_count = 0

    def backtrack(start, seen):
        nonlocal max_count
        if start == len(s):
            max_count = max(max_count, len(seen))
            return
        # Pruning: even if we split every remaining char, can we beat max_count?
        if len(s) - start + len(seen) <= max_count:
            return
        for end in range(start + 1, len(s) + 1):
            substring = s[start:end]
            if substring not in seen:
                seen.add(substring)
                backtrack(end, seen)
                seen.remove(substring)

    backtrack(0, set())
    return max_count
```

---

### Problem 28. 1079. Letter Tile Possibilities
**Archetype:** 9.2 Permutations (Blended with Frequency Counting)
**Type:** Interview Sim
**Statement:** You have n tiles, where each tile has one letter tiles[i] printed on it. Return the number of possible non-empty sequences of letters you can make using the letters printed on those tiles.
**Why it fits:** A permutation counting problem with duplicate characters. Instead of generating all permutations and deduplicating, you use a frequency counter and recurse on the remaining character counts.
**The Twist:** The input has duplicates, but the frequency map approach naturally avoids duplicate permutations without sorting or `used` arrays. It is a classic combinatorics backtracking problem.
**Code Skeleton:**
```python
from typing import List
from collections import Counter

def numTilePossibilities(tiles: str) -> int:
    count = Counter(tiles)

    def backtrack():
        total = 0
        for ch in list(count.keys()):
            if count[ch] > 0:
                count[ch] -= 1
                total += 1 + backtrack()  # 1 for current sequence, + deeper ones
                count[ch] += 1
        return total

    return backtrack()
```

---

### Problem 29. 1286. Iterator for Combination
**Archetype:** 9.3 Combinations (Blended with Iterator Design)
**Type:** Interview Sim
**Statement:** Design an Iterator class, which has a constructor that takes a string characters and a number combinationLength, and a method next() that returns the next combination of length combinationLength in lexicographical order.
**Why it fits:** It asks you to materialize the backtracking process into an iterator. Instead of generating all combinations at once, you generate the next one on demand using algorithmic next-combination logic.
**The Twist:** It can be solved by precomputing all combinations (backtracking) and storing them, but the optimal approach uses a pointer array to generate the lexicographically next combination in O(combinationLength) time.
**Code Skeleton:**
```python
from typing import List

class CombinationIterator:
    def __init__(self, characters: str, combinationLength: int):
        self.chars = characters
        self.length = combinationLength
        self.indices = list(range(combinationLength))
        self.has_next = True

    def next(self) -> str:
        result = "".join(self.chars[i] for i in self.indices)
        # Find next combination indices
        i = self.length - 1
        while i >= 0 and self.indices[i] == len(self.chars) - self.length + i:
            i -= 1
        if i < 0:
            self.has_next = False
        else:
            self.indices[i] += 1
            for j in range(i + 1, self.length):
                self.indices[j] = self.indices[j - 1] + 1
        return result

    def hasNext(self) -> bool:
        return self.has_next
```

---

### Problem 30. 1947. Maximum Compatibility Score Sum
**Archetype:** 9.2 Permutations (Blended with DP/Bitmask Assignment)
**Type:** Interview Sim
**Statement:** There are two groups of n students. You are given two n x n matrices where each matrix denotes the answers of students in a group. The compatibility score of two students is the number of answers that are the same. Return the maximum compatibility score sum.
**Why it fits:** This is an assignment problem solvable by backtracking (permuting one group and matching to the other) or by DP with bitmasks (Hungarian/DP over subsets). For n <= 8, backtracking is acceptable and elegant.
**The Twist:** You must match every student in group 1 to exactly one student in group 2. This is a perfect matching problem. Backtracking with pruning or bitmask DP are both valid approaches.
**Code Skeleton:**
```python
from typing import List

def maxCompatibilitySum(students: List[List[int]], mentors: List[List[int]]) -> int:
    n = len(students)
    m = len(students[0])

    # Precompute score matrix
    score = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            score[i][j] = sum(students[i][k] == mentors[j][k] for k in range(m))

    max_sum = 0
    used = [False] * n

    def backtrack(idx, curr_sum):
        nonlocal max_sum
        if idx == n:
            max_sum = max(max_sum, curr_sum)
            return
        for j in range(n):
            if not used[j]:
                used[j] = True
                backtrack(idx + 1, curr_sum + score[idx][j])
                used[j] = False

    backtrack(0, 0)
    return max_sum
```

---
