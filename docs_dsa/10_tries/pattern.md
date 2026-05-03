# Pattern 10: Tries

> **Pattern Recognition:** When you see "prefix", "auto-complete", "word search", "longest common prefix", "replace words" — think trie.
>
> **Fundamental Insight:** A trie is a tree where each node represents a character. The path from root to node spells a prefix. Tries excel at prefix-based operations: insert, search, starts_with — all in O(length of word).

---

## Archetype 10.1: Basic Trie Operations

### Recognition Signal
Words: **"implement trie", "prefix tree", "insert", "search", "starts with"**

### Template
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

### Problems
- Implement Trie (Prefix Tree) (LeetCode 208)
- Design Add and Search Words Data Structure (LeetCode 211) — with '.' wildcard

---

## Archetype 10.2: Word Search in Grid

### Recognition Signal
Words: **"word search", "find words", "board", "Boggle"**

### Problems
- Word Search (LeetCode 79) — DFS on board
- Word Search II (LeetCode 212) — Trie + DFS (optimal)

**Word Search II optimal approach:**
1. Build trie from words
2. DFS from each cell
3. Prune matched words from trie to avoid duplicates

---

## Archetype 10.3: Replace / Prefix Matching

### Recognition Signal
Words: **"replace words", "replace with root", "shortest prefix"**

### Problems
- Replace Words (LeetCode 648)
- Longest Word in Dictionary (LeetCode 720)
- Longest Common Prefix (LeetCode 14) — can use trie

---

## Archetype 10.4: XOR / Bit Trie

### Recognition Signal
Words: **"maximum XOR", "two numbers", "bitwise"**

### Template: Maximum XOR
```python
class TrieNode:
    def __init__(self):
        self.children = {}

class Solution:
    def find_maximum_xor(self, nums):
        root = TrieNode()
        max_xor = 0
        
        for num in nums:
            node = root
            xor_node = root
            current_xor = 0
            
            for i in range(31, -1, -1):
                bit = (num >> i) & 1
                # Insert
                if bit not in node.children:
                    node.children[bit] = TrieNode()
                node = node.children[bit]
                
                # Query for max XOR: try opposite bit
                toggled = 1 - bit
                if toggled in xor_node.children:
                    current_xor |= (1 << i)
                    xor_node = xor_node.children[toggled]
                else:
                    xor_node = xor_node.children[bit]
            
            max_xor = max(max_xor, current_xor)
        
        return max_xor
```

### Problems
- Maximum XOR of Two Numbers in an Array (LeetCode 421)
- Maximum XOR With an Element From Array (LeetCode 1707)

---

## Mastery Checklist
- [ ] Implement trie with insert, search, starts_with
- [ ] Word search II: build trie, DFS from each cell, prune
- [ ] Replace words: find shortest prefix in trie
- [ ] Maximum XOR: bit trie, greedily choose opposite bit
- [ ] Design search with wildcards (dots)

---

## Trie Variations

**Compressed Trie (Radix Tree):** Merge single-child nodes.
**Suffix Trie:** All suffixes of a string. Used for pattern matching.
**Suffix Array/Tree:** More space-efficient alternatives.

---

## Common Traps

**Trap:** Not marking `is_end` properly.
- Fix: `is_end = True` only at final character of inserted word.

**Trap:** Searching for prefix of inserted word.
- Fix: `search` checks `is_end`. `starts_with` does not.

**Trap:** Building trie for word search but not pruning.
- Fix: Remove matched words from trie to avoid finding same word multiple times.

**Near Miss: Word Search (LeetCode 79)**
- Can be solved with DFS only (no trie) for single word
- Trie needed for multiple words (Word Search II)
