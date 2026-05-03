# Pattern 09: Backtracking — Practice Problems

## Subsets

### 78. Subsets
**Statement:** All subsets of distinct integers.
**Code:**
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

### 90. Subsets II
**Statement:** All subsets with duplicates. No duplicates in output.
**Intuition:** Sort first. Skip duplicates: `if i > start and nums[i] == nums[i-1]: continue`

---

## Permutations

### 46. Permutations
**Statement:** All permutations of distinct integers.
**Code:**
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

### 47. Permutations II
**Statement:** Permutations with duplicates.
**Intuition:** Sort. Skip duplicates. Use `used` array to handle duplicates properly.

### 31. Next Permutation
**Statement:** Next lexicographical permutation in-place.
**Intuition:** Find first decreasing from right. Swap with smallest larger on right. Reverse suffix.

---

## Combinations

### 77. Combinations
**Statement:** All combinations of k numbers from 1 to n.
**Intuition:** Backtrack. Choose k elements.

### 39. Combination Sum
**Statement:** All combinations that sum to target. Reuse allowed.
**Code:**
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
            backtrack(i, path, remaining - candidates[i])
            path.pop()
    backtrack(0, [], target)
    return result
```

### 40. Combination Sum II
**Statement:** Each number used once. Array may have duplicates.
**Intuition:** Sort. `backtrack(i + 1, ...)`. Skip duplicates.

### 216. Combination Sum III
**Statement:** Find k numbers that sum to n, using 1-9 once each.
**Intuition:** Standard combination sum with k limit.

---

## N-Queens & Grid

### 51. N-Queens
**Statement:** All distinct solutions to N-Queens.
**Intuition:** Place queen row by row. Check column and diagonals.
**Code:**
```python
def solve_n_queens(n):
    def is_valid(board, row, col):
        for i in range(row):
            if board[i] == col or abs(board[i] - col) == abs(i - row):
                return False
        return True
    
    def backtrack(row):
        if row == n:
            result.append(['.' * board[i] + 'Q' + '.' * (n - board[i] - 1) for i in range(n)])
            return
        for col in range(n):
            if is_valid(board, row, col):
                board[row] = col
                backtrack(row + 1)
    
    result = []
    board = [-1] * n
    backtrack(0)
    return result
```

### 52. N-Queens II
**Statement:** Count distinct solutions.

### 37. Sudoku Solver
**Statement:** Solve Sudoku puzzle.
**Intuition:** Find empty cell. Try 1-9. If valid, recurse. Backtrack if fails.

---

## String Building

### 131. Palindrome Partitioning
**Statement:** Partition string so every substring is palindrome.
**Intuition:** For each start, expand while palindrome. Recurse on remainder.

### 93. Restore IP Addresses
**Statement:** All valid IP addresses from string.
**Intuition:** 4 segments, each 1-3 digits, value 0-255. No leading zeros unless "0".

### 282. Expression Add Operators
**Statement:** Add +, -, * to get target value.
**Intuition:** Backtrack. Track current value and last operand for multiplication precedence.

### 241. Different Ways to Add Parentheses
**Statement:** All results from different parenthesizations.
**Intuition:** Divide and conquer. For each operator, compute left and right combinations.

---

## Word / Dictionary

### 140. Word Break II
**Statement:** All possible sentence segmentations.
**Intuition:** Backtrack with memoization. Try each prefix in dictionary.

---

## Mixed Drill Set

1. 78 — Subsets
2. 46 — Permutations
3. 39 — Combination sum
4. 77 — Combinations
5. 51 — N-Queens
6. 131 — Palindrome partition
7. 37 — Sudoku solver
8. 93 — Restore IP
9. 90 — Subsets II (duplicates)
10. 47 — Permutations II (duplicates)
