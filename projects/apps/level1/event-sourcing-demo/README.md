# Event Sourcing Demo — Append-only events, project to state, replay history

Instead of storing current state, store every event that ever happened. The current state is computed by replaying all events. You can:
- See the full history of an account
- Replay events to reconstruct past state at any point in time
- Build new projections without losing data

## Endpoints
```
POST /accounts                       { email, name }
POST /accounts/:id/deposit           { amount }
POST /accounts/:id/withdraw          { amount }
POST /accounts/:id/change-name       { name }
GET  /accounts/:id                                       # current state
GET  /accounts/:id/events                               # all events
GET  /accounts/:id/events/at/:version                   # state at a past version
```

## Try
```bash
# Create account
ACC=$(curl -X POST http://localhost:3000/accounts -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "name": "Alice"}' | jq -r .id)

# Do some operations
curl -X POST http://localhost:3000/accounts/$ACC/deposit -H "Content-Type: application/json" -d '{"amount": 100}'
curl -X POST http://localhost:3000/accounts/$ACC/withdraw -H "Content-Type: application/json" -d '{"amount": 30}'
curl -X POST http://localhost:3000/accounts/$ACC/change-name -H "Content-Type: application/json" -d '{"name": "Alicia"}'

# See the event log
curl http://localhost:3000/accounts/$ACC/events
# [AccountCreated, MoneyDeposited, MoneyWithdrawn, NameChanged]

# Replay to version 2 (after the deposit, before the withdraw)
curl http://localhost:3000/accounts/$ACC/events/at/2
# { version: 2, state: { balance: 100, name: "Alice" } }
```

## What this teaches
1. **Events are facts**: AccountCreated, MoneyDeposited, NameChanged
2. **Append-only**: never update or delete events
3. **State is derived**: replay events to compute current state
4. **Optimistic concurrency**: each event has a version
5. **Time travel**: state at any past version
6. **New projections**: build new views from existing events
7. **Audit trail for free**: the event log IS the audit log
