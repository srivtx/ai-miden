# 07 — Files (Chat)

Upload files and share them in chat. Image previews, file metadata, security.

**What's new:**
- `files` table: id, filename, mime_type, size, uploader, room
- `file_id` on messages (a message can be a file share)
- Multipart upload endpoint (`POST /rooms/:id/files`)
- File metadata endpoint (`GET /files/:id`)
- Download endpoint with path-traversal protection
- 25MB size limit

**Why a separate `files` table?** Same as the blog — files have their own metadata (size, mime, uploader). Messages can reference them. One file could be shared in multiple rooms.

**Why size limit?** Without it, users can upload 10GB files and fill your disk. 25MB is a common default (Slack allows 1GB on paid plans, Discord allows 25MB on free).

## Run
```bash
npm install && node server.js
```

```bash
# Upload a file to a room
curl -X POST http://localhost:3000/rooms/general/files \
  -F "file=@/path/to/image.png" \
  -F "user_id=u_alice"
# 201 { file_id, message_id, url, mime_type, size }

# Get file info
curl http://localhost:3000/files/f_xxx

# Download
curl http://localhost:3000/files-download/abc123.png -o downloaded.png
```

## What this stage teaches
- File upload to chat
- Linking files to messages
- Path traversal protection
- Size limits

## Next
**08-reactions** — emoji reactions on messages. 👍 ❤️ 😂
