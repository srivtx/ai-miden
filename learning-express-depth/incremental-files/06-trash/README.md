# 06 — Trash (File Storage)

Soft delete. Files go to trash. Can be restored. Auto-purged after 30 days.

**What's new:**
- `deleted_at` and `deleted_by` columns
- Soft delete (the file isn't removed, just marked)
- `/trash` lists trashed files
- Restore from trash
- Manual purge (permanent delete)
- Auto-purge after 30 days (background job every hour)

**Why soft delete?** Users delete by accident. Trash gives them a window to recover. Google Drive, Dropbox, iCloud all do this.

**Why 30 days?** Industry standard. Long enough that users notice and recover. Short enough that storage doesn't grow forever.

**The auto-purge:** every hour, we check for trashed files older than 30 days and delete them for real.

## Run
```bash
npm install && node server.js
```

```bash
# Soft delete
curl -X DELETE http://localhost:3000/files/f_xxx -H "Content-Type: application/json" \
  -d '{"deleted_by": "u_alice"}'

# See trash
curl http://localhost:3000/trash

# Restore
curl -X POST http://localhost:3000/files/f_xxx/restore

# Permanent delete
curl -X DELETE http://localhost:3000/files/f_xxx/purge
```

## What this stage teaches
- Soft delete pattern
- TTL on deleted items
- Background cleanup jobs
- The "trash" pattern (Google Drive style)

## Next
**07-search** — full-text search across filenames and content.
