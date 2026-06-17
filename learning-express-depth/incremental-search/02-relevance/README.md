# 02 — Relevance (Search)

Rank results by score. Title matches count more. Word frequency matters.

**What's new:**
- Score function: count of query terms in doc + 5x title boost
- Sort by score (descending)
- Tokenize: split on non-alphanumeric, lowercase

**Why title boost?** A doc with the search term in the title is more likely to be what the user wants. Title is the human-curated summary.

**Why word frequency?** If a doc has "javascript" 3 times and another has it once, the first is more focused on that topic. Higher count = more relevant.

**The score:** `count_in_body + 5 * count_in_title`. Simple. Effective. Real search engines add many more signals (BM25, TF-IDF, page rank, etc.).

## Run
```bash
npm install && node server.js
```

```bash
curl 'http://localhost:3000/search?q=javascript'
# 1. "How to learn JavaScript" (title match + 3 body)
# 2. "Web development" (body only, 2 mentions)
# Both have "javascript" but the title match wins.

curl 'http://localhost:3000/search?q=python+data'
# 1. "Data science basics" (mentions both "python" and "data")
# 2. "Python tutorial" (only "python")
```

## What we learned
- Tokenization
- Term frequency scoring
- Title boost
- Sort by relevance

## Next
**03-filters** — combine search with filters. Search "phone" + filter "category: electronics".
