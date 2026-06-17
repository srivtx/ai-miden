# 11 — Todo (search)

Full-text search with relevance ranking using SQLite FTS5.

**What's new:**
- FTS5 virtual table (`todos_fts`)
- Triggers to keep FTS in sync with the main table
- BM25 ranking: best matches first
- Search by single word, phrase, or prefix

**Why FTS5?** Real search engine. Handles word stemming, prefix matching, phrase queries, ranking. Built into SQLite.

**Search syntax:**
- `search?q=milk` — find todos with "milk"
- `search?q="buy milk"` — exact phrase
- `search?q=mil*` — prefix (matches "milk", "million", etc.)

## Run
```bash
npm install && node server.js
```

```bash
# Add some todos
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Buy milk", "body": "from the store"}'
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Walk dog", "body": "in the morning"}'
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Drink milk", "body": "for calcium"}'

# Search
curl 'http://localhost:3000/search?q=milk'
# Returns both "Buy milk" and "Drink milk", ranked by relevance

# Phrase
curl 'http://localhost:3000/search?q=%22buy+milk%22'
# Only "Buy milk"

# Prefix
curl 'http://localhost:3000/search?q=mi*'
# Words starting with "mi"
```

## What this stage teaches
- FTS5 virtual tables
- Triggers to keep data in sync
- BM25 ranking
- Search query syntax

## Next
**12-todo-webhooks** — the final piece. Notify other systems when something changes.
