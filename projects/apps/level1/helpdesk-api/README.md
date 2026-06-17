# Helpdesk API — Step 16 in the learning path

Builds on Twitter. Adds: support tickets, agents, assignments, SLA tracking, priority levels, event history.

## Endpoints
```
GET    /agents                       # with open ticket count
POST   /agents

POST   /tickets                      # anyone can create { subject, body?, priority?, category? }
GET    /tickets?status=&priority=&assignee=&breached=
GET    /tickets/:id                  # with event history

POST   /tickets/:id/assign            # { assignee_id } (X-Agent-Id)
POST   /tickets/:id/comment           # { body }
POST   /tickets/:id/resolve
```

## SLA rules
- `critical`: 1 hour
- `high`: 4 hours
- `normal`: 24 hours
- `low`: 72 hours

## Try
```bash
# Create agent
AG=$(curl -X POST http://localhost:3000/agents -H "Content-Type: application/json" -d '{"name": "Bob", "email": "bob@x.com"}' | jq -r .id)

# Customer creates a critical ticket
curl -X POST http://localhost:3000/tickets -H "Content-Type: application/json" \
  -d '{"subject": "Site is down", "priority": "critical", "requester_id": "cust_42"}'

# Bob claims it
curl -X POST http://localhost:3000/tickets/<id>/assign -H "Content-Type: application/json" \
  -H "X-Agent-Id: $AG" -d '{"assignee_id": "<id>"}'

# Add a comment
curl -X POST http://localhost:3000/tickets/<id>/comment -H "Content-Type: application/json" \
  -H "X-Agent-Id: $AG" -d '{"body": "Looking into it now"}'

# Resolve
curl -X POST http://localhost:3000/tickets/<id>/resolve -H "X-Agent-Id: $AG"

# See only breached SLAs
curl 'http://localhost:3000/tickets?breached=true'
```

## What this teaches
1. **State machine**: open → assigned → in_progress → resolved → closed
2. **SLA tracking**: priority → hours, compute elapsed, flag breaches
3. **Event log**: every state change recorded in `ticket_events`
4. **Two roles**: customer (creates tickets) and agent (assigns/comments/resolves)
5. **Computed fields**: SLA status calculated on read, not stored

## Next project
→ **ticket-booking** — adds: events, venues, seat selection, payment
