# Pattern 06: Linked List

> **Pattern Recognition:** When you see "linked list", "reverse", "cycle", "merge", "reorder", "remove nth" — think pointer manipulation.
>
> **Fundamental Insight:** Linked lists are pure pointer manipulation. There is no random access. Every operation is O(n) unless you maintain extra pointers.

---

## Archetype 6.1: Basic Traversal & Modification

### Recognition Signal
Words: **"reverse", "delete", "insert", "remove", "modify"**

### Template: Reverse
```python
def reverse_list(head):
    prev = None
    current = head
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    return prev
```

### Problems
- Reverse Linked List (LeetCode 206)
- Reverse Linked List II (LeetCode 92) — reverse between positions m and n
- Palindrome Linked List (LeetCode 234) — reverse second half, compare
- Swap Nodes in Pairs (LeetCode 24)
- Reverse Nodes in k-Group (LeetCode 25)

---

## Archetype 6.2: Fast & Slow Pointers (Floyd's)

### Recognition Signal
Words: **"middle", "cycle", "detect loop", "circular", "duplicate number"**

### Core Idea
- Fast moves 2 steps, slow moves 1 step.
- If cycle: fast meets slow.
- Middle: when fast reaches end, slow is at middle.

### Template: Detect Cycle
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

### Template: Find Cycle Start
```python
def detect_cycle(head):
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

### Problems
- Linked List Cycle (LeetCode 141)
- Linked List Cycle II (LeetCode 142)
- Middle of the Linked List (LeetCode 876)
- Happy Number (LeetCode 202) — cycle detection in sequence
- Find the Duplicate Number (LeetCode 287) — Floyd's on array

---

## Archetype 6.3: Merge Operations

### Recognition Signal
Words: **"merge", "combine", "sorted lists", "add two numbers"**

### Template: Merge Two Sorted Lists
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

### Problems
- Merge Two Sorted Lists (LeetCode 21)
- Merge k Sorted Lists (LeetCode 23) — heap or divide-and-conquer
- Add Two Numbers (LeetCode 2) — reverse order digits
- Add Two Numbers II (LeetCode 445) — stack for forward order
- Sort List (LeetCode 148) — merge sort on linked list

---

## Archetype 6.4: Reordering & Rearrangement

### Recognition Signal
Words: **"reorder", "rearrange", "odd even", "partition", "rearrange by position"**

### Problems
- Odd Even Linked List (LeetCode 328)
- Reorder List (LeetCode 143) — find middle, reverse second half, interleave
- Partition List (LeetCode 86) — partition around value x
- Split Linked List in Parts (LeetCode 725)
- Swapping Nodes in a Linked List (LeetCode 1721)

---

## Archetype 6.5: Multi-List / Complex Operations

### Recognition Signal
Words: **"intersection", "copy", "deep copy", "flatten", "random pointer"**

### Problems
- Intersection of Two Linked Lists (LeetCode 160)
- Copy List with Random Pointer (LeetCode 138)
- Flatten a Multilevel Doubly Linked List (LeetCode 430)
- Design Linked List (LeetCode 707)
- Design Browser History (LeetCode 1472) — uses array, not list

---

## Archetype 6.6: Remove Operations

### Recognition Signal
Words: **"remove nth", "remove duplicates", "delete node", "remove elements"**

### Template: Remove Nth from End
```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy
    for _ in range(n + 1):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
```

### Problems
- Remove Nth Node From End of List (LeetCode 19)
- Remove Linked List Elements (LeetCode 203)
- Remove Duplicates from Sorted List (LeetCode 83)
- Remove Duplicates from Sorted List II (LeetCode 82) — remove all duplicates
- Delete Node in a Linked List (LeetCode 237) — given only access to that node

---

## Mastery Checklist
- [ ] Reverse linked list iteratively and recursively
- [ ] Floyd's cycle detection: detect, find start, find length
- [ ] Merge two sorted lists with dummy head
- [ ] Remove nth from end with fast/slow pointers
- [ ] Find middle with fast/slow pointers
- [ ] Copy list with random pointer (interweaving method)
- [ ] Reorder list: middle + reverse + merge
- [ ] Add two numbers with carry propagation

---

## The Dummy Node Trick

**Always use a dummy head when the head might change.**
- Removing first element
- Merging lists
- Any operation that modifies the head

```python
dummy = ListNode(0)
dummy.next = head
# ... do operations ...
return dummy.next
```

This eliminates all special cases for head modification.

---

## Common Traps

**Trap:** Forgetting to handle empty list or single node.
**Fix:** Always check `if not head: return head` first.

**Trap:** Modifying list while traversing without saving next pointer.
**Fix:** Save `next = current.next` before modifying `current.next`.

**Trap:** Off-by-one in fast pointer advance.
**Fix:** For remove nth from end, advance fast `n+1` steps (to maintain gap of n between fast and slow).

**Trap:** Cycle detection — moving fast before checking.
**Fix:** Check `while fast and fast.next:` before advancing.

**Near Miss:** LRU Cache (LeetCode 146)
- Looks like linked list
- But uses doubly linked list + hash map
- Pattern blend: Hash map + doubly linked list
