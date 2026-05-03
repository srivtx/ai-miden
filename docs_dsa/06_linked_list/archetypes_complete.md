# Pattern 06: Linked List — Complete Archetype Map

> **Pattern Recognition:** When you see "linked list", "singly linked", "next pointer", "head node", "in-place" — think linked list manipulation.
>
> **Fundamental Insight:** Most linked list problems can be solved with a combination of: careful pointer rewiring, dummy head sentinel, and/or two pointers moving at different speeds. Draw the rewiring on paper before coding.

---

## Archetype 6.1: Basic Traversal & Modification

### Recognition Signal (10 seconds)
Words: **"reverse", "delete node", "insert node", "remove elements", "in-place"**

The question: **"Modify the structure of a linked list by changing next pointers."**

### Core Structure
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def traverse_and_modify(head):
    dummy = ListNode(0, head)  # Sentinel node
    curr = head
    prev = dummy
    
    while curr:
        # Process curr
        prev = curr
        curr = curr.next
    
    return dummy.next
```

### The Invariant
The `dummy` sentinel ensures we never lose the head, even if the head itself is deleted or reversed. `prev` always trails `curr` by one node, allowing us to rewire `prev.next` at any time.

### Canonical Problem: Reverse Linked List (LeetCode 206)
**Statement:** Reverse a singly linked list.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None
    curr = head
    
    while curr:
        nxt = curr.next  # Save next
        curr.next = prev  # Reverse pointer
        prev = curr       # Move prev forward
        curr = nxt        # Move curr forward
    
    return prev  # New head
```

### Variation Family

**V1: Remove Linked List Elements (LeetCode 203)**
- **Twist:** Remove all nodes with a specific value
- **Change:** Use dummy head. Skip nodes where `curr.val == val` by doing `prev.next = curr.next`
- **Key insight:** Dummy handles removal of head node uniformly

```python
def remove_elements(head, val):
    dummy = ListNode(0, head)
    curr = dummy
    
    while curr.next:
        if curr.next.val == val:
            curr.next = curr.next.next  # Skip the node
        else:
            curr = curr.next
    
    return dummy.next
```

**V2: Remove Duplicates from Sorted List (LeetCode 83)**
- **Twist:** Remove duplicates from sorted list, keep only distinct
- **Change:** Compare `curr.val` with `curr.next.val`. If equal, skip `curr.next`

```python
def delete_duplicates(head):
    curr = head
    while curr and curr.next:
        if curr.val == curr.next.val:
            curr.next = curr.next.next
        else:
            curr = curr.next
    return head
```

**V3: Delete Node in a Linked List (LeetCode 237)**
- **Twist:** Only given access to the node to delete, not the head
- **Change:** Copy next node's value into current node, then delete next node
- **Key insight:** We can't delete the current node without prev, but we can make it a copy of the next node and delete the next node instead

```python
def delete_node(node):
    node.val = node.next.val
    node.next = node.next.next
```

**V4: Insert into a Sorted Circular Linked List (LeetCode 708)**
- **Twist:** Circular linked list, insert a value maintaining order
- **Change:** Handle circular nature. Find insertion point, insert, return head
- **Edge cases:** Insert before head, insert at end (largest), all same values

**Near Miss: Add Two Numbers**
- **Looks like:** Basic traversal
- **But:** Requires carrying digits and handling different length lists
- **Lesson:** Some "basic" traversals need additional state (carry, multiple pointers)

---

## Archetype 6.2: Fast & Slow Pointers

### Recognition Signal (10 seconds)
Words: **"cycle", "middle node", "detect loop", "circular", "entry point"**

The question: **"Find something about the structure of the list that requires knowing position relative to length."**

### Core Structure
```python
def fast_slow(head):
    slow = fast = head
    
    while fast and fast.next:
        slow = slow.next       # 1 step
        fast = fast.next.next  # 2 steps
    
    # When fast reaches end, slow is at middle
    # If they meet, there is a cycle
    return slow
```

### The Invariant
When `fast` moves 2 steps for every 1 step of `slow`:
- If no cycle: `fast` reaches end, `slow` is at middle (or first middle for even length)
- If cycle exists: `fast` and `slow` will eventually meet inside the cycle
- After meeting: reset one pointer to head, move both at 1 step. They meet at cycle entry.

### Canonical Problem: Linked List Cycle II (LeetCode 142)
**Statement:** Given head, return node where cycle begins. Return None if no cycle.

```python
def detect_cycle(head):
    if not head or not head.next:
        return None
    
    # Phase 1: Detect if cycle exists
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # No cycle
    
    # Phase 2: Find entry point
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    
    return slow
```

### Variation Family

**V1: Middle of the Linked List (LeetCode 876)**
- **Twist:** Return middle node
- **Change:** When fast reaches end, slow is at middle. For even length, returns second middle

```python
def middle_node(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

**V2: Happy Number (LeetCode 202)**
- **Twist:** Detect cycle in sequence of digit squares
- **Change:** The "list" is implicit. Use slow/fast on the number sequence

```python
def is_happy(n):
    def get_next(num):
        total = 0
        while num > 0:
            digit = num % 10
            total += digit * digit
            num //= 10
        return total
    
    slow = fast = n
    while fast != 1:
        slow = get_next(slow)
        fast = get_next(get_next(fast))
        if slow == fast and slow != 1:
            return False
    return True
```

**V3: Find the Duplicate Number (LeetCode 287)**
- **Twist:** Array treated as linked list (value at index i points to index nums[i])
- **Change:** Floyd's cycle detection on implicit linked list in array

```python
def find_duplicate(nums):
    # Phase 1: Find intersection in cycle
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    
    # Phase 2: Find entrance
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
```

**V4: Palindrome Linked List (LeetCode 234)**
- **Twist:** Check if list is palindrome in O(n) time and O(1) space
- **Change:** Find middle with slow/fast, reverse second half, compare, restore

**Near Miss: Remove Nth Node from End of List**
- **Looks like:** Fast/slow
- **But:** Actually a fixed-distance two-pointer problem (gap of n nodes)
- **Lesson:** Fast/slow is about ratio of speeds, not fixed gap

---

## Archetype 6.3: Merge Operations

### Recognition Signal (10 seconds)
Words: **"merge two sorted lists", "add two numbers", "combine", "interleave"**

The question: **"Combine two or more linked lists into one while preserving some order."**

### Core Structure
```python
def merge_lists(l1, l2):
    dummy = ListNode(0)
    tail = dummy
    
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    
    tail.next = l1 or l2  # Attach remainder
    return dummy.next
```

### The Invariant
The `dummy` head provides a stable insertion point. `tail` always points to the last node of the merged result. We always append the smaller (or appropriate) node and advance that list's pointer.

### Canonical Problem: Merge Two Sorted Lists (LeetCode 21)
**Statement:** Merge two sorted linked lists and return it as a new sorted list.

```python
def merge_two_lists(l1, l2):
    dummy = ListNode(0)
    tail = dummy
    
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    
    tail.next = l1 if l1 else l2
    return dummy.next
```

### Variation Family

**V1: Add Two Numbers (LeetCode 2)**
- **Twist:** Two numbers represented by linked lists (digits in reverse order)
- **Change:** Add digit by digit with carry. Create new nodes for result

```python
def add_two_numbers(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    carry = 0
    
    while l1 or l2 or carry:
        v1 = l1.val if l1 else 0
        v2 = l2.val if l2 else 0
        total = v1 + v2 + carry
        
        carry = total // 10
        curr.next = ListNode(total % 10)
        curr = curr.next
        
        if l1: l1 = l1.next
        if l2: l2 = l2.next
    
    return dummy.next
```

**V2: Merge k Sorted Lists (LeetCode 23)**
- **Twist:** Merge k sorted linked lists
- **Change:** Use a min-heap of (value, list_index, node). Pop smallest, push its next
- **Key insight:** Heap gives O(log k) per element, total O(N log k)

```python
import heapq

def merge_k_lists(lists):
    dummy = ListNode(0)
    curr = dummy
    heap = []
    
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    
    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    
    return dummy.next
```

**V3: Merge In Between Linked Lists (LeetCode 1669)**
- **Twist:** Remove nodes from list1 between positions a and b, insert list2 there
- **Change:** Find nodes at positions a-1 and b+1, wire in list2

**Near Miss: Intersection of Two Linked Lists**
- **Looks like:** Merge
- **But:** Finding common node, not creating a merged list. Uses length difference or two-pointer swap
- **Lesson:** "Two lists" does not always mean "merge them"

---

## Archetype 6.4: Reordering

### Recognition Signal (10 seconds)
Words: **"reorder", "rearrange", "odd even", "reverse in groups", "zigzag"**

The question: **"Change the order of nodes without changing their values."**

### Core Structure
```python
def reorder(head):
    # Step 1: Find middle
    # Step 2: Reverse second half
    # Step 3: Merge/interleave two halves
    pass
```

### The Invariant
Most reordering problems decompose into: find middle, reverse a portion, then interleave or reconnect. Each sub-operation is O(n) and O(1) space.

### Canonical Problem: Reorder List (LeetCode 143)
**Statement:** Reorder list to L0 -> Ln -> L1 -> Ln-1 -> L2 -> Ln-2 ...

```python
def reorder_list(head):
    if not head or not head.next:
        return
    
    # Step 1: Find middle
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    
    # Step 2: Reverse second half
    prev = None
    curr = slow.next
    slow.next = None  # Split into two lists
    
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    
    # Step 3: Interleave
    first, second = head, prev
    while second:
        nxt1, nxt2 = first.next, second.next
        first.next = second
        second.next = nxt1
        first, second = nxt1, nxt2
```

### Variation Family

**V1: Odd Even Linked List (LeetCode 328)**
- **Twist:** Group all odd-indexed nodes followed by even-indexed nodes
- **Change:** Two pointers: odd and even. Traverse, linking odds together and evens together. Connect odd tail to even head

```python
def odd_even_list(head):
    if not head:
        return head
    
    odd = head
    even = head.next
    even_head = even
    
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    
    odd.next = even_head
    return head
```

**V2: Reverse Nodes in a k-Group (LeetCode 25)**
- **Twist:** Reverse nodes k at a time
- **Change:** Count k nodes, reverse that segment, connect previous segment to new head
- **Key insight:** Use a dummy node and track the node before each group

```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    
    while True:
        # Check if there are k nodes
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next
        
        # Reverse the group
        prev = kth.next
        curr = group_prev.next
        while curr != group_next:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        
        # Move group_prev
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp
```

**V3: Swap Nodes in Pairs (LeetCode 24)**
- **Twist:** Swap every two adjacent nodes
- **Change:** Reverse k-group with k=2, but can be simpler

**Near Miss: Rotate List**
- **Looks like:** Reordering
- **But:** Requires finding length and connecting tail to head, then finding new tail
- **Lesson:** Rotation is a single shift, not interleaving

---

## Archetype 6.5: Multi-List Operations

### Recognition Signal (10 seconds)
Words: **"intersection", "copy with random", "deep copy", "flatten", "union"**

The question: **"Operate across multiple linked lists or complex node structures."**

### Core Structure
```python
# Often uses hash map for O(1) lookup of corresponding nodes
def multi_list_operation(head):
    node_map = {}  # old_node -> new_node
    # First pass: create all nodes
    # Second pass: connect next and random pointers
```

### The Invariant
When dealing with multiple lists or complex structures, a hash map from old nodes to new nodes ensures O(1) correlation. For intersection problems, aligning lengths or using two-pointer swap handles asymmetry.

### Canonical Problem: Copy List with Random Pointer (LeetCode 138)
**Statement:** Deep copy a linked list where each node has `val`, `next`, and `random` pointers.

```python
class Node:
    def __init__(self, x, next=None, random=None):
        self.val = int(x)
        self.next = next
        self.random = random

def copy_random_list(head):
    if not head:
        return None
    
    # Map old nodes to new nodes
    old_to_new = {}
    
    # First pass: create all nodes
    curr = head
    while curr:
        old_to_new[curr] = Node(curr.val)
        curr = curr.next
    
    # Second pass: connect pointers
    curr = head
    while curr:
        if curr.next:
            old_to_new[curr].next = old_to_new[curr.next]
        if curr.random:
            old_to_new[curr].random = old_to_new[curr.random]
        curr = curr.next
    
    return old_to_new[head]
```

### Variation Family

**V1: Intersection of Two Linked Lists (LeetCode 160)**
- **Twist:** Find node where two lists intersect
- **Change:** Two pointers: when one reaches end, redirect to other list's head. They meet at intersection (or both become None)
- **Key insight:** a + common + b = b + common + a, so both pointers traverse same total distance

```python
def get_intersection_node(headA, headB):
    a, b = headA, headB
    while a != b:
        a = a.next if a else headB
        b = b.next if b else headA
    return a
```

**V2: Flatten a Multilevel Doubly Linked List (LeetCode 430)**
- **Twist:** Nodes have `child` pointers to separate lists
- **Change:** DFS/stack. When encountering child, flatten it and insert between current and next

```python
def flatten(head):
    if not head:
        return head
    
    pseudo_head = Node(0, None, head, None)
    prev = pseudo_head
    stack = [head]
    
    while stack:
        curr = stack.pop()
        prev.next = curr
        curr.prev = prev
        
        if curr.next:
            stack.append(curr.next)
        if curr.child:
            stack.append(curr.child)
            curr.child = None
        
        prev = curr
    
    pseudo_head.next.prev = None
    return pseudo_head.next
```

**Near Miss: Linked List Cycle**
- **Looks like:** Multi-list (two pointers)
- **But:** Single list, fast/slow is about cycle detection, not cross-list operations
- **Lesson:** Multiple pointers on one list != multi-list operations

---

## Archetype 6.6: Remove Operations

### Recognition Signal (10 seconds)
Words: **"remove nth from end", "remove duplicates", "remove elements", "delete"**

The question: **"Remove specific nodes based on position or value criteria."**

### Core Structure
```python
def remove_operation(head, target):
    dummy = ListNode(0, head)
    # Use either:
    # - fast/slow with gap for "nth from end"
    # - single pointer with value check for "remove by value"
    return dummy.next
```

### The Invariant
The dummy sentinel is essential when the head itself might be removed. For "nth from end", maintaining a fixed gap between fast and slow pointers ensures slow lands exactly on the node before the target when fast reaches the end.

### Canonical Problem: Remove Nth Node From End of List (LeetCode 19)
**Statement:** Remove the nth node from the end of the list.

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    
    # Move fast n+1 steps ahead
    for _ in range(n + 1):
        fast = fast.next
    
    # Move together until fast reaches end
    while fast:
        fast = fast.next
        slow = slow.next
    
    # slow is at node before target
    slow.next = slow.next.next
    return dummy.next
```

### Variation Family

**V1: Remove Duplicates from Sorted List II (LeetCode 82)**
- **Twist:** Remove ALL nodes that have duplicates, keeping only distinct numbers
- **Change:** Use dummy. Track if current node has duplicates by checking next

```python
def delete_duplicates(head):
    dummy = ListNode(0, head)
    prev = dummy
    
    while prev.next and prev.next.next:
        if prev.next.val == prev.next.next.val:
            val = prev.next.val
            while prev.next and prev.next.val == val:
                prev.next = prev.next.next
        else:
            prev = prev.next
    
    return dummy.next
```

**V2: Remove Zero Sum Consecutive Nodes (LeetCode 1171)**
- **Twist:** Remove consecutive sequences that sum to zero
- **Change:** Prefix sum + hash map. If same prefix sum seen twice, nodes between them sum to zero

```python
def remove_zero_sum_sublists(head):
    dummy = ListNode(0, head)
    prefix_sum = 0
    sum_map = {}
    
    # First pass: record last occurrence of each prefix sum
    curr = dummy
    while curr:
        prefix_sum += curr.val
        sum_map[prefix_sum] = curr
        curr = curr.next
    
    # Second pass: skip to last occurrence
    prefix_sum = 0
    curr = dummy
    while curr:
        prefix_sum += curr.val
        curr.next = sum_map[prefix_sum].next
        curr = curr.next
    
    return dummy.next
```

**V3: Swapping Nodes in a Linked List (LeetCode 1721)**
- **Twist:** Swap values of kth node from beginning and kth node from end
- **Change:** Find kth from start, then find kth from end in same pass using gap technique. Swap values

**Near Miss: Delete Node in a Linked List (237)**
- **Looks like:** Remove operation
- **But:** No access to head or previous node. Requires value-copy trick
- **Lesson:** "Remove" implies different techniques depending on available access

---

## Pattern 06 Mastery Checklist

Before moving to Pattern 07, confirm you can:

- [ ] Reverse a linked list iteratively and recursively
- [ ] Use dummy head sentinel for all deletion problems
- [ ] Detect cycle and find entry point with Floyd's algorithm
- [ ] Find middle node with slow/fast pointers
- [ ] Merge two sorted lists in O(n) time
- [ ] Add two numbers represented as linked lists
- [ ] Reorder list: find middle, reverse half, interleave
- [ ] Copy list with random pointer using hash map
- [ ] Find intersection of two lists with two-pointer swap
- [ ] Remove nth node from end with gap pointers
- [ ] Remove ALL duplicates from sorted list (keep only distinct)
- [ ] Distinguish: when to use dummy, when to use fast/slow, when to use hash map

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Forgetting dummy head | Head node removal is a special case | Always use `dummy = ListNode(0, head)` |
| Not updating prev pointer | Pointer rewiring leaves gaps | Draw the rewiring: `prev.next = curr.next` |
| Fast/slow off by one | Wrong middle node or missed cycle | `while fast and fast.next:` for middle; `while fast and fast.next:` for cycle |
| Memory leak in reversal | Losing reference to remaining list | Save `nxt = curr.next` BEFORE rewiring |
| Not handling single node | Null pointer exception | Add `if not head or not head.next: return head` guard |
| Confusing "kth from end" indexing | Removing wrong node | Gap is `n+1` so slow lands on node BEFORE target |
| Modifying list while iterating | Skipping nodes or infinite loop | Save next pointer before any rewiring |

---

## Pattern Blends (What Comes Next)

Linked list does not live in isolation. It blends with:

- **Two Pointers:** Fast/slow, fixed-gap, two-pointer swap for intersection
- **Hash Map:** Node correlation in copy with random pointer, prefix sum mapping
- **Heap:** Merge k sorted lists
- **Recursion:** Reverse list recursively, merge sort on linked list
- **Stack:** Flatten multilevel list, check palindrome with stack

---

*Next: Pattern 07 — Trees*

(End of file)
