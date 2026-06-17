# 07 — Digest (Notifications)

Group notifications. Instead of 10 emails, send 1 daily digest.

**What's new:**
- Notifications have a `delivered_at` field (null = pending)
- `/digest/:user_id` shows all undelivered notifications in a window
- `/digest/:user_id/send` marks them all delivered

**Why digests?** 10 emails for 10 events is noise. Users tune out. One email with 10 items is signal. They read it.

**Why a 24h window?** Daily digest is the standard. The cron job runs at 9am: "Send each user the digest of yesterday's events."

**How it works:**
1. Throughout the day, notifications are queued
2. At 9am the next day, the cron job calls `/digest/:user_id` for each active user
3. Sends one email with all the pending items
4. Marks them as delivered

## Run
```bash
npm install && node server.js
```

```bash
# Queue some notifications
curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "type": "comment", "title": "New comment on your post"}'

curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "type": "follow", "title": "Bob started following you"}'

# Build the digest
curl http://localhost:3000/digest/u_alice
# { count: 2, summary: "You have 2 new notifications:\n\n- [comment] ...\n- [follow] ..." }

# Send it (marks delivered)
curl -X POST http://localhost:3000/digest/u_alice/send
# { delivered: 2 }
```

## What we learned
- Digest pattern (group + send)
- Pending vs delivered
- 24h window
- Cron-driven delivery

## Next
**08-batch** — group sends for efficiency. Send to 1000 users in one go.
