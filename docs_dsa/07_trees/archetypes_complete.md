# Pattern 07: Trees — Complete Archetype Map

> **Pattern Recognition:** When you see "tree", "root", "leaf", "binary tree", "BST", "level", "subtree" — think tree traversal or recursion.
>
> **Fundamental Insight:** Most tree problems are solved by one of: DFS traversal (pre/in/post-order), BFS level-order, or recursion with a helper that returns information to the parent. The key is deciding WHAT to return from each recursive call.

---

## Archetype 7.1: Basic Traversals

### Recognition Signal (10 seconds)
Words: **"inorder", "preorder", "postorder", "level order", "BFS", "DFS", "zigzag"**

The question: **"Visit every node in a specific order."**

### Core Structure
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Recursive DFS
def dfs(node):
    if not node:
        return
    # Preorder: process node here
    dfs(node.left)
    # Inorder: process node here
    dfs(node.right)
    # Postorder: process node here

# Iterative BFS
def bfs(root):
    from collections import deque
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)
```

### The Invariant
In DFS, the call stack implicitly tracks the path from root to current node. In BFS, the queue contains exactly the frontier of the next level. Preorder visits before children, inorder visits between children, postorder visits after children.

### Canonical Problem: Binary Tree Level Order Traversal (LeetCode 102)
**Statement:** Return level order traversal of nodes' values (from left to right, level by level).

```python
from collections import deque

def level_order(root):
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
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        
        result.append(level)
    
    return result
```

### Variation Family

**V1: Binary Tree Zigzag Level Order Traversal (LeetCode 103)**
- **Twist:** Traverse levels alternating left-to-right and right-to-left
- **Change:** Use a flag to reverse each level, or use deque and appendleft

```python
def zigzag_level_order(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    left_to_right = True
    
    while queue:
        level_size = len(queue)
        level = deque()
        
        for _ in range(level_size):
            node = queue.popleft()
            if left_to_right:
                level.append(node.val)
            else:
                level.appendleft(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        
        result.append(list(level))
        left_to_right = not left_to_right
    
    return result
```

**V2: Binary Tree Right Side View (LeetCode 199)**
- **Twist:** See only rightmost node at each level
- **Change:** BFS, only record last node of each level

**V3: Validate Binary Search Tree (LeetCode 98)**
- **Twist:** Check if tree is a valid BST
- **Change:** Inorder traversal of BST yields sorted sequence. Track previous value

```python
def is_valid_bst(root):
    prev = float('-inf')
    
    def inorder(node):
        nonlocal prev
        if not node:
            return True
        if not inorder(node.left):
            return False
        if node.val <= prev:
            return False
        prev = node.val
        return inorder(node.right)
    
    return inorder(root)
```

**V4: Kth Smallest Element in a BST (LeetCode 230)**
- **Twist:** Find kth smallest in BST
- **Change:** Inorder traversal (gives sorted order), count until k

**Near Miss: N-ary Tree Level Order Traversal**
- **Looks like:** Basic BFS
- **But:** Children are in a list, not left/right pointers
- **Lesson:** Tree traversal generalizes; adapt to the specific child representation

---

## Archetype 7.2: Path Problems

### Recognition Signal (10 seconds)
Words: **"root-to-leaf", "path sum", "all paths", "sum equals target"**

The question: **"Find paths from root to leaf that satisfy some condition."**

### Core Structure
```python
def path_problems(root, target):
    def dfs(node, current_path, current_sum):
        if not node:
            return
        
        current_path.append(node.val)
        current_sum += node.val
        
        if not node.left and not node.right:
            # Leaf node - check condition
            if current_sum == target:
                result.append(list(current_path))
        
        dfs(node.left, current_path, current_sum)
        dfs(node.right, current_path, current_sum)
        current_path.pop()  # Backtrack
    
    result = []
    dfs(root, [], 0)
    return result
```

### The Invariant
The `current_path` list always represents the path from root to the current node. We backtrack (pop) after exploring each child to maintain this invariant as we return up the recursion tree.

### Canonical Problem: Path Sum II (LeetCode 113)
**Statement:** Find all root-to-leaf paths where each path's sum equals targetSum.

```python
def path_sum(root, target_sum):
    def dfs(node, current_path, remaining):
        if not node:
            return
        
        current_path.append(node.val)
        remaining -= node.val
        
        if not node.left and not node.right and remaining == 0:
            result.append(list(current_path))
        
        dfs(node.left, current_path, remaining)
        dfs(node.right, current_path, remaining)
        current_path.pop()
    
    result = []
    dfs(root, [], target_sum)
    return result
```

### Variation Family

**V1: Path Sum III (LeetCode 437)**
- **Twist:** Path can start and end at any node, must go downward
- **Change:** Prefix sum technique. At each node, check how many paths ending here sum to target

```python
def path_sum_iii(root, target_sum):
    count = 0
    prefix_sums = {0: 1}  # empty path sums to 0
    
    def dfs(node, curr_sum):
        nonlocal count
        if not node:
            return
        
        curr_sum += node.val
        count += prefix_sums.get(curr_sum - target_sum, 0)
        prefix_sums[curr_sum] = prefix_sums.get(curr_sum, 0) + 1
        
        dfs(node.left, curr_sum)
        dfs(node.right, curr_sum)
        
        prefix_sums[curr_sum] -= 1  # Backtrack
    
    dfs(root, 0)
    return count
```

**V2: Binary Tree Maximum Path Sum (LeetCode 124)**
- **Twist:** Path can be any connected sequence, not just root-to-leaf
- **Change:** Post-order DFS. Return max single-path sum to parent. Update global max with left + node + right

```python
def max_path_sum(root):
    max_sum = float('-inf')
    
    def dfs(node):
        nonlocal max_sum
        if not node:
            return 0
        
        left = max(0, dfs(node.left))   # Ignore negative paths
        right = max(0, dfs(node.right))
        
        max_sum = max(max_sum, left + right + node.val)
        return max(left, right) + node.val
    
    dfs(root)
    return max_sum
```

**V3: Sum Root to Leaf Numbers (LeetCode 129)**
- **Twist:** Each root-to-leaf path represents a number. Sum all numbers
- **Change:** Pass accumulated value down: `curr * 10 + node.val`

**Near Miss: Diameter of Binary Tree**
- **Looks like:** Path problem
- **But:** Longest path between any two nodes, not involving sum. Uses post-order height
- **Lesson:** "Path" can mean different things - sum-based vs length-based

---

## Archetype 7.3: Tree Validation

### Recognition Signal (10 seconds)
Words: **"valid BST", "balanced", "symmetric", "same tree", "subtree"**

The question: **"Verify some structural or value property of the tree."**

### Core Structure
```python
def is_valid(node):
    if not node:
        return True  # Base case: empty is usually valid
    
    left_valid = is_valid(node.left)
    right_valid = is_valid(node.right)
    
    # Check current node condition
    return left_valid and right_valid and current_condition
```

### The Invariant
For validation problems, the recursive helper returns whether the SUBTREE rooted at the current node is valid. We combine children's validity with the current node's condition. For BST validation, we must pass down valid min/max ranges.

### Canonical Problem: Validate Binary Search Tree (LeetCode 98)
**Statement:** Determine if a binary tree is a valid BST.

```python
def is_valid_bst(root):
    def validate(node, min_val, max_val):
        if not node:
            return True
        
        if node.val <= min_val or node.val >= max_val:
            return False
        
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))
    
    return validate(root, float('-inf'), float('inf'))
```

### Variation Family

**V1: Balanced Binary Tree (LeetCode 110)**
- **Twist:** Check if tree is height-balanced (left and right subtrees differ by at most 1)
- **Change:** Post-order. Return height if balanced, -1 if unbalanced

```python
def is_balanced(root):
    def height(node):
        if not node:
            return 0
        
        left = height(node.left)
        if left == -1:
            return -1
        right = height(node.right)
        if right == -1:
            return -1
        
        if abs(left - right) > 1:
            return -1
        return max(left, right) + 1
    
    return height(root) != -1
```

**V2: Symmetric Tree (LeetCode 101)**
- **Twist:** Check if tree is mirror of itself
- **Change:** Recursive helper compares left subtree with right subtree (mirrored)

```python
def is_symmetric(root):
    def is_mirror(left, right):
        if not left and not right:
            return True
        if not left or not right:
            return False
        return (left.val == right.val and
                is_mirror(left.left, right.right) and
                is_mirror(left.right, right.left))
    
    return is_mirror(root.left, root.right) if root else True
```

**V3: Same Tree (LeetCode 100)**
- **Twist:** Check if two trees are identical
- **Change:** Compare current nodes, then recurse on both lefts and both rights

**V4: Subtree of Another Tree (LeetCode 572)**
- **Twist:** Check if tree s is a subtree of tree t
- **Change:** At each node of t, check if subtree rooted there matches s

```python
def is_subtree(root, sub_root):
    def is_same(s, t):
        if not s and not t:
            return True
        if not s or not t:
            return False
        return (s.val == t.val and
                is_same(s.left, t.left) and
                is_same(s.right, t.right))
    
    if not root:
        return False
    return (is_same(root, sub_root) or
            is_subtree(root.left, sub_root) or
            is_subtree(root.right, sub_root))
```

**Near Miss: Redundant Connection**
- **Looks like:** Tree validation
- **But:** Graph problem detecting cycle in undirected graph
- **Lesson:** "Valid tree" in a graph context is different from binary tree validation

---

## Archetype 7.4: LCA (Lowest Common Ancestor)

### Recognition Signal (10 seconds)
Words: **"lowest common ancestor", "LCA", "deepest common", "shared parent"**

The question: **"Find the deepest node that is an ancestor of both given nodes."**

### Core Structure
```python
def lca(root, p, q):
    if not root or root == p or root == q:
        return root
    
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    
    if left and right:
        return root  # Found one in each subtree
    return left or right
```

### The Invariant
If both target nodes are in different subtrees of the current node, the current node is the LCA. If both are in the left subtree, the LCA is in the left. If both are in the right, the LCA is in the right.

### Canonical Problem: Lowest Common Ancestor of a Binary Tree (LeetCode 236)
**Statement:** Given binary tree and two nodes, find their LCA.

```python
def lowest_common_ancestor(root, p, q):
    if not root or root == p or root == q:
        return root
    
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    if left and right:
        return root
    return left if left else right
```

### Variation Family

**V1: Lowest Common Ancestor of a BST (LeetCode 235)**
- **Twist:** Tree is a BST, values are unique
- **Change:** O(h) solution. If both values are less than root, go left. If both greater, go right. Otherwise, root is LCA

```python
def lowest_common_ancestor_bst(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

**V2: Lowest Common Ancestor of Deepest Leaves (LeetCode 1123)**
- **Twist:** Find LCA of all deepest leaves
- **Change:** Post-order. Return (lca_node, depth) tuple. If left and right depths equal, current node is LCA

```python
def lca_deepest_leaves(root):
    def dfs(node):
        if not node:
            return (None, 0)
        
        left_node, left_depth = dfs(node.left)
        right_node, right_depth = dfs(node.right)
        
        if left_depth > right_depth:
            return (left_node, left_depth + 1)
        elif right_depth > left_depth:
            return (right_node, right_depth + 1)
        else:
            return (node, left_depth + 1)
    
    return dfs(root)[0]
```

**Near Miss: Find Mode in Binary Search Tree**
- **Looks like:** LCA (searching for values)
- **But:** Inorder traversal to find most frequent element. No ancestor logic needed
- **Lesson:** Searching for values in BST != finding common ancestor

---

## Archetype 7.5: Views & Boundaries

### Recognition Signal (10 seconds)
Words: **"right view", "left view", "boundary", "vertical order", "top view"**

The question: **"See the tree from a specific angle or perspective."**

### Core Structure
```python
# Right view: BFS, take last element of each level
# Boundary: anti-clockwise: left boundary + leaves + right boundary reversed
```

### The Invariant
For views, we typically care about the FIRST or LAST node encountered at each level (for horizontal views) or at each vertical column. For boundaries, we decompose into left edge, leaves, and right edge.

### Canonical Problem: Binary Tree Right Side View (LeetCode 199)
**Statement:** Given root, imagine standing on right side of it. Return values visible from top to bottom.

```python
from collections import deque

def right_side_view(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # Last node in level
                result.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
    
    return result
```

### Variation Family

**V1: Boundary of Binary Tree (LeetCode 545)**
- **Twist:** Return values of boundary in anti-clockwise direction
- **Change:** Decompose into: left boundary (non-leaf), all leaves, right boundary (non-leaf, reversed)

```python
def boundary_of_binary_tree(root):
    if not root:
        return []
    
    def is_leaf(node):
        return not node.left and not node.right
    
    def add_left(node):
        if not node or is_leaf(node):
            return
        boundary.append(node.val)
        if node.left:
            add_left(node.left)
        else:
            add_left(node.right)
    
    def add_leaves(node):
        if not node:
            return
        if is_leaf(node):
            boundary.append(node.val)
            return
        add_leaves(node.left)
        add_leaves(node.right)
    
    def add_right(node):
        if not node or is_leaf(node):
            return
        if node.right:
            add_right(node.right)
        else:
            add_right(node.left)
        boundary.append(node.val)  # Add after recursion for reverse order
    
    boundary = [root.val]
    add_left(root.left)
    add_leaves(root.left)
    add_leaves(root.right)
    add_right(root.right)
    return boundary
```

**V2: Vertical Order Traversal of a Binary Tree (LeetCode 987)**
- **Twist:** Column by column, top to bottom, left to right within same position
- **Change:** BFS with (row, col) coordinates. Group by col, sort by (row, val)

**Near Miss: Binary Tree Level Order Traversal II**
- **Looks like:** View problem
- **But:** Just level order from bottom to top. Standard BFS with reversed result
- **Lesson:** "View" implies selective visibility, not full traversal

---

## Archetype 7.6: Serialization & Construction

### Recognition Signal (10 seconds)
Words: **"serialize", "deserialize", "build from", "construct from traversals", "string representation"**

The question: **"Convert tree to/from a string or build tree from traversal data."**

### Core Structure
```python
# Serialization: DFS/BFS to string
# Deserialization: Recursive builder with index or queue
```

### The Invariant
For serialization, we need a unique representation that captures structure (null markers for missing children). For construction from traversals, inorder + any one of preorder/postorder uniquely defines a binary tree.

### Canonical Problem: Serialize and Deserialize Binary Tree (LeetCode 297)
**Statement:** Design algorithm to serialize and deserialize binary tree.

```python
class Codec:
    def serialize(self, root):
        def helper(node):
            if not node:
                result.append("null")
                return
            result.append(str(node.val))
            helper(node.left)
            helper(node.right)
        
        result = []
        helper(root)
        return ",".join(result)
    
    def deserialize(self, data):
        def helper():
            val = next(values)
            if val == "null":
                return None
            node = TreeNode(int(val))
            node.left = helper()
            node.right = helper()
            return node
        
        values = iter(data.split(","))
        return helper()
```

### Variation Family

**V1: Construct Binary Tree from Preorder and Inorder Traversal (LeetCode 105)**
- **Twist:** Build tree given preorder and inorder arrays
- **Change:** First element of preorder is root. Find it in inorder to split left/right subtrees

```python
def build_tree(preorder, inorder):
    if not preorder or not inorder:
        return None
    
    root = TreeNode(preorder[0])
    mid = inorder.index(preorder[0])
    
    root.left = build_tree(preorder[1:mid+1], inorder[:mid])
    root.right = build_tree(preorder[mid+1:], inorder[mid+1:])
    return root
```

**V2: Construct Binary Tree from Inorder and Postorder Traversal (LeetCode 106)**
- **Twist:** Build tree given inorder and postorder
- **Change:** Last element of postorder is root. Find in inorder, split, recurse

**V3: Construct Binary Tree from Preorder and Postorder Traversal (LeetCode 889)**
- **Twist:** Build tree from preorder and postorder (tree is not unique, assume full/complete)
- **Change:** Preorder[0] is root, preorder[1] is left root. Find left root in postorder to determine left subtree size

**Near Miss: String Transformation**
- **Looks like:** Serialization
- **But:** String manipulation without tree structure preservation
- **Lesson:** Serialization must include structural information (null markers)

---

## Archetype 7.7: Tree Modification

### Recognition Signal (10 seconds)
Words: **"invert", "flatten", "trim", "prune", "merge", "delete"**

The question: **"Change the structure or shape of the tree."**

### Core Structure
```python
def modify_tree(node):
    if not node:
        return None
    
    # Modify left and right subtrees first (post-order)
    left = modify_tree(node.left)
    right = modify_tree(node.right)
    
    # Rewire current node
    node.left = something
    node.right = something
    return node
```

### The Invariant
For modifications, we typically use post-order processing: modify children first, then use their modified results to rewire the current node. This ensures subtrees are in final state before parent uses them.

### Canonical Problem: Invert Binary Tree (LeetCode 226)
**Statement:** Invert a binary tree (mirror it).

```python
def invert_tree(root):
    if not root:
        return None
    
    # Swap children
    root.left, root.right = root.right, root.left
    
    # Recurse on subtrees
    invert_tree(root.left)
    invert_tree(root.right)
    
    return root
```

### Variation Family

**V1: Flatten Binary Tree to Linked List (LeetCode 114)**
- **Twist:** Flatten tree to a right-linked list in-place (preorder)
- **Change:** Post-order. Flatten left and right, then rewire: left=None, right=flattened_left + root + flattened_right

```python
def flatten(root):
    if not root:
        return None
    
    # Flatten subtrees
    left_tail = flatten(root.left)
    right_tail = flatten(root.right)
    
    # Rewire
    if left_tail:
        left_tail.right = root.right
        root.right = root.left
        root.left = None
    
    return right_tail or left_tail or root
```

**V2: Trim a Binary Search Tree (LeetCode 669)**
- **Twist:** Remove nodes outside [low, high] range
- **Change:** If node.val < low, return trim of right. If node.val > high, return trim of left. Otherwise trim both children

```python
def trim_bst(root, low, high):
    if not root:
        return None
    
    if root.val < low:
        return trim_bst(root.right, low, high)
    if root.val > high:
        return trim_bst(root.left, low, high)
    
    root.left = trim_bst(root.left, low, high)
    root.right = trim_bst(root.right, low, high)
    return root
```

**V3: Delete Node in a BST (LeetCode 450)**
- **Twist:** Delete a node from BST
- **Change:** If node has two children, replace with inorder successor (min of right subtree)

```python
def delete_node(root, key):
    if not root:
        return None
    
    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        # Found node to delete
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        
        # Two children: find successor
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete_node(root.right, successor.val)
    
    return root
```

**V4: Merge Two Binary Trees (LeetCode 617)**
- **Twist:** Merge two trees by summing overlapping nodes
- **Change:** If both nodes exist, sum values and recurse. If one is null, return the other

**Near Miss: Populate Next Right Pointers**
- **Looks like:** Tree modification
- **But:** Adding cross-tree links. Uses BFS or parent-level traversal
- **Lesson:** Modification can mean adding new links, not just rearranging existing ones

---

## Archetype 7.8: Counting & Metrics

### Recognition Signal (10 seconds)
Words: **"diameter", "max path sum", "count nodes", "height", "depth", "width"**

The question: **"Compute a numerical metric about the tree's structure or values."**

### Core Structure
```python
def metric(node):
    if not node:
        return base_case
    
    left = metric(node.left)
    right = metric(node.right)
    
    # Update global answer using left and right results
    # Return value for parent
    return something_for_parent
```

### The Invariant
Post-order DFS is the natural fit for tree metrics: we need information from children before computing parent's contribution. We maintain a nonlocal/global variable for metrics that don't naturally return up the tree.

### Canonical Problem: Diameter of Binary Tree (LeetCode 543)
**Statement:** Length of longest path between any two nodes in a tree.

```python
def diameter_of_binary_tree(root):
    diameter = 0
    
    def height(node):
        nonlocal diameter
        if not node:
            return 0
        
        left = height(node.left)
        right = height(node.right)
        
        diameter = max(diameter, left + right)
        return max(left, right) + 1
    
    height(root)
    return diameter
```

### Variation Family

**V1: Binary Tree Maximum Path Sum (LeetCode 124)**
- **Twist:** Max sum path (already covered in Path Problems, but fits here too)
- **Change:** Post-order. Return max single path. Update global with left + right + node

**V2: Count Complete Tree Nodes (LeetCode 222)**
- **Twist:** Count nodes in complete binary tree in less than O(n)
- **Change:** Compare left depth and right depth. If equal, tree is perfect: 2^h - 1 nodes. Otherwise recurse

```python
def count_nodes(root):
    if not root:
        return 0
    
    left_depth = right_depth = 0
    left = right = root
    
    while left:
        left_depth += 1
        left = left.left
    while right:
        right_depth += 1
        right = right.right
    
    if left_depth == right_depth:
        return (1 << left_depth) - 1  # 2^h - 1
    
    return 1 + count_nodes(root.left) + count_nodes(root.right)
```

**V3: Maximum Depth of Binary Tree (LeetCode 104)**
- **Twist:** Find maximum depth
- **Change:** `return 1 + max(max_depth(left), max_depth(right))`

**V4: Minimum Depth of Binary Tree (LeetCode 111)**
- **Twist:** Find minimum depth (shortest root-to-leaf path)
- **Change:** If one child is null, must use the other. Only take min when both exist

```python
def min_depth(root):
    if not root:
        return 0
    if not root.left:
        return 1 + min_depth(root.right)
    if not root.right:
        return 1 + min_depth(root.left)
    return 1 + min(min_depth(root.left), min_depth(root.right))
```

**Near Miss: House Robber III**
- **Looks like:** Tree metrics
- **But:** DP on tree with rob/Skip states. Returns tuple, not single metric
- **Lesson:** Some tree problems need stateful returns, not just aggregation

---

## Pattern 07 Mastery Checklist

Before moving to Pattern 08, confirm you can:

- [ ] Implement recursive and iterative versions of pre/in/post-order traversals
- [ ] Do BFS level-order with correct level grouping
- [ ] Use backtracking to find all root-to-leaf paths
- [ ] Use prefix sums for path sum problems
- [ ] Validate BST with min/max ranges
- [ ] Check balanced tree with O(n) post-order
- [ ] Find LCA in both general binary tree and BST
- [ ] Serialize/deserialize with preorder + null markers
- [ ] Build tree from preorder+inorder and inorder+postorder
- [ ] Invert, flatten, trim BST with post-order processing
- [ ] Compute diameter using height post-order
- [ ] Count nodes in complete tree in O(log^2 n)
- [ ] Distinguish: what to return from recursive helper (height, sum, boolean, node)

---

## The Traps

| Trap | What Happens | Fix |
|---|---|---|
| Not handling empty tree | Null pointer exception | Always check `if not root: return ...` |
| Confusing height vs depth | Off-by-one in diameter/depth | Height = edges to deepest leaf. Depth = edges from root |
| BST validation without range | Only check immediate parent | Pass min/max bounds down recursion |
| Modifying tree without returning root | Lost tree reference | Always return node in modification functions |
| BFS without tracking level size | Wrong level grouping | `level_size = len(queue)` at start of each level |
| Building tree with O(n) index search | O(n^2) instead of O(n) | Use hash map for inorder indices |
| LCA returning wrong when one node absent | Incorrect result if p or q not in tree | Add existence check, or assume p and q exist |
| Flatten tree losing right subtree | Right subtree overwritten | Save references before rewiring |

---

## Pattern Blends (What Comes Next)

Trees do not live in isolation. They blend with:

- **DFS/Recursion:** Natural fit for tree traversal
- **BFS/Queue:** Level-order, shortest path in unweighted tree
- **Hash Map:** Vertical order, node correlation, inorder index lookup
- **Linked List:** Flatten tree to linked list, tree serialization
- **DP:** House robber on tree, max path sum with state
- **Binary Search:** Searching in BST, trimming BST

---

*Next: Pattern 08 — Heap*

(End of file)
