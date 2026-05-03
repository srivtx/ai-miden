# Pattern 09: Backtracking — Complete Archetype Map

> **Pattern Recognition:** When you see "all possible", "find all", "combinations", "permutations", "subsets", "generate", "partition", "solve" — think backtracking.
>
> **Fundamental Insight:** Backtracking is DFS on a state space tree. We build candidates incrementally, and abandon a candidate ("backtrack") as soon as we determine it cannot lead to a valid solution. The key is defining the STATE (what decision we're making) and the CONSTRAINTS (when to prune).

---

## Archetype 9.1: Subsets

### Recognition Signal (10 seconds)
Words: **"subsets", "power set", "all subsets", "subsequences", "include/exclude"**

The question: **"Generate all possible subsets of a collection."**

### Core Structure
```python
def subsets(nums):
    result = []
    
    def backtrack(start, current):
        result.append(list(current))
        
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()  # Backtrack
    
    backtrack(0, [])
    return result
```

### The Invariant
At each recursive call, `current` represents a valid partial subset containing elements from `nums[0...start-1]`. We either include `nums[i]` and recurse, or skip it. The base case is implicitly when we've considered all elements (loop completes).

### Canonical Problem: Subsets (LeetCode 78)
**Statement:** Given integer array nums of unique elements, return all possible subsets.

```python
def subsets(nums):
    result = []
    
    def backtrack(start, current):
        result.append(list(current))
        
        for i in range(start, len(nums)):
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()
    
    backtrack(0, [])
    return result
```

### Variation Family

**V1: Subsets II (LeetCode 90)**
- **Twist:** Array may contain duplicates, subsets must not contain duplicates
- **Change:** Sort first. Skip duplicates: `if i > start and nums[i] == nums[i-1]: continue`

```python
def subsets_with_dup(nums):
    result = []
    nums.sort()
    
    def backtrack(start, current):
        result.append(list(current))
        
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            current.append(nums[i])
            backtrack(i + 1, current)
            current.pop()
    
    backtrack(0, [])
    return result
```

**V2: Partition to K Equal Sum Subsets (LeetCode 698)**
- **Twist:** Partition array into k subsets with equal sum
- **Change:** Track current subset sum, target sum. Try adding each unused element to current subset

```python
def can_partition_k_subsets(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False
    target = total // k
    nums.sort(reverse=True)
    used = [False] * len(nums)
    
    def backtrack(start, k, current_sum):
        if k == 0:
            return True
        if current_sum == target:
            return backtrack(0, k - 1, 0)
        
        for i in range(start, len(nums)):
            if used[i] or current_sum + nums[i] > target:
                continue
            if i > start and not used[i - 1] and nums[i] == nums[i - 1]:
                continue
            
            used[i] = True
            if backtrack(i + 1, k, current_sum + nums[i]):
                return True
            used[i] = False
        
        return False
    
    return backtrack(0, k, 0)
```

**V3: Increasing Subsequences (LeetCode 491)**
- **Twist:** Find all increasing subsequences of length >= 2
- **Change:** Use set to track duplicates at each level, enforce increasing order

```python
def find_subsequences(nums):
    result = []
    
    def backtrack(start, current):
        if len(current) >= 2:
            result.append(list(current))
        
        used = set()
        for i in range(start, len(nums)):
            if nums[i] in used:
                continue
            if not current or nums[i] >= current[-1]:
                used.add(nums[i])
                current.append(nums[i])
                backtrack(i + 1, current)
                current.pop()
    
    backtrack(0, [])
    return result
```

**Near Miss: Maximum Subarray Sum**
- **Looks like:** Subsets
- **But:** Kadane's algorithm DP, not backtracking. Looking for ONE optimal subarray
- **Lesson:** "Subarray" (contiguous) often means DP/sliding window, "subset" (any combination) often means backtracking

---

## Archetype 9.2: Permutations

### Recognition Signal (10 seconds)
Words: **"permutations", "all arrangements", "order matters", "rearrange"**

The question: **"Generate all possible orderings of a collection."**

### Core Structure
```python
def permutations(nums):
    result = []
    
    def backtrack(current, used):
        if len(current) == len(nums):
            result.append(list(current))
            return
        
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            current.append(nums[i])
            backtrack(current, used)
            current.pop()
            used[i] = False
    
    backtrack([], [False] * len(nums))
    return result
```

### The Invariant
`current` contains a partial permutation of length `len(current)`. `used[i]` tracks which elements are already in `current`. When `len(current) == len(nums)`, we have a complete permutation.

### Canonical Problem: Permutations (LeetCode 46)
**Statement:** Given array of distinct integers, return all possible permutations.

```python
def permute(nums):
    result = []
    
    def backtrack(current, used):
        if len(current) == len(nums):
            result.append(list(current))
            return
        
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            current.append(nums[i])
            backtrack(current, used)
            current.pop()
            used[i] = False
    
    backtrack([], [False] * len(nums))
    return result
```

### Variation Family

**V1: Permutations II (LeetCode 47)**
- **Twist:** Array may contain duplicates
- **Change:** Sort first. Skip if `used[i-1]` is False (same level duplicate) and `nums[i] == nums[i-1]`

```python
def permute_unique(nums):
    result = []
    nums.sort()
    used = [False] * len(nums)
    
    def backtrack(current):
        if len(current) == len(nums):
            result.append(list(current))
            return
        
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            
            used[i] = True
            current.append(nums[i])
            backtrack(current)
            current.pop()
            used[i] = False
    
    backtrack([])
    return result
```

**V2: Next Permutation (LeetCode 31)**
- **Twist:** Modify array to next lexicographical permutation in-place
- **Change:** Find first decreasing element from right. Swap with next larger element to its right. Reverse suffix

```python
def next_permutation(nums):
    # Find first decreasing from right
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    
    if i >= 0:
        # Find next larger to the right
        j = len(nums) - 1
        while j >= 0 and nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    
    # Reverse suffix
    left, right = i + 1, len(nums) - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
```

**V3: Palindrome Permutation II (LeetCode 267)**
- **Twist:** Generate all palindromic permutations of a string
- **Change:** Count characters. If more than one odd count, no palindrome. Place half characters, mirror

```python
from collections import Counter

def generate_palindromes(s):
    count = Counter(s)
    odds = [c for c, v in count.items() if v % 2 == 1]
    
    if len(odds) > 1:
        return []
    
    mid = odds[0] if odds else ''
    half = []
    for c, v in count.items():
        half.extend([c] * (v // 2))
    
    result = []
    used = [False] * len(half)
    
    def backtrack(current):
        if len(current) == len(half):
            result.append(''.join(current) + mid + ''.join(reversed(current)))
            return
        
        for i in range(len(half)):
            if used[i]:
                continue
            if i > 0 and half[i] == half[i - 1] and not used[i - 1]:
                continue
            
            used[i] = True
            current.append(half[i])
            backtrack(current)
            current.pop()
            used[i] = False
    
    backtrack([])
    return result
```

**Near Miss: Permutation in String**
- **Looks like:** Permutations
- **But:** Check if s2 contains any permutation of s1. Fixed window + character count
- **Lesson:** "Contains a permutation" != "generate all permutations"

---

## Archetype 9.3: Combinations

### Recognition Signal (10 seconds)
Words: **"combinations", "choose k", "n choose k", "combination sum"**

The question: **"Select K elements from N that satisfy some condition."**

### Core Structure
```python
def combinations(n, k):
    result = []
    
    def backtrack(start, current):
        if len(current) == k:
            result.append(list(current))
            return
        
        for i in range(start, n + 1):
            current.append(i)
            backtrack(i + 1, current)
            current.pop()
    
    backtrack(1, [])
    return result
```

### The Invariant
`current` is a partial combination of size `len(current)`. We choose elements in increasing order to avoid duplicates. When `len(current) == k`, we have a valid combination.

### Canonical Problem: Combinations (LeetCode 77)
**Statement:** Given n and k, return all possible combinations of k numbers chosen from 1 to n.

```python
def combine(n, k):
    result = []
    
    def backtrack(start, current):
        if len(current) == k:
            result.append(list(current))
            return
        
        for i in range(start, n + 1):
            current.append(i)
            backtrack(i + 1, current)
            current.pop()
    
    backtrack(1, [])
    return result
```

### Variation Family

**V1: Combination Sum (LeetCode 39)**
- **Twist:** Find all unique combinations that sum to target, can reuse elements
- **Change:** Allow `i` (not `i+1`) in recursive call. Sort and prune if `current_sum > target`

```python
def combination_sum(candidates, target):
    result = []
    candidates.sort()
    
    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(list(current))
            return
        
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break
            current.append(candidates[i])
            backtrack(i, current, remaining - candidates[i])  # Reuse allowed
            current.pop()
    
    backtrack(0, [], target)
    return result
```

**V2: Combination Sum II (LeetCode 40)**
- **Twist:** Each number used at most once, array may have duplicates
- **Change:** Sort. Skip duplicates. Use `i + 1` in recursion (no reuse)

```python
def combination_sum2(candidates, target):
    result = []
    candidates.sort()
    
    def backtrack(start, current, remaining):
        if remaining == 0:
            result.append(list(current))
            return
        
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            if candidates[i] > remaining:
                break
            current.append(candidates[i])
            backtrack(i + 1, current, remaining - candidates[i])
            current.pop()
    
    backtrack(0, [], target)
    return result
```

**V3: Combination Sum III (LeetCode 216)**
- **Twist:** Find k numbers that sum to n, using only 1-9, each once
- **Change:** Backtrack with start (1-9), track count and sum

```python
def combination_sum3(k, n):
    result = []
    
    def backtrack(start, current, count, total):
        if count == k and total == n:
            result.append(list(current))
            return
        if count >= k or total >= n:
            return
        
        for i in range(start, 10):
            current.append(i)
            backtrack(i + 1, current, count + 1, total + i)
            current.pop()
    
    backtrack(1, [], 0, 0)
    return result
```

**V4: Letter Combinations of a Phone Number (LeetCode 17)**
- **Twist:** Generate all letter combinations from phone digits
- **Change:** Map digits to letters. Backtrack through each digit's possible letters

```python
def letter_combinations(digits):
    if not digits:
        return []
    
    phone = {
        '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
        '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz'
    }
    
    result = []
    
    def backtrack(index, current):
        if index == len(digits):
            result.append(''.join(current))
            return
        
        for char in phone[digits[index]]:
            current.append(char)
            backtrack(index + 1, current)
            current.pop()
    
    backtrack(0, [])
    return result
```

**Near Miss: Coin Change**
- **Looks like:** Combination sum
- **But:** Find MINIMUM coins to make amount. Pure DP, not backtracking
- **Lesson:** "All combinations" = backtracking, "minimum/maximum" = DP

---

## Archetype 9.4: N-Queens & Grid Placement

### Recognition Signal (10 seconds)
Words: **"N-Queens", "Sudoku", "place", "grid", "board", "attack", "valid placement"**

The question: **"Place items on a grid so that no two conflict according to rules."**

### Core Structure
```python
def solve_n_queens(n):
    board = [['.' for _ in range(n)] for _ in range(n)]
    result = []
    
    def is_valid(row, col):
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        # Check diagonals
        for i, j in zip(range(row - 1, -1, -1), range(col - 1, -1, -1)):
            if board[i][j] == 'Q':
                return False
        for i, j in zip(range(row - 1, -1, -1), range(col + 1, n)):
            if board[i][j] == 'Q':
                return False
        return True
    
    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return
        
        for col in range(n):
            if is_valid(row, col):
                board[row][col] = 'Q'
                backtrack(row + 1)
                board[row][col] = '.'
    
    backtrack(0)
    return result
```

### The Invariant
Each row has exactly one queen. We place queens row by row. `is_valid` ensures no two queens share a column or diagonal. When `row == n`, all queens are placed validly.

### Canonical Problem: N-Queens (LeetCode 51)
**Statement:** Place n queens on n x n chessboard so no two attack each other. Return all distinct solutions.

```python
def solve_n_queens(n):
    board = [['.' for _ in range(n)] for _ in range(n)]
    result = []
    
    def is_valid(row, col):
        for i in range(row):
            if board[i][col] == 'Q':
                return False
        for i, j in zip(range(row - 1, -1, -1), range(col - 1, -1, -1)):
            if board[i][j] == 'Q':
                return False
        for i, j in zip(range(row - 1, -1, -1), range(col + 1, n)):
            if board[i][j] == 'Q':
                return False
        return True
    
    def backtrack(row):
        if row == n:
            result.append([''.join(r) for r in board])
            return
        for col in range(n):
            if is_valid(row, col):
                board[row][col] = 'Q'
                backtrack(row + 1)
                board[row][col] = '.'
    
    backtrack(0)
    return result
```

### Variation Family

**V1: N-Queens II (LeetCode 52)**
- **Twist:** Return count of distinct solutions, not the boards
- **Change:** Same as N-Queens but increment counter instead of storing boards

**V2: Sudoku Solver (LeetCode 37)**
- **Twist:** Fill empty cells in Sudoku board
- **Change:** Find empty cell. Try digits 1-9. Check row, column, 3x3 box validity

```python
def solve_sudoku(board):
    def is_valid(row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        return True
    
    def backtrack():
        for i in range(9):
            for j in range(9):
                if board[i][j] == '.':
                    for num in '123456789':
                        if is_valid(i, j, num):
                            board[i][j] = num
                            if backtrack():
                                return True
                            board[i][j] = '.'
                    return False
        return True
    
    backtrack()
```

**V3: Word Search (LeetCode 79)**
- **Twist:** Find if word exists in grid, adjacent cells
- **Change:** DFS from each cell. Mark visited. Backtrack if path fails

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    
    def backtrack(r, c, index):
        if index == len(word):
            return True
        if (r < 0 or r >= rows or c < 0 or c >= cols or
            board[r][c] != word[index]):
            return False
        
        temp = board[r][c]
        board[r][c] = '#'  # Mark visited
        
        found = (backtrack(r + 1, c, index + 1) or
                 backtrack(r - 1, c, index + 1) or
                 backtrack(r, c + 1, index + 1) or
                 backtrack(r, c - 1, index + 1))
        
        board[r][c] = temp  # Unmark
        return found
    
    for i in range(rows):
        for j in range(cols):
            if backtrack(i, j, 0):
                return True
    return False
```

**V4: Rat in a Maze (GeeksforGeeks classic)**
- **Twist:** Find path from start to end in maze
- **Change:** DFS with direction checking. Mark visited. Backtrack on dead ends

**Near Miss: Unique Paths**
- **Looks like:** Grid placement
- **But:** Count paths from top-left to bottom-right. Pure combinatorics/DP
- **Lesson:** If only COUNT is needed (not enumerate), use DP or math

---

## Archetype 9.5: String / Expression Building

### Recognition Signal (10 seconds)
Words: **"generate parentheses", "add operators", "restore IP", "decode ways"**

The question: **"Build a valid string or expression by making choices at each position."**

### Core Structure
```python
def build_expression(s, target):
    result = []
    
    def backtrack(index, current, value, last):
        if index == len(s):
            if value == target:
                result.append(current)
            return
        
        for i in range(index, len(s)):
            if i > index and s[index] == '0':
                break
            num = int(s[index:i+1])
            
            if index == 0:
                backtrack(i + 1, str(num), num, num)
            else:
                backtrack(i + 1, current + '+' + str(num), value + num, num)
                backtrack(i + 1, current + '-' + str(num), value - num, -num)
                backtrack(i + 1, current + '*' + str(num), value - last + last * num, last * num)
    
    backtrack(0, '', 0, 0)
    return result
```

### The Invariant
`current` is the partially built expression string. `value` is the evaluated value so far. `last` tracks the last operand for correct multiplication handling (order of operations). At each step, we choose where to split the remaining string and which operator to insert.

### Canonical Problem: Generate Parentheses (LeetCode 22)
**Statement:** Given n pairs of parentheses, generate all well-formed combinations.

```python
def generate_parenthesis(n):
    result = []
    
    def backtrack(current, open_count, close_count):
        if len(current) == 2 * n:
            result.append(current)
            return
        
        if open_count < n:
            backtrack(current + '(', open_count + 1, close_count)
        if close_count < open_count:
            backtrack(current + ')', open_count, close_count + 1)
    
    backtrack('', 0, 0)
    return result
```

### Variation Family

**V1: Expression Add Operators (LeetCode 282)**
- **Twist:** Add operators to string so expression evaluates to target
- **Change:** Try all split points and operators. Track value and last operand for multiplication

```python
def add_operators(num, target):
    result = []
    
    def backtrack(index, path, value, last):
        if index == len(num):
            if value == target:
                result.append(path)
            return
        
        for i in range(index, len(num)):
            if i > index and num[index] == '0':
                break
            curr_str = num[index:i+1]
            curr = int(curr_str)
            
            if index == 0:
                backtrack(i + 1, curr_str, curr, curr)
            else:
                backtrack(i + 1, path + '+' + curr_str, value + curr, curr)
                backtrack(i + 1, path + '-' + curr_str, value - curr, -curr)
                backtrack(i + 1, path + '*' + curr_str, value - last + last * curr, last * curr)
    
    backtrack(0, '', 0, 0)
    return result
```

**V2: Restore IP Addresses (LeetCode 93)**
- **Twist:** Return all valid IP address combinations from string
- **Change:** Place 3 dots to create 4 segments. Each segment must be 0-255 and no leading zeros

```python
def restore_ip_addresses(s):
    result = []
    
    def backtrack(start, dots, current):
        if dots == 4 and start == len(s):
            result.append(current[:-1])  # Remove last dot
            return
        if dots > 4:
            return
        
        for i in range(start, min(start + 3, len(s))):
            segment = s[start:i+1]
            if int(segment) > 255 or (len(segment) > 1 and segment[0] == '0'):
                continue
            backtrack(i + 1, dots + 1, current + segment + '.')
    
    backtrack(0, 0, '')
    return result
```

**V3: Different Ways to Add Parentheses (LeetCode 241)**
- **Twist:** Compute all possible results from different parenthesizations
- **Change:** Divide and conquer. For each operator, recursively solve left and right, combine

```python
def diff_ways_to_compute(expression):
    def compute(left, right, op):
        results = []
        for l in left:
            for r in right:
                if op == '+':
                    results.append(l + r)
                elif op == '-':
                    results.append(l - r)
                elif op == '*':
                    results.append(l * r)
        return results
    
    # If pure number
    if expression.isdigit():
        return [int(expression)]
    
    results = []
    for i, char in enumerate(expression):
        if char in '+-*':
            left = diff_ways_to_compute(expression[:i])
            right = diff_ways_to_compute(expression[i+1:])
            results.extend(compute(left, right, char))
    
    return results
```

**Near Miss: Decode Ways**
- **Looks like:** String building
- **But:** Count ways to decode, not enumerate them. DP, not backtracking
- **Lesson:** "Count" usually means DP; "find all" means backtracking

---

## Archetype 9.6: Word Break / Dictionary

### Recognition Signal (10 seconds)
Words: **"word break", "dictionary", "word search", "concatenated", "sentence"**

The question: **"Break a string into valid words from a dictionary."**

### Core Structure
```python
def word_break(s, word_dict):
    word_set = set(word_dict)
    result = []
    
    def backtrack(start, current):
        if start == len(s):
            result.append(' '.join(current))
            return
        
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                current.append(word)
                backtrack(end, current)
                current.pop()
    
    backtrack(0, [])
    return result
```

### The Invariant
We try all possible prefixes of the remaining string. If a prefix is in the dictionary, we add it to the current sentence and recursively process the remainder. When `start == len(s)`, we've formed a valid sentence.

### Canonical Problem: Word Break II (LeetCode 140)
**Statement:** Given string s and dictionary, add spaces to s to construct valid sentences.

```python
def word_break(s, word_dict):
    word_set = set(word_dict)
    result = []
    
    def backtrack(start, path):
        if start == len(s):
            result.append(' '.join(path))
            return
        
        for end in range(start + 1, len(s) + 1):
            word = s[start:end]
            if word in word_set:
                path.append(word)
                backtrack(end, path)
                path.pop()
    
    backtrack(0, [])
    return result
```

### Variation Family

**V1: Word Search II (LeetCode 212)**
- **Twist:** Find all words from dictionary in a 2D board
- **Change:** Build Trie from words. DFS from each cell, prune if prefix not in Trie

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

class Solution:
    def find_words(self, board, words):
        # Build trie
        root = TrieNode()
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = word
        
        result = []
        rows, cols = len(board), len(board[0])
        
        def backtrack(r, c, parent):
            char = board[r][c]
            node = parent.children[char]
            
            if node.word:
                result.append(node.word)
                node.word = None  # Avoid duplicates
            
            board[r][c] = '#'  # Mark visited
            for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < rows and 0 <= nc < cols and
                    board[nr][nc] in node.children):
                    backtrack(nr, nc, node)
            board[r][c] = char
            
            # Prune leaf nodes
            if not node.children:
                parent.children.pop(char)
        
        for i in range(rows):
            for j in range(cols):
                if board[i][j] in root.children:
                    backtrack(i, j, root)
        
        return result
```

**V2: Concatenated Words (LeetCode 472)**
- **Twist:** Find all words that can be formed by concatenating other words
- **Change:** Sort by length. For each word, check if it can be formed from shorter words using DP or backtracking

```python
def find_all_concatenated_words(words):
    word_set = set(words)
    result = []
    
    def can_form(word):
        if not word:
            return False
        # DP: dp[i] = can form word[:i]
        dp = [False] * (len(word) + 1)
        dp[0] = True
        
        for i in range(1, len(word) + 1):
            for j in range(i):
                if dp[j] and word[j:i] in word_set:
                    dp[i] = True
                    break
        return dp[len(word)]
    
    for word in sorted(words, key=len):
        word_set.remove(word)
        if can_form(word):
            result.append(word)
        word_set.add(word)
    
    return result
```

**V3: Word Pattern II (LeetCode 291)**
- **Twist:** Pattern matching between pattern string and actual string
- **Change:** Map pattern characters to substrings. Backtrack with consistency checks

**Near Miss: Word Break I**
- **Looks like:** Word break dictionary
- **But:** Only return boolean (can break). Pure DP
- **Lesson:** Word Break I (139) is DP. Word Break II (140) is backtracking. Same pattern, different output type

---

## Pattern 09 Mastery Checklist

Before moving to Pattern 10, confirm you can:

- [ ] Generate all subsets with include/exclude backtracking
- [ ] Handle duplicates in subsets (sort + skip)
- [ ] Generate all permutations with used array
- [ ] Handle duplicates in permutations (sort + skip same level)
- [ ] Generate combinations C(n, k)
- [ ] Solve combination sum with and without reuse
- [ ] Place N queens with row-by-row backtracking
- [ ] Solve Sudoku with cell-by-cell backtracking
- [ ] Search word in 2D grid with DFS + backtracking
- [ ] Generate valid parentheses with open/close count tracking
- [ ] Add operators to expression string with value/last tracking
- [ ] Restore IP addresses with segment validation
- [ ] Break string into dictionary words with prefix checking
- [ ] Use Trie + backtracking for Word Search II
- [ ] Distinguish: backtracking (enumerate all) vs DP (count/optimize)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Not backtracking (not undoing choice) | Wrong state leaks between branches | Always undo: `current.pop()`, `used[i] = False`, restore grid |
| Missing base case | Infinite recursion or no results | Explicitly check termination condition and add to results |
| Including duplicates in subsets | Duplicate results | Sort array; `if i > start and nums[i] == nums[i-1]: continue` |
| Wrong order in permutation dedup | Miss valid permutations or include duplicates | `if not used[i-1] and nums[i] == nums[i-1]: continue` |
| Not pruning early | TLE on large inputs | Add constraints: `if current_sum > target: return/break` |
| Modifying shared list without copying | All results point to same object | `result.append(list(current))` not `result.append(current)` |
| Leading zeros in number strings | Invalid expressions like "05" | `if s[index] == '0' and i > index: break` |
| Confusing backtracking with pure recursion | Backtracking requires undoing choice | Backtracking = DFS + state restoration |

---

## Pattern Blends (What Comes Next)

Backtracking does not live in isolation. It blends with:

- **DFS:** Backtracking IS DFS on a state space tree
- **Trie:** Word Search II uses Trie for efficient prefix pruning
- **DP/Memoization:** Some backtracking problems can be memoized (e.g., Word Break)
- **Greedy:** Sometimes greedy provides bounds to prune backtracking search
- **Bit Manipulation:** Subsets can be generated with bit masks (iterative approach)
- **Graph:** Grid problems are backtracking on implicit graphs

---

*Next: Pattern 10 — Tries*

(End of file)
