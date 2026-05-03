# Pattern 01: Arrays & Hashing -- Drills Part 3

> **Focus:** Near Misses + Pattern Blends + Interview Simulation
> **Goal:** Build pattern-switching judgment and simulate real interview ambiguity.

---

## Near Misses (Looks like Pattern 01, but isn't)

### 16. 136. Single Number
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given a non-empty array where every element appears twice except one, find that single one.
**Why it fits:** At first glance, this is existence checking or frequency counting. A hash set or counter seems natural: track seen elements and find the singleton.
**The Twist:** Because the property is "exactly one unique" among pairs, XOR cancels all duplicates in O(n) time with O(1) space. Hashing works but misses the bit-manipulation optimization.
**Code Skeleton:**
```python
def single_number(nums):
    result = 0
    for n in nums:
        result ^= n
    return result
```

### 17. 15. 3Sum
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Find all unique triplets in the array which gives the sum of zero.
**Why it fits:** It is a direct extension of Two Sum: instead of a pair for target, we want triplets for zero. The complement-lookup instinct (hash map) is strong here.
**The Twist:** The array is unsorted and we need all unique combinations. Sorting + two pointers eliminates the need for a hash map and automatically handles deduplication by skipping equal neighbors.
**Code Skeleton:**
```python
def three_sum(nums):
    nums.sort()
    result = []
    n = len(nums)
    for i in range(n - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s < 0:
                left += 1
            elif s > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
    return result
```

### 18. 3. Longest Substring Without Repeating Characters
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given a string, find the length of the longest substring without repeating characters.
**Why it fits:** The "no repeating" constraint screams existence checking. A hash set tracking characters in the current substring seems like the natural O(n) approach.
**The Twist:** A pure hash set is insufficient because we need to know where the last duplicate occurred to move the left boundary. A hash map of last-seen indices turns this into a sliding-window problem.
**Code Skeleton:**
```python
def length_of_longest_substring(s):
    last_seen = {}
    max_len = 0
    left = 0
    for right, c in enumerate(s):
        if c in last_seen and last_seen[c] >= left:
            left = last_seen[c] + 1
        last_seen[c] = right
        max_len = max(max_len, right - left + 1)
    return max_len
```

### 19. 238. Product of Array Except Self
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an integer array, return an array such that answer[i] is the product of all elements except nums[i].
**Why it fits:** The prefix-product instinct is strong: if we store running products in a hash map or array, we can compute each answer as prefix[i-1] * suffix[i+1].
**The Twist:** No hash map is needed. Two linear passes--one left-to-right accumulating prefix products, one right-to-left accumulating suffix products--solve it in O(n) time and O(1) extra space (excluding output).
**Code Skeleton:**
```python
def product_except_self(nums):
    n = len(nums)
    result = [1] * n
    prefix = 1
    for i in range(n):
        result[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= nums[i]
    return result
```

### 20. 75. Sort Colors
**Archetype:** (None -- Near Miss)
**Type:** Near Miss
**Statement:** Given an array with n objects colored red, white, or blue, sort them in-place so that objects of the same color are adjacent.
**Why it fits:** Frequency counting is the obvious approach: count 0s, 1s, and 2s, then overwrite the array. This is O(n) time and O(1) space using a small hash map or array of size 3.
**The Twist:** The two-pass counting approach works, but the optimal solution uses Dutch National Flag partitioning with three pointers in a single pass. It is a partitioning problem, not a counting problem.
**Code Skeleton:**
```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

## Pattern Blends (Pattern 01 + Another Pattern)

### 21. 438. Find All Anagrams in a String
**Archetype:** 1.2 + Sliding Window
**Type:** Pattern Blend
**Statement:** Given strings s and p, return the start indices of all anagrams of p in s.
**Why it fits:** We need frequency counts of p, but applied across every window of len(p) in s. The hash map stores the target frequency, and a sliding window maintains the current frequency.
**The Twist:** Instead of rebuilding the frequency map for each window, we update it incrementally: add the new right character and remove the old left character. This reduces O(n * k) to O(n).
**Code Skeleton:**
```python
from collections import Counter

def find_anagrams(s, p):
    if len(p) > len(s):
        return []
    p_count = Counter(p)
    window_count = Counter(s[:len(p) - 1])
    result = []
    for i in range(len(p) - 1, len(s)):
        window_count[s[i]] += 1
        if window_count == p_count:
            result.append(i - len(p) + 1)
        window_count[s[i - len(p) + 1]] -= 1
        if window_count[s[i - len(p) + 1]] == 0:
            del window_count[s[i - len(p) + 1]]
    return result
```

### 22. 30. Substring with Concatenation of All Words
**Archetype:** 1.2 + Sliding Window
**Type:** Pattern Blend
**Statement:** Given a string and an array of words, find all starting indices of substring(s) that is a concatenation of each word exactly once.
**Why it fits:** We treat the multiset of words as a frequency map. A sliding window of fixed length (total words length) checks whether the words inside match the required frequencies.
**The Twist:** The window does not slide one character at a time; it slides word-by-word. We must also try every possible word-aligned starting offset (0 to word_len-1) because the concatenation must align to word boundaries.
**Code Skeleton:**
```python
from collections import Counter, defaultdict

def find_substring(s, words):
    if not s or not words:
        return []
    word_len = len(words[0])
    total_len = word_len * len(words)
    target = Counter(words)
    result = []
    for i in range(word_len):
        left = i
        current = defaultdict(int)
        count = 0
        for j in range(i, len(s) - word_len + 1, word_len):
            word = s[j:j + word_len]
            if word in target:
                current[word] += 1
                count += 1
                while current[word] > target[word]:
                    left_word = s[left:left + word_len]
                    current[left_word] -= 1
                    count -= 1
                    left += word_len
                if count == len(words):
                    result.append(left)
            else:
                current.clear()
                count = 0
                left = j + word_len
    return result
```

### 23. 554. Brick Wall
**Archetype:** 1.5 + Greedy
**Type:** Pattern Blend
**Statement:** Given a brick wall represented as rows of bricks with varying widths, draw a vertical line from top to bottom that crosses the fewest bricks.
**Why it fits:** We compute prefix sums of brick widths for each row. A prefix sum that appears in many rows represents a vertical edge. The hash map counts edge frequencies.
**The Twist:** We are not looking for a subarray sum; we are using prefix aggregates to find the most common boundary. The greedy choice is to cut at the position with the maximum number of aligned edges.
**Code Skeleton:**
```python
from collections import defaultdict

def least_bricks(wall):
    edge_count = defaultdict(int)
    for row in wall:
        edge = 0
        for brick in row[:-1]:
            edge += brick
            edge_count[edge] += 1
    if not edge_count:
        return len(wall)
    return len(wall) - max(edge_count.values())
```

### 24. 380. Insert Delete GetRandom O(1)
**Archetype:** 1.6 + Array
**Type:** Pattern Blend
**Statement:** Implement a data structure that supports insert, remove, and getRandom in average O(1) time.
**Why it fits:** The hash map provides O(1) existence checking and maps values to indices. The array provides O(1) random access for getRandom. They work together to achieve O(1) deletion via swap-with-last.
**The Twist:** Deletion from an array is normally O(n) due to shifting. By swapping the target element with the last element and updating the hash map, deletion becomes O(1) while preserving the dense array for random selection.
**Code Skeleton:**
```python
import random

class RandomizedSet:
    def __init__(self):
        self.val_to_idx = {}
        self.values = []

    def insert(self, val):
        if val in self.val_to_idx:
            return False
        self.val_to_idx[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val):
        if val not in self.val_to_idx:
            return False
        last_val = self.values[-1]
        idx = self.val_to_idx[val]
        self.values[idx] = last_val
        self.val_to_idx[last_val] = idx
        self.values.pop()
        del self.val_to_idx[val]
        return True

    def getRandom(self):
        return random.choice(self.values)
```

### 25. 460. LFU Cache
**Archetype:** 1.6 + Linked List
**Type:** Pattern Blend
**Statement:** Design a Least Frequently Used cache with O(1) get and put operations.
**Why it fits:** A hash map stores key-to-node mappings for O(1) access. Nodes are grouped by frequency into doubly linked lists, and another hash map stores frequency-to-list mappings.
**The Twist:** When capacity is exceeded, we evict the least frequently used item, breaking ties by least recently used. Tracking the minimum frequency and moving nodes between frequency lists makes this a complex hash-plus-list design.
**Code Skeleton:**
```python
from collections import defaultdict

class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.freq = 1
        self.prev = None
        self.next = None

class DLinkedList:
    def __init__(self):
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def append(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def pop(self, node=None):
        if self.size == 0:
            return None
        if node is None:
            node = self.tail.prev
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        return node

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.min_freq = 0
        self.node_map = {}  # key -> Node
        self.freq_map = defaultdict(DLinkedList)

    def get(self, key):
        if key not in self.node_map:
            return -1
        node = self.node_map[key]
        self._update(node)
        return node.val

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.node_map:
            node = self.node_map[key]
            node.val = value
            self._update(node)
            return
        if self.size >= self.capacity:
            node = self.freq_map[self.min_freq].pop()
            del self.node_map[node.key]
            self.size -= 1
        node = Node(key, value)
        self.node_map[key] = node
        self.freq_map[1].append(node)
        self.min_freq = 1
        self.size += 1

    def _update(self, node):
        freq = node.freq
        self.freq_map[freq].pop(node)
        if self.min_freq == freq and self.freq_map[freq].size == 0:
            self.min_freq += 1
        node.freq += 1
        self.freq_map[node.freq].append(node)
```

## Interview Simulation (No archetype label given)

### 26. 1462. Course Schedule IV
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given the total number of courses, a list of prerequisite pairs, and queries, return whether each query [u, v] implies u is a prerequisite of v.
**Why it fits:** We need transitive closure over a directed graph. For each course, we compute all reachable descendants and store them in a hash set for O(1) query answering.
**The Twist:** The naive DFS per query is too slow. Precomputing reachability with topological order and set merging turns this into a set-inclusion problem. Hash sets compress the adjacency information.
**Code Skeleton:**
```python
from collections import defaultdict, deque

def check_if_prerequisite(numCourses, prerequisites, queries):
    adj = defaultdict(list)
    indegree = [0] * numCourses
    for a, b in prerequisites:
        adj[a].append(b)
        indegree[b] += 1
    prereq_sets = [set() for _ in range(numCourses)]
    queue = deque([i for i in range(numCourses) if indegree[i] == 0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            prereq_sets[v].add(u)
            prereq_sets[v].update(prereq_sets[u])
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    return [u in prereq_sets[v] for u, v in queries]
```

### 27. 348. Design Tic-Tac-Toe
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Design a Tic-Tac-Toe game that returns the current winner after each move.
**Why it fits:** Instead of simulating the board, we track row, column, and diagonal sums for each player. A hash map or arrays store aggregate counts, and a win is detected when any aggregate reaches +/- n.
**The Twist:** No need for a 2D grid. By mapping player 1 to +1 and player 2 to -1, we can use a single integer per row/col/diag. The game state is fully captured by O(n) counters.
**Code Skeleton:**
```python
class TicTacToe:
    def __init__(self, n):
        self.n = n
        self.rows = [0] * n
        self.cols = [0] * n
        self.diag = 0
        self.anti_diag = 0

    def move(self, row, col, player):
        val = 1 if player == 1 else -1
        self.rows[row] += val
        self.cols[col] += val
        if row == col:
            self.diag += val
        if row + col == self.n - 1:
            self.anti_diag += val
        if (abs(self.rows[row]) == self.n or
            abs(self.cols[col]) == self.n or
            abs(self.diag) == self.n or
            abs(self.anti_diag) == self.n):
            return player
        return 0
```

### 28. 359. Logger Rate Limiter
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Design a logger system that receives a stream of messages and prints each message only if it has not been printed in the last 10 seconds.
**Why it fits:** The system must check existence (has this message been seen?) and enforce a time constraint. A hash map from message to last-printed timestamp gives O(1) decisions.
**The Twist:** Unlike a simple set, entries become stale but do not need explicit cleanup for correctness--old timestamps naturally fail the "within 10 seconds" check. This is a time-bounded existence check.
**Code Skeleton:**
```python
class Logger:
    def __init__(self):
        self.msg_to_time = {}

    def shouldPrintMessage(self, timestamp, message):
        if message not in self.msg_to_time or timestamp - self.msg_to_time[message] >= 10:
            self.msg_to_time[message] = timestamp
            return True
        return False
```

### 29. 621. Task Scheduler
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given tasks and a cooling time n, find the least number of units of time that the CPU will take to finish all tasks.
**Why it fits:** Frequency counting tells us which tasks are most common. The most frequent task dictates the minimum schedule length, but idle slots can sometimes be filled by other tasks.
**The Twist:** The optimal schedule is derived from a formula involving max frequency and the number of tasks sharing that frequency. Hash maps give frequencies; greedy arrangement determines the final count.
**Code Skeleton:**
```python
from collections import Counter

def least_interval(tasks, n):
    freq = Counter(tasks)
    max_freq = max(freq.values())
    max_count = sum(1 for v in freq.values() if v == max_freq)
    part_count = max_freq - 1
    part_length = n - (max_count - 1)
    empty_slots = part_count * part_length
    available_tasks = len(tasks) - max_freq * max_count
    idles = max(0, empty_slots - available_tasks)
    return len(tasks) + idles
```

### 30. 149. Max Points on a Line
**Archetype:** (Not given -- Interview Sim)
**Type:** Interview Sim
**Statement:** Given an array of points on a plane, return the maximum number of points that lie on the same straight line.
**Why it fits:** For each point, we compute slopes to all other points. A hash map keyed by reduced slope fraction counts how many points align with the current anchor.
**The Twist:** Vertical lines and duplicate points require special handling. To avoid floating-point precision issues, slopes are stored as reduced (dy/gcd, dx/gcd) tuples with sign normalization.
**Code Skeleton:**
```python
import math
from collections import defaultdict

def max_points(points):
    if len(points) <= 2:
        return len(points)
    result = 0
    for i in range(len(points)):
        slopes = defaultdict(int)
        duplicate = 1
        for j in range(i + 1, len(points)):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            if dx == 0 and dy == 0:
                duplicate += 1
                continue
            g = math.gcd(dx, dy)
            dx //= g
            dy //= g
            if dx < 0:
                dx, dy = -dx, -dy
            elif dx == 0:
                dy = 1
            slopes[(dx, dy)] += 1
        result = max(result, (max(slopes.values()) if slopes else 0) + duplicate)
    return result
```
