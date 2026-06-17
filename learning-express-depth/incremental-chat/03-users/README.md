# 03 — Users (Chat)

User accounts. Display names, avatars, status. Messages are linked to users.

**What's new:**
- `users` table: id, username, display_name, avatar_url, status
- `user_id` on every message (replaces `sender` string)
- `X-User-Id` header for simple auth
- Messages JOINed with users to show display name + avatar

**Why a separate display_name and username?** Username is the unique identifier (like an email). Display name is what other users see (like "Alice Smith" or just "Alice"). You can change your display name without losing your account.

## Run
```bash
npm install && node server.js
```

```bash
# Create a user
USER=$(curl -X POST http://localhost:3000/users -H "Content-Type: application/json" \
  -d '{"username": "alice", "display_name": "Alice", "avatar_url": "https://..."}' | grep -o '"id":"[^"]*' | cut -d'"' -f4)

# Post as that user
curl -X POST http://localhost:3000/rooms/general/messages \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $USER" \
  -d '{"text": "Hello!"}'

# Get messages with user info
curl http://localhost:3000/rooms/general/messages
# { messages: [{ text: "Hello!", username: "alice", display_name: "Alice", avatar_url: "..." }] }
```

## What this stage teaches
- Users as first-class entities
- Display name vs username
- JOIN to attach user info to messages
- Simple auth via header (real apps use JWT)

## Next
**04-presence** — who's online right now? Track user activity.
