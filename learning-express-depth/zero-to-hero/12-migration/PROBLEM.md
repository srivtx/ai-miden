# The Problem

> *"The schema is never done. New columns. New tables. New constraints. The data must survive every change."*

## Why Migrations Exist

In project 11, we have one `db.exec(...)` that creates the tables. The schema is hardcoded. If we want to add a column, we have two options:

### Option 1: Drop and recreate

```js
db.exec(`DROP TABLE posts; DROP TABLE users;`);
db.exec(`CREATE TABLE ... (with new column)`);
```

This works. It also **deletes all data**. The user table is empty. The post table is empty. Every signup, every post — gone.

This is unacceptable for a real app. We can't lose user data.

### Option 2: Add the column manually

```bash
sqlite3 app.db "ALTER TABLE users ADD COLUMN email TEXT"
```

This works for the dev database. But what about the production database? What about the test database? What about the database on the developer's laptop? What about the database on the staging server? Each one needs the same ALTER TABLE run. We can't do this manually for every environment.

### Option 3: Migrations

A migration is a *file* (or string) of SQL that changes the schema, *versioned*. The application tracks which migrations have been applied. On startup, it applies any that haven't been applied yet. The same code runs in every environment, automatically.

This is the right answer. Migrations are how every real app evolves its schema.

## What Pain Is This Solving?

Imagine the alternative. You're a backend engineer at a startup. The product team says "add an `email` column to users." You:

1. Update the `CREATE TABLE` in the code
2. Run a manual `ALTER TABLE` on the dev database
3. Push the code
4. The CI tests fail because the test database has the old schema
5. You write a script to alter the test database
6. Push again
7. The staging database has the old schema, the new code crashes
8. You write a manual migration for staging
9. Production is the same, plus you have a customer who's already signed up
10. You take the site down for 30 seconds to run the ALTER TABLE
11. The next feature needs another column
12. Repeat the chaos

This is unsustainable. The fix is a *migration system*. Migrations are code. Migrations are versioned. Migrations run automatically. Every environment is in sync. Every change is documented.

## The Deeper Problem: Order Matters

Migrations must be applied in order. If migration 1 creates `users` and migration 2 adds a column to `users`, applying them in reverse order would fail (the column doesn't exist yet).

Migrations must be *idempotent*. If you run them twice, they don't fail. They detect that they've already been applied and skip.

Migrations must be *transactional*. If a migration has 5 SQL statements and the 3rd fails, the database should be in the same state as before (the first 2 are rolled back).

Migrations must be *tracked*. We need a `migrations` table that records which migrations have been applied. Without it, we can't tell.

## What This Project Will Solve

This project will:

1. Introduce a `MIGRATIONS` array of versioned SQL statements
2. Create a `migrations` table to track applied migrations
3. On startup, apply any new migrations in order
4. Wrap each migration in a transaction
5. Add migration 2: `ALTER TABLE users ADD COLUMN email`

By the end, we can add a column by adding one line to the `MIGRATIONS` array. The migration is applied on next startup. Existing data is preserved.

## What This Project Will *Not* Solve

- **Down migrations** — we don't have a `down` for each migration. If we need to roll back, we manually revert. Real systems have both `up` and `down`. We keep it simple.
- **Multi-file migrations** — we use an array, not files. Real systems use `001_initial.sql`, `002_add_email.sql`, etc. We use an array of strings.
- **Migration history** — we don't store who ran the migration. Just the version and timestamp.
- **Migration validation** — we don't check that the migration is well-formed.
- **Data migrations** — we only do schema migrations. Moving data (e.g., splitting `name` into `first_name` and `last_name`) is out of scope.
- **Concurrent migrations** — SQLite has a single writer, so we don't worry. For Postgres, we'd need advisory locks.
- **Migration library** — we hand-write a simple system. Real systems use Knex, Prisma Migrate, Flyway, etc.

## The Question This Project Answers

> *"How do I change the schema without losing data?"*

If you can answer: "use a migration — a versioned SQL file that changes the schema, applied automatically on startup, tracked in a migrations table," you are ready for project 13.
