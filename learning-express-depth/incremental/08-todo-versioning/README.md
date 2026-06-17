# 08 — Todo (versioning)

Optimistic locking. The client sends the version they last saw. The server rejects if the row has been updated since.

**What's new:**
- `version` column on every todo
- `PATCH` requires `version` in the body
- If `version` doesn't match the current version: 409 Conflict
- Server returns the current state so the client can retry
- Status 428 (Precondition Required) when version is missing

**Why?** Two people editing the same todo. Without versioning, the second save overwrites the first. With versioning, the second save gets rejected, and they see the latest version.

## Run
```bash
npm install && node server.js
```

```bash
# Create a todo
T=$(curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Original"}')
ID=$(echo $T | grep -o '"id":[0-9]*' | cut -d: -f2)
VER=$(echo $T | grep -o '"version":[0-9]*' | cut -d: -f2)

# Update with the correct version
curl -X PATCH http://localhost:3000/todos/$ID -H "Content-Type: application/json" \
  -d "{\"version\": $VER, \"title\": \"Updated\"}"
# 200 with new version

# Try to update with the OLD version
curl -X PATCH http://localhost:3000/todos/$ID -H "Content-Type: application/json" \
  -d "{\"version\": $VER, \"title\": \"Conflict\"}"
# 409 with current state
```

## What this stage teaches
- Optimistic concurrency control
- 409 Conflict status
- 428 Precondition Required
- Conflict resolution (client re-fetches and retries)

## Next
**09-todo-caching** — add Redis. Cache the list, invalidate on changes.
