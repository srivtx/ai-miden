# 08 — Batch (Notifications)

Bulk send. Send to many users at once. Efficient and fast.

**What's new:**
- `/broadcast` — send to all users in a segment
- `/bulk` — send to a list of user_ids
- Batch insert (one statement, many rows)

**Why batch?** Sending to 1000 users one at a time is 1000 round-trips. Batching: 1 round-trip with 1000 inserts. 10x-100x faster.

**Why segments?** A common pattern: "send to all premium users" or "send to users in the US". Instead of listing them every time, you group by segment.

**Why bulk insert?** `INSERT INTO ... VALUES (...), (...), (...)` is much faster than 1000 individual inserts. SQLite (and most DBs) optimize this.

## Run
```bash
npm install && node server.js
```

```bash
# Broadcast to all premium users
curl -X POST http://localhost:3000/broadcast -H "Content-Type: application/json" \
  -d '{"segment": "premium", "title": "Premium feature available", "body": "Check out the new dashboard"}'
# 202 { sent_to: 34 }

# Bulk to specific users
curl -X POST http://localhost:3000/bulk -H "Content-Type: application/json" \
  -d '{"user_ids": ["u_1", "u_5", "u_10"], "title": "Hi", "body": "..."}'
# 202 { sent_to: 3 }
```

## What we learned
- Bulk insert (one statement, many rows)
- Segment-based broadcast
- 202 Accepted for batch operations
- The "send to 1000" pattern

## Next
**09-priority** — some notifications are urgent, some can wait.
