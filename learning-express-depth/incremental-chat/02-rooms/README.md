# 02 — Rooms (Chat)

Multiple rooms. Each room has its own message timeline.

**What's new:**
- `rooms` table: id, name, public/private
- `room_id` on every message
- `/rooms` to list and create
- `/rooms/:id/messages` to list/post in a room
- Auto-create rooms on first message (Twitter-style "any name works")

**Why rooms?** Without them, every user sees every message. With rooms, the team has #general, #random, #projects. Different conversations in different places.

**Why auto-create?** Lower friction. The user doesn't have to create a room before chatting. Just type a room name.

## Run
```bash
npm install && node server.js
```

```bash
# Create explicit
curl -X POST http://localhost:3000/rooms -H "Content-Type: application/json" -d '{"name": "general"}'

# Or just post — auto-creates
curl -X POST http://localhost:3000/rooms/general/messages -H "Content-Type: application/json" -d '{"sender": "alice", "text": "Hello team!"}'

# Get room messages
curl http://localhost:3000/rooms/general/messages
```

## What this stage teaches
- Nested resources (rooms → messages)
- Get-or-create pattern (auto-create on first access)
- Private vs public rooms
- The pattern of "any unique name is a room"

## Next
**03-users** — proper user accounts. Login, display names, avatars.
