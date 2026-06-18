# The Connect

> *"The schema is code. The code is versioned. The data is safe. Now we need an ORM, validation, and a real error strategy."*

This project introduced migrations. The pain of "I can't evolve the schema without losing data" is solved. We have a `MIGRATIONS` array, a `migrations` table, and a `runMigrations()` function. The schema is versioned. The data is preserved.

But the data layer is still hand-coded. We write `db.prepare(...)` for every query. We write `INSERT INTO ...` and `SELECT ...` by hand. The code is repetitive. We want a higher-level API.

Project 13 (ORM Detour) will introduce an ORM. We won't hand-write SQL anymore. The ORM will generate it for us. The data layer will be cleaner.

## What Works

- The schema is versioned (migrations)
- Migrations apply on startup, idempotently
- The `migrations` table tracks what's been applied
- Each migration is wrapped in a transaction
- Migration 1 creates the tables
- Migration 2 adds an `email` column to users
- Existing data is preserved across schema changes

## What Doesn't Work

### 1. We hand-write SQL

Every query is a `db.prepare(...)` call. Every insert is a `db.exec(...)` or `statement.run(...)`. The code is repetitive. We want a higher-level API.

**The pain**: ORM. Project 13.

### 2. We don't validate input

`POST /signup` accepts any `username`, `password`, `email`. No length, no format, no strength.

**The pain**: Validation. Project 14.

### 3. We have no error handling

If the unique constraint on `username` fails, we get a SQLite error. We want a clean 409 with a friendly message.

**The pain**: Error handling. Project 15.

### 4. We have no logging

We don't log migrations, signups, logins, or DB queries.

**The pain**: Observability. Project 16.

### 5. We have no REST structure

Our URLs are ad-hoc. `GET /posts` and `GET /users/:id/posts` are not consistent. We want resource-shaped URLs.

**The pain**: REST. Project 17.

### 6. We have no pagination

`GET /posts` returns all posts. For 1M posts, the response is huge.

**The pain**: Pagination. Project 18.

### 7. We have no search

`GET /posts?search=hello` would be a `LIKE` query. Slow, no relevance.

**The pain**: Search. Project 19.

### 8. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 9. We have no security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

### 10. We have no tests

We can't verify the schema evolution works.

**The pain**: Tests. Project 36.

---

## What This Project Forbids Us From Doing

This server can:

- Evolve the schema without losing data
- Track which migrations have been applied
- Apply migrations in order, transactionally

It cannot:

- Hide the SQL behind a clean API (no ORM)
- Validate input strictly
- Handle errors gracefully
- Log requests
- Have REST-shaped URLs
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Be protected by security headers
- Be tested automatically

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 13 | The ORM Detour | "I want to stop hand-writing SQL." |
| 14 | The Validator | "I want to reject bad input." |
| 15 | The Error Wall | "I want to handle errors with proper status codes." |
| 16 | The Logger | "I want to see what's happening." |

Project 13 is the natural next step. We have a solid data layer with migrations. Now we want a cleaner API. An ORM will hide the SQL and provide a JavaScript-friendly interface.

---

## What You Should Do Now

1. **Read the code.** Notice the `MIGRATIONS` array and the `runMigrations()` function. The auth and post flows are unchanged. The new piece is the migration system.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Add a new migration** that adds a column. See how the migration system applies it on restart.
4. **Add a broken migration**. See how the transaction rolls back.
5. **Reset the database** (delete `app.db`). See how the migrations re-apply.
6. **When you are ready**, move to [Project 13: The ORM Detour](../13-orm-detour/).
7. **If anything is unclear**, do not proceed. Migrations are the foundation of schema evolution. They must be solid.

---

## A Note on the Bigger Picture

You now have a *versioned* database. The schema is code. The code is applied automatically. The data is safe.

This is the foundation of every real app. From here, the path diverges:

- **ORM** (project 13): cleaner database code
- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle constraint violations
- **Logging** (project 16): observe the database
- **REST refactor** (project 17): resource-shaped endpoints
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The data layer is solid. The schema evolves. The path continues.

---

## Phase 2 Complete: Identity & Persistence

With project 12, we finish Phase 2 (Identity & Persistence). The 6 projects in this phase:

- 07: Framework Pivot (Express)
- 08: Bcrypt Vault (passwords)
- 09: JWT (stateless auth)
- 10: SQLite Notebook (persistence)
- 11: Foreign Key (relations)
- 12: Migration (schema evolution)

The identity layer is solid. The data layer is solid. The schema evolves. The path continues to Phase 3: Robustness & Quality.
