# Multi-Tenancy Demo — Row-level isolation with shared schema

One database, many tenants. Every row has a `tenant_id`. Every query filters by it. Tenants can't see each other's data.

## Endpoints
```
GET  /me                        # current tenant (from X-Tenant-Id header)
GET  /projects                  # projects for current tenant
POST /projects                  # create project for current tenant
GET  /tasks                     # tasks for current tenant
GET  /tasks/:id                 # single task (404 if not yours)
GET  /admin/tenants             # list all tenants (no auth)
```

## Try
```bash
# Get Acme's projects
curl -H "X-Tenant-Id: <acme-id>" http://localhost:3000/projects
# { tenant: "Acme Corp", count: 1, projects: [...] }

# Get Beta's projects
curl -H "X-Tenant-Id: <beta-id>" http://localhost:3000/projects
# { tenant: "Beta Inc", count: 1, projects: [...] }

# Try to read Acme's task as Beta → 404
curl -H "X-Tenant-Id: <beta-id>" http://localhost:3000/tasks/<acme-task-id>
# { error: "not_found_or_not_yours" }

# Find the tenant IDs by running GET /admin/tenants
```

## What this teaches
1. **Shared schema, shared DB**: cheapest, fastest, but isolation is your responsibility
2. **`tenant_id` column on every row**: every query filters by it
3. **Tenant resolution**: from header, subdomain, or JWT claim
4. **Cross-tenant access**: 404, not 403 (don't leak existence)
5. **Helper functions**: `tenantQuery(tenantId, table)` to make scoping automatic
6. **vs schema-per-tenant**: more isolation, more cost. Row-level is fine for most SaaS.
7. **vs database-per-tenant**: full isolation, but operationally expensive
