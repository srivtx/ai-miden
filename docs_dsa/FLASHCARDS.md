# DSA Flashcards — Spaced Repetition Deck

> **How to use this:** Read the question. Cover the answer. Say it out loud. Check. Mark easy/hard. Review daily for 10 minutes.
>
> **Anki import:** Each card is `Q: ... A: ...` block. Copy into Anki's "Import" or use a markdown-to-Anki converter.
> **Tags per card:** Pattern number + archetype name (e.g., `p01`, `existence`, `hashing`).

---

## Pattern 01: Arrays & Hashing

Q1: You see "contains duplicate" in an unsorted array. What is the fastest pattern?
A1: Pattern 01 — Arrays & Hashing (1.1 Existence Check). Use a hash set: O(n) time, O(n) space. If space is restricted, sort first: O(n log n) time, O(1) space.

Q2: You need to check if two strings are anagrams. What do you count?
A2: Pattern 01 — Arrays & Hashing (1.2 Frequency Counter). Count character frequencies in a hashmap or fixed-size array (26 for lowercase letters). Compare counts: O(n) time, O(1) or O(k) space.

Q3: Problem says "find two numbers that add to target." Array is unsorted. What pattern?
A3: Pattern 01 — Arrays & Hashing (1.3 Complement Lookup). Hashmap stores `complement = target - num` as you iterate. O(n) time, O(n) space. Do NOT sort unless the array is already sorted (then use two pointers).

Q4: You need to group strings that are anagrams of each other. What is the grouping key?
A4: Pattern 01 — Arrays & Hashing (1.4 Grouping). The key is the sorted string or a character count tuple. Group in a hashmap: `groups[key] = [strings]`. O(n * k log k) time if sorting each string.

Q5: Problem asks for "product of array except self" and forbids division. How?
A5: Pattern 01 — Arrays & Hashing (1.5 Prefix-Suffix). Compute prefix products left-to-right, then suffix products right-to-left in the same output array. Two passes, O(n) time, O(1) extra space.

Q6: You need O(1) insert, delete, AND getRandom. What data structures combine?
A6: Pattern 01 — Arrays & Hashing (1.6 Design Hybrid). Hashmap stores `value -> index` in array. Array stores values. Swap with last element on delete to keep array dense. O(1) for all three operations.

Q7: You see "longest consecutive sequence" in an unsorted array. Naive sort is O(n log n). Can you do O(n)?
A7: Pattern 01 — Arrays & Hashing (1.8 Sequence Building). Put all numbers in a hash set. For each number, only start a sequence if `num - 1` is NOT in the set. Then count forward. O(n) time, O(n) space.

Q8: What is the trade-off between hash set and sorted array for existence queries?
A8: Hash set: O(1) time, O(n) space, unsorted. Sorted array: O(log n) time with binary search, O(1) space if in-place, but O(n log n) to sort. Choose based on query frequency vs build cost.

Q9: Why can frequency counting use a fixed-size array for lowercase letters instead of a hashmap?
A9: Because the key space is bounded (26 letters). A `counts[26]` array is faster and uses less memory than a hashmap. Generalize to hashmap only when the key space is large or unknown.

Q10: What is the single most common mistake in "two sum" when using a hashmap?
A10: Returning the indices of the complement that was already inserted vs the current number. The correct logic: check if `num` exists in the map (it is the complement of a previous element), then insert `complement = target - num`.

Q11: You need to find the intersection of two arrays with duplicates preserved. What data structure?
A11: Pattern 01 — Arrays & Hashing (1.2 Frequency Counter). Count frequencies in the smaller array. Iterate the larger array and decrement counts. O(n + m) time, O(min(n, m)) space.

Q12: Problem says "find all unique triplets that sum to zero." What is the high-level plan?
A12: Sort the array first. Fix one element, then use two pointers on the rest to find pairs that sum to the negative of the fixed element. Skip duplicates at every level. O(n^2) time.

---

## Pattern 02: Two Pointers

Q13: Array is sorted. Find a pair with sum = target. What pattern and complexity?
A13: Pattern 02 — Two Pointers (2.1 Converging Pointers). `left = 0, right = n-1`. Move inward based on `sum < target` (left++) or `sum > target` (right--). O(n) time, O(1) space.

Q14: You need to remove duplicates in-place from a sorted array. Which pointer technique?
A14: Pattern 02 — Two Pointers (2.3 In-Place Modification). Slow pointer `k` tracks the write position. Fast pointer `i` scans. When `nums[i] != nums[k]`, write `nums[++k] = nums[i]`. Return `k + 1`.

Q15: What is the Dutch National Flag problem, and what pointer setup solves it?
A15: Sort an array of 0s, 1s, 2s in one pass. Three pointers: `low` (0 boundary), `mid` (scanning), `high` (2 boundary). Swap `mid` with `low` when 0, advance `mid` when 1, swap `mid` with `high` when 2. O(n) time.

Q16: You need to check if a string is a palindrome ignoring non-alphanumeric characters. Pointer approach?
A16: Pattern 02 — Two Pointers (2.4 Palindrome Check). `left` starts at 0, `right` at end. Skip non-alphanumeric. Compare characters case-insensitively. If mismatch, return False. O(n) time, O(1) space.

Q17: Container With Most Water: what are the two pointers measuring?
A17: Pattern 02 — Two Pointers (2.5 Container). `left` and `right` form the width. Area = `min(height[left], height[right]) * (right - left)`. Move the shorter line inward because moving the taller line cannot increase area.

Q18: Trapping Rain Water with two pointers: what state do you track at each boundary?
A18: Pattern 02 — Two Pointers (2.5 Container). Track `left_max` and `right_max`. Water at `left` = `max(0, left_max - height[left])` if `left_max < right_max`, else process `right`. O(n) time, O(1) space.

Q19: Two Sum II says the input array is already sorted. Why is two pointers better than hashmap here?
A19: Because two pointers gives O(n) time and O(1) space. Hashmap would be O(n) space. The sorted property enables the converging strategy.

Q20: When should you NOT use two pointers on a sorted array?
A20: When you need more than two elements (3Sum+), when the array is not sorted and sorting would destroy index requirements, or when you need subsequence (not subarray) properties.

Q21: Merge two sorted arrays in-place into the first array (which has extra space). Where do pointers start?
A21: Pattern 02 — Two Pointers (2.2 Diverging/Merge). Start from the END of both arrays. Fill `nums1` from back to front with the larger of the two tails. This avoids overwriting unmerged elements.

Q22: Move all zeros to the end while preserving order of non-zero elements. Two-pointer trick?
A22: Pattern 02 — Two Pointers (2.3 In-Place). `write` pointer tracks where the next non-zero goes. `read` pointer scans. After writing all non-zeros, fill the rest with zeros. Single pass, O(n).

Q23: 3Sum: why sort first? Does this violate the "no sorting" rule?
A23: Sorting is allowed because we do not need original indices. The two-pointer technique requires sorted order. Sorting costs O(n log n), and the two-pointer scan is O(n^2), total O(n^2). No better deterministic algorithm exists.

Q24: What is the core invariant in the Dutch National Flag algorithm?
A24: Everything before `low` is 0, everything after `high` is 2, everything between `low` and `mid` is 1. `mid` scans the unknown region. This invariant is maintained with every swap.

---

## Pattern 03: Stack

Q25: "Valid Parentheses" — what goes on the stack?
A25: Pattern 03 — Stack (3.1 Matching). Push opening brackets. When you see a closing bracket, check if it matches the top of the stack. If stack is empty or mismatched, return False. O(n) time.

Q26: Min Stack: how do you get O(1) for push, pop, AND getMin?
A26: Pattern 03 — Stack (3.4 History Tracking). Store pairs `(value, current_min)` on the stack. Each entry knows the minimum of everything below it. Alternatively, use a second stack for mins.

Q27: "Next Greater Element" — monotonic stack, increasing or decreasing?
A27: Pattern 03 — Stack (3.2 Monotonic). Decreasing (or non-increasing) stack. As you iterate, pop elements smaller than current — they found their next greater. Push current index. O(n) amortized.

Q28: Daily Temperatures: what does the monotonic stack store?
A28: Pattern 03 — Stack (3.2 Monotonic). Store indices with decreasing temperatures. For each day, pop all indices with lower temperature; their "next warmer day" is the current index. Push current index.

Q29: Evaluate Reverse Polish Notation: when do you push vs pop?
A29: Pattern 03 — Stack (3.3 Expression). Push numbers. When you see an operator, pop two numbers (second pop is left operand), apply operator, push result. At end, stack has one element.

Q30: Largest Rectangle in Histogram: what does the stack represent?
A30: Pattern 03 — Stack (3.2 Monotonic). Increasing stack of bar indices. When a shorter bar arrives, pop taller bars and calculate area with popped bar as the shortest. Width extends from previous stack top to current index.

Q31: Car Fleet: why is a stack or simple iteration from the end sufficient?
A31: Pattern 03 — Stack (3.2 Monotonic). Cars cannot pass each other. Process from the destination backward. If a car catches up to the fleet ahead (arrives sooner or equal), it joins that fleet. Count fleets.

Q32: What is the defining property of a monotonic stack?
A32: Elements in the stack are kept in strictly increasing or decreasing order. Every new element may trigger pops of elements that violate the monotonicity. Each element is pushed and popped at most once.

Q33: Generate Parentheses (n pairs): what does the backtracking state track?
A33: Pattern 03 — Stack (3.1 Matching, via backtracking). Track `open` and `close` counts. Add `(` if `open < n`. Add `)` if `close < open`. Valid when both reach n.

Q34: What is the difference between using a stack for "matching" vs "history" problems?
A34: Matching: stack stores elements that need future pairs (parentheses). History: stack stores state snapshots so you can retrieve previous min/max/context without reprocessing. Both use LIFO, but the semantic meaning differs.

---

## Pattern 04: Binary Search

Q35: Classic binary search: what is the loop invariant?
A35: Pattern 04 — Binary Search (4.1 Classic). The target, if it exists, is always within `[left, right]`. `mid = left + (right - left) // 2`. If `nums[mid] < target`, search right half (`left = mid + 1`). Else search left half (`right = mid - 1`).

Q36: Search in rotated sorted array: how do you know which half is sorted?
A36: Pattern 04 — Binary Search (4.2 Rotated). Check `nums[left] <= nums[mid]`. If true, left half is sorted. Determine if target lies in the sorted half. If yes, search there; else, search the other half.

Q37: Find minimum in rotated sorted array: what comparison tells you where the minimum lives?
A37: Pattern 04 — Binary Search (4.2 Rotated). Compare `nums[mid]` with `nums[right]`. If `nums[mid] > nums[right]`, the minimum is in the right half (`left = mid + 1`). Else, it is at `mid` or left (`right = mid`).

Q38: Koko Eating Bananas: what is the search space?
A38: Pattern 04 — Binary Search (4.5 Answer Space). Search space is eating speed `k` in `[1, max(piles)]`. For each `k`, calculate total hours needed. If hours <= `h`, `k` might work; try smaller (`right = mid`). Else try larger (`left = mid + 1`).

Q39: Median of Two Sorted Arrays: why is binary search on the smaller array?
A39: Pattern 04 — Binary Search (4.7 Median). Binary search the partition point in the smaller array. The partition in the larger array is determined by the total left-half size. Check if max(left) <= min(right) on both sides.

Q40: Time Based Key-Value Store: what makes binary search applicable?
A40: Pattern 04 — Binary Search (4.1 Classic). Timestamps are strictly increasing for each key. Store `(timestamp, value)` list per key. Binary search the list for the greatest timestamp <= query.

Q41: What is the generic template for "find first/last position" binary search?
A41: Pattern 04 — Binary Search (4.3 Boundary). For first: `if nums[mid] >= target: right = mid - 1` and record `mid`. For last: `if nums[mid] <= target: left = mid + 1` and record `mid`. Post-process to verify.

Q42: Why use `left + (right - left) // 2` instead of `(left + right) // 2`?
A42: To prevent integer overflow in languages with fixed-size integers. In Python it is unnecessary, but it is a good habit for cross-language consistency and signals you understand the overflow risk.

Q43: When does binary search NOT apply?
A43: When the array is unsorted and cannot be sorted (e.g., original indices needed), when the predicate is not monotonic, or when the answer space is not a range of integers.

Q44: Search a 2D Matrix: how do you treat a row-sorted, column-sorted matrix?
A44: Pattern 04 — Binary Search (4.6 2D). If fully row-major sorted (each row starts > previous row ends), treat as 1D array with index mapping. If only row-sorted, start from top-right or bottom-left and eliminate rows/columns.

Q45: What is the difference between binary search on an array vs binary search on an answer space?
A45: Array BS: the search space IS the data. Answer-space BS: you guess an answer and verify if it is feasible. The verification step is problem-specific. Answer-space BS works when feasibility is monotonic with respect to the answer.

---

## Pattern 05: Sliding Window

Q46: Fixed-size window of k: what do you track as the window slides?
A46: Pattern 05 — Sliding Window (5.1 Fixed). Add `nums[right]` on expansion, subtract `nums[left]` on contraction. Track running sum, max, or frequency counts. Update answer at each valid window.

Q47: Longest substring without repeating characters: what data structure tracks uniqueness?
A47: Pattern 05 — Sliding Window (5.2 Variable). Hash set or hashmap of character -> last seen index. Expand `right`. If duplicate found inside current window, contract `left` past the previous occurrence.

Q48: Longest Repeating Character Replacement: what does the window condition check?
A48: Pattern 05 — Sliding Window (5.2 Variable). Window is valid if `window_length - max_freq <= k` (we can replace at most k characters). If invalid, shrink from left. Track max valid window length.

Q49: Minimum Window Substring: how do you know when the window is "complete"?
A49: Pattern 05 — Sliding Window (5.3 Minimum). A hashmap counts needed characters. `formed` increments when a character count meets its requirement. When `formed == required`, try shrinking from left to find minimum.

Q50: Sliding Window Maximum (deque approach): why does the front hold the maximum?
A50: Pattern 05 — Sliding Window (5.6 Monotonic Deque). The deque stores indices in decreasing value order. Before adding a new index, remove from back all indices with smaller values. Remove front if outside window. Front is always the max.

Q51: Permutation in String: how is this a fixed window problem?
A51: Pattern 05 — Sliding Window (5.1 Fixed). The permutation length is fixed. Slide a window of that size. Compare character frequency counts of the window with the target. O(n) time, O(1) space (26 letters).

Q52: What is the difference between "at most K distinct" and "exactly K distinct"?
A52: "Exactly K" = "at most K" minus "at most K-1". Use the same sliding window logic twice. This is a common trick to avoid trying to count exact K directly.

Q53: When should you use a monotonic deque vs a hashmap in sliding window?
A53: Use a monotonic deque when you need to query the maximum or minimum in O(1) per window step. Use a hashmap when you need to track arbitrary frequencies, uniqueness, or character counts.

Q54: What is the time complexity of a typical sliding window problem?
A54: O(n) because both `left` and `right` pointers traverse the array at most once each. The inner work (hashmap ops) is O(1) amortized.

Q55: Minimum Size Subarray Sum: why is this a variable window, not binary search?
A55: Pattern 05 — Sliding Window (5.3 Minimum, or 2.7). Positive numbers only allow the two-pointer window approach. If numbers can be negative, prefix sum + hashmap is needed instead.

---

## Pattern 06: Linked List

Q56: Reverse a linked list iteratively: what three pointers do you need?
A56: Pattern 06 — Linked List (6.1 Reverse). `prev = None`, `curr = head`, `next_temp = curr.next`. Iterate: save next, point `curr.next` to `prev`, advance `prev` and `curr`. Return `prev` as new head.

Q57: Detect cycle in a linked list: Floyd's algorithm. Fast and slow pointer speeds?
A57: Pattern 06 — Linked List (6.2 Floyd's Cycle). `slow` moves 1 step, `fast` moves 2 steps. If they meet, cycle exists. To find entry: reset one pointer to head, both move 1 step; meeting point is the cycle start.

Q58: Merge Two Sorted Lists: recursive vs iterative?
A58: Pattern 06 — Linked List (6.3 Merge). Iterative: dummy head, tail pointer, compare nodes. Recursive: return the smaller node, attach the merge result of the rest. Both O(n + m) time, O(1) or O(n + m) space.

Q59: Reorder List (L0 -> Ln -> L1 -> Ln-1): what are the three steps?
A59: Pattern 06 — Linked List (6.4 Reorder). 1) Find middle (slow/fast). 2) Reverse second half. 3) Interleave first half and reversed second half. Be careful with odd-length lists.

Q60: Remove Nth Node From End: how to do it in one pass?
A60: Pattern 06 — Linked List (6.6 Remove). Fast pointer advances n steps. Then both advance together. When fast reaches end, slow is at the node before the target. Remove `slow.next`.

Q61: Merge k Sorted Lists: what data structure makes this efficient?
A61: Pattern 06 — Linked List (6.3 Merge) + Pattern 08 — Heap. Min-heap of size k. Pop smallest, push its next. O(n log k) time, O(k) space. Naive merge-one-by-one is O(n * k).

Q62: Copy List with Random Pointer: what is the two-pass trick?
A62: Pattern 06 — Linked List (6.5 Deep Copy). Pass 1: interleave copied nodes (`A -> A' -> B -> B'`). Pass 2: assign random pointers for copies using `orig.random.next`. Pass 3: separate the two lists.

Q63: What is the standard cycle detection proof: why does the meeting point guarantee a cycle?
A63: If there is a cycle, fast pointer enters it first. Slow enters later. Fast gains 1 step per iteration. They must meet because the distance between them modulo cycle length becomes 0.

Q64: Find middle of linked list: why does slow/fast work with `fast` and `fast.next`?
A64: `fast` moves 2 steps, `slow` moves 1. When `fast` reaches the end, `slow` is at the middle. For even length, this returns the second middle. Use `fast.next and fast.next.next` for the first middle if needed.

Q65: LRU Cache: what two data structures combine?
A65: Pattern 06 — Linked List (6.7 Design) + Hashing. Hashmap stores `key -> node` for O(1) lookup. Doubly linked list maintains usage order. Move accessed node to tail. Evict from head when over capacity.

---

## Pattern 07: Trees

Q66: Maximum Depth of Binary Tree: recursive vs iterative?
A66: Pattern 07 — Trees (7.1 Traversal). Recursive: `max(depth(left), depth(right)) + 1`. Iterative: BFS level counting or DFS stack tracking depth. Both O(n) time.

Q67: Same Tree: when do you return False immediately?
A67: Pattern 07 — Trees (7.3 Validation). If one node is None and the other is not, or if values differ, return False. Recursively check left and right subtrees.

Q68: Invert Binary Tree: what is the single recursive line?
A68: Pattern 07 — Trees (7.7 Modification). `node.left, node.right = self.invert(node.right), self.invert(node.left)`. Post-order: invert children, then swap.

Q69: Maximum Path Sum: what does the recursive helper return vs what does it compute?
A69: Pattern 07 — Trees (7.8 Metrics). Helper returns the max sum of a path starting at this node and going down (for parent to use). It also computes the max path that passes through this node (`left + node.val + right`) and updates global max.

Q70: Binary Tree Level Order Traversal: queue or recursion?
A70: Pattern 07 — Trees (7.1 BFS). Queue (iterative BFS) is standard. Track queue size per level to separate levels. Recursive DFS with depth parameter also works but BFS is more natural.

Q71: Serialize and Deserialize Binary Tree: what traversal works best?
A71: Pattern 07 — Trees (7.6 Serialization). Pre-order (root, left, right) with null markers. Easy to reconstruct: read root, recursively build left, then right. Use a queue or iterator for deserialization.

Q72: Subtree of Another Tree: how do you avoid O(n * m) worst case?
A72: Pattern 07 — Trees (7.3 Validation). Merkle hashing or tree serialization. Compute a hash for each subtree. Compare root hash with target hash. Alternatively, use the naive O(n * m) approach with early exit; often passes.

Q73: Lowest Common Ancestor (LCA) in BST: how is it simpler than LCA in a general binary tree?
A73: Pattern 07 — Trees (7.4 LCA). In BST: compare node values with p and q. If both are smaller, go left. If both larger, go right. Otherwise, current node is LCA. O(h) time. General tree requires storing paths or recursive search.

Q74: Construct Binary Tree from Preorder and Inorder: what does the first element of preorder tell you?
A74: Pattern 07 — Trees (7.5 Construction). Preorder[0] is the root. Find it in inorder. Everything left of it in inorder is the left subtree; right is the right subtree. Recurse. Use a hashmap for inorder index lookups: O(n) time.

Q75: Validate Binary Search Tree: why is `node.val > min and node.val < max` not enough?
A75: Pattern 07 — Trees (7.3 Validation). You must pass down valid ranges. A node must be greater than ALL ancestors on the left path and less than ALL on the right path. Range is `(min_bound, max_bound)` updated per recursion.

Q76: Kth Smallest Element in BST: iterative inorder traversal stops early. How?
A76: Pattern 07 — Trees (7.2 Inorder). Use a stack. Push all left children. Pop, decrement k. If k == 0, return value. Push right child and its left descendants. O(h + k) time, O(h) space.

Q77: What is Morris Traversal, and when is it useful?
A77: Pattern 07 — Trees (7.2 Inorder). Threaded traversal using null right pointers to point to inorder successor. O(1) space, O(n) time. Useful when space is extremely constrained and tree modification is allowed.

Q78: Diameter of Binary Tree: what does the recursive function return vs track?
A78: Pattern 07 — Trees (7.8 Metrics). Returns the height of the subtree. Tracks the max path length (left_height + right_height) seen so far. Diameter is the max path length, which may or may not pass through root.

---

## Pattern 08: Heap / Priority Queue

Q79: Kth Largest Element in an Array: min-heap or max-heap?
A79: Pattern 08 — Heap (8.1 Kth Element). Min-heap of size k. Iterate elements: if heap size < k, push. Else if element > heap top, pop and push. Top is kth largest. O(n log k) time, O(k) space.

Q80: Top K Frequent Elements: two-step process?
A80: Pattern 08 — Heap (8.1 Kth Element) + Pattern 01. Count frequencies with hashmap. Use a min-heap (or bucket sort by frequency) to get top k. O(n log k) with heap, or O(n) with bucket sort.

Q81: Merge k Sorted Lists: why heap over divide-and-conquer?
A81: Pattern 08 — Heap (8.2 K-Way Merge). Heap gives O(n log k) with simple code. Divide-and-conquer merge also gives O(n log k) but with more code. Heap is the standard interview answer.

Q82: Find Median from Data Stream: what two heaps maintain?
A82: Pattern 08 — Heap (8.3 Running Median). Max-heap for the lower half, min-heap for the upper half. Invariant: sizes differ by at most 1, and all elements in max-heap <= all in min-heap. Rebalance after each insertion.

Q83: Task Scheduler: what does the heap represent in the greedy approach?
A83: Pattern 08 — Heap (8.4 Scheduling). Max-heap of task frequencies. Pick the most frequent task. Decrement count, put it in a cooldown queue. After n intervals, reinsert if count > 0. Also solvable with math: idle slots = max(0, (max_freq - 1) * (n + 1) + max_freq_count - tasks.length).

Q84: When do you use a heap instead of sorting?
A84: When you only need the top k elements (heap: O(n log k)) rather than a full sorted order (sort: O(n log n)). When elements arrive dynamically (streaming median). When merging multiple sorted sequences.

Q85: Design Twitter: what data structure for the news feed?
A85: Pattern 08 — Heap (8.2 K-Way Merge). Merge k sorted tweet lists (one per followed user) using a max-heap by timestamp. Fetch at most 10 most recent tweets. O(followed * log(followed)) per fetch.

Q86: What is the Pythonic way to implement a max-heap?
A86: Python's `heapq` is a min-heap. For max-heap, push negated values (`-x`). Pop and negate to retrieve. For objects, use tuples `(-priority, item)`.

Q87: Why is heapify O(n) and not O(n log n)?
A87: Because heapify processes nodes from the bottom up. Most nodes are at lower levels and sift down a short distance. The math sums to O(n) rather than n individual O(log n) insertions.

---

## Pattern 09: Backtracking

Q88: Subsets: what is the recursive decision at each element?
A88: Pattern 09 — Backtracking (9.1 Subsets). For each element, choose to include it or not. Recurse to next index. When index == len(nums), add current subset to results. O(2^n) subsets.

Q89: Permutations: how does the recursive state differ from subsets?
A89: Pattern 09 — Backtracking (9.2 Permutations). Every element must be used exactly once. Use a `used` boolean array. For each unused element, include it, mark used, recurse, unmark. O(n!) permutations.

Q90: Combination Sum (unlimited usage): what is the loop structure?
A90: Pattern 09 — Backtracking (9.3 Combinations). Recursive function takes `start_index`. Loop from `start_index` to end. If `target - nums[i] >= 0`, include `nums[i]`, recurse with same `i` (unlimited). Backtrack.

Q91: Combination Sum II (each number used once): what prevents duplicates?
A91: Pattern 09 — Backtracking (9.3 Combinations). Sort first. Skip `nums[i]` if `i > start` and `nums[i] == nums[i-1]` to avoid duplicate combinations at the same level. Recurse with `i + 1`.

Q92: Palindrome Partitioning: what are the two checks?
A92: Pattern 09 — Backtracking (9.4 Constraint Satisfaction). 1) Is the current substring a palindrome? 2) If yes, add it to the path and recurse on the remainder. Backtrack and try longer substrings.

Q93: N-Queens: what does the `is_valid` helper check?
A93: Pattern 09 — Backtracking (9.5 Search). For placing a queen at (row, col), check no queen in same column or on either diagonal. Diagonals: `row - col` is constant for one, `row + col` for the other. Use sets.

Q94: Word Search: what makes backtracking slow, and how do you optimize?
A94: Pattern 09 — Backtracking (9.5 Search). Mark board cell as visited (e.g., temp modify to '#'), recurse in 4 directions, restore. Prune early if first character doesn't match. No further optimization needed for standard constraints.

Q95: What is the difference between backtracking and DFS?
A95: Backtracking IS DFS with explicit undo (restore state). DFS explores paths in a graph; backtracking explores possibilities in a state space, undoing choices to explore alternatives. The undo step is the defining feature.

Q96: When should you use memoization with backtracking?
A96: When the same subproblem is reached via different paths (overlapping subproblems). Convert to DP. Pure backtracking is for non-overlapping state spaces (permutations, subsets, N-queens).

Q97: Generate Parentheses: what are the constraints on open and close counts?
A97: Pattern 09 — Backtracking (9.1 Subsets/Construction). Add `(` if `open < n`. Add `)` if `close < open`. Stop when both reach n. This guarantees valid strings without needing validation.

---

## Pattern 10: Tries

Q98: Implement Trie: what does each node store?
A98: Pattern 10 — Tries (10.1 Prefix Storage). A hashmap (or array of size 26) of children and a boolean `is_end_of_word`. No need to store the character at the node; the edge represents it.

Q99: Why is a Trie better than a hash set for prefix queries?
A99: Pattern 10 — Tries (10.2 Prefix Search). Hash set: O(n * m) to check all strings for prefix. Trie: O(m) where m is prefix length. Tries win when there are many strings and many prefix queries.

Q100: Word Search II: why put words in a Trie instead of checking each word separately?
A100: Pattern 10 — Tries (10.3 Multi-Pattern). Board DFS explores paths. Trie allows pruning: if the current path is not a prefix of any word, stop exploring. Also collect all matching words in one DFS pass.

Q101: Design Add and Search Words Data Structure: how do you handle '.' wildcard?
A101: Pattern 10 — Tries (10.2 Prefix Search). On '.', recursively search all children. On a letter, follow that child only. The '.' makes search O(26^d) in worst case where d is word length.

Q102: Maximum XOR of Two Numbers in an Array: Trie trick?
A102: Pattern 10 — Tries (10.4 Bit Trie). Build a binary Trie of numbers (bits from MSB to LSB). For each number, greedily try to take the opposite bit at each level to maximize XOR. O(n) time after build.

Q103: What is the space complexity of a Trie with n words of average length m?
A103: O(n * m) in the worst case (no shared prefixes). In practice, it is much less due to prefix sharing. This is the trade-off: space for time on prefix operations.

---

## Pattern 11: Graphs

Q104: Number of Islands: BFS or DFS?
A104: Pattern 11 — Graphs (11.1 Traversal). Either works. DFS is simpler to code recursively. BFS uses a queue and avoids recursion stack limits. Both O(rows * cols) time and space.

Q105: Clone Graph: how do you avoid infinite loops?
A105: Pattern 11 — Graphs (11.2 Clone). Hashmap from original node to cloned node. DFS: if node in map, return clone. Else create clone, add to map, recursively clone neighbors.

Q106: Course Schedule: what graph problem is this?
A106: Pattern 11 — Graphs (11.4 Cycle Detection / Topological Sort). Directed graph. Detect cycle using DFS with states (unvisited, visiting, visited) or Kahn's algorithm (in-degree counting). No cycle = possible to finish all courses.

Q107: Pacific Atlantic Water Flow: why BFS from oceans instead of from land?
A107: Pattern 11 — Graphs (11.1 Multi-Source BFS). Reverse the problem: water flows from ocean inward to higher/equal cells. Find all cells reachable from Pacific and all from Atlantic. Intersection is the answer.

Q108: Rotting Oranges: what is the BFS initialization?
A108: Pattern 11 — Graphs (11.1 Multi-Source BFS). Enqueue ALL initially rotten oranges. BFS level by level. Each level = one minute. Count levels until no fresh oranges remain. If fresh remain, return -1.

Q109: Word Ladder: why BFS and not DFS?
A109: Pattern 11 — Graphs (11.3 Shortest Path). BFS finds the shortest path in an unweighted graph. DFS would explore too deep and not guarantee shortest. Each word is a node; edges connect words differing by one letter.

Q110: What is the difference between adjacency list and adjacency matrix?
A110: Adjacency list: O(V + E) space, good for sparse graphs. Adjacency matrix: O(V^2) space, O(1) edge lookup. Use list for most interview problems; matrix only for dense graphs or when given as grid.

Q111: When do you use DFS vs BFS on a graph?
A111: BFS for shortest path in unweighted graphs, level-order processing, or finding minimum steps. DFS for path existence, topological sort, cycle detection, connected components, or when you need to explore deeply.

Q112: Redundant Connection: how do you detect the extra edge?
A112: Pattern 11 — Graphs (11.5 Union-Find). Union-Find (Disjoint Set Union). Process edges. If two nodes are already connected, this edge is redundant. Return it.

---

## Pattern 12: Advanced Graphs

Q113: Network Delay Time: which algorithm finds the shortest path from source to all nodes?
A113: Pattern 12 — Advanced Graphs (12.1 Shortest Path). Dijkstra's algorithm with a min-heap. Pop closest unvisited node, relax edges. The answer is the maximum distance among all nodes. If any node is unreachable, return -1.

Q114: Why does Dijkstra fail with negative edge weights?
A114: Because it greedily commits to the shortest distance once a node is popped. Negative weights from other paths could provide a shorter route later. Use Bellman-Ford for negative weights (no negative cycles).

Q115: Minimum Spanning Tree: Prim's vs Kruskal's?
A115: Pattern 12 — Advanced Graphs (12.2 MST). Prim's: grow tree from a node, add cheapest edge crossing the cut. O(E log V) with heap. Kruskal's: sort all edges, add cheapest that doesn't form cycle (Union-Find). O(E log E).

Q116: Cheapest Flights Within K Stops: why modified Bellman-Ford?
A116: Pattern 12 — Advanced Graphs (12.3 Constrained Shortest Path). Standard shortest path ignores stops. Modified Bellman-Ford relaxes edges for exactly K iterations, tracking distances per stop count. Or use BFS with state `(node, stops)`.

Q117: Reconstruct Itinerary: what graph traversal with edge removal?
A117: Pattern 12 — Advanced Graphs (12.4 Eulerian Path). Hierholzer's algorithm. DFS from start, always take lexicographically smallest next airport. Post-order append to itinerary. Reverse at end. Remove used edges.

Q118: Alien Dictionary: what graph do you build?
A118: Pattern 12 — Advanced Graphs (12.5 Topological Sort). Compare adjacent words to find character order edges. Topological sort (Kahn's or DFS) gives the alien alphabet. Detect cycle = invalid order.

Q119: What is the time complexity of Dijkstra with a binary heap?
A119: O(E log V). Each edge may cause a heap update (decrease-key), which is O(log V). With a Fibonacci heap, it is O(E + V log V), but that is rarely needed in interviews.

Q120: When do you use Floyd-Warshall instead of Dijkstra?
A120: When you need all-pairs shortest paths in a dense graph. Floyd-Warshall is O(V^3) and handles negative weights (no negative cycles). Dijkstra from every node is O(V * E log V), which can be better for sparse graphs.

---

## Pattern 13: 1-D Dynamic Programming

Q121: Climbing Stairs: what is the recurrence relation?
A121: Pattern 13 — 1D DP (13.1 Linear). `dp[i] = dp[i-1] + dp[i-2]`. Ways to reach step i = ways from i-1 (single step) + ways from i-2 (double step). Base: `dp[0] = 1, dp[1] = 1`. Fibonacci.

Q122: House Robber: why can't you rob adjacent houses?
A122: Pattern 13 — 1D DP (13.2 Decision). `dp[i] = max(dp[i-1], dp[i-2] + nums[i])`. Either skip house i (take dp[i-1]) or rob it (take dp[i-2] + nums[i]). Adjacent rob triggers alarm.

Q123: Maximum Subarray (Kadane's): what is the state definition?
A123: Pattern 13 — 1D DP (13.3 Kadane). `dp[i]` = maximum subarray sum ending at index i. `dp[i] = max(nums[i], dp[i-1] + nums[i])`. Global max tracks the best `dp[i]`. O(n) time, O(1) space (rolling variable).

Q124: Coin Change (minimum coins): recurrence and base case?
A124: Pattern 13 — 1D DP (13.5 Unbounded Knapsack). `dp[amount] = min(dp[amount], dp[amount - coin] + 1)` for each coin. Base: `dp[0] = 0`, others = infinity. If `dp[amount]` stays infinity, return -1.

Q125: Longest Increasing Subsequence (LIS): O(n^2) DP definition?
A125: Pattern 13 — 1D DP (13.6 LIS). `dp[i]` = length of LIS ending at index i. `dp[i] = max(dp[j] + 1)` for all `j < i` where `nums[j] < nums[i]`. Answer is `max(dp)`. O(n^2). Patience sorting gives O(n log n).

Q126: Partition Equal Subset Sum: what is the subset-sum reduction?
A126: Pattern 13 — 1D DP (13.7 Subset). Total must be even. Target = total / 2. `dp[j]` = can we make sum j? `dp[j] = dp[j] or dp[j - num]`. 1D boolean array. O(n * target) time.

Q127: Word Break: DP state and transition?
A127: Pattern 13 — 1D DP (13.4 String). `dp[i]` = can first i characters be segmented? `dp[i] = any(dp[j] and s[j:i] in word_set)` for `j < i`. Base: `dp[0] = True`. O(n^2 * m) naive, optimized with max word length.

Q128: Decode Ways: what are the valid transitions?
A128: Pattern 13 — 1D DP (13.4 String). `dp[i]` = ways to decode first i chars. Single digit (if `s[i-1] != '0'`): `dp[i] += dp[i-1]`. Two digits (if `10 <= int(s[i-2:i]) <= 26`): `dp[i] += dp[i-2]`. Base: `dp[0] = 1`.

Q129: What is the difference between top-down (memoization) and bottom-up DP?
A129: Top-down: recursive, natural to write from the problem statement, may have recursion overhead. Bottom-up: iterative, often more space-efficient, harder to intuit but easier to optimize space. Both have the same time complexity.

Q130: When can you reduce 2D DP to 1D DP?
A130: When the recurrence only depends on the previous row (or previous column). Overwrite the 1D array in reverse order if the recurrence depends on the same row's earlier elements (like knapsack).

---

## Pattern 14: 2-D Dynamic Programming

Q131: Unique Paths: recurrence relation on grid?
A131: Pattern 14 — 2D DP (14.1 Grid). `dp[i][j] = dp[i-1][j] + dp[i][j-1]`. Ways to reach (i,j) = ways from above + ways from left. Base: first row and first column are all 1s. O(m*n) time, O(n) space with rolling array.

Q132: Longest Common Subsequence (LCS): what does dp[i][j] represent?
A132: Pattern 14 — 2D DP (14.2 String). `dp[i][j]` = LCS of `text1[0:i]` and `text2[0:j]`. If `text1[i-1] == text2[j-1]`: `dp[i][j] = dp[i-1][j-1] + 1`. Else: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`.

Q133: Edit Distance: three operations, what are the transitions?
A133: Pattern 14 — 2D DP (14.2 String). If chars match: `dp[i][j] = dp[i-1][j-1]`. Else: `dp[i][j] = 1 + min(insert: dp[i][j-1], delete: dp[i-1][j], replace: dp[i-1][j-1])`.

Q134: Regular Expression Matching: what do '.' and '*' mean for DP?
A134: Pattern 14 — 2D DP (14.2 String). `dp[i][j]`: does `p[0:j]` match `s[0:i]`? If `p[j-1] == '*': zero occurrences (`dp[i][j-2]`) or one+ if preceding char matches (`dp[i-1][j]`). If match or '.': `dp[i][j] = dp[i-1][j-1]`.

Q135: Best Time to Buy/Sell Stock with Cooldown: what are the states?
A135: Pattern 14 — 2D DP (14.3 State Machine). States: `hold` (have stock), `sold` (just sold), `rest` (no stock, can buy). Transitions: `hold = max(hold, rest - price)`, `sold = hold + price`, `rest = max(rest, sold)`. Answer is max(rest, sold).

Q136: Target Sum: how do you reduce it to subset sum?
A136: Pattern 14 — 2D DP (14.4 Transform). Let P = positive subset, N = negative subset. `P - N = target`, `P + N = total`. So `2P = target + total`. P must be integer. Count subsets with sum P. Use 1D DP.

Q137: Interleaving String: what is the 2D state?
A137: Pattern 14 — 2D DP (14.2 String). `dp[i][j]`: can `s1[0:i]` and `s2[0:j]` interleave to form `s3[0:i+j]`? If `s1[i-1] == s3[i+j-1]`: check `dp[i-1][j]`. If `s2[j-1] == s3[i+j-1]`: check `dp[i][j-1]`.

Q138: Dungeon Game: why do you compute from bottom-right instead of top-left?
A138: Pattern 14 — 2D DP (14.1 Grid). The required health at a cell depends on the minimum health needed in future cells. Compute backward: `dp[i][j] = max(1, min(dp[i+1][j], dp[i][j+1]) - dungeon[i][j])`. Bottom-up from destination.

Q139: What is the space optimization for grid DP when only the previous row is needed?
A139: Keep a 1D array representing the current row. Update it in place from left to right (or right to left depending on recurrence). Reduces space from O(m*n) to O(n).

Q140: What makes a problem a "state machine" DP vs standard 2D DP?
A140: State machine DP has explicit states that represent your condition (e.g., holding stock, not holding, cooldown). The recurrence transitions between states rather than positions. Often reduces to O(n) time with O(1) or O(k) space.

---

## Pattern 15: Greedy

Q141: Maximum Subarray after one deletion: greedy insight?
A141: Pattern 15 — Greedy (15.3 One-Pass Tracking). Track max subarray sum ending at i (no deletion) and max subarray sum ending at i with one deletion. Answer is the max of both across all i.

Q142: Jump Game: greedy condition for reachability?
A142: Pattern 15 — Greedy (15.2 Reachability). Track `max_reach`. For each index, if `i > max_reach`, unreachable. Else `max_reach = max(max_reach, i + nums[i])`. Return `max_reach >= last_index`.

Q143: Jump Game II: greedy to minimize jumps?
A143: Pattern 15 — Greedy (15.2 Reachability). Track `current_end` (farthest reachable with current jumps) and `farthest` (farthest reachable with one more jump). When `i == current_end`, increment jumps and set `current_end = farthest`.

Q144: Gas Station: how do you prove the greedy starting point?
A144: Pattern 15 — Greedy (15.1 Resource Allocation). If total gas >= total cost, a solution exists. Track `tank`. When `tank < 0`, reset start to `i + 1` and tank to 0. The logic: any station between the failed start and current station cannot be a valid start either.

Q145: Hand of Straights: greedy grouping strategy?
A145: Pattern 15 — Greedy (15.1 Resource Allocation). Count frequencies with a min-heap or sorted map. Repeatedly take the smallest card and try to form a consecutive group of size W. If any card in the group is missing, return False.

Q146: Merge Triplets to Form Target: greedy selection?
A146: Pattern 15 — Greedy (15.4 Selection). Only use triplets where each value <= target's corresponding value. Track the max seen for each position. If max equals target, success. Any triplet exceeding target in any position is unusable.

Q147: What is the proof strategy for greedy algorithms in interviews?
A147: Show that making the locally optimal choice does not exclude a globally optimal solution. Common techniques: exchange argument (swap any optimal solution to use the greedy choice), or stay-ahead (greedy is always at least as good).

Q148: When should you NOT use greedy?
A148: When local optimal choices lead to dead ends or suboptimal global results. Classic counterexample: longest path in a graph. If you cannot prove the greedy property, use DP or brute force with pruning.

---

## Pattern 16: Intervals

Q149: Merge Intervals: what is the sort key?
A149: Pattern 16 — Intervals (16.1 Merge). Sort by start time. Iterate: if current.start <= last.end, merge (`last.end = max(last.end, current.end)`). Else add current as new interval. O(n log n) time.

Q150: Insert Interval: cases when new interval overlaps?
A150: Pattern 16 — Intervals (16.2 Insert). Three cases: 1) new interval is before current (no overlap, append current). 2) new interval is after current (append current). 3) overlap: merge (`new.start = min(...)`, `new.end = max(...)`).

Q151: Non-Overlapping Intervals: greedy to remove minimum?
A151: Pattern 16 — Intervals (16.3 Scheduling). Sort by end time. Keep the interval that ends earliest (leaves most room). If next interval overlaps with last kept, skip it. Count skips. O(n log n).

Q152: Meeting Rooms II: how many conference rooms needed?
A152: Pattern 16 — Intervals (16.3 Scheduling). Sort start and end times separately. Two pointers: count active meetings. Increment on start, decrement on end. Max active = min rooms. Or min-heap of end times.

Q153: Minimum Interval to Include Each Query: offline processing trick?
A153: Pattern 16 — Intervals (16.4 Range Queries). Sort intervals by start. Sort queries with original indices. Use a min-heap of `(interval_size, end_time)` for intervals that have started. Pop expired intervals. Answer query with heap top.

Q154: Employee Free Time: how do you find common gaps?
A154: Pattern 16 — Intervals (16.1 Merge). Flatten all intervals into one list, sort by start, merge. The gaps between merged intervals are free times. O(n log n) where n is total intervals across all employees.

Q155: Interval List Intersections: two-pointer approach?
A155: Pattern 16 — Intervals (16.1 Merge). `i` on list A, `j` on list B. Intersection of `A[i]` and `B[j]` exists if `max(starts) <= min(ends)`. Add intersection. Advance the list with the earlier end time.

Q156: What is the most common mistake in interval sorting?
A156: Forgetting to sort by start time. Some problems sort by end time (greedy scheduling). Know which sort key the algorithm requires.

---

## Pattern 17: Math & Geometry

Q157: Rotate Image (matrix 90 degrees): in-place approach?
A157: Pattern 17 — Math & Geometry (17.1 Matrix). Transpose then reverse each row. Or reverse top-bottom then transpose. In-place, O(n^2) time, O(1) extra space.

Q158: Set Matrix Zeroes: O(1) space trick?
A158: Pattern 17 — Math & Geometry (17.1 Matrix). Use first row and first column as markers. Track if first row/col needs zero separately. Then zero based on markers. O(m*n) time, O(1) space.

Q159: Spiral Matrix: boundary tracking?
A159: Pattern 17 — Math & Geometry (17.1 Matrix). Track `top, bottom, left, right`. Traverse right, down, left, up. Shrink boundaries after each direction. Stop when boundaries cross.

Q160: Happy Number: cycle detection method?
A160: Pattern 17 — Math & Geometry (17.2 Number Theory). Compute sum of squared digits. Use Floyd's cycle detection (fast/slow) or a hash set. If 1, happy. If cycle without 1, not happy.

Q161: Plus One: where does the carry propagate?
A161: Pattern 17 — Math & Geometry (17.2 Number Theory). Add 1 to last digit. Propagate carry left while digit == 10. If carry exits the most significant digit, insert 1 at front.

Q162: Pow(x, n): divide and conquer approach?
A162: Pattern 17 — Math & Geometry (17.2 Number Theory). `x^n = x^(n/2) * x^(n/2)` if n even, `x * x^(n//2) * x^(n//2)` if n odd. Handle negative n by computing `1/x^|n|`. O(log n) time.

Q163: Multiply Strings: grade-school multiplication simulation?
A163: Pattern 17 — Math & Geometry (17.2 Number Theory). Result length = len1 + len2. Multiply each digit pair, add to correct position. Handle carry in a second pass. Convert back to string.

Q164: Detect Squares: what do you count?
A164: Pattern 17 — Math & Geometry (17.3 Geometry). For each new point, check all existing points as potential diagonal pairs. If a diagonal pair exists at (dx, dy), the other two corners must exist. Count valid squares.

Q165: What is the GCD formula, and what algorithm computes it?
A165: `gcd(a, b) = gcd(b, a % b)`. Euclidean algorithm. Base case: `gcd(a, 0) = a`. O(log min(a, b)) time.

---

## Pattern 18: Bit Manipulation

Q166: Single Number (others appear twice): what operation?
A166: Pattern 18 — Bit Manipulation (18.1 XOR Properties). XOR all elements. `a ^ a = 0`, `a ^ 0 = a`. Result is the single number. O(n) time, O(1) space.

Q167: Number of 1 Bits (Hamming Weight): Brian Kernighan's algorithm?
A167: Pattern 18 — Bit Manipulation (18.2 Counting). `n &= n - 1` clears the lowest set bit. Count iterations until n == 0. O(number of set bits) time.

Q168: Counting Bits: DP approach for 0 to n?
A168: Pattern 18 — Bit Manipulation (18.2 Counting). `dp[i] = dp[i >> 1] + (i & 1)`. Number of bits in i = number of bits in i/2 plus the least significant bit. O(n) time.

Q169: Reverse Bits: standard 32-bit reversal?
A169: Pattern 18 — Bit Manipulation (18.3 Shifting). Iterate 32 times. Result = (result << 1) | (n & 1). n >>= 1. O(1) time (fixed 32 iterations).

Q170: Missing Number (0 to n, one missing): XOR or sum?
A170: Pattern 18 — Bit Manipulation (18.1 XOR). XOR all indices 0 to n with all array values. Missing number remains. Or use expected sum `n*(n+1)/2` minus actual sum. XOR avoids integer overflow issues.

Q171: Sum of Two Integers without +/-: bit operations?
A171: Pattern 18 — Bit Manipulation (18.4 Arithmetic). `a ^ b` gives sum without carry. `(a & b) << 1` gives carry. Repeat until carry is 0. In Python, mask to 32 bits to simulate integer overflow.

Q172: Power of Two: single bit check?
A172: Pattern 18 — Bit Manipulation (18.1 XOR). `n > 0 and (n & (n - 1)) == 0`. Powers of two have exactly one bit set. `n & (n - 1)` clears the lowest set bit; result should be 0.

Q173: What does `n & (n - 1)` do, and why is it useful?
A173: It clears the lowest set bit in n. Useful for: counting set bits, checking if n is power of two, finding the rightmost set bit, iterating over all subsets.

Q174: Generate all subsets of a set using bit manipulation?
A174: Pattern 18 — Bit Manipulation (18.5 Subsets). For `n` elements, iterate `mask` from `0` to `(1 << n) - 1`. Include element `i` if `(mask >> i) & 1 == 1`. O(n * 2^n) time.

---

## Cross-Pattern Blends & Traps

Q175: You see "sorted array" + "find target". Two patterns compete. How do you choose?
A175: If only existence/index is needed: Pattern 04 Binary Search. If pair/triplet sum: Pattern 02 Two Pointers. If count of elements: Pattern 04 with boundary search. The word "sorted" is the trigger for both.

Q176: Problem says "maximum subarray sum with at most one deletion." Which patterns blend?
A176: Pattern 13 Kadane's DP + greedy tracking. Forward Kadane (max ending at i) and backward Kadane (max starting at i). Answer is max of `forward[i-1] + backward[i+1]` across all split points.

Q177: "K closest points to origin." Two valid patterns?
A177: Pattern 08 Heap (min-heap of size k, O(n log k)) or Pattern 04 Binary Search on distance (quickselect, O(n) average). Both are valid; heap is simpler to code correctly under pressure.

Q178: "Longest substring with at most K distinct characters" — what pattern, and what is the trap?
A178: Pattern 05 Sliding Window (variable). Trap: confusing "at most K" with "exactly K". For exactly K, compute `atMost(K) - atMost(K-1)`. Also trap: forgetting to shrink the window when distinct count exceeds K.

Q179: "Course Schedule II" (return valid order). What pattern and extension?
A179: Pattern 11 Graphs (topological sort) via Kahn's algorithm (BFS with in-degree) or DFS post-order. Extension from Cycle Detection (Q106) to actually returning the order.

Q180: "Word Search II" — what three patterns combine?
A180: Pattern 09 Backtracking (DFS on board) + Pattern 10 Trie (prefix pruning) + Pattern 11 Graphs (grid as implicit graph). Build Trie of words first, then DFS from each cell, pruning when prefix not in Trie.

Q181: "Trapping Rain Water" — two valid solutions?
A181: Pattern 02 Two Pointers (two-pass with left_max/right_max, O(n), O(1)) or Pattern 13 DP (precompute max heights from left and right, O(n), O(n)). Two-pointer is preferred for space optimization.

Q182: "Find Median from Data Stream" — what data structures?
A182: Pattern 08 Heap (max-heap for lower half, min-heap for upper half) + careful rebalancing. Or Pattern 04 Order Statistic Tree (rare in interviews). Heap is the standard answer.

Q183: "All nodes distance K in binary tree." What transformation makes this solvable?
A183: Pattern 07 Trees + Pattern 11 Graphs. Convert tree to undirected graph (parent pointers via DFS), then BFS from target node for K levels.

Q184: "Design In-Memory File System." What patterns?
A184: Pattern 07 Trees (directory hierarchy) + Pattern 01 Hashing (path -> node mapping) + Pattern 03 Stack/Recursion (path splitting). Trie of directories is the cleanest model.

Q185: "Range Sum Query 2D - Mutable." What advanced pattern?
A185: Pattern 14 2D DP (prefix sums) + Pattern 01 Design. Immutable: 2D prefix sum. Mutable: Binary Indexed Tree (Fenwick) 2D or Segment Tree 2D. Know both if interviewing for hard system design.

Q186: What is the most common reason a correct algorithm gets "Time Limit Exceeded"?
A186: Using the wrong pattern for the constraints. Example: O(n^2) DP when O(n log n) LIS with binary search exists. Or using BFS when Dijkstra is needed for weighted graphs. Always check constraints before coding.

Q187: You have 25 minutes for a hard problem. What is the 5-10-10 split?
A187: 5 minutes: clarify, examples, edge cases. 10 minutes: discuss brute force + optimal approach with the interviewer. 10 minutes: code + test. Do not start coding until the interviewer agrees with the approach.

Q188: Interviewer says "Can you do better?" What does that signal?
A188: Your current complexity is not optimal. Common leaps: O(n^2) -> O(n log n) via sorting/heap/binary search, O(n^2) -> O(n) via hashmap or two pointers, O(n) -> O(log n) via binary search on answer space.

Q189: What is the "interviewer's hint" decoding guide?
A189: "Think about sorting" -> two pointers or binary search. "What if you preprocessed?" -> hashing or prefix sums. "What about duplicates?" -> edge case you missed. "Is there a greedy approach?" -> optimal substructure exists, try greedy or DP.

Q190: You finish coding with 5 minutes left. What should you do?
A190: Walk through a test case verbally. Trace variable values. Check edge cases: empty input, single element, all same elements, maximum constraints. State time and space complexity. Ask if the interviewer wants you to optimize further.

Q191: What is the difference between O(n) space and O(1) space in a string problem?
A191: O(n) space often means using a hashmap or auxiliary array. O(1) space means modifying in-place or using fixed-size arrays (e.g., 26 letters). Interviewers often ask for O(1) space after you solve with O(n).

Q192: When should you mention that Python's sort is Timsort (O(n log n) stable)?
A192: When stability matters (e.g., sorting objects by key while preserving original order for ties) or when comparing with counting sort/radix sort. Most interviews do not require this detail unless sorting is the core topic.

Q193: What does "expected linear time" usually mean in probability questions?
A193: Algorithms with randomized behavior (e.g., Quickselect, randomized pivot QuickSort) where the average case is linear but worst case is worse. Mention that the bound is probabilistic, not deterministic.

Q194: How do you handle "design" problems with no clear algorithm?
A194: Pattern 01 Design + 06 Linked List + 08 Heap. Identify operations needed. Choose data structures that optimize the hot path. Trade space for time. Example: LRU needs O(1) get/put -> hashmap + doubly linked list.

Q195: What is the one question you should ask before every solution?
A195: "What are the constraints?" N <= 10^6 means O(n log n) or O(n). N <= 20 means O(2^n) backtracking is fine. N <= 10^3 means O(n^2) might pass. Constraints dictate the acceptable complexity class.

Q196: Recursion depth limit in Python is ~1000. What problems does this break?
A196: Deep tree/graph DFS on skewed trees with height > 1000. Solutions: increase recursion limit (`sys.setrecursionlimit`), convert to iterative DFS with explicit stack, or use BFS.

Q197: What is the space complexity of iterative BFS on a binary tree?
A197: O(w) where w is the maximum width of the tree. For a balanced tree, w = O(n/2) at the last level, so O(n). For a skewed tree, w = O(1). This is the queue space, separate from the output.

Q198: You are asked to solve in O(n) time but O(1) space on an array. What technique family?
A198: Pattern 02 Two Pointers (in-place modification), Pattern 01 Hashing with fixed-size array (bounded key space), or Pattern 18 Bit Manipulation (using array indices as hash keys by negating values, if values are in range).

Q199: What is the difference between a subarray and a subsequence?
A199: Subarray: contiguous elements, defined by start and end indices. Subsequence: elements in original order but not necessarily contiguous. Subset: any selection, order does not matter. Know which one the problem asks for.

Q200: Final checklist before saying "I'm done": what five things?
A200: 1) Edge cases tested (empty, single, max, duplicates). 2) Time complexity stated. 3) Space complexity stated. 4) Variable names are clear. 5) No off-by-one errors in loops. Say them out loud.

---

## Complexity Quick-Recall

Q201: What is the time complexity of binary search on n elements?
A201: O(log n). The search space halves each iteration.

Q202: What is the time complexity of building a heap from n elements?
A202: O(n), not O(n log n). Heapify is linear due to the structure of the binary tree.

Q203: What is the time complexity of Dijkstra's algorithm with a binary heap?
A203: O(E log V). Each edge may trigger a heap update.

Q204: What is the time complexity of topological sort (Kahn's algorithm)?
A204: O(V + E). Process each node and edge once.

Q205: What is the time complexity of the Union-Find data structure with path compression and union by rank?
A205: O(alpha(V)) per operation, effectively O(1). Alpha is the inverse Ackermann function, which grows slower than log.

Q206: What is the time complexity of merge sort?
A206: O(n log n) in all cases. Space: O(n) for the auxiliary arrays.

Q207: What is the time complexity of quicksort in the average and worst cases?
A207: Average: O(n log n). Worst (bad pivot): O(n^2). Randomized pivot or median-of-three mitigates this.

Q208: What is the time complexity of finding the LCA in a BST?
A208: O(h), where h is the height. For balanced BST, O(log n). For skewed, O(n).

Q209: What is the space complexity of recursive DFS on a tree?
A209: O(h) for the recursion stack, where h is the height. For skewed trees, this is O(n). For balanced, O(log n).

Q210: What is the time complexity of Kadane's algorithm (maximum subarray)?
A210: O(n) time, O(1) space. Single pass with rolling variables.

Q211: What is the time complexity of the sliding window template?
A211: O(n) time. Each element is visited by `left` and `right` at most once. O(k) or O(1) extra space depending on tracking structure.

Q212: What is the time complexity of backtracking for subsets vs permutations?
A212: Subsets: O(2^n) to generate all subsets, each of size O(n) to copy. Permutations: O(n! * n). Combinations: O(C(n,k) * k).

Q213: What is the time complexity of Trie operations (insert, search, startsWith)?
A213: O(m) where m is the word length. Independent of the number of words in the Trie.

Q214: What is the space complexity of DFS on a graph with a visited set?
A214: O(V) for the visited set + O(V) for the recursion stack in the worst case. Total O(V).

Q215: What is the time complexity of counting sort?
A215: O(n + k) where k is the range of input values. Requires O(k) extra space. Only works for integers or bounded discrete values.

Q216: What is the time complexity of the Sieve of Eratosthenes for primes up to n?
A216: O(n log log n). Space: O(n). Standard for generating all primes up to n.

Q217: What is the time complexity of matrix chain multiplication (2D DP)?
A217: O(n^3) for n matrices. State is `dp[i][j]` = min cost to multiply chain i to j.

Q218: What is the time complexity of the longest increasing subsequence with patience sorting?
A218: O(n log n). Binary search on the `tails` array to find the insertion position.

Q219: What is the time complexity of the edit distance (Levenshtein) algorithm?
A219: O(m * n) time and space. Can optimize space to O(min(m, n)) with rolling arrays.

Q220: What is the amortized time complexity of append in Python lists?
A220: O(1) amortized. Dynamic array doubling ensures that occasional O(n) copies are spread over many O(1) appends.

---

*End of deck. 220 cards total. Review 20 cards per day for 11 days to complete first pass. Mark cards you get wrong and review them again the next day.*
