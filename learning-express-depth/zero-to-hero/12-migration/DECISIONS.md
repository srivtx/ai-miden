# The Decisions

> *"Migrations are versioned changes. The version is the order. The change is the SQL. The database remembers what it has seen."*

## Decision 1: A simple in-code array, not files

**Alternative**: One `.sql` file per migration in a `migrations/` directory.

**Why an array**: Simpler. We don't need to read the file system. The migration is right next to the code that uses it. Easy to see the order at a glance.

**Trade-off**: Less standard. Most teams use files. We can refactor later. The pattern is the same.

## Decision 2: Integer versions

**Alternative**: Timestamps (e.g., `1700000000000`).

**Why integer**: Easier to read. Easier to order. The convention in most migration systems (Rails, Django, Knex, etc.).

**Trade-off**: If two developers create migrations at the same time, they might pick the same number. In a real team, you'd use timestamps or a queue. We use integers for simplicity.

## Decision 3: No down migrations

**Alternative**: Each migration has both `up` and `down` SQL.

**Why no down**: Down migrations are useful for reverting, but they double the maintenance burden. If we get the down wrong, we can lose data. Real systems have both, but they require careful review.

**Trade-off**: We can't easily revert. If we need to revert, we write a new migration that does the reverse. This is the modern convention (forward-only migrations).

## Decision 4: `ALTER TABLE ADD COLUMN` only

**Alternative**: More complex alterations (DROP COLUMN, change type, etc.).

**Why ADD COLUMN only**: It's the safest, most common alteration. SQLite supports it natively. Existing data is preserved. New rows have the column.

**Trade-off**: We can't easily rename a column, change a type, or drop a column in SQLite. For complex changes, we'd do a "table rebuild" (create new, copy data, drop old, rename). Out of scope.

## Decision 5: Transaction per migration

**Alternative**: Run the whole migration list in one transaction.

**Why per-migration**: If migration 5 fails, we don't want to roll back migrations 1-4 (which are correct). We want migration 5 to be rolled back, but the earlier ones to stay applied.

**Trade-off**: Slightly more code (one transaction per migration). We accept this for safety.

## Decision 6: `migrations` table with `version` and `applied_at`

**Alternative**: Just `version` (no timestamp).

**Why timestamp: Useful for debugging. "When was this migration applied?" We can answer.

**Trade-off**: An extra column. Negligible.

## Decision 7: No checksum validation

**Alternative**: Store a hash of the migration SQL. On apply, compare the hash. If the file has been edited, refuse to apply (the system trusts that applied migrations are immutable).

**Why we don't**: We don't have files (we have an array). The check would be: "did the migration in the array change since it was applied?" Possible, but overkill. We trust the developer not to edit applied migrations.

**Trade-off**: If you edit a migration in the array after it's been applied, the system will re-apply it (because the version is no longer in the `migrations` table, since we only check versions). Wait — actually no. The version *is* in the table. The system would skip it (because `applied.has(m.version)`). So editing doesn't cause re-application. The mismatch between "applied SQL" and "current SQL" is silent. We accept this.

## Decision 8: One-time setup, no separate command

**Alternative**: A separate CLI command like `npm run migrate` to apply migrations.

**Why no separate command: Simpler. The migrations run on server start. No need to remember to run a command.

**Trade-off**: Migrations run on every startup. If they're slow, the server is slow to start. For our scale, migrations are microseconds. For huge migrations, you'd run them separately.

## Decision 9: `IF NOT EXISTS` in the migration SQL

**Alternative**: Just `CREATE TABLE users ...`.

**Why IF NOT EXISTS: Idempotent. If the table already exists (from a previous migration or manual setup), this is a no-op. Safe.

**Trade-off**: We can't tell if the table was just created or already existed. We don't care.

## Decision 10: Single `app.db` file

**Alternative**: Separate files per environment (dev, test, prod).

**Why single file: For learning. In production, you'd use different databases for different environments. We don't have environments yet.

**Trade-off**: Not production-ready. We'll address this in project 39 (Observability) or a deployment project.

---

## What We Did Not Decide

- **Down migrations** — out of scope
- **Multi-file migrations** — out of scope (we use an array)
- **Migration checksum validation** — out of scope
- **Data migrations** (moving data, not just schema) — out of scope
- **Concurrent migration safety** (advisory locks for Postgres) — out of scope
- **Migration CLI** (`npm run migrate`) — out of scope
- **Migration history audit** (who ran it) — out of scope
- **ORM-style migrations** (Prisma Migrate, Knex) — out of scope; we hand-write the system. Project 13 covers ORMs.

Each is a future decision.

---

## The Meta-Decision: The Schema Is Code

For 11 projects, the schema was either implicit (in-memory) or a one-off `db.exec(...)`. The schema was *in the code*, but it was *not* versioned, *not* applied automatically, *not* safe to evolve.

Now the schema is *versioned code*. Each change is a migration. Each migration has a number. The system applies them in order. The database remembers what it has seen.

This is the foundation of *production database management*. Real apps have hundreds of migrations. Each one is a small change. Each one is documented. Each one is reversible (in theory). The schema evolves; the data survives.

The next 28 projects will assume migrations exist. The data layer is complete. The path diverges:

- **ORM** (project 13): cleaner database code
- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle constraint violations
- **Logging** (project 16): observe the database
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The data layer is solid. The schema evolves. The path continues.
