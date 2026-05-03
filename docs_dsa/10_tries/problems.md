# Pattern 10: Tries — Practice Problems

## Basic Trie

### 208. Implement Trie (Prefix Tree)
**Statement:** Implement trie with insert, search, starts_with.
**Code:**
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
    
    def search(self, word):
        node = self._find_node(word)
        return node is not None and node.is_end
    
    def starts_with(self, prefix):
        return self._find_node(prefix) is not None
    
    def _find_node(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

### 211. Design Add and Search Words Data Structure
**Statement:** Search with '.' wildcard matching any letter.
**Intuition:** DFS from current node when encountering '.'.

---

## Word Search

### 79. Word Search
**Statement:** Does word exist in grid? Adjacent cells.
**Intuition:** DFS from each cell. Mark visited.
**Code:**
```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[i]:
            return False
        temp = board[r][c]
        board[r][c] = '#'
        found = dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or dfs(r, c+1, i+1) or dfs(r, c-1, i+1)
        board[r][c] = temp
        return found
    
    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False
```

### 212. Word Search II
**Statement:** Find all words in grid.
**Intuition:** Build trie from words. DFS from each cell. When word found, add to result and remove from trie (prune).

---

## Prefix Matching

### 648. Replace Words
**Statement:** Replace words in sentence with their root from dictionary.
**Intuition:** Build trie from roots. For each word, find shortest root prefix.

### 720. Longest Word in Dictionary
**Statement:** Longest word that can be built one character at a time from other words.
**Intuition:** Sort by length. Build trie. Check if all prefixes exist.

### 14. Longest Common Prefix
**Statement:** Longest common prefix among strings.
**Intuition:** Build trie. Find deepest node with single child path. Or simple vertical scanning.

---

## XOR / Bit Trie

### 421. Maximum XOR of Two Numbers in an Array
**Statement:** Find maximum XOR of any two numbers.
**Intuition:** Bit trie. For each number, greedily choose opposite bit.
**Code:**
```python
def find_maximum_xor(nums):
    root = {}
    max_xor = 0
    
    for num in nums:
        node = root
        xor_node = root
        current_xor = 0
        
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            # Insert
            if bit not in node:
                node[bit] = {}
            node = node[bit]
            
            # Query
            toggled = 1 - bit
            if toggled in xor_node:
                current_xor |= (1 << i)
                xor_node = xor_node[toggled]
            else:
                xor_node = xor_node[bit]
        
        max_xor = max(max_xor, current_xor)
    
    return max_xor
```

### 1707. Maximum XOR With an Element From Array
**Statement:** For each query (xi, mi), find max XOR with element <= mi.
**Intuition:** Sort nums and queries by limit. Add nums to trie as we go. Query trie for each xi.

---

## Mixed Drill Set

1. 208 — Implement trie
2. 79 — Word search (single word)
3. 212 — Word search II (trie + DFS)
4. 648 — Replace words
5. 421 — Maximum XOR
6. 211 — Search with wildcards
7. 720 — Longest word
8. 14 — Longest common prefix
