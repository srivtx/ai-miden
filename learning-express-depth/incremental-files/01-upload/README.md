# 01 — Upload (File Storage)

File upload. Metadata in DB, content on disk. SHA-256 for integrity.

**What's here:**
- `files` table: id, user_id, filename (on disk), original_name, mime_type, size, sha256
- Multipart upload with multer
- 100MB size limit
- Random filenames on disk (no path traversal)
- SHA-256 hash for dedup and integrity

**Why random filenames?** If we use the user's filename, two users uploading "report.pdf" would overwrite each other. Random names prevent this.

**Why SHA-256?** Two reasons:
1. **Dedup**: if two users upload the same file, the SHA matches. We could store only one copy.
2. **Integrity**: the user can verify their file isn't corrupted.

**Why 100MB limit?** Without it, users can upload huge files. The default in multer is unlimited (dangerous).

## Run
```bash
npm install && node server.js
```

```bash
# Upload
curl -X POST http://localhost:3000/files \
  -F "file=@/path/to/image.png" \
  -F "user_id=u_alice"
# 201 { id, filename, size, mime_type, sha256 }

# Get info
curl http://localhost:3000/files/f_xxx
```

## What this stage teaches
- File upload with metadata
- Random filenames for safety
- SHA-256 hashing
- Size limits

## Next
**02-download** — let users download the files they uploaded.
