# Pattern 06: Linked List — Practice Problems

## Reverse & Modify

### 206. Reverse Linked List
**Statement:** Reverse a singly linked list.
**Code:**
```python
def reverse_list(head):
    prev = None
    current = head
    while current:
        nxt = current.next
        current.next = prev
        prev = current
        current = nxt
    return prev
```

### 92. Reverse Linked List II
**Statement:** Reverse nodes between positions left and right.
**Intuition:** Find node before left. Reverse sublist. Reconnect.

### 234. Palindrome Linked List
**Statement:** Check if palindrome. O(n) time, O(1) space.
**Intuition:** Find middle, reverse second half, compare, restore.

### 24. Swap Nodes in Pairs
**Statement:** Swap every two adjacent nodes.
**Intuition:** Iterative with dummy. Swap pairs, advance.

### 25. Reverse Nodes in k-Group
**Statement:** Reverse every k nodes.
**Intuition:** Count k nodes, reverse, connect, repeat.

### 328. Odd Even Linked List
**Statement:** Group all odd indices together, then even.
**Intuition:** Two pointers: odd tail and even tail. Connect at end.

### 143. Reorder List
**Statement:** L0→Ln→L1→Ln-1→L2→Ln-2→...
**Intuition:** Find middle, reverse second half, interleave.

---

## Fast & Slow Pointers

### 141. Linked List Cycle
**Statement:** Detect if cycle exists.
**Code:**
```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### 142. Linked List Cycle II
**Statement:** Find node where cycle begins.
**Intuition:** Distance from head to cycle start = distance from meeting point to cycle start.

### 876. Middle of the Linked List
**Statement:** Return middle node. If two, return second.
**Intuition:** Fast reaches end, slow is at middle.

### 287. Find the Duplicate Number
**Statement:** Array of n+1 integers between 1 and n. Find duplicate.
**Intuition:** Treat array as linked list (value is next index). Floyd's cycle detection.

### 202. Happy Number
**Statement:** Sum of squares of digits. Repeat. Does it reach 1?
**Intuition:** Floyd's cycle detection on sequence.

---

## Merge & Add

### 21. Merge Two Sorted Lists
**Statement:** Merge two sorted linked lists.
**Code:**
```python
def merge_two_lists(l1, l2):
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

### 23. Merge k Sorted Lists
**Statement:** Merge k sorted linked lists.
**Intuition:** Min heap of (value, list). Pop smallest, push next.

### 2. Add Two Numbers
**Statement:** Two numbers represented by linked lists (reverse order). Add them.
**Intuition:** Traverse both, sum with carry, create new node.

### 445. Add Two Numbers II
**Statement:** Forward order representation.
**Intuition:** Stack for both lists. Pop, add, build result in reverse.

### 148. Sort List
**Statement:** Sort linked list in O(n log n) time, O(1) space.
**Intuition:** Merge sort. Find middle, split, merge.

---

## Remove Operations

### 19. Remove Nth Node From End of List
**Statement:** Remove nth node from end.
**Code:**
```python
def remove_nth_from_end(head, n):
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

### 203. Remove Linked List Elements
**Statement:** Remove all elements with given value.
**Intuition:** Dummy head. Skip nodes with target value.

### 83. Remove Duplicates from Sorted List
**Statement:** Remove duplicates so each appears once.
**Intuition:** Compare current with next. Skip duplicates.

### 82. Remove Duplicates from Sorted List II
**Statement:** Remove ALL nodes that have duplicates.
**Intuition:** Skip entire duplicate groups. Need prev pointer.

### 237. Delete Node in a Linked List
**Statement:** Delete given node. Only access to that node.
**Intuition:** Copy next node's value, skip next node.

---

## Complex Operations

### 160. Intersection of Two Linked Lists
**Statement:** Find node where two lists intersect.
**Intuition:** Two pointers. When reaching end, switch to other list. They meet at intersection.

```python
def get_intersection_node(headA, headB):
    a, b = headA, headB
    while a != b:
        a = a.next if a else headB
        b = b.next if b else headA
    return a
```

### 138. Copy List with Random Pointer
**Statement:** Deep copy list with random pointers.
**Intuition:** Interweave: original → copy → original → copy. Set random. Extract.

### 430. Flatten a Multilevel Doubly Linked List
**Statement:** Flatten multilevel doubly linked list.
**Intuition:** DFS with stack. When child exists, push next, connect child.

### 725. Split Linked List in Parts
**Statement:** Split into k consecutive parts.
**Intuition:** Length // k parts of size n, first (length % k) parts get +1.

### 1721. Swapping Nodes in a Linked List
**Statement:** Swap kth node from beginning and end.
**Intuition:** Find kth from start. Use fast pointer to find kth from end simultaneously.

### 707. Design Linked List
**Statement:** Implement MyLinkedList class.
**Intuition:** Singly linked list with size tracking. Index validation.

---

## Near Misses & Pattern Blends

**Pattern Blend: Hash Map + Linked List**
- LRU Cache (146) — hash map + doubly linked list
- LFU Cache (460) — hash map + multiple linked lists

**Pattern Blend: Linked List + Stack**
- Add Two Numbers II (445) — stack for forward order
- Reorder List (143) — can use stack instead of reverse

**Pattern Blend: Linked List + Heap**
- Merge k Sorted Lists (23) — min heap

**Near Miss: Design HashMap (706)**
- Not really a linked list problem
- But uses chaining with linked lists for collision resolution

---

## Mixed Drill Set

1. 206 — Reverse list
2. 141 — Detect cycle
3. 142 — Find cycle start
4. 21 — Merge two sorted
5. 19 — Remove nth from end
6. 160 — Find intersection
7. 234 — Palindrome check
8. 143 — Reorder list
9. 138 — Deep copy with random
10. 25 — Reverse k-group
