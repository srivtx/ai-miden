# 08 — Reactions (Chat)

Emoji reactions on messages. Add, remove, count.

**What's new:**
- `reactions` table: message_id, user_id, emoji
- Whitelist of allowed emojis (security — prevent XSS via emoji names)
- Add a reaction (one per user per message per emoji)
- Remove a reaction
- Get aggregated reactions (emoji → count)
- Messages in a room come with their reactions

**Why a whitelist?** Without it, a user could send any "emoji" — including `<script>` if we rendered it as HTML. Whitelisting prevents injection.

**Why one per user per emoji?** If Bob clicks 👍 5 times, it shouldn't be 5 reactions. Just one.

**Why GROUP_CONCAT?** To get the list of users in one query. SQLite-specific syntax; other DBs have similar (Postgres has `array_agg`).

## Run
```bash
npm install && node server.js
```

```bash
# React to a message
curl -X POST http://localhost:3000/messages/1/reactions -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "emoji": "👍"}'

# Get reactions for the message
curl http://localhost:3000/messages/1/reactions
# { reactions: [{ emoji: "👍", count: 1, users: "u_bob" }] }

# Remove
curl -X DELETE http://localhost:3000/messages/1/reactions -H "Content-Type: application/json" \
  -d '{"user_id": "u_bob", "emoji": "👍"}'

# Get messages with reactions
curl http://localhost:3000/rooms/general/messages
```

## What this stage teaches
- Reaction pattern (unique per user/emoji)
- Aggregation (count by emoji)
- Whitelisting for security
- GROUP_CONCAT for inline lists

## Next
**09-threads** — replies that don't clutter the main channel. Slack-style threads.
