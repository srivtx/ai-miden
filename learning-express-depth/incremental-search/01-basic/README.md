# 01 — Basic Search

Simple search. Substring match. No ranking.

**What's here:**
- Documents table: title, body
- `GET /search?q=X` returns matching documents
- Case-insensitive substring match
- No ranking — order is whatever SQLite returns

**Why substring first?** It's the simplest thing. Word: "Learn JavaScript" contains "java". Done.

**Why not this in real apps?** No ranking. "Java" matches "JavaScript" the same as "Java" matches "Java". No relevance. No stemming (running = run, ran, runs). No synonyms.

## Run
```bash
npm install && node server.js
```

```bash
curl 'http://localhost:3000/search?q=java'
# Returns: docs that contain "java" anywhere

curl 'http://localhost:3000/search?q=python'
# Returns: Python tutorial, Data science basics (both contain "python")
```

## What we learned
- Substring search with LIKE
- Case-insensitive matching
- The baseline (before ranking)

## Next
**02-relevance** — add ranking. Title matches count more than body matches. Word frequency matters.
