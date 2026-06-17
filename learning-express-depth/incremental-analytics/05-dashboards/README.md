# 05 — Dashboards (Analytics)

Pre-computed metrics in one endpoint. Powers the dashboard UI.

**What's new:**
- `/dashboard` returns all the key numbers in one call
- DAU / WAU / MAU (daily/weekly/monthly active users)
- Total events, events in last 24h
- Top events
- Revenue (sum of `amount` property on `purchase` events)
- Daily event counts (for charts)

**Why one endpoint?** The dashboard loads faster. One HTTP call, all the data. The client doesn't have to coordinate 5 requests.

**Why pre-computed?** We could compute on every request, but that's slow at scale. In production, these would be pre-computed every minute or hour by a background job. Here we compute on read.

**DAU/WAU/MAU:** the three most important metrics. "How many people used the product today? This week? This month?" Growth in DAU = product-market fit.

## Run
```bash
npm install && node server.js
```

```bash
# Track some events
curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "page_view"}'

curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "purchase", "properties": {"amount": 29.99}}'

# Get the dashboard
curl http://localhost:3000/dashboard
# {
#   totals: { events: 2, events_24h: 2 },
#   active_users: { dau: 1, wau: 1, mau: 1 },
#   top_events: [{ event_name: "page_view", count: 1 }, ...],
#   revenue_30d: 29.99,
#   daily_counts: [{ day: "2024-12-15", count: 2 }]
# }
```

## What this stage teaches
- One endpoint, many metrics
- DAU/WAU/MAU
- Aggregation in one query
- The dashboard pattern

## Next
**06-exports** — let users export data. CSV, JSON, large file support.
