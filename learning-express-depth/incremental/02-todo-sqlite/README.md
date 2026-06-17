# 02 — Todo (SQLite)

Same CRUD, but data lives in SQLite. Survives restarts.

**What's new:**
- `better-sqlite3` library
- `todos.db` file (created on first run)
- Schema: `CREATE TABLE IF NOT EXISTS`
- Prepared statements (compiled once, used many times)

**Why prepared statements?** Faster, safer (no SQL injection). The DB parses the SQL once, then you just pass values.

**Why SQLite?** No setup. The DB is a file. Perfect for dev, fine for small production.

## Run
```bash
npm install
node server.js
```

Add some todos, then restart the server. They're still there.

```bash
ls *.db
# todos.db
```

## What this stage teaches
- Connecting to a database
- Schema (CREATE TABLE)
- Prepared statements
- Survives restart

## Next
**03-todo-relations** — add tags (many-to-many) and categories.
