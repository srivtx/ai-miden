# Backtracking: Drills Part 2 — Warm-ups + Core Drills

---

### Problem 1. 78. Subsets
**Archetype:** 9.1 Subsets
**Type:** Warm-Up
**Statement:** Given an integer array nums of unique elements, return all possible subsets (the power set).
**Why it fits:** The canonical subsets problem. It introduces the core backtracking template: a recursive helper that decides "include" or "exclude" for each element, then backtracks.
**The Twist:** None — the standard template. The decision space is binary for each element. Master the `start_index` parameter to avoid duplicates.
**Code Skeleton:**
```python
from typing import List

def subsets(nums: List[int]) -> List[List[int]]:
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

---

### Problem 2. 46. Permutations
**Archetype:** 9.2 Permutations
**Type:** Warm-Up
**Statement:** Given an array nums of distinct integers, return all the possible permutations.
**Why it fits:** The canonical permutations problem. It teaches backtracking where the decision space is "which unused element to place next." A used-set or in-place swap technique is required.
**The Twist:** None — the standard template. Use a `used` boolean array or in-place swapping to track which elements have been placed.
**Code Skeleton:**
```python
from typing import List

def permute(nums: List[int]) -> List[List[int]]:
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

---

### Problem 3. 77. Combinations
**Archetype:** 9.3 Combinations
**Type:** Warm-Up
**Statement:** Given two integers n and k, return all possible combinations of k numbers out of the range [1, n].
**Why it fits:** The canonical combinations problem. It is structurally identical to subsets but with a fixed target length `k`. It enforces the `start_index` pattern to maintain lexicographical order and avoid duplicates.
**The Twist:** None — the standard template. The termination condition is `len(path) == k` instead of reaching the end of the array.
**Code Skeleton:**
```python
from typing import List

def combine(n: int, k: int) -> List[List[int]]:
    result = []

    def backtrack(start, path):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result
```

---

### Problem 4. 784. Letter Case Permutation
**Archetype:** 9.2 Permutations
**Type:** Warm-Up
**Statement:** Given a string s, we can transform every letter individually to be lowercase or uppercase to create another string. Return a list of all possible strings we could create.
**Why it fits:** A gentle introduction to backtracking on strings rather than arrays. The decision at each step is either "keep the character as is" (if it's a digit) or "choose lower/upper case" (if it's a letter).
**The Twist:** None — a straightforward pattern. It demonstrates that backtracking applies to any sequence where branching decisions exist at each position.
**Code Skeleton:**
```python
from typing import List

def letterCasePermutation(s: str) -> List[str]:
    result = []

    def backtrack(i, path):
        if i == len(s):
            result.append("".join(path))
            return
        if s[i].isalpha():
            path.append(s[i].lower())
            backtrack(i + 1, path)
            path.pop()
            path.append(s[i].upper())
            backtrack(i + 1, path)
            path.pop()
        else:
            path.append(s[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

---

### Problem 5. 257. Binary Tree Paths
**Archetype:** 9.2 Permutations / 9.1 Subsets
**Type:** Warm-Up
**Statement:** Given the root of a binary tree, return all root-to-leaf paths in any order.
**Why it fits:** Although it involves a tree, the solution is pure backtracking. You build a path from root to leaf, and when you hit a leaf, you record the path. This teaches backtracking in a recursive tree structure.
**The Twist:** None — the path is not explicitly a combination or permutation, but the include/backtrack pattern is identical. The base case is reaching a leaf node.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def binaryTreePaths(root: Optional[TreeNode]) -> List[str]:
    result = []

    def backtrack(node, path):
        if not node:
            return
        path.append(str(node.val))
        if not node.left and not node.right:
            result.append("->".join(path))
        else:
            backtrack(node.left, path)
            backtrack(node.right, path)
        path.pop()

    backtrack(root, [])
    return result
```

---

### Problem 6. 90. Subsets II
**Archetype:** 9.1 Subsets
**Type:** Core Drill
**Statement:** Given an integer array nums that may contain duplicates, return all possible subsets (the power set).
**Why it fits:** The canonical "subsets with duplicates" problem. It introduces the critical sorting + skip-duplicate pattern. If `nums[i] == nums[i-1]` and `i > start`, skip `nums[i]` to avoid duplicate subsets.
**The Twist:** Duplicates in the input create duplicate paths in the decision tree. Sorting makes duplicates adjacent, allowing you to skip them conditionally.
**Code Skeleton:**
```python
from typing import List

def subsetsWithDup(nums: List[int]) -> List[List[int]]:
    nums.sort()
    result = []

    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

---

### Problem 7. 47. Permutations II
**Archetype:** 9.2 Permutations
**Type:** Core Drill
**Statement:** Given a collection of numbers, nums, that might contain duplicates, return all possible unique permutations in any order.
**Why it fits:** The canonical "permutations with duplicates" problem. It teaches two duplicate-avoidance strategies: sorting + skipping used duplicates, or using a Counter/frequency map.
**The Twist:** In the `used` array approach, you skip `nums[i]` if `nums[i] == nums[i-1]` and `nums[i-1]` is not used. This ensures duplicates are only used in a fixed left-to-right order.
**Code Skeleton:**
```python
from typing import List

def permuteUnique(nums: List[int]) -> List[List[int]]:
    nums.sort()
    result = []

    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False

    backtrack([], [False] * len(nums))
    return result
```

---

### Problem 8. 39. Combination Sum
**Archetype:** 9.3 Combinations
**Type:** Core Drill
**Statement:** Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target.
**Why it fits:** The canonical unbounded knapsack / combination-sum problem. The same number can be used unlimited times. The `start_index` ensures combinations are non-decreasing, avoiding permutations of the same combination.
**The Twist:** Because elements can be reused, the recursive call is `backtrack(i, ...)` instead of `backtrack(i + 1, ...)`. This is the defining feature of unbounded combination problems.
**Code Skeleton:**
```python
from typing import List

def combinationSum(candidates: List[int], target: int) -> List[List[int]]:
    result = []

    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return
        for i in range(start, len(candidates)):
            path.append(candidates[i])
            backtrack(i, path, remaining - candidates[i])  # Reuse allowed
            path.pop()

    backtrack(0, [], target)
    return result
```

---

### Problem 9. 40. Combination Sum II
**Archetype:** 9.3 Combinations
**Type:** Core Drill
**Statement:** Given a collection of candidate numbers and a target number, find all unique combinations where the candidate numbers sum to target. Each number may only be used once.
**Why it fits:** Combines the combination sum pattern with the duplicate-skipping pattern. It is the bridge between subset-II and combination-sum, requiring both sorting and careful `start_index` management.
**The Twist:** Each number can be used at most once, but the input contains duplicates. You must skip duplicates at the same recursion level while allowing the same value to appear in the path from different original indices.
**Code Skeleton:**
```python
from typing import List

def combinationSum2(candidates: List[int], target: int) -> List[List[int]]:
    candidates.sort()
    result = []

    def backtrack(start, path, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        if remaining < 0:
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            path.append(candidates[i])
            backtrack(i + 1, path, remaining - candidates[i])
            path.pop()

    backtrack(0, [], target)
    return result
```

---

### Problem 10. 17. Letter Combinations of a Phone Number
**Archetype:** 9.5 String/Expression Building
**Type:** Core Drill
**Statement:** Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent.
**Why it fits:** The canonical string-building backtracking problem. It demonstrates backtracking over a mapping (digit -> letters) where the branching factor varies per digit.
**The Twist:** None — the standard template for building strings from a decision tree where each level corresponds to a digit and each branch is a possible letter.
**Code Skeleton:**
```python
from typing import List

def letterCombinations(digits: str) -> List[str]:
    if not digits:
        return []
    mapping = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }
    result = []

    def backtrack(index, path):
        if index == len(digits):
            result.append("".join(path))
            return
        for char in mapping[digits[index]]:
            path.append(char)
            backtrack(index + 1, path)
            path.pop()

    backtrack(0, [])
    return result
```

---

### Problem 11. 51. N-Queens
**Archetype:** 9.4 N-Queens & Grid
**Type:** Core Drill
**Statement:** The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other. Return all distinct solutions.
**Why it fits:** The canonical grid-constraint backtracking problem. It teaches how to model complex constraints (columns, diagonals) with sets and how to prune the search space aggressively.
**The Twist:** None — the standard template. The key insight is representing diagonals as `r - c` and `r + c` to detect conflicts in O(1) time.
**Code Skeleton:**
```python
from typing import List

def solveNQueens(n: int) -> List[List[str]]:
    result = []
    cols = set()
    diag1 = set()  # r - c
    diag2 = set()  # r + c
    board = []

    def backtrack(r):
        if r == n:
            result.append(["." * c + "Q" + "." * (n - c - 1) for c in board])
            return
        for c in range(n):
            if c in cols or (r - c) in diag1 or (r + c) in diag2:
                continue
            cols.add(c)
            diag1.add(r - c)
            diag2.add(r + c)
            board.append(c)
            backtrack(r + 1)
            board.pop()
            cols.remove(c)
            diag1.remove(r - c)
            diag2.remove(r + c)

    backtrack(0)
    return result
```

---

### Problem 12. 79. Word Search
**Archetype:** 9.4 N-Queens & Grid / 9.6 Word Break/Dictionary
**Type:** Core Drill
**Statement:** Given an m x n grid of characters board and a string word, return true if word exists in the grid.
**Why it fits:** The canonical grid backtracking problem. It requires exploring all paths from each cell while marking cells as visited to prevent reuse. It is the foundation for all grid-dictionary problems.
**The Twist:** None — the standard template. Early termination when the current character does not match is crucial for passing large test cases.
**Code Skeleton:**
```python
from typing import List

def exist(board: List[List[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])

    def backtrack(r, c, index):
        if index == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[index]:
            return False
        temp = board[r][c]
        board[r][c] = "#"  # Mark as visited
        found = (backtrack(r + 1, c, index + 1) or
                 backtrack(r - 1, c, index + 1) or
                 backtrack(r, c + 1, index + 1) or
                 backtrack(r, c - 1, index + 1))
        board[r][c] = temp  # Unmark
        return found

    for r in range(rows):
        for c in range(cols):
            if backtrack(r, c, 0):
                return True
    return False
```

---

### Problem 13. 131. Palindrome Partitioning
**Archetype:** 9.1 Subsets / 9.5 String/Expression Building
**Type:** Core Drill
**Statement:** Given a string s, partition s such that every substring of the partition is a palindrome. Return all possible palindrome partitioning of s.
**Why it fits:** A beautiful blend of subset generation (where to cut) and string validation (is palindrome). It teaches that backtracking decisions can be "where to place the next separator" rather than "which element to pick."
**The Twist:** The branching factor is not fixed by an input array but by the possible cut positions from the current index. Each cut creates a new substring that must pass a validation check.
**Code Skeleton:**
```python
from typing import List

def partition(s: str) -> List[List[str]]:
    result = []

    def is_pal(left, right):
        while left < right:
            if s[left] != s[right]:
                return False
            left += 1
            right -= 1
        return True

    def backtrack(start, path):
        if start == len(s):
            result.append(path[:])
            return
        for end in range(start, len(s)):
            if is_pal(start, end):
                path.append(s[start:end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return result
```

---

### Problem 14. 93. Restore IP Addresses
**Archetype:** 9.5 String/Expression Building
**Type:** Core Drill
**Statement:** A valid IP address consists of exactly four integers separated by single dots. Given a string s containing only digits, return all possible valid IP addresses that can be formed by inserting dots into s.
**Why it fits:** A constrained string-building problem where exactly 3 dots must be placed. It teaches pruning: segments must be <= 255, cannot have leading zeros unless they are "0", and the total length is fixed.
**The Twist:** The constraints are tight (exactly 4 parts, 3 dots). Aggressive pruning is possible: if the remaining digits cannot form the required number of parts, return early.
**Code Skeleton:**
```python
from typing import List

def restoreIpAddresses(s: str) -> List[str]:
    result = []

    def backtrack(start, parts, path):
        if parts == 4:
            if start == len(s):
                result.append(".".join(path))
            return
        # Pruning: not enough digits left for remaining parts
        if len(s) - start < (4 - parts) or len(s) - start > 3 * (4 - parts):
            return
        for length in range(1, 4):
            if start + length > len(s):
                break
            segment = s[start:start + length]
            if (segment[0] == "0" and len(segment) > 1) or int(segment) > 255:
                continue
            path.append(segment)
            backtrack(start + length, parts + 1, path)
            path.pop()

    backtrack(0, 0, [])
    return result
```

---

### Problem 15. 212. Word Search II
**Archetype:** 9.4 N-Queens & Grid / 9.6 Word Break/Dictionary
**Type:** Core Drill
**Statement:** Given an m x n board of characters and a list of strings words, return all words on the board.
**Why it fits:** The hardest standard grid backtracking problem. It requires searching for multiple words efficiently. A Trie (prefix tree) is used to batch-process words and enable early termination when a prefix does not match.
**The Twist:** A naive backtrack per word is too slow. Building a Trie of all words allows you to explore the board once and find all matching words simultaneously. Pruning the Trie as words are found prevents duplicate work.
**Code Skeleton:**
```python
from typing import List

class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None  # Store complete word at terminal node

class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                node = node.children.setdefault(char, TrieNode())
            node.word = word

        rows, cols = len(board), len(board[0])
        result = []

        def backtrack(r, c, parent):
            char = board[r][c]
            curr = parent.children[char]
            if curr.word:
                result.append(curr.word)
                curr.word = None  # Prevent duplicates

            board[r][c] = "#"
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] in curr.children:
                    backtrack(nr, nc, curr)
            board[r][c] = char

            # Prune leaf nodes to speed up subsequent searches
            if not curr.children:
                parent.children.pop(char)

        for r in range(rows):
            for c in range(cols):
                if board[r][c] in root.children:
                    backtrack(r, c, root)
        return result
```

---
