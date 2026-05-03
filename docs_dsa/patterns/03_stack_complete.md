# Pattern 03: Stack — Complete Archetype Map

> **Pattern Recognition:** When you see "valid parentheses", "next greater", "history", "undo", "reverse order", "nested" — think stack.
>
> **Fundamental Insight:** Stack = LIFO (Last In, First Out). Whatever was most recently added is the first to be removed. This models: nesting, history, undo, and "process the most recent first."

---

## Archetype 3.1: Matching & Validation (Balanced Structures)

### Recognition Signal (10 seconds)
Words: **"valid", "balanced", "parentheses", "brackets", "matching", "nested", "well-formed"**

The question is always: **"Does every opening symbol have a corresponding closing symbol in the correct order?"**

### Core Structure
```
stack = []
for char in string:
    if char is opening:
        stack.push(char)
    elif char is closing:
        if stack is empty or stack.top() doesn't match:
            return False
        stack.pop()
return stack is empty
```

### The Invariant
The stack always contains the unmatched opening symbols in the order they were encountered. The most recent opening must be closed first.

### Canonical Problem: Valid Parentheses (LeetCode 20)
**Statement:** Determine if string of brackets is valid.

```python
def is_valid(s):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    for char in s:
        if char in pairs.values():  # Opening
            stack.append(char)
        else:  # Closing
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return not stack
```

### Variation Family

**V1: Minimum Add to Make Parentheses Valid (LeetCode 921)**
- **Twist:** Find minimum number of parentheses to add to make valid
- **Change:** Count unmatched opens and unmatched closes.

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

**V2: Minimum Remove to Make Valid Parentheses (LeetCode 1249)**
- **Twist:** Remove minimum invalid parentheses to make string valid
- **Change:** Track unmatched opens. Mark positions to remove.

**V3: Score of Parentheses (LeetCode 856)**
- **Twist:** Compute score: () = 1, (A) = 2*A, AB = A+B
- **Change:** Stack stores scores. When seeing ')', pop and compute.

```python
def score_of_parentheses(s):
    stack = [0]  # Current score at this depth
    for char in s:
        if char == '(':
            stack.append(0)
        else:
            v = stack.pop()
            stack[-1] += max(2 * v, 1)
    return stack[0]
```

**V4: Longest Valid Parentheses (LeetCode 32)**
- **Twist:** Find length of longest valid substring
- **Change:** Stack stores indices. Push -1 as base. Track max when popping.

```python
def longest_valid_parentheses(s):
    stack = [-1]
    max_len = 0
    for i, char in enumerate(s):
        if char == '(':
            stack.append(i)
        else:
            stack.pop()
            if not stack:
                stack.append(i)
            else:
                max_len = max(max_len, i - stack[-1])
    return max_len
```

**Near Miss: Generate Parentheses (LeetCode 22)**
- **Looks like:** Parentheses problem
- **But:** Backtracking to generate all valid combinations, not validate one.
- **Lesson:** "Valid parentheses" can mean validation (stack) OR generation (backtracking).

---

## Archetype 3.2: Monotonic Stack (Next Greater/Smaller)

### Recognition Signal (10 seconds)
Words: **"next greater", "next smaller", "previous greater", "stock span", "daily temperatures", "nearest"**

The question is always: **"For each element, find the nearest element to the left/right that is greater/smaller."**

### Core Structure
```
stack = []  # Stores indices or values, maintaining monotonic order
for i in range(n):
    while stack and condition(stack[-1], current):
        stack.pop()
    # Stack top is now the answer for current element
    stack.append(current)
```

**Monotonic decreasing stack:** Stack elements decrease from bottom to top. When current > stack.top(), pop until stack.top() >= current.

### Canonical Problem: Daily Temperatures (LeetCode 739)
**Statement:** For each day, find days until a warmer temperature.

```python
def daily_temperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []  # Stores indices of temperatures
    
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_idx = stack.pop()
            result[prev_idx] = i - prev_idx
        stack.append(i)
    return result
```

**Why this works:** The stack maintains indices of temperatures in decreasing order. When we see a warmer temperature, we resolve all previous cooler temperatures.

### Variation Family

**V1: Next Greater Element I (LeetCode 496)**
- **Twist:** For each element in nums1, find next greater in nums2
- **Change:** Precompute next greater for all of nums2 using monotonic stack. Store in map.

```python
def next_greater_element(nums1, nums2):
    next_greater = {}
    stack = []
    for num in nums2:
        while stack and num > stack[-1]:
            next_greater[stack.pop()] = num
        stack.append(num)
    # Remaining elements have no next greater
    while stack:
        next_greater[stack.pop()] = -1
    return [next_greater.get(x, -1) for x in nums1]
```

**V2: Next Greater Element II (LeetCode 503)**
- **Twist:** Circular array. Next greater can wrap around.
- **Change:** Iterate twice (2n elements). Use modulo for circular access.

**V3: Largest Rectangle in Histogram (LeetCode 84)**
- **Twist:** Find largest rectangle in histogram
- **Change:** For each bar, find previous smaller and next smaller. Width = next - prev - 1.

```python
def largest_rectangle_area(heights):
    stack = []
    max_area = 0
    for i, h in enumerate(heights + [0]):  # Add 0 to flush stack
        while stack and h < heights[stack[-1]]:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

**V4: Maximal Rectangle (LeetCode 85)**
- **Twist:** Largest rectangle of 1s in binary matrix
- **Change:** For each row, build histogram heights. Apply largest rectangle in histogram.
- **Pattern blend:** Dynamic programming + monotonic stack.

**V5: Sum of Subarray Minimums (LeetCode 907)**
- **Twist:** Sum of minimums of all subarrays
- **Change:** For each element, find distance to previous smaller and next smaller or equal. Contribution = arr[i] * left_dist * right_dist.

**Near Miss: Trapping Rain Water (LeetCode 42)**
- **Looks like:** "Find boundaries for each element"
- **But:** Two pointers from ends, not monotonic stack.
- **Lesson:** Both can solve it, but two pointers is O(1) space vs stack's O(n).

---

## Archetype 3.3: Expression Evaluation

### Recognition Signal (10 seconds)
Words: **"evaluate", "expression", "calculator", "RPN", "postfix", "infix", "polish notation"**

The question is always: **"Compute the result of an arithmetic expression."**

### Core Structure
```
For RPN: Push operands, when operator: pop two, apply, push result
For infix: Use two stacks (operands and operators), handle precedence
```

### Canonical Problem: Evaluate Reverse Polish Notation (LeetCode 150)
**Statement:** Evaluate value of arithmetic expression in RPN.

```python
def eval_rpn(tokens):
    stack = []
    for token in tokens:
        if token in '+-*/':
            b = stack.pop()
            a = stack.pop()
            if token == '+': stack.append(a + b)
            elif token == '-': stack.append(a - b)
            elif token == '*': stack.append(a * b)
            else: stack.append(int(a / b))
        else:
            stack.append(int(token))
    return stack[0]
```

### Variation Family

**V1: Basic Calculator (LeetCode 224)**
- **Twist:** Evaluate expression with +, -, parentheses, spaces
- **Change:** Stack stores intermediate results and signs when encountering '('.

```python
def calculate(s):
    stack = []
    num = 0
    sign = 1
    result = 0
    for char in s + '+':
        if char.isdigit():
            num = num * 10 + int(char)
        elif char in '+-':
            result += sign * num
            num = 0
            sign = 1 if char == '+' else -1
        elif char == '(':
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif char == ')':
            result += sign * num
            num = 0
            result *= stack.pop()
            result += stack.pop()
    return result
```

**V2: Basic Calculator II (LeetCode 227)**
- **Twist:** Add multiplication and division
- **Change:** Stack stores numbers. When seeing * or /, pop and apply immediately.

```python
def calculate_ii(s):
    stack = []
    num = 0
    sign = '+'
    for i, char in enumerate(s + '+'):
        if char.isdigit():
            num = num * 10 + int(char)
        if char in '+-*/' or i == len(s):
            if sign == '+':
                stack.append(num)
            elif sign == '-':
                stack.append(-num)
            elif sign == '*':
                stack.append(stack.pop() * num)
            elif sign == '/':
                stack.append(int(stack.pop() / num))
            sign = char
            num = 0
    return sum(stack)
```

**V3: Decode String (LeetCode 394)**
- **Twist:** Decode "3[a2[c]]" → "accaccacc"
- **Change:** Two stacks: one for counts, one for strings. When seeing ']', pop and build.

```python
def decode_string(s):
    count_stack = []
    string_stack = []
    current = ''
    num = 0
    for char in s:
        if char.isdigit():
            num = num * 10 + int(char)
        elif char == '[':
            count_stack.append(num)
            string_stack.append(current)
            num = 0
            current = ''
        elif char == ']':
            current = string_stack.pop() + current * count_stack.pop()
        else:
            current += char
    return current
```

**Near Miss: Different Ways to Add Parentheses (LeetCode 241)**
- **Looks like:** Expression with parentheses
- **But:** Divide and conquer / recursion, not stack evaluation.
- **Lesson:** "Evaluate expression" uses stack. "Ways to parenthesize" uses divide and conquer.

---

## Archetype 3.4: History / Undo Tracking

### Recognition Signal (10 seconds)
Words: **"history", "back", "undo", "previous state", "browser", "file path", "command"**

The question is always: **"Track a sequence of actions and support going back to previous states."**

### Canonical Problem: Min Stack (LeetCode 155)
**Statement:** Stack that supports push, pop, top, AND getMin in O(1).

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []
    
    def push(self, val):
        self.stack.append(val)
        min_val = min(val, self.min_stack[-1] if self.min_stack else val)
        self.min_stack.append(min_val)
    
    def pop(self):
        self.stack.pop()
        self.min_stack.pop()
    
    def top(self):
        return self.stack[-1]
    
    def getMin(self):
        return self.min_stack[-1]
```

**Key insight:** Maintain a parallel stack that stores the minimum at each depth.

### Variation Family

**V1: Design Browser History (LeetCode 1472)**
- **Twist:** Visit URLs, go back, go forward
- **Change:** Array + pointer. Stack is implicit in the pointer movement.

```python
class BrowserHistory:
    def __init__(self, homepage):
        self.history = [homepage]
        self.current = 0
    
    def visit(self, url):
        self.current += 1
        self.history = self.history[:self.current]
        self.history.append(url)
    
    def back(self, steps):
        self.current = max(0, self.current - steps)
        return self.history[self.current]
    
    def forward(self, steps):
        self.current = min(len(self.history) - 1, self.current + steps)
        return self.history[self.current]
```

**V2: Simplify Path (LeetCode 71)**
- **Twist:** Convert Unix-style absolute path to simplified canonical path
- **Change:** Split by '/', process each part. ".." pops, "." and "" ignored.

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

**V3: Baseball Game (LeetCode 682)**
- **Twist:** Compute score from operations: integer, "C" (cancel), "D" (double), "+" (sum last two)
- **Change:** Straight stack operations.

**V4: Crawler Log Folder (LeetCode 1598)**
- **Twist:** Find min operations to return to main folder
- **Change:** Stack tracks current depth. "../" pops if possible, "./" does nothing, else pushes.

**Near Miss: Implement Queue using Stacks (LeetCode 232)**
- **Looks like:** Stack problem
- **But:** Uses TWO stacks to simulate queue (FIFO). One for input, one for output.
- **Lesson:** Stack models LIFO. Queue models FIFO. Two stacks can simulate a queue.

---

## Archetype 3.5: DFS Simulation (Iterative Traversal)

### Recognition Signal (10 seconds)
Words: **"inorder", "preorder", "postorder", "tree traversal without recursion", "iterative DFS"**

The question is always: **"Traverse a tree/graph depth-first without using recursion."**

### Core Structure
```
stack = [root]
while stack:
    node = stack.pop()
    process(node)
    if node.right: stack.append(node.right)
    if node.left: stack.append(node.left)
```

**Note:** Push right before left so that left is processed first (LIFO).

### Canonical Problem: Binary Tree Inorder Traversal (LeetCode 94)
**Statement:** Inorder traversal without recursion.

```python
def inorder_traversal(root):
    result = []
    stack = []
    current = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result
```

### Variation Family

**V1: Binary Tree Preorder Traversal (LeetCode 144)**
- **Change:** Process node before pushing children.

**V2: Binary Tree Postorder Traversal (LeetCode 145)**
- **Change:** Trickier. Use two stacks, or track visited nodes.

**V3: Flatten Binary Tree to Linked List (LeetCode 114)**
- **Twist:** Flatten tree to right-linked list in-place
- **Change:** Stack-based or Morris traversal.

**V4: Kth Smallest Element in BST (LeetCode 230)**
- **Twist:** Find kth smallest in BST
- **Change:** Inorder traversal (stack-based) until k elements found.

```python
def kth_smallest(root, k):
    stack = []
    current = root
    while True:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        k -= 1
        if k == 0:
            return current.val
        current = current.right
```

**Near Miss: Binary Tree Level Order Traversal (LeetCode 102)**
- **Looks like:** Tree traversal
- **But:** BFS uses queue, not stack.
- **Lesson:** DFS = stack. BFS = queue. Don't confuse them.

---

## Archetype 3.6: String Processing (Nested Structures)

### Recognition Signal (10 seconds)
Words: **"remove duplicates", "adjacent", "delete", "cancel", "string reduction"**

The question is always: **"Process string by considering adjacent or nested characters."**

### Canonical Problem: Remove All Adjacent Duplicates in String (LeetCode 1047)
**Statement:** Remove adjacent duplicates repeatedly until no more.

```python
def remove_duplicates(s):
    stack = []
    for char in s:
        if stack and stack[-1] == char:
            stack.pop()
        else:
            stack.append(char)
    return ''.join(stack)
```

### Variation Family

**V1: Remove All Adjacent Duplicates in String II (LeetCode 1209)**
- **Twist:** Remove k adjacent duplicates
- **Change:** Stack stores (char, count). When count reaches k, pop.

```python
def remove_duplicates_ii(s, k):
    stack = []  # [(char, count)]
    for char in s:
        if stack and stack[-1][0] == char:
            stack[-1] = (char, stack[-1][1] + 1)
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append((char, 1))
    return ''.join(c * count for c, count in stack)
```

**V2: Make String Great (LeetCode 1544)**
- **Twist:** Remove adjacent characters that are same letter but different case (a and A)
- **Change:** Check if abs(ord(char) - ord(stack[-1])) == 32

**V3: Remove Digit From Number to Maximize Result**
- **Twist:** Remove one digit to maximize result
- **Change:** Find first digit where next digit is larger. Remove it. If none, remove last.
- **Key insight:** Greedy, not stack. But some variations use stack.

**Near Miss: Valid Parentheses String (LeetCode 678)**
- **Looks like:** String with parentheses
- **But:** Has '*' which can be '(', ')', or empty. Greedy with range tracking.
- **Lesson:** Stack for matching. Greedy for wildcard flexibility.

---

## Pattern 03 Mastery Checklist

Before moving to Pattern 04, confirm you can:

- [ ] **Matching:** See "valid parentheses" and write stack solution in 30 seconds
- [ ] **Monotonic:** See "next greater" and write monotonic decreasing stack in 45 seconds
- [ ] **Evaluation:** See "RPN" and write two-operand stack evaluation in 30 seconds
- [ ] **History:** Explain how MinStack maintains O(1) getMin
- [ ] **DFS Sim:** Write iterative inorder traversal without looking it up
- [ ] **String:** See "remove adjacent duplicates" and write stack solution in 30 seconds
- [ ] **Distinguish:** Know when to use stack vs queue vs recursion

---

*Next: Pattern 04 — Binary Search*
