# 09 — Priority (Notifications)

Some notifications are urgent, some can wait. Priority levels: critical, high, normal, low.

**What's new:**
- `priority` field on notifications
- Critical and high: send immediately
- Normal and low: queue for batch processing
- `/process-queue` endpoint to flush the queue

**Why priority?** "Your payment failed" should be immediate. "5 people liked your post" can wait. Different urgencies need different handling.

**The trade-off:** Immediate = bad batching, more costs. Batched = better throughput, but a 15-min delay. Priority lets you balance.

**The cron job:** every minute, call `/process-queue` to flush high-priority queued items. Normal items can wait 5-15 min. Low items get batched with the daily digest.

## Run
```bash
npm install && node server.js
```

```bash
# Critical: sent immediately
curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "title": "Payment failed!", "priority": "critical"}'
# 202 { status: "sending" }

# Normal: queued
curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "title": "New follower", "priority": "normal"}'
# 202 { status: "queued" }

# Process the queue
curl -X POST http://localhost:3000/process-queue
# { processed: 1 }

# Bad priority
curl -X POST http://localhost:3000/notifications -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "title": "Test", "priority": "urgent"}'
# 422 invalid priority
```

## What we learned
- Priority levels
- Immediate vs batched delivery
- The cron-driven queue flush
- When to use which priority

## Next
**10-analytics** — the final stage. Track delivery, open, click rates.
