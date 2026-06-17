# 02 — Sessions (Analytics)

Group events into sessions. A session is a continuous visit (30 min idle timeout).

**What's new:**
- `sessions` table: id, user_id/anonymous_id, started_at, ended_at, event_count
- Auto-attach each event to a session
- 30-minute idle timeout: a new event after 30 min of inactivity starts a new session
- Session stats: total sessions, unique users, avg events per session

**Why sessions?** A user does many events in one visit. You want to count visits, not events. "1000 page views" is less interesting than "500 visits with 2 page views each on average."

**Why 30 min?** Industry standard. Google Analytics uses 30 min. After 30 min of no events, the user is considered gone.

## Run
```bash
npm install && node server.js
```

```bash
# Track a few events
curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "page_view"}'

curl -X POST http://localhost:3000/track -H "Content-Type: application/json" \
  -d '{"user_id": "u_alice", "event_name": "page_view"}'

# See sessions
curl 'http://localhost:3000/sessions?user_id=u_alice'
# { sessions: [{ id, started_at, event_count: 2 }] }

# Stats
curl http://localhost:3000/sessions/stats
# { total_sessions: 1, unique_users: 1, avg_events_per_session: 2 }
```

## What this stage teaches
- Session boundaries (idle timeout)
- Auto-attach events to sessions
- Unique user counting (user_id OR anonymous_id)
- Aggregation: avg events per session

## Next
**03-funnels** — track a sequence of events. "How many people signed up?"
