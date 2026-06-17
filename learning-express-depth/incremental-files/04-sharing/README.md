# 04 — Sharing (File Storage)

Share files with other users. Permissions: read, write, owner.

**What's new:**
- `shares` table: file_id, user_id, permission
- `canAccess()` helper: check if user can read or write
- Share endpoint: only owner can share
- Permission levels: read, write, owner
- Access check on every read

**Why permissions?** Without them, any logged-in user could read anyone's files. With them, you decide who sees what.

**Why a separate table?** Many-to-many: a file can be shared with many users, a user can have many files shared with them. A junction table is the standard pattern.

## Run
```bash
npm install && node server.js
```

```bash
# Owner creates a file
curl -X POST http://localhost:3000/files -H "Content-Type: application/json" \
  -d '{"name": "secret.txt", "owner_id": "u_alice"}'

# Owner shares with read access
curl -X POST http://localhost:3000/files/f_xxx/shares -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "user_id_to_share": "u_bob", "permission": "read"}'

# Bob can read
curl 'http://localhost:3000/files/f_xxx?user_id=u_bob'
# { name: "secret.txt", your_permission: "read" }

# Random user cannot
curl 'http://localhost:3000/files/f_xxx?user_id=u_eve'
# 403 no_access
```

## What this stage teaches
- Permission system
- Many-to-many via junction table
- Access check helper
- Owner can share, others can't

## Next
**05-versions** — every save creates a version. Restore old versions.
