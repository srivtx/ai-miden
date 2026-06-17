# 10 — Quotas (File Storage, final stage)

Per-user storage limits. Check before upload. Reject if over quota.

**What's new:**
- `quota_bytes` on users (default 1GB)
- Check before every upload
- 413 (Payload Too Large) with usage info
- Get quota usage
- Update quota (admin action)

**Why quotas?** Without them, one user can fill your entire disk. With quotas, every user has a fair share. Free tier: 1GB. Pro: 100GB. Enterprise: unlimited.

**Why check before insert?** Don't waste disk by accepting uploads you'd reject. Check first, then insert.

**Why 413?** Status code for "too big." Different from 400 (bad request) and 507 (insufficient storage). 413 is right for "the user's quota is full."

## Run
```bash
npm install && node server.js
```

```bash
# Upload within quota
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "doc.pdf", "size_bytes": 1000000, "user_id": "u_alice"}'
# 201

# Try to upload a huge file
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "huge.zip", "size_bytes": 2000000000, "user_id": "u_alice"}'
# 413 quota_exceeded

# Check usage
curl http://localhost:3000/users/u_alice/quota
# { used: 1000000, quota: 1073741824, available: 1072741824, percent_used: 0.1 }

# Increase quota
curl -X PATCH http://localhost:3000/users/u_alice/quota -H "Content-Type: application/json" \
  -d '{"quota_bytes": 107374182400}'  # 100GB
```

## What we learned
- Per-user storage limits
- Quota check before upload
- 413 status code
- Available vs used

## 🎉 10 stages complete!

The full file storage app has:
- Upload ✓
- Download ✓
- Folders ✓
- Sharing ✓
- Versions ✓
- Trash ✓
- Search ✓
- Thumbnails ✓
- Compression ✓
- Quotas ✓

This is how Dropbox, Google Drive, OneDrive all work. Same 10 patterns, different code.

## The 10 patterns
1. **Upload** — metadata + content on disk
2. **Download** — stream, content-disposition
3. **Folders** — self-referencing parent_id
4. **Sharing** — many-to-many with permissions
5. **Versions** — append-only history
6. **Trash** — soft delete with TTL
7. **Search** — FTS with ranking
8. **Thumbnails** — small previews
9. **Compression** — gzip text files
10. **Quotas** — per-user limits

These 10 patterns are the building blocks of every file storage system.
