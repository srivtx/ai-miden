# Calendar API — Step 8 in the learning path

Builds on Forum. Adds: events with time ranges, recurring events, attendees with RSVP, conflict detection.

## Endpoints
```
GET    /events?from=&to=                        # events in a range (expands recurring)
POST   /events                                  # create (with optional recurrence, attendees)
GET    /events/:id                              # details + attendees
POST   /events/:id/rsvp                         # { email, status: pending|accepted|declined }
GET    /conflicts?start_at=&end_at=             # find overlapping events
```

## Try
```bash
# Create a single event
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"title": "Standup", "start_at": "2024-12-15T09:00:00Z", "end_at": "2024-12-15T09:30:00Z", "attendees": ["bob@x.com"]}'

# Recurring (daily standup for 2 weeks)
curl -X POST http://localhost:3000/events \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"title": "Daily Standup", "start_at": "2024-12-15T09:00:00Z", "end_at": "2024-12-15T09:15:00Z", "recurrence": "daily", "attendees": ["team@x.com"]}'

# List events in a range (expands the recurring one)
curl 'http://localhost:3000/events?from=2024-12-15&to=2024-12-20' \
  -H "X-User-Id: u_alice"

# RSVP
curl -X POST http://localhost:3000/events/<id>/rsvp \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@x.com", "status": "accepted"}'

# Check conflicts when scheduling
curl 'http://localhost:3000/conflicts?start_at=2024-12-15T09:00:00Z&end_at=2024-12-15T10:00:00Z' \
  -H "X-User-Id: u_alice"
```

## What this teaches
1. **Time handling**: ISO 8601, timezones (always UTC in storage)
2. **Recurring events**: expand RRULE on read
3. **Range queries**: `start_at < X AND end_at > Y` (overlap detection)
4. **Many-to-many**: events ↔ attendees
5. **RSVP pattern**: pending → accepted/declined
6. **Conflict detection**: same query as range filter

## Next project
→ **reminders-api** — adds: scheduled tasks, time-based triggers
