# Pattern 06: Linked List — Drills Part 3

> 5 Near Misses + 5 Pattern Blends + 5 Interview Simulations

---

## Near Misses

### 16. LeetCode 234. Palindrome Linked List
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Near Miss
**Statement:** Check if a singly linked list is a palindrome.
**Why it fits:** We find the middle, reverse the second half, compare the two halves, and optionally restore the list.
**The Twist:** O(1) space requires reversing half the list in-place, which temporarily mutates the structure.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def is_palindrome(head: ListNode) -> bool:
    if not head or not head.next:
        return True

    # Find middle
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # Reverse second half
    prev = None
    while slow:
        next_temp = slow.next
        slow.next = prev
        prev = slow
        slow = next_temp

    # Compare
    first = head
    second = prev
    while second:
        if first.val != second.val:
            return False
        first = first.next
        second = second.next
    return True
```

### 17. LeetCode 25. Reverse Nodes in k-Group
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Near Miss
**Statement:** Reverse the nodes of the list k at a time.
**Why it fits:** We reverse sublists of exactly k nodes, using the standard reversal pattern, and reconnect the reversed chunks back into the main list.
**The Twist:** Must first verify that at least k nodes remain before reversing; otherwise, leave them as-is.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_k_group(head: ListNode, k: int) -> ListNode:
    dummy = ListNode(0, head)
    group_prev = dummy

    while True:
        # Check if k nodes exist
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next

        # Reverse current group
        prev = kth.next
        current = group_prev.next
        while current != group_next:
            next_temp = current.next
            current.next = prev
            prev = current
            current = next_temp

        # Move group_prev to the tail of the reversed group (originally the first node)
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp
```

### 18. LeetCode 86. Partition List
**Archetype:** 6.4 Reordering
**Type:** Near Miss
**Statement:** Partition the list around value x so all nodes < x come before all nodes >= x.
**Why it fits:** We build two separate lists (less than x, greater or equal to x), then concatenate them.
**The Twist:** Must preserve the relative order within each partition. Two dummy heads make this straightforward.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def partition(head: ListNode, x: int) -> ListNode:
    less_dummy = ListNode(0)
    greater_dummy = ListNode(0)
    less = less_dummy
    greater = greater_dummy
    current = head
    while current:
        if current.val < x:
            less.next = current
            less = less.next
        else:
            greater.next = current
            greater = greater.next
        current = current.next
    greater.next = None
    less.next = greater_dummy.next
    return less_dummy.next
```

### 19. LeetCode 237. Delete Node in a Linked List
**Archetype:** 6.6 Remove Operations
**Type:** Near Miss
**Statement:** Delete a given node when you only have access to that node (not the head).
**Why it fits:** We copy the next node's value into the current node, then skip the next node.
**The Twist:** This only works if the node is not the tail. You cannot delete the last node without access to the previous node.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def delete_node(node: ListNode) -> None:
    # Copy next node's value
    node.val = node.next.val
    # Skip next node
    node.next = node.next.next
```

### 20. LeetCode 725. Split Linked List in Parts
**Archetype:** 6.4 Reordering
**Type:** Near Miss
**Statement:** Split the list into k consecutive parts as evenly as possible.
**Why it fits:** Compute the length, determine part sizes (base size + 1 for the first `length % k` parts), then cut the list at computed lengths.
**The Twist:** The first `n % k` parts get one extra node. We must carefully sever links after each part.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def split_list_to_parts(head: ListNode, k: int) -> list:
    # Compute length
    length = 0
    current = head
    while current:
        length += 1
        current = current.next

    base_size = length // k
    extra = length % k
    result = []
    current = head
    for i in range(k):
        part_size = base_size + (1 if i < extra else 0)
        result.append(current)
        for _ in range(part_size - 1):
            if current:
                current = current.next
        if current:
            next_part = current.next
            current.next = None
            current = next_part
    return result
```

---

## Pattern Blends

### 21. LeetCode 138. Copy List with Random Pointer
**Archetype:** 6.5 Multi-List Operations
**Type:** Pattern Blend
**Statement:** Create a deep copy of a linked list where each node has a random pointer.
**Why it fits:** We need to map each original node to its copy. The interweaving method inserts copies next to originals, then assigns random pointers, then separates the lists.
**The Twist:** Random pointers require knowing the mapping between original and copy nodes. The interweaving method avoids a hash map.
**Code Skeleton:**
```python
class Node:
    def __init__(self, val=0, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def copy_random_list(head: 'Node') -> 'Node':
    if not head:
        return None

    # Step 1: Interweave copies
    current = head
    while current:
        copy = Node(current.val, current.next)
        current.next = copy
        current = copy.next

    # Step 2: Assign random pointers
    current = head
    while current:
        if current.random:
            current.next.random = current.random.next
        current = current.next.next

    # Step 3: Separate lists
    current = head
    new_head = head.next
    while current:
        copy = current.next
        current.next = copy.next
        if copy.next:
            copy.next = copy.next.next
        current = current.next
    return new_head
```

### 22. LeetCode 445. Add Two Numbers II
**Archetype:** 6.3 Merge Operations
**Type:** Pattern Blend
**Statement:** Add two numbers represented by linked lists (digits stored in forward order).
**Why it fits:** Since addition proceeds from least significant digit, but the lists are stored most-significant-first, we use stacks to reverse the digits implicitly.
**The Twist:** The stack simulates reversal without mutating the input lists. We then build the result list in reverse.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def add_two_numbers_ii(l1: ListNode, l2: ListNode) -> ListNode:
    stack1, stack2 = [], []
    while l1:
        stack1.append(l1.val)
        l1 = l1.next
    while l2:
        stack2.append(l2.val)
        l2 = l2.next

    carry = 0
    result = None
    while stack1 or stack2 or carry:
        val1 = stack1.pop() if stack1 else 0
        val2 = stack2.pop() if stack2 else 0
        total = val1 + val2 + carry
        carry = total // 10
        new_node = ListNode(total % 10)
        new_node.next = result
        result = new_node
    return result
```

### 23. LeetCode 148. Sort List
**Archetype:** 6.3 Merge Operations
**Type:** Pattern Blend
**Statement:** Sort a linked list in O(n log n) time and O(1) space.
**Why it fits:** Merge sort on a linked list. Find the middle with fast/slow pointers, recursively sort halves, then merge.
**The Twist:** Bottom-up merge sort achieves O(1) space by iteratively merging sublists of size 1, 2, 4, etc.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def sort_list(head: ListNode) -> ListNode:
    if not head or not head.next:
        return head

    # Split list into two halves
    slow = head
    fast = head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    mid = slow.next
    slow.next = None

    left = sort_list(head)
    right = sort_list(mid)
    return merge(left, right)

def merge(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    current = dummy
    while l1 and l2:
        if l1.val < l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next
    current.next = l1 or l2
    return dummy.next
```

### 24. LeetCode 430. Flatten a Multilevel Doubly Linked List
**Archetype:** 6.5 Multi-List Operations
**Type:** Pattern Blend
**Statement:** Flatten a multilevel doubly linked list into a single-level sorted doubly linked list.
**Why it fits:** DFS traversal. When a node has a child, we recursively flatten the child list and insert it between the current node and the next node.
**The Twist:** Must maintain the `prev` and `next` pointers of a doubly linked list while splicing in the child list.
**Code Skeleton:**
```python
class Node:
    def __init__(self, val=0, prev=None, next=None, child=None):
        self.val = val
        self.prev = prev
        self.next = next
        self.child = child

def flatten(head: 'Node') -> 'Node':
    if not head:
        return head

    current = head
    while current:
        if current.child:
            # Save next pointer
            next_node = current.next

            # Flatten child and attach
            child_head = flatten(current.child)
            current.next = child_head
            child_head.prev = current
            current.child = None

            # Find tail of flattened child
            tail = child_head
            while tail.next:
                tail = tail.next

            # Reconnect to next_node
            tail.next = next_node
            if next_node:
                next_node.prev = tail

        current = current.next
    return head
```

### 25. LeetCode 1472. Design Browser History
**Archetype:** 6.5 Multi-List Operations
**Type:** Pattern Blend
**Statement:** Implement browser history with visit, back, and forward operations.
**Why it fits:** Conceptually uses a doubly linked list or array with a pointer. Forward history is cleared on a new visit.
**The Twist:** While an array with an index pointer is more efficient, the problem is framed as a linked list traversal with back/forward pointer movement.
**Code Skeleton:**
```python
class BrowserHistory:
    def __init__(self, homepage: str):
        self.history = [homepage]
        self.current = 0
        self.last = 0

    def visit(self, url: str) -> None:
        self.current += 1
        if self.current < len(self.history):
            self.history[self.current] = url
        else:
            self.history.append(url)
        self.last = self.current

    def back(self, steps: int) -> str:
        self.current = max(0, self.current - steps)
        return self.history[self.current]

    def forward(self, steps: int) -> str:
        self.current = min(self.last, self.current + steps)
        return self.history[self.current]
```

---

## Interview Simulations

### 26. LeetCode 23. Merge k Sorted Lists
**Archetype:** 6.3 Merge Operations
**Type:** Interview Sim
**Statement:** Merge k sorted linked lists into one sorted list.
**Why it fits:** Repeatedly extract the minimum node using a min-heap, or use divide-and-conquer pairwise merging.
**The Twist:** Heap gives O(N log k) where N is total nodes. Divide-and-conquer has the same complexity but better constants and no heap overhead.
**Code Skeleton:**
```python
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_k_lists(lists: list[ListNode]) -> ListNode:
    # Use heapq with counter to avoid comparison errors on ListNode objects
    counter = 0
    heap = []
    for l in lists:
        if l:
            heapq.heappush(heap, (l.val, counter, l))
            counter += 1

    dummy = ListNode(0)
    current = dummy
    while heap:
        val, _, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, (node.next.val, counter, node.next))
            counter += 1
    return dummy.next
```

### 27. LeetCode 1171. Remove Zero Sum Consecutive Nodes from Linked List
**Archetype:** 6.6 Remove Operations
**Type:** Interview Sim
**Statement:** Remove consecutive sequences of nodes that sum to zero.
**Why it fits:** We compute prefix sums as we traverse. If the same prefix sum appears twice, the nodes between them sum to zero and can be removed.
**The Twist:** Requires a hash map from prefix sum to node, and a dummy head because the entire list might sum to zero.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_zero_sum_sublists(head: ListNode) -> ListNode:
    dummy = ListNode(0, head)
    prefix_map = {}
    prefix = 0
    current = dummy

    # First pass: record last occurrence of each prefix sum
    while current:
        prefix += current.val
        prefix_map[prefix] = current
        current = current.next

    # Second pass: skip zero-sum segments
    prefix = 0
    current = dummy
    while current:
        prefix += current.val
        current.next = prefix_map[prefix].next
        current = current.next
    return dummy.next
```

### 28. LeetCode 1669. Merge In Between Linked Lists
**Archetype:** 6.5 Multi-List Operations
**Type:** Interview Sim
**Statement:** Remove nodes from list1 between positions a and b, and insert list2 in their place.
**Why it fits:** Find the node at position a-1 and the node at position b+1, then splice list2 between them.
**The Twist:** Straightforward pointer manipulation, but requires accurate traversal to the correct nodes and preserving list2's tail.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_in_between(list1: ListNode, a: int, b: int, list2: ListNode) -> ListNode:
    before_a = list1
    for _ in range(a - 1):
        before_a = before_a.next

    after_b = before_a
    for _ in range(b - a + 2):
        after_b = after_b.next

    # Find tail of list2
    tail2 = list2
    while tail2.next:
        tail2 = tail2.next

    before_a.next = list2
    tail2.next = after_b
    return list1
```

### 29. LeetCode 2181. Merge Nodes in Between Zeros
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Interview Sim
**Statement:** Merge nodes between consecutive zeros into a single node with their sum.
**Why it fits:** Single pass: accumulate the sum between zeros, create a new node when a zero is encountered, and link it into the result list.
**The Twist:** The input starts and ends with zero, so the first and last nodes are always zeros and should not appear in the output.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_nodes(head: ListNode) -> ListNode:
    dummy = ListNode(0)
    current = dummy
    head = head.next  # Skip first zero
    running_sum = 0
    while head:
        if head.val == 0:
            current.next = ListNode(running_sum)
            current = current.next
            running_sum = 0
        else:
            running_sum += head.val
        head = head.next
    return dummy.next
```

### 30. LeetCode 2807. Insert Greatest Common Divisors in Linked List
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Interview Sim
**Statement:** Insert a new node with the GCD of every two adjacent nodes between them.
**Why it fits:** Single pass through the list: for each pair of adjacent nodes, compute GCD, create a new node, and insert it.
**The Twist:** Math operation (GCD) between nodes; straightforward but tests careful traversal and pointer updates.
**Code Skeleton:**
```python
import math

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def insert_greatest_common_divisors(head: ListNode) -> ListNode:
    current = head
    while current and current.next:
        gcd_val = math.gcd(current.val, current.next.val)
        new_node = ListNode(gcd_val, current.next)
        current.next = new_node
        current = new_node.next
    return head
```
