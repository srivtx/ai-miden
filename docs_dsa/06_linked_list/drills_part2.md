# Pattern 06: Linked List — Drills Part 2

> 5 Warm-ups + 10 Core Drills

---

## Warm-Ups

### 1. LeetCode 206. Reverse Linked List
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Warm-Up
**Statement:** Reverse a singly linked list.
**Why it fits:** This is the fundamental linked list operation. We iteratively rewire three pointers: `prev`, `current`, and `next`.
**The Twist:** None — every linked list problem builds on this pattern.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    prev = None
    current = head
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    return prev
```

### 2. LeetCode 21. Merge Two Sorted Lists
**Archetype:** 6.3 Merge Operations
**Type:** Warm-Up
**Statement:** Merge two sorted linked lists into a single sorted list.
**Why it fits:** We use a dummy head to simplify edge cases, then iteratively attach the smaller node to the result list.
**The Twist:** The dummy head eliminates all special-case handling for empty input lists or when the head changes.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_two_lists(l1: ListNode, l2: ListNode) -> ListNode:
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

### 3. LeetCode 141. Linked List Cycle
**Archetype:** 6.2 Fast & Slow Pointers
**Type:** Warm-Up
**Statement:** Determine if a linked list has a cycle.
**Why it fits:** Floyd's cycle detection: fast moves 2 steps, slow moves 1. If they meet, there is a cycle.
**The Twist:** The loop condition must check both `fast` and `fast.next` before advancing to avoid NoneType errors.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def has_cycle(head: ListNode) -> bool:
    if not head or not head.next:
        return False
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### 4. LeetCode 876. Middle of the Linked List
**Archetype:** 6.2 Fast & Slow Pointers
**Type:** Warm-Up
**Statement:** Return the middle node of the linked list.
**Why it fits:** When fast reaches the end, slow is at the middle. Fast moves 2 steps for every 1 step of slow.
**The Twist:** For an even-length list, this returns the second middle node (the preferred LeetCode behavior).
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def middle_node(head: ListNode) -> ListNode:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

### 5. LeetCode 203. Remove Linked List Elements
**Archetype:** 6.6 Remove Operations
**Type:** Warm-Up
**Statement:** Remove all elements with a given value from the linked list.
**Why it fits:** We use a dummy head because the head itself might need removal. Single pass through the list.
**The Twist:** Without a dummy head, you would need separate logic for removing the first element.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_elements(head: ListNode, val: int) -> ListNode:
    dummy = ListNode(0, head)
    current = dummy
    while current.next:
        if current.next.val == val:
            current.next = current.next.next
        else:
            current = current.next
    return dummy.next
```

---

## Core Drills

### 6. LeetCode 19. Remove Nth Node From End of List
**Archetype:** 6.6 Remove Operations
**Type:** Core Drill
**Statement:** Remove the nth node from the end of the list.
**Why it fits:** Fast and slow pointers maintain a gap of n. When fast reaches the end, slow is at the node before the one to remove.
**The Twist:** We advance fast `n+1` steps (including the dummy node) so that slow ends up at the predecessor of the target node.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_nth_from_end(head: ListNode, n: int) -> ListNode:
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
```

### 7. LeetCode 92. Reverse Linked List II
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Core Drill
**Statement:** Reverse the nodes of the list from position left to position right (1-indexed).
**Why it fits:** We find the node at position `left - 1`, then reverse the sublist of length `right - left + 1`, and reconnect the reversed portion.
**The Twist:** We must save pointers to the node before the reversal and the first node of the reversal (which becomes the last), to reconnect properly.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_between(head: ListNode, left: int, right: int) -> ListNode:
    if not head or left == right:
        return head
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next

    current = prev.next
    # Reverse nodes from left to right
    for _ in range(right - left):
        next_node = current.next
        current.next = next_node.next
        next_node.next = prev.next
        prev.next = next_node
    return dummy.next
```

### 8. LeetCode 142. Linked List Cycle II
**Archetype:** 6.2 Fast & Slow Pointers
**Type:** Core Drill
**Statement:** Return the node where the cycle begins.
**Why it fits:** After detecting the cycle with Floyd's algorithm, reset slow to the head. Both pointers move 1 step; they meet at the cycle start.
**The Twist:** The mathematical insight: distance from head to cycle start equals distance from meeting point to cycle start.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detect_cycle(head: ListNode) -> ListNode:
    if not head or not head.next:
        return None
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None

    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    return slow
```

### 9. LeetCode 2. Add Two Numbers
**Archetype:** 6.3 Merge Operations
**Type:** Core Drill
**Statement:** Add two numbers represented by linked lists (digits stored in reverse order).
**Why it fits:** We simulate elementary addition digit by digit, carrying over to the next position.
**The Twist:** The lists may have different lengths, and a final carry may create an additional node.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def add_two_numbers(l1: ListNode, l2: ListNode) -> ListNode:
    dummy = ListNode(0)
    current = dummy
    carry = 0
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        total = val1 + val2 + carry
        carry = total // 10
        current.next = ListNode(total % 10)
        current = current.next
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next
    return dummy.next
```

### 10. LeetCode 24. Swap Nodes in Pairs
**Archetype:** 6.1 Basic Traversal & Modification
**Type:** Core Drill
**Statement:** Swap every two adjacent nodes and return the head.
**Why it fits:** Iterative swapping requires careful pointer rewiring. We track the node before each pair to reconnect the list after swapping.
**The Twist:** The first pair changes the head, so a dummy node is essential.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def swap_pairs(head: ListNode) -> ListNode:
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next and prev.next.next:
        first = prev.next
        second = prev.next.next
        # Swap
        prev.next = second
        first.next = second.next
        second.next = first
        prev = first
    return dummy.next
```

### 11. LeetCode 83. Remove Duplicates from Sorted List
**Archetype:** 6.6 Remove Operations
**Type:** Core Drill
**Statement:** Remove duplicates from a sorted linked list so each element appears only once.
**Why it fits:** Single pass: if the next node has the same value, skip it. The sorted property guarantees duplicates are adjacent.
**The Twist:** We only keep the first occurrence of each value and skip all subsequent duplicates.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def delete_duplicates(head: ListNode) -> ListNode:
    current = head
    while current and current.next:
        if current.val == current.next.val:
            current.next = current.next.next
        else:
            current = current.next
    return head
```

### 12. LeetCode 328. Odd Even Linked List
**Archetype:** 6.4 Reordering
**Type:** Core Drill
**Statement:** Group all odd-indexed nodes followed by even-indexed nodes.
**Why it fits:** Two pointers track the tail of the odd list and the tail of the even list. We traverse once, appending nodes to the appropriate list.
**The Twist:** Must preserve relative order within odd and even groups; after traversal, connect odd tail to even head.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def odd_even_list(head: ListNode) -> ListNode:
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

### 13. LeetCode 143. Reorder List
**Archetype:** 6.4 Reordering
**Type:** Core Drill
**Statement:** Reorder the list to L0 -> Ln -> L1 -> Ln-1 -> ...
**Why it fits:** Decompose into three sub-problems: find the middle, reverse the second half, and interleave the two halves.
**The Twist:** This is three standard linked list patterns combined into one problem. Each step must be done carefully to avoid losing references.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reorder_list(head: ListNode) -> None:
    if not head or not head.next:
        return

    # Step 1: Find middle
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next

    # Step 2: Reverse second half
    prev = None
    current = slow.next
    slow.next = None  # Split list
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp

    # Step 3: Interleave
    first = head
    second = prev
    while second:
        tmp1 = first.next
        tmp2 = second.next
        first.next = second
        second.next = tmp1
        first = tmp1
        second = tmp2
```

### 14. LeetCode 160. Intersection of Two Linked Lists
**Archetype:** 6.5 Multi-List Operations
**Type:** Core Drill
**Statement:** Find the node at which the intersection of two linked lists begins.
**Why it fits:** Two pointers traverse both lists. When reaching the end of one list, they switch to the head of the other. They meet at the intersection.
**The Twist:** The switching mechanism equalizes the total path lengths, so both pointers traverse exactly the same number of nodes before meeting.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def get_intersection_node(headA: ListNode, headB: ListNode) -> ListNode:
    if not headA or not headB:
        return None
    ptr_a = headA
    ptr_b = headB
    while ptr_a != ptr_b:
        ptr_a = ptr_a.next if ptr_a else headB
        ptr_b = ptr_b.next if ptr_b else headA
    return ptr_a
```

### 15. LeetCode 82. Remove Duplicates from Sorted List II
**Archetype:** 6.6 Remove Operations
**Type:** Core Drill
**Statement:** Remove all nodes that have duplicate values, leaving only distinct numbers.
**Why it fits:** We use a dummy head and track whether the current node should be kept. If a value repeats, we skip the entire group.
**The Twist:** Unlike LeetCode 83, we remove ALL occurrences of duplicate values, not just the extras.
**Code Skeleton:**
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def delete_duplicates_ii(head: ListNode) -> ListNode:
    dummy = ListNode(0, head)
    prev = dummy
    current = head
    while current:
        # Check if current is the start of duplicates
        if current.next and current.val == current.next.val:
            # Skip all nodes with this value
            val = current.val
            while current and current.val == val:
                current = current.next
            prev.next = current
        else:
            prev = prev.next
            current = current.next
    return dummy.next
```
