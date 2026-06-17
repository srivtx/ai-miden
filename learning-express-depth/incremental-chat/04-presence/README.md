# 04 — Presence (Chat)

Track who's online. Heartbeat from the client, "last seen" on the server.

**What's new:**
- `presence` table: user_id, last_seen_at, status
- Heartbeat endpoint (called by client every 30s)
- Offline endpoint (called when client closes)
- Who's online query (filtered by recent activity)
- 30-second timeout: if you don't heartbeat, you're offline

**Why heartbeats?** Servers don't know when a client disconnects. The client has to tell us. "I'm still here" every 30 seconds. If we don't hear from you for 30s, we mark you offline.

**Why 30s?** Trade-off: shorter = more accurate but more requests. Longer = less accurate but fewer requests. 30s is common (Slack uses 30s, WhatsApp uses 30s).

## Run
```bash
npm install && node server.js
```

```bash
# Heartbeat
curl -X POST http://localhost:3000/presence/heartbeat -H "Content-Type: application/json" -d '{"user_id": "u_xxx"}'

# See who's online
curl http://localhost:3000/presence
# { count: N, online: [{ id, username, display_name, last_seen_at }] }

# Wait 30 seconds — those users are now offline
```

## What this stage teaches
- Heartbeat pattern
- Last-seen-at
- "Online" is a state, not a fact
- The trade-off between accuracy and request count

## Next
**05-typing** — show "Alice is typing..." indicators.
