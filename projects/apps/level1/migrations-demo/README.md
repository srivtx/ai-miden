# Migrations Demo — Versioned schema migrations with up/down

Database schema changes over time. Migrations = a versioned history of every change. Each migration has an `up` (apply) and `down` (revert). The framework tracks which versions are applied.

## Endpoints
```
POST /migrate              # apply all pending migrations
POST /rollback?steps=N     # revert the last N migrations
GET  /migrations           # see applied and pending
GET  /schema               # see current tables
```

## Try
```bash
# See what's pending
curl http://localhost:3000/migrations
# { total: 5, applied: 0, pending: 5, migrations: [...] }

# Apply all
curl -X POST http://localhost:3000/migrate
# { applied: 5, migrations: [{version: 1, name: "create_users"}, ...] }

# Check schema
curl http://localhost:3000/schema
# { tables: ["users", "posts", "comments", "schema_migrations"] }

# Rollback 2
curl -X POST 'http://localhost:3000/rollback?steps=2'
# { reverted: 2, versions: [5, 4] }
```

## What this teaches
1. **Versioned migrations**: every change is a versioned file
2. **Up and down**: each migration has an apply and a revert
3. **Tracking table**: `schema_migrations` records which versions ran
4. **Transactional**: each migration runs in BEGIN/COMMIT — if it fails, nothing changes
5. **Rollback**: when something breaks, revert
6. **Idempotent migrate**: running `migrate` twice is safe (only applies pending)
