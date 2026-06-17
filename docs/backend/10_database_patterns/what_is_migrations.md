## Why it exists (THE PROBLEM)

Your app's database schema changes. You add a `phone` column to `users`. You deploy. Production crashes — the app expects `phone` but the column doesn't exist yet. You forgot to run `ALTER TABLE`. Now you're SSH-ing into production at 2 AM, running SQL by hand.

**Migrations** are version-controlled schema changes. Every change (add column, create table, add index) is a SQL file with an `up` (apply) and `down` (rollback). The migration tool tracks which migrations have been run. Deploy script: `run pending migrations` → `start app`. Never manual SQL in production.

## Key patterns

**Migration file format:**
```sql
-- 001_add_phone_to_users.up.sql
ALTER TABLE users ADD COLUMN phone TEXT;

-- 001_add_phone_to_users.down.sql  
ALTER TABLE users DROP COLUMN phone;
```

**Seeding:** initial data for development/testing. Admin user, categories, sample products. Run once: `npm run seed`.

**Rollback:** If deployment fails, revert the migration (`down`) and deploy the old code. Both schema and code are in sync at all times.

**Tools:** Knex.js (JS), Sequelize (JS), Alembic (Python), Flyway (Java), golang-migrate (Go).

## Common confusion

1. **"I'll just run SQL manually."** Works once. Fails when you have 3 environments (dev, staging, production) with different states. Migrations ensure all environments are identical.

2. **"Migrations are only for production."** No. Every developer runs migrations on their local DB. If the migration fails locally, it fails in CI. It never reaches production.

3. **"I can't roll back a migration."** Some migrations are irreversible (dropping a column that had data). Mark them as `irreversible`. For reversible ones, always write the `down` script.

## Practice pattern for Express

```javascript
// migrate.js — run with: node migrate.js up|down|status
const db = require('better-sqlite3')('data.db');
const migrations = [
  { name: '001_create_users', up: `CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE)`, down: `DROP TABLE users` },
  { name: '002_add_role', up: `ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'`, down: `ALTER TABLE users DROP COLUMN role` },
];

db.exec(`CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY, run_at TEXT)`);

function migrate(direction) {
  const run = db.prepare('SELECT name FROM _migrations').all().map(r => r.name);
  if (direction === 'up') {
    for (const m of migrations) {
      if (!run.includes(m.name)) {
        db.exec(m.up);
        db.prepare('INSERT INTO _migrations VALUES (?, ?)').run(m.name, new Date().toISOString());
        console.log(`  Up: ${m.name}`);
      }
    }
  } else if (direction === 'down') {
    for (const m of [...migrations].reverse()) {
      if (run.includes(m.name)) {
        db.exec(m.down);
        db.prepare('DELETE FROM _migrations WHERE name = ?').run(m.name);
        console.log(`  Down: ${m.name}`);
      }
    }
  }
  console.log(`Done. Pending: ${migrations.filter(m => !db.prepare('SELECT name FROM _migrations WHERE name = ?').get(m.name)).length}`);
}

migrate(process.argv[2] || 'up');
```
