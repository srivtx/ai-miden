# 08 — Search

Full-text search using FTS5. Ranked by relevance. Autocomplete suggestions.

**What's new:**
- FTS5 virtual table synced with triggers
- Search across title, body, tags
- Status filter (only published by default)
- BM25 ranking (best matches first)
- Autocomplete endpoint

**Why triggers?** When you INSERT a post, the trigger automatically adds it to the FTS table. When you UPDATE or DELETE, the FTS table is updated too. No need to remember.

## Run
```bash
npm install && node server.js
```

```bash
# Add some posts
curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "Learning backend", "body": "How to learn backend development", "status": "published", "tags": "tutorial"}'

curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "Frontend tips", "body": "Some frontend tricks", "status": "published", "tags": "tutorial"}'

# Search
curl 'http://localhost:3000/search?q=backend'
# Returns: "Learning backend" first (most relevant)

# Autocomplete
curl 'http://localhost:3000/suggest?q=lear'
# Returns: ["Learning backend"]
```

## What this stage teaches
- FTS5 virtual tables
- Triggers to keep FTS in sync
- BM25 ranking
- Autocomplete (prefix matching with `*`)

## Next
**09-rss** — generate an RSS feed. Let readers subscribe.
