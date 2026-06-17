# 10 — Realtime (Analytics, final stage)

Real-time event stream. SSE for one-to-many. Live counts updated every 5 seconds.

**What's new:**
- `/stream` — SSE endpoint, live event stream
- `POST /track` — also broadcasts to all connected clients
- `/live/counts` — counts per event in the last minute
- `/recent` — latest 20 events

**Why real-time?** Dashboards should feel alive. You track an event and it shows up on the dashboard. No "refresh" needed. Real-time updates are now standard for analytics tools.

**Why SSE instead of WebSocket?** SSE is one-way (server to client). For analytics dashboards, that's enough. WebSocket is bidirectional. SSE is simpler.

**The flow:**
1. Client connects to `/stream`
2. Server adds the client to the set
3. On every `POST /track`, server inserts the event AND broadcasts
4. The broadcast goes to all connected clients
5. When the client disconnects, server removes it from the set

## Run
```bash
npm install && node server.js
```

Open two terminals:

```bash
# Terminal 1: subscribe to the stream
curl -N http://localhost:3000/stream
# event: connected
# data: {"ts":"2024-12-15T..."}
# (waits for events)

# Terminal 2: track an event
curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "page_view"}'
```

Terminal 1 now shows:
```
event: page_view
data: {"id":1,"user_id":"u_alice","properties":{},"ts":"..."}
```

```bash
# Live counts
curl http://localhost:3000/live/counts

# Recent
curl http://localhost:3000/recent
```

## What this stage teaches
- Server-Sent Events
- One-to-many broadcast
- The "live dashboard" pattern
- When to use SSE vs WebSocket

## 🎉 10 stages complete!

The full analytics app has:
- Events ✓
- Sessions ✓
- Funnels ✓
- Cohorts ✓
- Dashboards ✓
- Exports ✓
- Alerts ✓
- Segments ✓
- A/B tests ✓
- Realtime ✓

This is how Mixpanel, Amplitude, PostHog, Heap all work. Same 10 patterns, different code.

## The 10 patterns
1. **Events** — track anything
2. **Sessions** — group events into visits
3. **Funnels** — measure drop-off
4. **Cohorts** — group by signup, track retention
5. **Dashboards** — pre-computed metrics
6. **Exports** — CSV/JSON, streamed
7. **Alerts** — rule-based notifications
8. **Segments** — filter users
9. **A/B tests** — measure variants
10. **Realtime** — live updates

These 10 patterns are the building blocks of every analytics platform.
