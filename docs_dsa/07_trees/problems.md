# Pattern 07: Trees — Practice Problems

## Basic Traversals

### 144. Binary Tree Preorder Traversal
**Statement:** Root, left, right.
**Code (Iterative):**
```python
def preorder_traversal(root):
    if not root:
        return []
    result, stack = [], [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result
```

### 94. Binary Tree Inorder Traversal
**Statement:** Left, root, right.
**Code (Iterative):**
```python
def inorder_traversal(root):
    result, stack = [], []
    current = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result
```

### 145. Binary Tree Postorder Traversal
**Statement:** Left, right, root.
**Code (Iterative with two stacks):**
```python
def postorder_traversal(root):
    if not root:
        return []
    stack1, stack2 = [root], []
    while stack1:
        node = stack1.pop()
        stack2.append(node.val)
        if node.left:
            stack1.append(node.left)
        if node.right:
            stack1.append(node.right)
    return stack2[::-1]
```

### 102. Binary Tree Level Order Traversal
**Statement:** Return level by level.
**Code:**
```python
def level_order(root):
    if not root:
        return []
    result, queue = [], [root]
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

### 103. Binary Tree Zigzag Level Order Traversal
**Statement:** Left to right, then right to left.
**Intuition:** Same as level order, reverse every other level.

### 429. N-ary Tree Level Order Traversal
**Statement:** Level order for N-ary tree.
**Intuition:** Queue. For each node, add all children to queue.

---

## Path Problems

### 112. Path Sum
**Statement:** Has root-to-leaf path with target sum?
**Code:**
```python
def has_path_sum(root, target):
    if not root:
        return False
    if not root.left and not root.right:
        return target == root.val
    return has_path_sum(root.left, target - root.val) or has_path_sum(root.right, target - root.val)
```

### 113. Path Sum II
**Statement:** All root-to-leaf paths with target sum.
**Intuition:** Backtracking DFS.

### 257. Binary Tree Paths
**Statement:** All root-to-leaf paths as strings.
**Intuition:** DFS, build path string.

### 129. Sum Root to Leaf Numbers
**Statement:** Each root-to-leaf path is a number. Sum all.
**Intuition:** DFS with current number. At leaf, add to total.

### 437. Path Sum III
**Statement:** Paths can start anywhere, end anywhere. Count paths with sum target.
**Intuition:** Prefix sums on tree. Hash map: prefix_sum -> count.

```python
def path_sum_iii(root, target):
    count = {0: 1}
    def dfs(node, current_sum):
        if not node:
            return 0
        current_sum += node.val
        result = count.get(current_sum - target, 0)
        count[current_sum] = count.get(current_sum, 0) + 1
        result += dfs(node.left, current_sum) + dfs(node.right, current_sum)
        count[current_sum] -= 1
        return result
    return dfs(root, 0)
```

---

## Validation

### 100. Same Tree
**Statement:** Check if two trees are identical.
**Intuition:** Same root val, same left, same right.

### 101. Symmetric Tree
**Statement:** Mirror of itself.
**Intuition:** Left subtree is mirror of right subtree.

### 98. Validate Binary Search Tree
**Statement:** Is valid BST?
**Intuition:** Inorder is sorted. Or bounds checking.
**Code:**
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

### 110. Balanced Binary Tree
**Statement:** Height difference of subtrees <= 1.
**Intuition:** Postorder. Return -1 if unbalanced.

### 572. Subtree of Another Tree
**Statement:** Is subRoot a subtree of root?
**Intuition:** For each node in root, check if same tree as subRoot.

---

## LCA

### 235. Lowest Common Ancestor of a Binary Search Tree
**Statement:** LCA in BST.
**Code:**
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

### 236. Lowest Common Ancestor of a Binary Tree
**Statement:** LCA in binary tree.
**Code:**
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

---

## Views & Boundaries

### 199. Binary Tree Right Side View
**Statement:** Values visible from right side.
**Intuition:** BFS, take last element of each level.

### 987. Vertical Order Traversal
**Statement:** Column by column, top to bottom.
**Intuition:** BFS with column tracking. Sort by (column, row, val).

---

## Serialization & Construction

### 297. Serialize and Deserialize Binary Tree
**Statement:** Convert tree to string and back.
**Intuition:** BFS with null markers. Or DFS with pre-order.

### 105. Construct Binary Tree from Preorder and Inorder
**Statement:** Build tree from traversals.
**Intuition:** Preorder[0] is root. Find in inorder. Recurse.

### 106. Construct Binary Tree from Inorder and Postorder
**Statement:** Postorder[-1] is root.

### 889. Construct Binary Tree from Preorder and Postorder
**Statement:** Preorder[0] is root, preorder[1] is left root.

### 1008. Construct Binary Search Tree from Preorder Traversal
**Statement:** Build BST from preorder.
**Intuition:** First element is root. Elements < root go left, > root go right.

---

## Modification

### 226. Invert Binary Tree
**Statement:** Mirror tree.
**Intuition:** Swap left and right recursively.

### 114. Flatten Binary Tree to Linked List
**Statement:** In-place flatten to right-linked list.
**Intuition:** Reverse postorder. Or iterative with stack.

### 669. Trim a Binary Search Tree
**Statement:** Remove nodes outside [low, high].
**Intuition:** If root < low, return right subtree. If root > high, return left subtree.

### 108. Convert Sorted Array to BST
**Statement:** Height-balanced BST.
**Intuition:** Middle element is root. Recurse on left and right halves.

### 538. Convert BST to Greater Tree
**Statement:** Each node becomes sum of all nodes >= it.
**Intuition:** Reverse inorder. Track running sum.

### 617. Merge Two Binary Trees
**Statement:** Overlay two trees. Sum overlapping nodes.
**Intuition:** Recurse. If both nodes exist, sum. If one exists, use it.

---

## Counting & Metrics

### 104. Maximum Depth of Binary Tree
**Statement:** Height of tree.
**Intuition:** 1 + max(depth left, depth right).

### 543. Diameter of Binary Tree
**Statement:** Longest path between any two nodes.
**Intuition:** Max of (left_height + right_height) across all nodes.

### 124. Binary Tree Maximum Path Sum
**Statement:** Max sum path (can start/end anywhere).
**Intuition:** Postorder. Max path through node = node.val + max(left, 0) + max(right, 0).

### 222. Count Complete Tree Nodes
**Statement:** Count nodes in complete tree faster than O(n).
**Intuition:** If left height == right height, tree is full: 2^h - 1 nodes.

### 1448. Count Good Nodes in Binary Tree
**Statement:** Node is good if no ancestor has greater value.
**Intuition:** DFS with max_so_far.

---

## Mixed Drill Set

1. 104 — Max depth
2. 226 — Invert tree
3. 98 — Validate BST
4. 102 — Level order
5. 112 — Path sum
6. 235 — LCA BST
7. 236 — LCA binary tree
8. 543 — Diameter
9. 124 — Max path sum
10. 297 — Serialize/deserialize
11. 105 — Build from traversals
12. 114 — Flatten to list
13. 437 — Path sum III (prefix sums)
14. 572 — Subtree check
15. 110 — Balanced tree
