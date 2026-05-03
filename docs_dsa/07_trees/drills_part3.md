# Trees: Drills Part 3 — Near Misses + Pattern Blends + Interview Simulation

---

### Problem 16. 129. Sum Root to Leaf Numbers
**Archetype:** 7.2 Path Problems
**Type:** Near Miss
**Statement:** You are given the root of a binary tree containing digits from 0 to 9 only. Each root-to-leaf path represents a number. Return the total sum of all root-to-leaf numbers.
**Why it fits:** It follows the exact same root-to-leaf DFS pattern as Path Sum, but instead of checking equality at the leaf, you accumulate a base-10 number along the path. The recursive state carries the partial number.
**The Twist:** The accumulated state is a constructed integer (`curr * 10 + node.val`), not a running sum or a path list. Focus on integer accumulation rather than path reconstruction.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def sumNumbers(root: Optional[TreeNode]) -> int:
    def dfs(node, curr):
        if not node:
            return 0
        curr = curr * 10 + node.val
        # Leaf node: return the formed number
        if not node.left and not node.right:
            return curr
        return dfs(node.left, curr) + dfs(node.right, curr)

    return dfs(root, 0)
```

---

### Problem 17. 173. Binary Search Tree Iterator
**Archetype:** 7.1 Basic Traversals
**Type:** Near Miss
**Statement:** Implement the BSTIterator class that represents an iterator over the in-order traversal of a binary search tree (BST).
**Why it fits:** It takes the iterative inorder traversal pattern and amortizes it across multiple `next()` calls. The controlled stack is the same as inorder traversal, but state is persisted in the object.
**The Twist:** Instead of printing all values at once, you lazily reveal the next smallest element. This is a controlled traversal problem disguised as a class design problem.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BSTIterator:
    def __init__(self, root: Optional[TreeNode]):
        self.stack = []
        self._leftmost_inorder(root)

    def _leftmost_inorder(self, node):
        # Push all left nodes onto the stack
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        topmost_node = self.stack.pop()
        # If the node has a right child, push its leftmost branch
        if topmost_node.right:
            self._leftmost_inorder(topmost_node.right)
        return topmost_node.val

    def hasNext(self) -> bool:
        return len(self.stack) > 0
```

---

### Problem 18. 333. Largest BST Subtree
**Archetype:** 7.3 Tree Validation
**Type:** Near Miss
**Statement:** Given the root of a binary tree, find the largest subtree, which is also a Binary Search Tree (BST), and return its size (number of nodes).
**Why it fits:** It combines validation (7.3) with subtree metrics (7.8). For every node, you must determine if its subtree is a BST and, if so, calculate its size. The post-order return type becomes a tuple of (is_bst, size, min_val, max_val).
**The Twist:** Unlike simple validation, you must return metadata up the tree so the parent can decide if its own subtree is a BST. Null nodes are treated as valid BSTs with size 0.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def largestBSTSubtree(root: Optional[TreeNode]) -> int:
    max_size = 0

    def dfs(node):
        nonlocal max_size
        if not node:
            # is_bst, size, min_val, max_val
            return True, 0, float('inf'), float('-inf')
        left_is_bst, left_size, left_min, left_max = dfs(node.left)
        right_is_bst, right_size, right_min, right_max = dfs(node.right)

        if left_is_bst and right_is_bst and left_max < node.val < right_min:
            size = 1 + left_size + right_size
            max_size = max(max_size, size)
            return True, size, min(left_min, node.val), max(right_max, node.val)
        return False, 0, 0, 0

    dfs(root)
    return max_size
```

---

### Problem 19. 314. Binary Tree Vertical Order Traversal
**Archetype:** 7.5 Views & Boundaries
**Type:** Near Miss
**Statement:** Given the root of a binary tree, return the vertical order traversal of its nodes' values.
**Why it fits:** A view problem that requires column indexing and BFS level-order to maintain top-to-bottom ordering. It extends the level-order traversal by adding a horizontal dimension.
**The Twist:** Nodes in the same row and column must be ordered by their level (BFS order), so DFS alone is insufficient. A BFS with column tracking is required.
**Code Skeleton:**
```python
from typing import Optional, List
from collections import deque, defaultdict

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def verticalOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    col_table = defaultdict(list)
    queue = deque([(root, 0)])
    min_col = max_col = 0

    while queue:
        node, col = queue.popleft()
        col_table[col].append(node.val)
        min_col = min(min_col, col)
        max_col = max(max_col, col)
        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))

    return [col_table[x] for x in range(min_col, max_col + 1)]
```

---

### Problem 20. 449. Serialize and Deserialize BST
**Archetype:** 7.6 Serialization & Construction
**Type:** Near Miss
**Statement:** Design an algorithm to serialize and deserialize a binary search tree (BST).
**Why it fits:** It is the BST-optimized version of the general serialization problem. Because BSTs have an ordering property, the preorder traversal alone is sufficient for reconstruction without needing null markers.
**The Twist:** No null markers are needed. During deserialization, use the BST property (all left descendants < val < all right descendants) to split the preorder array into left and right subtrees.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        def preorder(node):
            if not node:
                return
            vals.append(str(node.val))
            preorder(node.left)
            preorder(node.right)
        vals = []
        preorder(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        if not data:
            return None
        vals = list(map(int, data.split(",")))

        def build(lower, upper):
            if not vals or vals[0] < lower or vals[0] > upper:
                return None
            val = vals.pop(0)
            node = TreeNode(val)
            node.left = build(lower, val)
            node.right = build(val, upper)
            return node

        return build(float('-inf'), float('inf'))
```

---

### Problem 21. 437. Path Sum III
**Archetype:** 7.2 Path Problems (Blended with Prefix Sum / Hashing)
**Type:** Pattern Blend
**Statement:** Given the root of a binary tree and an integer targetSum, return the number of paths where the sum of the values along the path equals targetSum.
**Why it fits:** It looks like a tree path problem, but the optimal solution uses the prefix-sum hashmap pattern from arrays. Any downward path can be solved in O(n) time by tracking running sums and their frequencies.
**The Twist:** The path does not need to start at the root or end at a leaf. This removes the easy root-to-leaf constraint and demands a frequency map of prefix sums, just like subarray sum equals k.
**Code Skeleton:**
```python
from typing import Optional
from collections import defaultdict

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def pathSum(root: Optional[TreeNode], targetSum: int) -> int:
    count = 0
    prefix = defaultdict(int)
    prefix[0] = 1  # Empty path sum

    def dfs(node, curr_sum):
        nonlocal count
        if not node:
            return
        curr_sum += node.val
        # If curr_sum - target exists in prefix, we found valid paths ending here
        count += prefix[curr_sum - targetSum]
        prefix[curr_sum] += 1
        dfs(node.left, curr_sum)
        dfs(node.right, curr_sum)
        prefix[curr_sum] -= 1  # Backtrack

    dfs(root, 0)
    return count
```

---

### Problem 22. 105. Construct Binary Tree from Preorder and Inorder Traversal
**Archetype:** 7.6 Serialization & Construction (Blended with Arrays / Hash Maps)
**Type:** Pattern Blend
**Statement:** Given two integer arrays preorder and inorder, construct the binary tree.
**Why it fits:** It blends tree construction with array indexing and hashmap lookups. Preorder tells you the root; inorder tells you the left/right subtree sizes via the root's position.
**The Twist:** You must efficiently find the root's index in the inorder array. A hashmap reduces this from O(n) search to O(1), making the total complexity O(n).
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def buildTree(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    inorder_index = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = 0

    def build(in_left, in_right):
        nonlocal pre_idx
        if in_left > in_right:
            return None
        root_val = preorder[pre_idx]
        root = TreeNode(root_val)
        pre_idx += 1
        idx = inorder_index[root_val]
        root.left = build(in_left, idx - 1)
        root.right = build(idx + 1, in_right)
        return root

    return build(0, len(inorder) - 1)
```

---

### Problem 23. 958. Check Completeness of a Binary Tree
**Archetype:** 7.3 Tree Validation (Blended with BFS / Queues)
**Type:** Pattern Blend
**Statement:** Given the root of a binary tree, determine if it is a complete binary tree.
**Why it fits:** Validation usually relies on structural properties (BST, balanced), but completeness is best checked via BFS level-order traversal. You must verify that no node appears after the first null in a level-order sequence.
**The Twist:** A single pass BFS is sufficient. After encountering the first null node, all subsequent nodes must also be null. This blends tree validation with queue-based traversal.
**Code Skeleton:**
```python
from typing import Optional
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isCompleteTree(root: Optional[TreeNode]) -> bool:
    if not root:
        return True
    queue = deque([root])
    seen_null = False
    while queue:
        node = queue.popleft()
        if not node:
            seen_null = True
        else:
            if seen_null:
                return False
            queue.append(node.left)
            queue.append(node.right)
    return True
```

---

### Problem 24. 1026. Maximum Difference Between Node and Ancestor
**Archetype:** 7.2 Path Problems / 7.8 Counting & Metrics
**Type:** Pattern Blend
**Statement:** Given the root of a binary tree, find the maximum value `v` for which there exist different nodes `a` and `b` where `v = |a.val - b.val|` and `a` is an ancestor of `b`.
**Why it fits:** It appears to be a path problem, but the key insight is that the maximum difference for any path is determined solely by the max and min values seen along that root-to-node path. No need to store the entire path.
**The Twist:** You only need to propagate `min_so_far` and `max_so_far` down the tree. The absolute difference at the leaf is derived from these two values alone.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def maxAncestorDiff(root: Optional[TreeNode]) -> int:
    def dfs(node, curr_min, curr_max):
        if not node:
            return curr_max - curr_min
        curr_min = min(curr_min, node.val)
        curr_max = max(curr_max, node.val)
        left = dfs(node.left, curr_min, curr_max)
        right = dfs(node.right, curr_min, curr_max)
        return max(left, right)

    return dfs(root, root.val, root.val)
```

---

### Problem 25. 863. All Nodes Distance K in Binary Tree
**Archetype:** 7.4 LCA (Blended with Graph BFS)
**Type:** Pattern Blend
**Statement:** Given the root of a binary tree, the value of a target node, and an integer `k`, return an array of the values of all nodes that have a distance `k` from the target node.
**Why it fits:** It starts as a tree problem but requires traversing "upward" to parents, effectively turning the tree into an undirected graph. You must first build an adjacency list (parent pointers) and then run BFS.
**The Twist:** Trees have no parent pointers by default. You must first populate a parent map via DFS, then perform a graph BFS from the target node in all three directions (left, right, parent).
**Code Skeleton:**
```python
from typing import Optional, List
from collections import deque, defaultdict

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def distanceK(root: Optional[TreeNode], target: TreeNode, k: int) -> List[int]:
    parent_map = {}

    def dfs(node, parent):
        if not node:
            return
        if parent:
            parent_map[node] = parent
        dfs(node.left, node)
        dfs(node.right, node)

    dfs(root, None)

    queue = deque([(target, 0)])
    visited = {target}
    result = []

    while queue:
        node, dist = queue.popleft()
        if dist == k:
            result.append(node.val)
        for neighbor in (node.left, node.right, parent_map.get(node)):
            if neighbor and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return result
```

---

### Problem 26. 230. Kth Smallest Element in a BST
**Archetype:** 7.4 LCA / 7.8 Counting & Metrics
**Type:** Interview Sim
**Statement:** Given the root of a binary search tree and an integer `k`, return the `k`-th smallest value (1-indexed) of all the values of the nodes in the tree.
**Why it fits:** An extremely common interview question that tests BST property understanding. Inorder traversal yields sorted order, so the kth element is simply the kth node visited in an inorder traversal.
**The Twist:** Interviewers often ask for the follow-up: what if the tree is modified often? This motivates augmenting nodes with subtree counts. For the base problem, iterative inorder with a counter is optimal.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def kthSmallest(root: Optional[TreeNode], k: int) -> int:
    stack = []
    curr = root
    count = 0
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        count += 1
        if count == k:
            return curr.val
        curr = curr.right
    return -1  # Should not reach here for valid k
```

---

### Problem 27. 889. Construct Binary Tree from Preorder and Postorder Traversal
**Archetype:** 7.6 Serialization & Construction
**Type:** Interview Sim
**Statement:** Given two integer arrays, preorder and postorder, construct a binary tree.
**Why it fits:** A harder construction problem because you cannot uniquely determine left subtree size without additional constraints. However, with the assumption that all values are unique, the first element of the left subtree in preorder identifies the split point in postorder.
**The Twist:** Unlike preorder+inorder, the boundary between left and right subtrees is implicit. The first element after the root in preorder is the root of the left subtree; finding it in postorder tells you the left subtree's size.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def constructFromPrePost(preorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    post_index = {val: i for i, val in enumerate(postorder)}
    pre_idx = 0

    def build(post_left, post_right):
        nonlocal pre_idx
        if pre_idx >= len(preorder) or post_left > post_right:
            return None
        root_val = preorder[pre_idx]
        root = TreeNode(root_val)
        pre_idx += 1
        # If only one node in this range, return it
        if post_left == post_right:
            return root
        # The next value in preorder is the root of the left subtree
        left_val = preorder[pre_idx]
        left_post_idx = post_index[left_val]
        root.left = build(post_left, left_post_idx)
        root.right = build(left_post_idx + 1, post_right - 1)
        return root

    return build(0, len(postorder) - 1)
```

---

### Problem 28. 968. Binary Tree Cameras
**Archetype:** 7.2 Path Problems / 7.7 Tree Modification
**Type:** Interview Sim
**Statement:** You are given the root of a binary tree. Install cameras on the nodes of the tree such that every node is monitored. Return the minimum number of cameras needed.
**Why it fits:** A hard tree DP/greedy problem often seen at top companies. It requires assigning states to nodes (has camera, covered, not covered) and making optimal decisions in post-order.
**The Twist:** Greedy from the bottom works best. A leaf should never have a camera; instead, its parent should. This bottom-up state machine (0=uncovered, 1=camera, 2=covered) is the key insight.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def minCameraCover(root: Optional[TreeNode]) -> int:
    cameras = 0
    # States: 0 = not covered, 1 = has camera, 2 = covered (no camera)
    def dfs(node):
        nonlocal cameras
        if not node:
            return 2  # Null nodes are considered covered
        left = dfs(node.left)
        right = dfs(node.right)
        # If any child is not covered, we MUST place a camera here
        if left == 0 or right == 0:
            cameras += 1
            return 1
        # If any child has a camera, this node is covered
        if left == 1 or right == 1:
            return 2
        # Otherwise, children are covered but have no camera; node is not covered
        return 0

    root_state = dfs(root)
    # If root is not covered, add one camera at the root
    return cameras + (1 if root_state == 0 else 0)
```

---

### Problem 29. 99. Recover Binary Search Tree
**Archetype:** 7.3 Tree Validation / 7.7 Tree Modification
**Type:** Interview Sim
**Statement:** You are given the root of a binary search tree (BST), where the values of exactly two nodes were swapped by mistake. Recover the tree without changing its structure.
**Why it fits:** A classic hard interview problem. It tests deep understanding of inorder traversal in BSTs. Since inorder of a BST is sorted, the swapped elements create exactly two "out of order" pairs.
**The Twist:** You must identify the two swapped nodes during a single inorder traversal using O(1) extra space (Morris traversal) or O(h) space (iterative stack). Swapping values (not nodes) is sufficient.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def recoverTree(root: Optional[TreeNode]) -> None:
    first = second = prev = None
    curr = root
    stack = []
    while curr or stack:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        # Detect out-of-order pair
        if prev and prev.val > curr.val:
            if not first:
                first = prev
            second = curr
        prev = curr
        curr = curr.right
    # Swap the values of the two identified nodes
    first.val, second.val = second.val, first.val
```

---

### Problem 30. 1372. Longest ZigZag Path in a Binary Tree
**Archetype:** 7.2 Path Problems / 7.8 Counting & Metrics
**Type:** Interview Sim
**Statement:** You are given the root of a binary tree. A ZigZag path for a binary tree is defined as a sequence of nodes starting from the root where each node in the sequence is the left or right child of the previous node, alternating between left and right. Return the longest ZigZag path contained in that tree.
**Why it fits:** Tests the ability to carry directional state through a DFS. The path length depends not just on the node, but on whether you arrived from a left or right parent.
**The Twist:** The recursive state must include the direction (left or right). If you came from a left child, you must go right next (and vice versa), resetting the streak otherwise.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def longestZigZag(root: Optional[TreeNode]) -> int:
    max_len = 0

    def dfs(node, go_left, length):
        nonlocal max_len
        if not node:
            return
        max_len = max(max_len, length)
        if go_left:
            dfs(node.left, False, length + 1)
            dfs(node.right, True, 1)  # Reset streak
        else:
            dfs(node.right, True, length + 1)
            dfs(node.left, False, 1)  # Reset streak

    dfs(root, True, 0)
    dfs(root, False, 0)
    return max_len
```

---
