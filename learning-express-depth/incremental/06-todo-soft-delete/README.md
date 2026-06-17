# 06 — Todo (soft delete)

Never actually delete. Mark with `deleted_at`. Restore on demand. Permanent delete only when explicitly asked.

**What's new:**
- `deleted_at` and `deleted_by` columns
- `DELETE` sets the timestamp (doesn't remove the row)
- `POST /todos/:id/restore` brings it back
- `GET /todos/trash` shows deleted items
- `DELETE /todos/:id/hard` for permanent deletion

**Why soft delete?**
- Users delete things by accident
- Compliance: keep data for N years
- Audit: know who deleted what
- Restore: "undo" without database backup

**Trade-off:** The table grows forever. You need a real cleanup job for very old trash.

## Run
```bash
npm install && node server.js
```

```bash
# Create
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" -d '{"title": "Test"}'

# Soft delete
curl -X DELETE http://localhost:3000/todos/1 -H "Content-Type: application/json" -d '{"deletedBy": "alice"}'

# Try to list (it's gone)
curl http://localhost:3000/todos
# count: 0

# But it's in the trash
curl http://localhost:3000/todos/trash
# count: 1

# Restore
curl -X POST http://localhost:3000/todos/1/restore

# It's back
curl http://localhost:3000/todos
# count: 1

# Hard delete (permanent)
curl -X DELETE http://localhost:3000/todos/1/hard
```

## What this stage teaches
- Soft delete pattern
- Trash + restore
- Hard delete escape hatch
- Audit fields (`deleted_by`)

## Next
**07-todo-audit** — log every change: who, what, when, from where.
