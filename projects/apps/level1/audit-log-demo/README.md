# Audit Log Demo — Append-only log of who did what, with diffs

For compliance, debugging, and security. Every change to a resource is recorded: who, when, from where, before/after state.

## Endpoints
```
POST   /users                 # create (audited)
PUT    /users/:id             # update (audited with diff)
DELETE /users/:id             # delete (audited)

GET /admin/audit                       # query the log
GET /admin/audit/resource/:type/:id    # history of a specific resource
GET /admin/audit/actor/:id             # everything an actor did
```

## Try
```bash
# Create as alice
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: alice@x.com" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# Update as bob
curl -X PUT http://localhost:3000/users/u_abc \
  -H "Content-Type: application/json" \
  -H "X-Actor-Id: bob@x.com" \
  -d '{"name": "Alicia"}'

# Query alice's actions
curl 'http://localhost:3000/admin/audit/actor/alice@x.com'
# { actor: "alice@x.com", count: 1, recent: [...] }

# See the history of a user (with diffs)
curl 'http://localhost:3000/admin/audit/resource/user/u_abc'
# { resource: "user:u_abc", history: [{ action: "user.create", ... }, { action: "user.update", ... }] }
```

## What this teaches
1. **Append-only**: never update or delete audit entries
2. **Before/after state**: capture both for diff and rollback
3. **Who/when/where**: actor, IP, timestamp, request ID
4. **Diff calculation**: only changed fields in updates
5. **Query patterns**: by actor, by resource, by time
6. **Compliance**: GDPR, SOX, HIPAA all require audit trails
