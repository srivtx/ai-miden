# 01 — Events (Analytics)

Track events. Anything users do: page view, button click, purchase, etc.

**What's here:**
- `events` table: user_id (or anonymous_id), event_name, properties (JSON), timestamp
- Single track: `POST /track`
- Batch track: `POST /track/batch`
- Query: filter by event name, user, time
- Top events by count

**Why anonymous_id?** Track users before they sign up. You get a cookie or localStorage ID. When they sign up, you can merge the two streams.

**Why JSON properties?** Each event has different fields. `page_view` has `url`, `button_click` has `button_id`, `purchase` has `amount`. JSON keeps it flexible.

**Why batch?** Reduces HTTP overhead. 100 events in 1 request is faster than 100 in 100 requests.

## Run
```bash
npm install && node server.js
```

```bash
# Single event
curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "page_view", "properties": {"url": "/home"}}'

# Batch
curl -X POST http://localhost:3000/track/batch -H "Content-Type: application/json" \
  -d '{"events": [
    {"event_name": "page_view", "properties": {"url": "/home"}},
    {"event_name": "button_click", "properties": {"button": "signup"}}
  ]}'

# Top events
curl http://localhost:3000/events/top
```

## What this stage teaches
- Event tracking
- Single + batch ingestion
- JSON properties
- Querying by time, user, event

## Next
**02-sessions** — group events into sessions. Each visit is one session.
