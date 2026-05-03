# Pattern 03: Stack -- Drills Part 3

> **Focus:** Near Misses + Pattern Blends + Interview Simulation
> **Goal:** Build pattern-switching judgment and simulate real interview ambiguity.

---

## Near Misses (Looks like Pattern 03, but isn't)

### 16. 22. Generate Parentheses
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given n pairs of parentheses, generate all combinations of well-formed parentheses.
**Why it fits:** The output is valid parentheses, which strongly triggers the matching/validation archetype. A stack seems relevant for ensuring balance during generation.
**The Twist:** We are not validating a given string; we are generating all valid strings. This is a combinatorial backtracking problem where we track open and close counts, not a stack-based validation.
**Code Skeleton:**
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

### 17. 241. Different Ways to Add Parentheses
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given a string of numbers and operators, return all possible results from computing all different possible ways to group numbers and operators.
**Why it fits:** Parentheses in an expression suggest stack-based evaluation. The problem involves expression parsing and operator precedence, which feels like the expression-evaluation archetype.
**The Twist:** We are not evaluating a single expression; we are enumerating all parenthesizations. Divide and conquer: for each operator, split the expression into left and right subproblems and combine results.
**Code Skeleton:**
```python
def diff_ways_to_compute(expression):
    if expression.isdigit():
        return [int(expression)]
    result = []
    for i, char in enumerate(expression):
        if char in '+-*':
            left = diff_ways_to_compute(expression[:i])
            right = diff_ways_to_compute(expression[i+1:])
            for l in left:
                for r in right:
                    if char == '+':
                        result.append(l + r)
                    elif char == '-':
                        result.append(l - r)
                    else:
                        result.append(l * r)
    return result
```

### 18. 42. Trapping Rain Water
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given n non-negative integers representing an elevation map, compute how much water it can trap after raining.
**Why it fits:** Water is trapped between bars, which suggests a container/area problem. Two pointers from the ends could try to find the tallest boundaries, similar to the maximal rectangle or container problems.
**The Twist:** While a monotonic stack can solve this, the optimal solution uses two pointers tracking max heights from left and right. It is not a stack problem at its core.
**Code Skeleton:**
```python
def trap(height):
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
```

### 19. 200. Number of Islands
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given a 2D grid of '1's (land) and '0's (water), count the number of islands.
**Why it fits:** Islands are connected components. A stack can be used for DFS to explore each island iteratively, which feels like the DFS-simulation archetype.
**The Twist:** The stack is merely an implementation detail of iterative DFS. The problem is fundamentally about graph traversal (BFS/DFS/Union-Find). Recursion is often cleaner; the stack does not provide a special insight.
**Code Skeleton:**
```python
def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        stack = [(r, c)]
        while stack:
            i, j = stack.pop()
            if 0 <= i < rows and 0 <= j < cols and grid[i][j] == '1':
                grid[i][j] = '0'
                stack.extend([(i+1,j), (i-1,j), (i,j+1), (i,j-1)])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                count += 1
                dfs(r, c)
    return count
```

### 20. 10. Regular Expression Matching
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an input string and a pattern, implement regular expression matching with support for '.' and '*'.
**Why it fits:** String processing with special characters strongly suggests a stack for handling the Kleene star and backtracking. The pattern is processed left-to-right against the string.
**The Twist:** The problem is fundamentally about recursive state transitions with memoization (DP). A stack does not naturally handle the look-ahead required for '*' matching zero or more of the preceding element.
**Code Skeleton:**
```python
def is_match(s, p):
    memo = {}

    def dp(i, j):
        if (i, j) in memo:
            return memo[(i, j)]
        if j == len(p):
            return i == len(s)
        first_match = i < len(s) and p[j] in {s[i], '.'}
        if j + 1 < len(p) and p[j + 1] == '*':
            ans = dp(i, j + 2) or (first_match and dp(i + 1, j))
        else:
            ans = first_match and dp(i + 1, j + 1)
        memo[(i, j)] = ans
        return ans

    return dp(0, 0)
```

## Pattern Blends (Pattern 03 + Another Pattern)

### 21. 85. Maximal Rectangle
**Archetype:** 3.2 + DP
**Type:** Pattern Blend
**Statement:** Given a rows x cols binary matrix filled with 0's and 1's, find the largest rectangle containing only 1's.
**Why it fits:** For each row, we compute histogram heights of consecutive 1s ending at that row. Then we apply the monotonic stack to find the largest rectangle in the histogram.
**The Twist:** The stack solves the 1D subproblem (largest rectangle in histogram), but we must iterate over all rows and update heights. This is a classic stack-plus-DP blend.
**Code Skeleton:**
```python
def maximal_rectangle(matrix):
    if not matrix or not matrix[0]:
        return 0
    cols = len(matrix[0])
    heights = [0] * (cols + 1)
    max_area = 0
    for row in matrix:
        for i in range(cols):
            heights[i] = heights[i] + 1 if row[i] == '1' else 0
        stack = [-1]
        for i in range(cols + 1):
            while heights[i] < heights[stack[-1]]:
                h = heights[stack.pop()]
                w = i - stack[-1] - 1
                max_area = max(max_area, h * w)
            stack.append(i)
    return max_area
```

### 22. 316. Remove Duplicate Letters
**Archetype:** 3.2 + Greedy
**Type:** Pattern Blend
**Statement:** Given a string, remove duplicate letters so that every letter appears once and only once, and return the result in the smallest lexicographical order.
**Why it fits:** We want to build the result greedily. A monotonic increasing stack ensures the result is lexicographically smallest, but we must not discard a character entirely if it won't appear again.
**The Twist:** We combine a monotonic stack with a frequency map and a "seen" set. Before popping a smaller character, we check if it occurs later in the string. This is greedy plus monotonic stack.
**Code Skeleton:**
```python
from collections import Counter

def remove_duplicate_letters(s):
    count = Counter(s)
    stack = []
    seen = set()
    for char in s:
        count[char] -= 1
        if char in seen:
            continue
        while stack and char < stack[-1] and count[stack[-1]] > 0:
            seen.remove(stack.pop())
        stack.append(char)
        seen.add(char)
    return ''.join(stack)
```

### 23. 456. 132 Pattern
**Archetype:** 3.2 + Math
**Type:** Pattern Blend
**Statement:** Given an array of n integers, find if there is a 132 pattern: a subsequence a[i], a[j], a[k] such that i < j < k and a[i] < a[k] < a[j].
**Why it fits:** We need to find a middle element a[j] that has a smaller element before it and a slightly larger element after it. A monotonic stack helps find candidate "2" values (a[k]) from the right.
**The Twist:** We scan from the right while maintaining a stack of potential "2" values. We track the maximum valid "2" seen so far. If any element is smaller than this max, we have a 132 pattern.
**Code Skeleton:**
```python
def find132pattern(nums):
    stack = []
    second = float('-inf')
    for n in reversed(nums):
        if n < second:
            return True
        while stack and n > stack[-1]:
            second = stack.pop()
        stack.append(n)
    return False
```

### 24. 282. Expression Add Operators
**Archetype:** 3.3 + Backtracking
**Type:** Pattern Blend
**Statement:** Given a string of digits and a target, add binary operators to the expression so it evaluates to target.
**Why it fits:** We are evaluating expressions, but we must also decide where to insert operators. The expression-evaluation pattern is a subcomponent of the larger search.
**The Twist:** Backtracking generates all possible expression trees. During evaluation, we must handle operator precedence implicitly by tracking the last term for multiplication (to avoid re-evaluating from scratch).
**Code Skeleton:**
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
            curr_str = num[index:i + 1]
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

### 25. 388. Longest Absolute File Path
**Archetype:** 3.4 + String Processing
**Type:** Pattern Blend
**Statement:** Given a string representing a file system with tabs indicating depth, return the length of the longest absolute path to a file.
**Why it fits:** Tabs represent nesting depth. A stack tracks the cumulative path length at each depth level. When we encounter a file, we compute the total path length.
**The Twist:** The input is a single string with newline separators. We parse each line to determine its depth (number of tabs) and name. The stack simulates the directory hierarchy.
**Code Skeleton:**
```python
def length_longest_path(input_str):
    max_len = 0
    path_len = {0: 0}
    for line in input_str.split('\n'):
        name = line.lstrip('\t')
        depth = len(line) - len(name)
        if '.' in name:
            max_len = max(max_len, path_len[depth] + len(name))
        else:
            path_len[depth + 1] = path_len[depth] + len(name) + 1
    return max_len
```

## Interview Simulation (No archetype label given)

### 26. 735. Asteroid Collision
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an array of integers representing asteroids moving in a line, return the state after all collisions.
**Why it fits:** Asteroids move left or right. A right-moving asteroid can only collide with a left-moving asteroid to its right. The stack tracks surviving asteroids moving right.
**The Twist:** Collisions are not always mutual annihilation. The larger asteroid survives. Equal sizes annihilate. A left-moving asteroid at the start never collides. The stack resolves collisions in LIFO order.
**Code Skeleton:**
```python
def asteroid_collision(asteroids):
    stack = []
    for a in asteroids:
        while stack and a < 0 < stack[-1]:
            if stack[-1] < -a:
                stack.pop()
                continue
            elif stack[-1] == -a:
                stack.pop()
            break
        else:
            stack.append(a)
    return stack
```

### 27. 402. Remove K Digits
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given a non-negative integer represented as a string, remove k digits so that the new number is the smallest possible.
**Why it fits:** We want the smallest lexicographical number. A monotonic increasing stack ensures digits are in non-decreasing order. When we see a smaller digit, we pop larger previous digits if we still have removals left.
**The Twist:** Leading zeros must be stripped. If k remains after the scan, we truncate from the end. The stack directly encodes the greedy choice of removing locally maximal digits.
**Code Skeleton:**
```python
def remove_kdigits(num, k):
    stack = []
    for digit in num:
        while k > 0 and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    while k > 0:
        stack.pop()
        k -= 1
    result = ''.join(stack).lstrip('0')
    return result or '0'
```

### 28. 84. Largest Rectangle in Histogram
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an array of bar heights, find the largest rectangle in the histogram.
**Why it fits:** For each bar, the maximal rectangle height is the bar itself; the width extends until a shorter bar is met. We need the nearest smaller bar on both sides.
**The Twist:** A monotonic increasing stack tracks indices of bars in ascending order. When a shorter bar arrives, it triggers resolution of previous taller bars, computing their maximal width.
**Code Skeleton:**
```python
def largest_rectangle_area(heights):
    stack = []
    max_area = 0
    heights.append(0)  # sentinel
    for i, h in enumerate(heights):
        while stack and h < heights[stack[-1]]:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

### 29. 901. Online Stock Span
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Design an algorithm that collects daily price quotes and returns the span of the stock's price for the current day.
**Why it fits:** The span is the number of consecutive days before today with price <= today's price. We need to find the previous greater element, which is the monotonic stack pattern.
**The Twist:** Unlike the static Next Greater Element, this is an online problem. We store (price, span) pairs on the stack. When a new price arrives, we pop all smaller prices and accumulate their spans.
**Code Skeleton:**
```python
class StockSpanner:
    def __init__(self):
        self.stack = []  # (price, span)

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span
```

### 30. 895. Maximum Frequency Stack
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Design a stack-like data structure that pushes elements and pops the most frequent element. Ties are broken by most recent.
**Why it fits:** We need to track frequencies and the order of insertion for each frequency level. A stack of stacks lets us pop from the highest frequency group in LIFO order.
**The Twist:** We maintain a frequency map and a map from frequency to a stack of elements. When pushing, we increment frequency and push onto the corresponding group stack. When popping, we pop from the max frequency group.
**Code Skeleton:**
```python
from collections import defaultdict

class FreqStack:
    def __init__(self):
        self.freq = defaultdict(int)
        self.group = defaultdict(list)
        self.max_freq = 0

    def push(self, val):
        self.freq[val] += 1
        f = self.freq[val]
        self.max_freq = max(self.max_freq, f)
        self.group[f].append(val)

    def pop(self):
        val = self.group[self.max_freq].pop()
        self.freq[val] -= 1
        if not self.group[self.max_freq]:
            self.max_freq -= 1
        return val
```
