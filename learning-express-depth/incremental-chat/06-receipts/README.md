# 06 — Receipts (Chat)

Read receipts. Mark messages as read. Unread count. Who has read what.

**What's new:**
- `read_receipts` table: user_id, message_id, read_at
- Mark single message as read
- Mark all messages in a room up to a point as read (the "I'm caught up" case)
- Unread count per user per room
- Who-read-this-message query

**Why receipts?** "Did they see my message?" You want to know. WhatsApp shows blue checkmarks for read, gray for delivered. Slack shows "Seen by 3."

**Why mark a range?** When you open a chat, you've read everything up to the latest. Marking each one is wasteful. Marking the highest id covers all below it.

## Run
```bash
npm install && node server.js
```

```bash
# Mark a message as read
curl -X POST http://localhost:3000/read -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "message_id": 5}'

# Mark all messages in a room up to id 10 as read
curl -X POST http://localhost:3000/read -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "room_id": "general", "up_to": 10}'

# Unread count
curl 'http://localhost:3000/rooms/general/unread?user_id=u_bob'

# Who read message 5
curl http://localhost:3000/messages/5/receipts
```

## What this stage teaches
- Read receipts pattern
- Marking ranges (more efficient than marking each)
- Unread counts
- The "caught up" pattern

## Next
**07-files** — let users share images, PDFs, and other files in chat.
