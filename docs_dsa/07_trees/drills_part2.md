# Trees: Drills Part 2 — Warm-ups + Core Drills

---

### Problem 1. 104. Maximum Depth of Binary Tree
**Archetype:** 7.1 Basic Traversals / 7.8 Counting & Metrics
**Type:** Warm-Up
**Statement:** Find the maximum depth of a binary tree.
**Why it fits:** This is the quintessential tree starter. It teaches recursive thinking on trees (max of left/right + 1) and serves as the foundation for almost every subsequent DFS pattern.
**The Twist:** None — this is the canonical form. Master this before moving on.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def maxDepth(root: Optional[TreeNode]) -> int:
    # Base case: null node contributes 0 depth
    if not root:
        return 0
    # Recursive case: depth is 1 (current node) + max subtree depth
    return 1 + max(maxDepth(root.left), maxDepth(root.right))
```

---

### Problem 2. 226. Invert Binary Tree
**Archetype:** 7.7 Tree Modification
**Type:** Warm-Up
**Statement:** Invert a binary tree by swapping every left and right child.
**Why it fits:** A pure post-order modification drill. It solidifies the idea that you can mutate the tree structure during traversal without returning a new tree.
**The Twist:** None — the classic "Google home screen" problem. Focus on clean swap logic.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def invertTree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if not root:
        return None
    # Post-order: invert children first, then swap
    invertTree(root.left)
    invertTree(root.right)
    root.left, root.right = root.right, root.left
    return root
```

---

### Problem 3. 144. Binary Tree Preorder Traversal
**Archetype:** 7.1 Basic Traversals
**Type:** Warm-Up
**Statement:** Return the preorder traversal of a binary tree's nodes.
**Why it fits:** Preorder (Root-Left-Right) is the simplest traversal to internalize. It builds the mental model for DFS stack behavior and is often the first pattern students implement iteratively.
**The Twist:** None — canonical recursive and iterative forms. Try both.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def preorderTraversal(root: Optional[TreeNode]) -> List[int]:
    result = []
    # Iterative using explicit stack to avoid recursion limit issues
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push right first so left is processed first (LIFO)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result
```

---

### Problem 4. 94. Binary Tree Inorder Traversal
**Archetype:** 7.1 Basic Traversals
**Type:** Warm-Up
**Statement:** Return the inorder traversal of a binary tree's nodes.
**Why it fits:** Inorder traversal is critical for BSTs because it yields sorted values. The iterative version (with a stack and a pointer) is slightly trickier than preorder and is a must-know pattern.
**The Twist:** None — the standard template for iterative DFS with a cursor.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorderTraversal(root: Optional[TreeNode]) -> List[int]:
    result = []
    stack = []
    curr = root
    while curr or stack:
        # Go all the way left
        while curr:
            stack.append(curr)
            curr = curr.left
        # Process node
        curr = stack.pop()
        result.append(curr.val)
        # Move to right subtree
        curr = curr.right
    return result
```

---

### Problem 5. 145. Binary Tree Postorder Traversal
**Archetype:** 7.1 Basic Traversals
**Type:** Warm-Up
**Statement:** Return the postorder traversal of a binary tree's nodes.
**Why it fits:** Postorder (Left-Right-Root) is essential for "cleanup" or "aggregation" problems where children must be processed before the parent. The iterative version requires a visited flag or a clever reversal trick.
**The Twist:** None — master the iterative version; it appears in many advanced tree DP problems.
**Code Skeleton:**
```python
from typing import Optional, List

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def postorderTraversal(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    # Trick: root-right-left traversal, then reverse
    result = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return result[::-1]
```

---

### Problem 6. 102. Binary Tree Level Order Traversal
**Archetype:** 7.1 Basic Traversals
**Type:** Core Drill
**Statement:** Return the level order traversal of a binary tree's nodes' values (i.e., from left to right, level by level).
**Why it fits:** The canonical BFS problem. It establishes the queue-based level processing pattern that underlies tree views, connect nodes, and zigzag traversals.
**The Twist:** None — but notice how tracking `level_size` separates nodes by depth cleanly.
**Code Skeleton:**
```python
from typing import Optional, List
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

---

### Problem 7. 112. Path Sum
**Archetype:** 7.2 Path Problems
**Type:** Core Drill
**Statement:** Given the root of a binary tree and an integer targetSum, return true if the tree has a root-to-leaf path such that adding up all the values along the path equals targetSum.
**Why it fits:** The foundational path-sum problem. It teaches how to carry state (running sum or remaining sum) down recursive calls and how to identify leaf nodes for termination.
**The Twist:** None — the canonical root-to-leaf DFS template. Note: must end on a leaf.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def hasPathSum(root: Optional[TreeNode], targetSum: int) -> bool:
    if not root:
        return False
    # Leaf check: if no children, value must match remaining sum
    if not root.left and not root.right:
        return root.val == targetSum
    # Recurse with reduced target
    return hasPathSum(root.left, targetSum - root.val) or \
           hasPathSum(root.right, targetSum - root.val)
```

---

### Problem 8. 543. Diameter of Binary Tree
**Archetype:** 7.8 Counting & Metrics
**Type:** Core Drill
**Statement:** Given the root of a binary tree, return the length of the diameter of the tree.
**Why it fits:** Teaches the "return value vs. global state" dichotomy. The recursive function returns height, but a non-local variable captures the diameter (left height + right height). This pattern is ubiquitous in tree metrics.
**The Twist:** None — the standard template for computing a global tree metric during height calculation.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def diameterOfBinaryTree(root: Optional[TreeNode]) -> int:
    diameter = 0

    def height(node):
        nonlocal diameter
        if not node:
            return -1  # Edge count: null node has height -1
        left = height(node.left)
        right = height(node.right)
        # Diameter passing through this node
        diameter = max(diameter, 2 + left + right)
        return 1 + max(left, right)

    height(root)
    return diameter
```

---

### Problem 9. 110. Balanced Binary Tree
**Archetype:** 7.3 Tree Validation
**Type:** Core Drill
**Statement:** Given a binary tree, determine if it is height-balanced.
**Why it fits:** A validation problem that requires height information from subtrees. The key optimization is short-circuiting: return -1 if unbalanced to avoid redundant traversals. This teaches early-exit recursion.
**The Twist:** None — the canonical "return sentinel on failure" pattern to achieve O(n) time.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isBalanced(root: Optional[TreeNode]) -> bool:
    def check(node):
        if not node:
            return 0
        left = check(node.left)
        if left == -1:
            return -1
        right = check(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)

    return check(root) != -1
```

---

### Problem 10. 98. Validate Binary Search Tree
**Archetype:** 7.3 Tree Validation
**Type:** Core Drill
**Statement:** Given the root of a binary tree, determine if it is a valid binary search tree (BST).
**Why it fits:** The definitive BST validation problem. It requires passing down valid ranges (min, max) rather than just comparing parent and child, which is a common pitfall for beginners.
**The Twist:** None — canonical range-passing recursion. Beware of only comparing immediate parent-child values.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def isValidBST(root: Optional[TreeNode]) -> bool:
    def validate(node, low, high):
        if not node:
            return True
        # Current node must be strictly within the range
        if not (low < node.val < high):
            return False
        # Left subtree must be < node.val, right must be > node.val
        return validate(node.left, low, node.val) and \
               validate(node.right, node.val, high)

    return validate(root, float('-inf'), float('inf'))
```

---

### Problem 11. 199. Binary Tree Right Side View
**Archetype:** 7.5 Views & Boundaries
**Type:** Core Drill
**Statement:** Given the root of a binary tree, imagine yourself standing on the right side of it, return the values of the nodes you can see ordered from top to bottom.
**Why it fits:** A view problem that can be solved with either BFS (last node per level) or DFS (preorder with depth tracking, prioritizing right). It bridges traversal and view archetypes.
**The Twist:** None — canonical view problem. Try solving with both BFS and DFS for deeper understanding.
**Code Skeleton:**
```python
from typing import Optional, List
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def rightSideView(root: Optional[TreeNode]) -> List[int]:
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result
```

---

### Problem 12. 235. Lowest Common Ancestor of a Binary Search Tree
**Archetype:** 7.4 LCA
**Type:** Core Drill
**Statement:** Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given nodes.
**Why it fits:** The BST property allows an elegant O(h) iterative or recursive solution without storing paths. This teaches leveraging structural constraints for algorithmic simplification.
**The Twist:** None — the canonical LCA for BSTs. Compare values to decide direction.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def lowestCommonAncestor(root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    curr = root
    while curr:
        # If both values are greater, LCA is in right subtree
        if p.val > curr.val and q.val > curr.val:
            curr = curr.right
        # If both values are smaller, LCA is in left subtree
        elif p.val < curr.val and q.val < curr.val:
            curr = curr.left
        else:
            # Divergence found: current node is the LCA
            return curr
    return None  # Should never reach here for valid input
```

---

### Problem 13. 236. Lowest Common Ancestor of a Binary Tree
**Archetype:** 7.4 LCA
**Type:** Core Drill
**Statement:** Given a binary tree, find the lowest common ancestor (LCA) of two given nodes.
**Why it fits:** The general tree version of LCA. It requires post-order logic: if a node is found in left and right subtrees (or is one of the targets), it is the LCA. This is a high-frequency interview problem.
**The Twist:** None — canonical general LCA. The return-value logic (null vs. node) is the critical insight.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def lowestCommonAncestor(root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
    if not root or root == p or root == q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    # If both sides return a node, current is the LCA
    if left and right:
        return root
    # Otherwise, return the non-null side (or None if both are null)
    return left if left else right
```

---

### Problem 14. 124. Binary Tree Maximum Path Sum
**Archetype:** 7.2 Path Problems
**Type:** Core Drill
**Statement:** A path in a binary tree is a sequence of nodes where each pair of adjacent nodes has an edge connecting them. Return the maximum path sum of any non-empty path.
**Why it fits:** The hardest pure path problem. The recursive helper returns the maximum "straight" path (root-to-leaf style) for extension upward, while a global variable tracks the maximum "arch" path (through the node). This dichotomy is crucial.
**The Twist:** None — canonical hard path problem. Handles negative values, so max(0, child) is often used to prune.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def maxPathSum(root: Optional[TreeNode]) -> int:
    max_sum = float('-inf')

    def max_gain(node):
        nonlocal max_sum
        if not node:
            return 0
        # Recursively call on children. Prune negative contributions.
        left_gain = max(max_gain(node.left), 0)
        right_gain = max(max_gain(node.right), 0)
        # Price of the path going through the current node
        price_newpath = node.val + left_gain + right_gain
        max_sum = max(max_sum, price_newpath)
        # Return the max gain if we continue the same path upward
        return node.val + max(left_gain, right_gain)

    max_gain(root)
    return max_sum
```

---

### Problem 15. 297. Serialize and Deserialize Binary Tree
**Archetype:** 7.6 Serialization & Construction
**Type:** Core Drill
**Statement:** Design an algorithm to serialize and deserialize a binary tree.
**Why it fits:** The canonical construction/serialization problem. It tests your ability to traverse a tree and then perfectly reconstruct it. Preorder with null markers is the standard approach.
**The Twist:** None — but note that any traversal that preserves structure (with nulls) works. Preorder is most intuitive.
**Code Skeleton:**
```python
from typing import Optional

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        def preorder(node):
            if not node:
                vals.append("#")
                return
            vals.append(str(node.val))
            preorder(node.left)
            preorder(node.right)
        vals = []
        preorder(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> Optional[TreeNode]:
        vals = iter(data.split(","))
        def build():
            val = next(vals)
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node
        return build()
```

---
