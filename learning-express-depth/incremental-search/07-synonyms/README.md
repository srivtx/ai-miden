# 07 — Synonyms (Search)

"phone" should match "mobile". Query expansion via synonym table.

**What's new:**
- `synonyms` table: word → synonym mappings
- Query expansion: for each query word, add its synonyms
- FTS5 OR query: matches any of the expanded terms
- Admin endpoints to add synonyms

**Why synonyms?** Same thing, different words. Without them, the user has to guess the "right" word. With them, the system is more forgiving.

**Why bidirectional?** "phone" → "mobile" and "mobile" → "phone". We store both. This is simpler than one-way rules.

**The OR in FTS5:** `phone OR mobile OR cellphone` matches docs containing any of them. The FTS5 engine handles the boolean logic.

## Run
```bash
npm install && node server.js
```

```bash
# Search for "phone"
curl 'http://localhost:3000/search?q=phone'
# { expanded_query: "phone OR mobile OR cellphone", results: [...] }

# Search for "cellphone" — same results
curl 'http://localhost:3000/search?q=cellphone'
# { expanded_query: "cellphone OR phone", results: [...] }

# Add a synonym
curl -X POST http://localhost:3000/admin/synonyms -H "Content-Type: application/json" \
  -d '{"word": "js", "synonym": "javascript"}'

# See all synonyms
curl http://localhost:3000/admin/synonyms
```

## What we learned
- Synonym table pattern
- Query expansion
- FTS5 OR queries
- The "forgive typos and synonyms" pattern

## Next
**08-ranking** — learn from clicks. Pages that get clicked rank higher.
