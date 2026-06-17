# 07 — Todo (audit log)

Every change is logged. Who did what, when, from where, what was the before/after.

**What's new:**
- `audit_log` table with `entity_type`, `entity_id`, `action`, `actor_id`, `actor_ip`, `before_state`, `after_state`, `request_id`
- Every state-changing action calls `audit()`
- `GET /audit?entity_id=X` to query the log
- `X-Request-Id` propagation

**Why?** Compliance (GDPR, SOX, HIPAA). Debugging. Security. "Who deleted this?" "When was this changed?" "What did it look like before?"

## Run
```bash
npm install && node server.js
```

```bash
# Make a change
curl -X POST http://localhost:3000/todos -H "Content-Type: application/json" \
  -H "X-Actor-Id: alice" -H "X-Request-Id: req_001" \
  -d '{"title": "Test", "actorId": "alice"}'

# Update
curl -X PATCH http://localhost:3000/todos/1 -H "Content-Type: application/json" \
  -d '{"done": true, "actorId": "alice"}'

# See the audit log
curl 'http://localhost:3000/audit?actor_id=alice'
# { count: 2, entries: [
#   { action: "update", before_state: {...}, after_state: {...}, ... },
#   { action: "create", after_state: {...}, ... }
# ] }
```

## What this stage teaches
- Append-only audit log
- Before/after state for diffs
- Request ID propagation for correlation
- Querying the audit log

## Next
**08-todo-versioning** — optimistic locking. Detect conflicts when two clients edit the same row.
