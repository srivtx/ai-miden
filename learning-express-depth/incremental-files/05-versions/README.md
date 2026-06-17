# 05 — Versions (File Storage)

Every upload creates a new version. See history, restore old versions.

**What's new:**
- `versions` table: file_id, version_number, filename, message
- `current_version` on the file
- New version: `POST /files/:id/versions` (upload again)
- List versions: `GET /files/:id/versions`
- Get a specific version: `GET /files/:id/versions/:v`
- Restore: `POST /files/:id/restore/:v` (creates a new version that's a copy)

**Why versions?** "I deleted something by accident." "What did this look like last week?" Versions are the safety net.

**Why restore creates a new version?** Never delete history. If you "restore" version 3, you actually create version 5 that's a copy of version 3. You can always go back.

**The version_number is monotonic.** 1, 2, 3, 4, 5. Even if you delete the file, the counter doesn't reset.

## Run
```bash
npm install && node server.js
```

```bash
# Upload v1
curl -X POST http://localhost:3000/files -F "file=@/path/v1.txt" -F "user_id=u_alice"

# Upload v2
curl -X POST http://localhost:3000/files/f_xxx/versions -F "file=@/path/v2.txt" -F "user_id=u_alice" -F "message=updated"

# See history
curl http://localhost:3000/files/f_xxx/versions
# { versions: [{ version_number: 2, message: "updated" }, { version_number: 1, message: "initial" }] }

# Get v1
curl http://localhost:3000/files/f_xxx/versions/1 -o v1.txt

# Restore v1
curl -X POST http://localhost:3000/files/f_xxx/restore/1 -H "Content-Type: application/json" -d '{"user_id": "u_alice"}'
# { new_version: 3, restored_from: 1 }
```

## What this stage teaches
- Versioning pattern
- Append-only history
- Restore by copy
- Monotonic version numbers

## Next
**06-trash** — soft delete. Files stay 30 days, then are purged.
