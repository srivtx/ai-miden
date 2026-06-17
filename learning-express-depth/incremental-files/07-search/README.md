# 07 — Search (File Storage)

Full-text search on filenames and content. SQLite FTS5.

**What's new:**
- FTS5 virtual table synced with triggers
- Search across filename AND content
- BM25 ranking
- Autocomplete (prefix matching with `*`)

**Why FTS5?** Real search engine. Word stemming, prefix matching, phrase queries, ranking. Built into SQLite.

## Run
```bash
npm install && node server.js
```

```bash
# Add some files
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "meeting notes", "content": "Discussed Q1 plans and budget"}'
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "budget report", "content": "Q1 budget analysis"}'

# Search
curl 'http://localhost:3000/search?q=budget'
# Returns: "budget report" first (matches title + content)

# Autocomplete
curl 'http://localhost:3000/suggest?q=budg'
# Returns: ["budget report"]
```

## What we learned
- FTS5 virtual tables
- Triggers for sync
- BM25 ranking
- Autocomplete

## Next
**08-thumbnails** — generate image thumbnails. Don't make users download 4MB to see a preview.
