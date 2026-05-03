# Pattern 07: Trees

> **Pattern Recognition:** When you see "binary tree", "root-to-leaf", "level order", "LCA", "path sum", "symmetric" — think tree traversal.
>
> **Fundamental Insight:** Trees are recursive by nature. Every tree problem can be solved by: (1) solving for root, (2) recursively solving for children, (3) combining results.

---

## Archetype 7.1: Basic Traversals

### Recognition Signal
Words: **"inorder", "preorder", "postorder", "level order", "BFS", "DFS"**

### Templates

**DFS Recursive:**
```python
def dfs(node):
    if not node:
        return
    # Preorder: process here
    dfs(node.left)
    # Inorder: process here
    dfs(node.right)
    # Postorder: process here
```

**BFS Level Order:**
```python
def bfs(root):
    if not root:
        return []
    result = []
    queue = [root]
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

### Problems
- Binary Tree Preorder Traversal (LeetCode 144)
- Binary Tree Inorder Traversal (LeetCode 94)
- Binary Tree Postorder Traversal (LeetCode 145)
- Binary Tree Level Order Traversal (LeetCode 102)
- N-ary Tree Level Order Traversal (LeetCode 429)
- Binary Tree Zigzag Level Order Traversal (LeetCode 103)

---

## Archetype 7.2: Path Problems

### Recognition Signal
Words: **"root-to-leaf", "path sum", "sum of paths", "binary tree paths"**

### Template: Root-to-Leaf Paths
```python
def path_sum(root, target):
    def dfs(node, current_sum, path):
        if not node:
            return
        current_sum += node.val
        path.append(node.val)
        if not node.left and not node.right and current_sum == target:
            result.append(path[:])
        dfs(node.left, current_sum, path)
        dfs(node.right, current_sum, path)
        path.pop()
    result = []
    dfs(root, 0, [])
    return result
```

### Problems
- Path Sum (LeetCode 112)
- Path Sum II (LeetCode 113)
- Binary Tree Paths (LeetCode 257)
- Sum Root to Leaf Numbers (LeetCode 129)
- Path Sum III (LeetCode 437) — path can start anywhere, prefix sums

---

## Archetype 7.3: Tree Validation

### Recognition Signal
Words: **"valid", "balanced", "symmetric", "same tree", "BST", "mirror"**

### Problems
- Same Tree (LeetCode 100)
- Symmetric Tree (LeetCode 101)
- Validate Binary Search Tree (LeetCode 98)
- Balanced Binary Tree (LeetCode 110)
- Subtree of Another Tree (LeetCode 572)

**Validate BST trick:** Inorder traversal should be sorted. Or pass min/max bounds.

```python
def is_valid_bst(root):
    def validate(node, low, high):
        if not node:
            return True
        if not (low < node.val < high):
            return False
        return validate(node.left, low, node.val) and validate(node.right, node.val, high)
    return validate(root, float('-inf'), float('inf'))
```

---

## Archetype 7.4: LCA (Lowest Common Ancestor)

### Recognition Signal
Words: **"lowest common ancestor", "LCA", "common parent"**

### Templates

**BST LCA:**
```python
def lowest_common_ancestor_bst(root, p, q):
    while root:
        if p.val < root.val > q.val:
            root = root.left
        elif p.val > root.val < q.val:
            root = root.right
        else:
            return root
```

**Binary Tree LCA:**
```python
def lowest_common_ancestor(root, p, q):
    if not root or root == p or root == q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    if left and right:
        return root
    return left or right
```

### Problems
- Lowest Common Ancestor of BST (LeetCode 235)
- Lowest Common Ancestor of Binary Tree (LeetCode 236)
- Lowest Common Ancestor of Deepest Leaves (LeetCode 1123)

---

## Archetype 7.5: Tree Views & Boundaries

### Recognition Signal
Words: **"right view", "left view", "boundary", "top view", "vertical order"**

### Problems
- Binary Tree Right Side View (LeetCode 199)
- Boundary of Binary Tree (LeetCode 545)
- Vertical Order Traversal (LeetCode 987)
- Top View of Binary Tree
- Bottom View of Binary Tree

---

## Archetype 7.6: Serialization & Construction

### Recognition Signal
Words: **"serialize", "deserialize", "construct", "build from traversal"**

### Problems
- Serialize and Deserialize Binary Tree (LeetCode 297)
- Construct Binary Tree from Preorder and Inorder (LeetCode 105)
- Construct Binary Tree from Inorder and Postorder (LeetCode 106)
- Construct Binary Tree from Preorder and Postorder (LeetCode 889)
- Construct BST from Preorder (LeetCode 1008)

**Key insight:** Preorder gives root. Inorder gives left/right subtrees.

---

## Archetype 7.7: Tree Modification

### Recognition Signal
Words: **"invert", "flatten", "trim", "delete", "merge"**

### Problems
- Invert Binary Tree (LeetCode 226)
- Flatten Binary Tree to Linked List (LeetCode 114)
- Trim a Binary Search Tree (LeetCode 669)
- Convert Sorted Array to BST (LeetCode 108)
- Convert BST to Greater Tree (LeetCode 538)
- Merge Two Binary Trees (LeetCode 617)

---

## Archetype 7.8: Counting & Metrics

### Recognition Signal
Words: **"diameter", "max path sum", "count nodes", "width", "depth"**

### Problems
- Maximum Depth of Binary Tree (LeetCode 104)
- Diameter of Binary Tree (LeetCode 543)
- Binary Tree Maximum Path Sum (LeetCode 124)
- Count Complete Tree Nodes (LeetCode 222)
- Count Good Nodes in Binary Tree (LeetCode 1448)

**Diameter trick:** Diameter = max(left_height + right_height) across all nodes.

```python
def diameter_of_binary_tree(root):
    self.diameter = 0
    def height(node):
        if not node:
            return 0
        left = height(node.left)
        right = height(node.right)
        self.diameter = max(self.diameter, left + right)
        return 1 + max(left, right)
    height(root)
    return self.diameter
```

---

## Mastery Checklist
- [ ] All 4 DFS traversals recursively and iteratively
- [ ] BFS level order with queue
- [ ] LCA in BST (O(h)) and binary tree (O(n))
- [ ] Validate BST with bounds and inorder
- [ ] Path sum with backtracking
- [ ] Diameter / max path sum with postorder
- [ ] Serialize/deserialize with BFS/DFS
- [ ] Construct tree from traversals
- [ ] Invert/flatten/merge trees

---

## Common Traps

**Trap:** Confusing height and depth.
- Height of node = max distance to leaf.
- Depth of node = distance from root.

**Trap:** Forgetting to handle empty tree.
- Fix: `if not root: return 0` or `return []` at start.

**Trap:** Modifying tree during traversal.
- Fix: If modifying structure, consider cloning or process children before parent.

**Trap:** O(n) space for recursion on skewed tree.
- Fix: Morris traversal for O(1) space (advanced).

**Near Miss:** Binary Search Tree Iterator (LeetCode 173)
- Looks like traversal
- But needs controlled iteration. Use stack for iterative inorder.
