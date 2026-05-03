# Pattern 03: Stack -- Drills Part 2

> **Focus:** Warm-ups and Core Drills
> **Goal:** Solidify recognition of Stack archetypes with progressive difficulty.

---

## Warm-ups

### 1. 20. Valid Parentheses
**Archetype:** 3.1 Matching/Validation
**Type:** Warm-Up
**Statement:** Given a string containing just '(', ')', '{', '}', '[' and ']', determine if the input string is valid.
**Why it fits:** Every opening bracket must be closed by the same type and in the correct order. A stack naturally tracks the most recent unmatched opening bracket.
**The Twist:** None--this is the canonical matching problem. We push openings and pop on closings, verifying the top matches the expected pair.
**Code Skeleton:**
```python
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in pairs.values():
            stack.append(char)
        else:
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return not stack
```

### 2. 739. Daily Temperatures
**Archetype:** 3.2 Monotonic Stack
**Type:** Warm-Up
**Statement:** Given a list of daily temperatures, return a list where each entry tells you how many days until a warmer temperature.
**Why it fits:** For each day, we need the next day with a higher temperature. A monotonic decreasing stack stores indices of days awaiting a warmer future day.
**The Twist:** None--this is the canonical monotonic stack problem. When a warmer day is found, it resolves all previous cooler days that were waiting.
**Code Skeleton:**
```python
def daily_temperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)
    return result
```

### 3. 150. Evaluate Reverse Polish Notation
**Archetype:** 3.3 Expression Evaluation
**Type:** Warm-Up
**Statement:** Evaluate the value of an arithmetic expression in Reverse Polish Notation.
**Why it fits:** RPN is inherently stack-based: operands are pushed, and operators pop the top two operands, compute, and push the result. This is exactly how a stack processes postfix expressions.
**The Twist:** None--this is the canonical expression evaluation problem. Division must truncate toward zero, requiring explicit integer conversion in Python.
**Code Skeleton:**
```python
def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if token in "+-*/":
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(token))
    return stack[0]
```

### 4. 155. Min Stack
**Archetype:** 3.4 History/Undo
**Type:** Warm-Up
**Statement:** Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.
**Why it fits:** We need historical context: the minimum changes as elements are pushed and popped. A secondary stack tracks the minimum at each layer of history.
**The Twist:** None--this is the canonical history/undo problem. The min-stack mirrors the main stack but only stores values that are smaller than or equal to the current minimum.
**Code Skeleton:**
```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val):
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self):
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self):
        return self.stack[-1]

    def getMin(self):
        return self.min_stack[-1]
```

### 5. 71. Simplify Path
**Archetype:** 3.6 String Processing
**Type:** Warm-Up
**Statement:** Given a string path for a Unix-style file system, simplify it to the canonical path.
**Why it fits:** The path is a sequence of commands separated by '/'. A stack naturally models directory navigation: push folder names and pop on '..'.
**The Twist:** None--this is the canonical string-processing stack problem. Empty components and single dots are ignored; double dots trigger a pop.
**Code Skeleton:**
```python
def simplify_path(path):
    stack = []
    for part in path.split('/'):
        if part == '..':
            if stack:
                stack.pop()
        elif part and part != '.':
            stack.append(part)
    return '/' + '/'.join(stack)
```

## Core Drills

### 6. 921. Minimum Add to Make Parentheses Valid
**Archetype:** 3.1 Matching/Validation
**Type:** Core Drill
**Statement:** Given a parentheses string, return the minimum number of parentheses needed to add to make it valid.
**Why it fits:** We track unmatched opening and closing parentheses. An opening increments the need for a future close; a close without a match increments the need for a past open.
**The Twist:** Instead of storing actual parentheses in the stack, we use counters. This is a space-optimized validation problem where we only care about the magnitude of imbalance.
**Code Skeleton:**
```python
def min_add_to_make_valid(s):
    open_needed = 0
    close_needed = 0
    for char in s:
        if char == '(':
            open_needed += 1
        else:
            if open_needed > 0:
                open_needed -= 1
            else:
                close_needed += 1
    return open_needed + close_needed
```

### 7. 1249. Minimum Remove to Make Valid Parentheses
**Archetype:** 3.1 Matching/Validation
**Type:** Core Drill
**Statement:** Given a string of '(' , ')' and lowercase English characters, remove the minimum number of parentheses to make it valid.
**Why it fits:** We use a stack to track indices of unmatched '('. When we see an unmatched ')', we mark it for removal. After the scan, remaining '(' in the stack are also removed.
**The Twist:** Unlike simple validation, we must preserve non-parenthesis characters. We collect indices to remove and build the result by skipping those indices.
**Code Skeleton:**
```python
def min_remove_to_make_valid(s):
    stack = []
    chars = list(s)
    for i, char in enumerate(chars):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if stack:
                stack.pop()
            else:
                chars[i] = ''  # mark for removal
    for i in stack:
        chars[i] = ''
    return ''.join(chars)
```

### 8. 496. Next Greater Element I
**Archetype:** 3.2 Monotonic Stack
**Type:** Core Drill
**Statement:** For each element in nums1 (subset of nums2), find the next greater element in nums2.
**Why it fits:** We process nums2 with a monotonic decreasing stack. For each element, we resolve pending elements that are smaller than it, recording their next greater.
**The Twist:** We need to answer queries for only a subset of elements (nums1). A hash map stores the precomputed next-greater answers for O(1) lookup per query.
**Code Skeleton:**
```python
def next_greater_element(nums1, nums2):
    next_greater = {}
    stack = []
    for n in nums2:
        while stack and n > stack[-1]:
            next_greater[stack.pop()] = n
        stack.append(n)
    return [next_greater.get(n, -1) for n in nums1]
```

### 9. 503. Next Greater Element II
**Archetype:** 3.2 Monotonic Stack
**Type:** Core Drill
**Statement:** Given a circular array, return the next greater number for every element.
**Why it fits:** The array is circular, so we process it twice (or iterate 2n times with modulo). The monotonic stack still resolves pending elements when a greater value is found.
**The Twist:** Circularity means the next greater element may appear before the current index in the original array. We simulate this by scanning the doubled array but only storing results for the first n indices.
**Code Skeleton:**
```python
def next_greater_elements(nums):
    n = len(nums)
    result = [-1] * n
    stack = []
    for i in range(2 * n):
        idx = i % n
        while stack and nums[idx] > nums[stack[-1]]:
            result[stack.pop()] = nums[idx]
        if i < n:
            stack.append(idx)
    return result
```

### 10. 224. Basic Calculator
**Archetype:** 3.3 Expression Evaluation
**Type:** Core Drill
**Statement:** Given a string expression containing non-negative integers, '+', '-', '(', ')', and spaces, evaluate it.
**Why it fits:** We evaluate as we scan, pushing the current result and sign onto the stack whenever we encounter '('. On ')', we pop and combine with the subexpression result.
**The Twist:** The stack stores both the accumulated result and the pending sign before a parenthesized group. This allows nested expressions to be resolved in LIFO order.
**Code Skeleton:**
```python
def calculate(s):
    stack = []
    num = 0
    sign = 1
    result = 0
    for char in s:
        if char.isdigit():
            num = num * 10 + int(char)
        elif char == '+':
            result += sign * num
            num = 0
            sign = 1
        elif char == '-':
            result += sign * num
            num = 0
            sign = -1
        elif char == '(':
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif char == ')':
            result += sign * num
            num = 0
            result *= stack.pop()  # sign
            result += stack.pop()  # previous result
    result += sign * num
    return result
```

### 11. 227. Basic Calculator II
**Archetype:** 3.3 Expression Evaluation
**Type:** Core Drill
**Statement:** Given a string expression containing non-negative integers, '+', '-', '*', '/', and spaces, evaluate it.
**Why it fits:** Multiplication and division have higher precedence. We push the result of the previous number and operator onto the stack, then sum the stack at the end.
**The Twist:** We delay addition/subtraction by pushing signed numbers onto the stack. When we see '*' or '/', we immediately apply it to the last stack element and the current number.
**Code Skeleton:**
```python
def calculate_ii(s):
    stack = []
    num = 0
    op = '+'
    for i, char in enumerate(s):
        if char.isdigit():
            num = num * 10 + int(char)
        if (not char.isdigit() and char != ' ') or i == len(s) - 1:
            if op == '+':
                stack.append(num)
            elif op == '-':
                stack.append(-num)
            elif op == '*':
                stack.append(stack.pop() * num)
            elif op == '/':
                stack.append(int(stack.pop() / num))
            op = char
            num = 0
    return sum(stack)
```

### 12. 394. Decode String
**Archetype:** 3.6 String Processing
**Type:** Core Drill
**Statement:** Given an encoded string, return its decoded form. Encoding rule: k[encoded_string], where k is positive integer.
**Why it fits:** Nested brackets must be resolved from the inside out. A stack stores the current string and repetition count before entering a new bracket layer.
**The Twist:** Numbers may have multiple digits. We accumulate digits until we hit '['. On ']', we pop the count and previous string, then expand the current segment.
**Code Skeleton:**
```python
def decode_string(s):
    stack = []
    current_string = ''
    current_num = 0
    for char in s:
        if char.isdigit():
            current_num = current_num * 10 + int(char)
        elif char == '[':
            stack.append((current_string, current_num))
            current_string = ''
            current_num = 0
        elif char == ']':
            prev_string, num = stack.pop()
            current_string = prev_string + num * current_string
        else:
            current_string += char
    return current_string
```

### 13. 726. Number of Atoms
**Archetype:** 3.6 String Processing
**Type:** Core Drill
**Statement:** Given a chemical formula, return the count of each atom in a sorted string representation.
**Why it fits:** The formula is nested with parentheses and multipliers. A stack of counters lets us resolve inner formulas, multiply them, and merge into the outer scope.
**The Twist:** Element names have an uppercase followed by optional lowercase. Multipliers may have multiple digits. We parse tokens carefully and use a stack of dictionaries.
**Code Skeleton:**
```python
from collections import Counter

def count_of_atoms(formula):
    stack = [Counter()]
    i = 0
    while i < len(formula):
        if formula[i] == '(':
            stack.append(Counter())
            i += 1
        elif formula[i] == ')':
            top = stack.pop()
            i += 1
            num = 0
            while i < len(formula) and formula[i].isdigit():
                num = num * 10 + int(formula[i])
                i += 1
            num = max(num, 1)
            for atom, count in top.items():
                stack[-1][atom] += count * num
        else:
            atom = formula[i]
            i += 1
            while i < len(formula) and formula[i].islower():
                atom += formula[i]
                i += 1
            num = 0
            while i < len(formula) and formula[i].isdigit():
                num = num * 10 + int(formula[i])
                i += 1
            num = max(num, 1)
            stack[-1][atom] += num
    result = []
    for atom in sorted(stack[0]):
        count = stack[0][atom]
        result.append(atom)
        if count > 1:
            result.append(str(count))
    return ''.join(result)
```

### 14. 331. Verify Preorder Serialization of a Binary Tree
**Archetype:** 3.5 DFS Simulation
**Type:** Core Drill
**Statement:** Given a preorder serialization of a binary tree where null nodes are '#', verify it is valid.
**Why it fits:** Each non-null node consumes one slot and provides two new slots (children). A stack tracks available slots. '#' consumes one slot.
**The Twist:** We do not reconstruct the tree. Instead, we simulate the slot consumption. If slots ever go negative, or if slots are not exactly zero at the end, the serialization is invalid.
**Code Skeleton:**
```python
def is_valid_serialization(preorder):
    slots = 1
    for node in preorder.split(','):
        if slots == 0:
            return False
        slots -= 1
        if node != '#':
            slots += 2
    return slots == 0
```

### 15. 636. Exclusive Time of Functions
**Archetype:** 3.4 History/Undo
**Type:** Core Drill
**Statement:** Given logs of function starts and ends, return the exclusive time of each function.
**Why it fits:** Functions are nested in a LIFO manner. A stack tracks which function is currently executing. When a function ends, we pop it and credit its duration.
**The Twist:** Logs are not strictly nested by function ID (the same function may be re-entered). We use the stack to track execution context, and we handle the "resume" of the previous function by subtracting the elapsed time from the gap.
**Code Skeleton:**
```python
def exclusive_time(n, logs):
    result = [0] * n
    stack = []
    prev_time = 0
    for log in logs:
        fid, typ, timestamp = log.split(':')
        fid, timestamp = int(fid), int(timestamp)
        if typ == 'start':
            if stack:
                result[stack[-1]] += timestamp - prev_time
            stack.append(fid)
            prev_time = timestamp
        else:
            result[stack.pop()] += timestamp - prev_time + 1
            prev_time = timestamp + 1
    return result
```
