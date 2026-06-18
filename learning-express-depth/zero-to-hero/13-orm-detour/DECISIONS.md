# The Decisions

> *"SQL is a language. JavaScript is a language. A query builder is a translator."*

## Decision 1: Knex and not Prisma / Drizzle / TypeORM

**Alternatives**:
- **Prisma** — full ORM, schema-first, TypeScript types, migration system
- **Drizzle** — TypeScript-first ORM, type-safe queries
- **TypeORM** — decorator-based, Active Record / Data Mapper patterns
- **Sequelize** — old-school ORM, model classes
- **Objection.js** — built on Knex, adds a model layer

**Why Knex**: It's a *query builder*, not a full ORM. Simpler. More transparent. You can see the SQL it generates. Easy to debug.

**Trade-off**: No model classes. No TypeScript types (unless you add them manually). No automatic joins. For a full ORM, use Prisma or Drizzle.

## Decision 2: Query builder and not full ORM

**Alternative**: A full ORM (Prisma) that hides the database behind models.

**Why a query builder**: More transparent. We can see the SQL it generates. We can drop to raw SQL when needed. Less magic.

**Trade-off**: More verbose. No model classes. No automatic relationship traversal. For a small app, a query builder is enough. For a large app with complex relations, a full ORM helps.

## Decision 3: Schema built in JavaScript and not in raw SQL

**Alternative**: `db.exec('CREATE TABLE ...')` (raw SQL).

**Why JavaScript schema**: The query builder's `createTable` is more readable. The types (`string`, `integer`) are clear. The constraints (`.unique()`, `.notNullable()`) are chainable.

**Trade-off**: Some SQL features are not exposed by the builder. For complex schema (e.g., partial indexes, custom types), we'd need raw SQL.

## Decision 4: `useNullAsDefault: true`

**Alternative**: Set explicit defaults on every column.

**Why true**: SQLite complains about default values in some cases. This option tells Knex to use `NULL` as the default. Standard for SQLite.

**Trade-off**: All columns default to `NULL` if not specified. We always specify `notNullable()` for required columns, so this is fine.

## Decision 5: Async API

**Alternative**: `better-sqlite3`'s sync API (what we used in project 10-12).

**Why async**: Knex uses an async API. `db('users').where(...).first()` returns a Promise. We `await` it.

**Trade-off**: Slightly more code (`async`/`await`). The actual query is still microseconds (SQLite is fast). For Postgres, async is essential (network I/O).

## Decision 6: Migrations in JavaScript, not files

**Alternative**: Use Knex's CLI migration system (`knex migrate:make`, `knex migrate:latest`).

**Why in JavaScript**: We can see the migration code. We don't need a separate CLI step. The migration is part of the app code.

**Trade-off**: Less standard. Most teams use Knex's CLI. In a real project, you'd use the CLI for consistency.

## Decision 7: No connection pool

**Alternative**: Configure a connection pool for SQLite (even though it's a single file).

**Why no pool**: SQLite is a single file. There's nothing to pool. For Postgres, Knex provides a pool (default: 10 connections).

## Decision 8: Idempotent migration (`hasColumn`)

**Alternative**: Use a `migrations` table like project 12.

**Why `hasColumn`: Simpler for the demo. We check if the column exists; if not, add it. No `migrations` table.

**Trade-off**: Doesn't track migration history. Doesn't track who ran them. Doesn't support down migrations. For production, use a real migration system.

## Decision 9: `insert` returns an array

`db('users').insert({...})` returns an array of IDs. `const [id] = ...` destructures the first.

**Why array**: Knex supports bulk inserts. `db('users').insert([{...}, {...}])` returns an array of IDs. We always insert one row, so we destructure the first.

## Decision 10: `first()` and not `[]`

`db('users').where({...}).first()` returns the first row or `undefined`. `db('users').where({...})` returns an array (possibly empty).

**Why `.first()`**: For "find one" queries, we want `undefined` if not found, not `[]`. Cleaner code: `if (!user)` instead of `if (user.length === 0)`.

---

## What We Did Not Decide

- **Model classes** (Prisma's `prisma.user.findMany()`, etc.) — Knex doesn't have them
- **TypeScript types** (Prisma generates them) — Knex doesn't
- **Migration CLI** (Knex has one) — we use the app code
- **Connection pool** (for Postgres) — not needed for SQLite
- **Multiple databases** — we use one
- **Read replicas** — out of scope
- **Sharding** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Database Has an API

For 12 projects, the database was a *string-formatting exercise*. We wrote `INSERT INTO ...` and `SELECT ...` by hand. The pattern was repetitive. Errors were silent.

Now the database has an *API*. `db('users').where({...}).first()` is a function call. It returns a JavaScript object. The SQL is generated. The parameters are safe. The boilerplate is gone.

This is the foundation of *every* modern backend. ORMs and query builders are the standard. Raw SQL is for special cases (performance-critical queries, complex reports).

The data layer is now a *JavaScript module*. The handlers are simpler. The migrations are clearer. The patterns are universal.

The next 27 projects will assume Knex (or similar). The data layer is solid. The path diverges:

- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle constraint violations
- **Logging** (project 16): observe the database
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The database has an API. The handlers are clean. The path continues.
