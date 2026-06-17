# 05 — Typing (Chat)

"Alice is typing..." indicators. Ephemeral — auto-clears after 5 seconds.

**What's new:**
- `typing_indicators` table: room_id, user_id, started_at
- Start typing endpoint (called when user focuses the input)
- Stop typing endpoint (called when they send or blur)
- Background cleanup of stale indicators (every 10s)
- 5-second timeout (if you don't update, the indicator disappears)

**Why ephemeral?** Typing indicators should not persist. If Alice closes her laptop mid-typing, the indicator shouldn't stay forever. We use a timeout.

**The flow:**
1. Alice focuses the message input
2. Client calls `POST /typing`
3. Every few seconds, client re-calls (refreshes `started_at`)
4. Other users see "Alice is typing..." 
5. If Alice stops (5s) or sends the message, indicator disappears

## Run
```bash
npm install && node server.js
```

```bash
# Start typing
curl -X POST http://localhost:3000/rooms/general/typing -H "Content-Type: application/json" -d '{"user_id": "u_alice"}'

# Who's typing
curl http://localhost:3000/rooms/general/typing
# { count: 1, typing: [{ user_id: "u_alice", started_at: "..." }] }

# Wait 5 seconds — indicator gone

# Stop typing (when sending message)
curl -X DELETE http://localhost:3000/rooms/general/typing?user_id=u_alice
```

## What this stage teaches
- Ephemeral state
- Auto-expiry via timestamps
- Background cleanup tasks
- The "presence" pattern (transient state)

## Next
**06-receipts** — read receipts. Who has read which messages?
