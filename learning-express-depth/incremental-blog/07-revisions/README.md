# 07 — Revisions

Every save creates a revision. See history, restore old versions, diff.

**What's new:**
- `revisions` table: every save creates a row
- `current_revision_id` on the post
- List, get, restore, diff endpoints
- Optional `message` field on each save (like a commit message)

**Why revisions?** "I deleted a paragraph by accident." "What did this look like last week?" "We agreed on version 3 of the text, where did that go?"

Real-world: Wikipedia, Google Docs, Notion. All keep full revision history.

## Run
```bash
npm install && node server.js
```

```bash
# Create
curl -X POST http://localhost:3000/posts -H "Content-Type: application/json" \
  -d '{"title": "First draft", "body": "v1 content", "author_id": "alice"}'

# Make some changes
curl -X PATCH http://localhost:3000/posts/1 -H "Content-Type: application/json" \
  -d '{"body": "v2 content", "author_id": "alice", "message": "fixed typo"}'

# See history
curl http://localhost:3000/posts/1/revisions
# [{ id: 2, message: "fixed typo", ... }, { id: 1, message: "initial", ... }]

# See a specific revision
curl http://localhost:3000/posts/1/revisions/1

# Restore
curl -X POST http://localhost:3000/posts/1/restore/1 -H "Content-Type: application/json" -d '{"author_id": "alice"}'

# Diff
curl 'http://localhost:3000/posts/1/diff?from=1&to=2'
```

## What this stage teaches
- Append-only history
- Restore from any point
- Diff between revisions
- Commit-style messages

## Next
**08-search** — full-text search across all published posts.
