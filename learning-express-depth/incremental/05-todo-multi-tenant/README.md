# 05 — Todo (multi-tenant)

Users belong to tenants (teams, workspaces, organizations). Data is isolated by tenant. User A in tenant X cannot see tenant Y's data.

**What's new:**
- `tenants` table
- `tenant_id` column on users and todos
- `X-Tenant-Id` header on every request
- Middleware checks the tenant from the JWT matches the header
- Every todo query filters by `tenant_id`

**This is how SaaS apps work.** A single database, many customers, complete data isolation.

## Run
```bash
npm install && node server.js
```

```bash
# Create a tenant
curl -X POST http://localhost:3000/tenants -H "Content-Type: application/json" -d '{"name": "Acme"}'

# Create a user in that tenant
RESP=$(curl -X POST http://localhost:3000/tenants/t_xxx/users -H "Content-Type: application/json" -d '{"email": "alice@acme.com", "role": "admin"}')
TOKEN=$(echo $RESP | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# Create a todo (with both token AND tenant header)
curl -H "Authorization: Bearer $TOKEN" -H "X-Tenant-Id: t_xxx" \
  -X POST http://localhost:3000/todos \
  -H "Content-Type: application/json" -d '{"title": "Build feature"}'

# Try the same token with a different tenant header
curl -H "Authorization: Bearer $TOKEN" -H "X-Tenant-Id: t_yyy" \
  http://localhost:3000/todos
# 403 wrong tenant
```

## What this stage teaches
- Tenant data isolation
- The `X-Tenant-Id` header pattern
- Defense in depth (JWT AND header must match)
- SaaS architecture

## Next
**06-todo-soft-delete** — never actually delete. Mark with `deleted_at`. Restore on demand.
