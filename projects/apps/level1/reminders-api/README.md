# Reminders API — Step 9 in the learning path

Builds on Calendar. Adds: simple scheduled tasks, recurring reminders, "what's due now" queries, completion tracking.

## Endpoints
```
GET    /reminders?completed=&due_before=&due_after=    # list, filter
POST   /reminders                                     # create { title, notes?, due_at, recurrence? }
PATCH  /reminders/:id/complete                        # mark done; if recurring, creates next instance
GET    /reminders/now?window=60                       # what's due in next 60 min + overdue
```

## Try
```bash
# Create a reminder
curl -X POST http://localhost:3000/reminders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"title": "Call mom", "due_at": "2024-12-15T18:00:00Z"}'

# Recurring (every Monday)
curl -X POST http://localhost:3000/reminders \
  -H "Content-Type: application/json" \
  -H "X-User-Id: u_alice" \
  -d '{"title": "Weekly review", "due_at": "2024-12-16T10:00:00Z", "recurrence": "weekly"}'

# What's due now?
curl 'http://localhost:3000/reminders/now?window=120' \
  -H "X-User-Id: u_alice"

# Complete one (creates next weekly instance)
curl -X PATCH http://localhost:3000/reminders/<id>/complete \
  -H "X-User-Id: u_alice"
# { completed: "r_...", next: "r_..." }
```

## What this teaches
1. **Time-based queries**: range filters with ISO timestamps
2. **Recurring tasks**: complete → create next
3. **"Now" window**: what's due in the next N minutes + overdue
4. **Auto-create on complete**: chaining events

## Next project
→ **books-api** — adds: rich content, ratings, reviews, ISBN lookup
