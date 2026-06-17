# Soft Delete Demo — Mark deleted, never remove, restore, audit

Soft delete = don't actually remove the row. Mark it with a `deleted_at` timestamp. It stays in the table, but queries filter it out. You can restore it later.

## Endpoints
```
GET    /items                       # active items only
GET    /items?include_deleted=true  # all items
GET    /items/deleted               # only deleted items
GET    /items/:id                   # 410 Gone if deleted
POST   /items                       # create
DELETE /items/:id                   # soft delete
POST   /items/:id/restore           # restore
DELETE /items/:id/hard              # actually delete (careful)
```

## Try
```bash
# Soft delete
curl -X DELETE http://localhost:3000/items/it_1
# { id: "it_1", deleted: true }

# Try to read it
curl http://localhost:3000/items/it_1
# 410 { error: "gone", deletedAt: "2024-..." }

# Restore it
curl -X POST http://localhost:3000/items/it_1/restore
# { id: "it_1", restored: true }

# See deleted items
curl http://localhost:3000/items/deleted
```

## What this teaches
1. **Soft vs hard delete**: soft = reversible, hard = permanent
2. **`deleted_at` column**: nullable, set on delete, null on restore
3. **`deleted_by` audit**: who deleted it
4. **410 Gone**: the resource existed but was intentionally removed
5. **Every list query must filter `WHERE deleted_at IS NULL`**: easy to forget
6. **Trade-off**: simpler to implement, but table grows forever and queries get slower
7. **When to use**: legal/audit requirements, accidental deletes, undo
