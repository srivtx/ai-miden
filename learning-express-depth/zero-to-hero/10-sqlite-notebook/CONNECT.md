# The Connect

> *"The data persists. Now we need relations, schema evolution, and clean database code."*

This project introduced SQLite. The pain of "I lose all data on restart" is solved. Users are rows in a `users` table. Sign up inserts. Login queries. The data survives.

But the data layer is still simple. We have one table. No relations. No way to have a post reference a user. No way to evolve the schema safely. No way to write database code without SQL injection risk.

Project 11 (Foreign Key) will add a `posts` table with a foreign key to `users`. We'll be able to do `SELECT posts WHERE user_id = ?` — the foundation of relations.

## What Works

- Users are stored in a SQLite database
- Signup inserts a row
- Login queries a row
- Data persists across restarts
- Prepared statements prevent SQL injection
- Numeric IDs as primary keys
- Bcrypt hashing is unchanged

## What Doesn't Work

### 1. We have only one entity type

`users` is the only table. We don't have posts, comments, orders, etc. A real app has many.

**The pain**: Multiple entities. Project 11 (Foreign Key).

### 2. We can't connect entities

If we had a `posts` table, we couldn't link a post to its author. We can't say "show me all posts by user 1."

**The pain**: Foreign keys. Project 11.

### 3. We can't evolve the schema

If we want to add an `email` column to `users`, we have to drop the table and recreate it. All data is lost. We can't migrate.

**The pain**: Schema migrations. Project 12.

### 4. We hand-write SQL

We have 2 prepared statements. If we had 50, the code would be repetitive. We want a higher-level API.

**The pain**: ORM. Project 13.

### 5. We don't validate input

`POST /signup` accepts any `username` and `password`. No length, no format, no strength.

**The pain**: Validation. Project 14 (Validator).

### 6. We have no error handling for handler errors

If `db.prepare(...).run(...)` throws (e.g., constraint violation), Express's default returns 500. We should return 409 for unique constraint violations.

**The pain**: Error handling. Project 15 (Error Wall).

### 7. We have no logging

We don't log signups, logins, or DB queries.

**The pain**: Observability. Project 16 (Logger).

### 8. We have no pagination

If we had `GET /users`, we'd return all users. For 1 million users, that's a 100MB response.

**The pain**: Pagination. Project 18.

### 9. We have no search

`GET /users?search=ali` would do a `LIKE` query. Slow, no relevance ranking.

**The pain**: Search. Project 19.

### 10. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

---

## What This Project Forbids Us From Doing

This server can:

- Store users in a database
- Sign up, log in, get session
- Persist data across restarts

It cannot:

- Have multiple entity types with relations (no FK)
- Evolve the schema safely (no migrations)
- Avoid SQL injection at scale (need ORM)
- Validate input strictly
- Handle errors gracefully
- Log requests
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 11 | The Foreign Key | "I want users and posts connected by a user_id." |
| 12 | The Migration | "I want to evolve the schema safely." |
| 13 | The ORM Detour | "I want to stop hand-writing SQL." |
| 14 | The Validator | "I want to reject bad input." |

Project 11 is the natural next step. We have one table. We need at least two, connected by a foreign key. This is the foundation of *relations* — the core of a relational database.

---

## What You Should Do Now

1. **Read the code.** Notice the `USERS` Map is gone. The `db` object is the source of truth. The auth flow is the same.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Sign up, log in, restart, log in again.** See how the data persists.
4. **Open the database with `sqlite3 app.db`.** See the rows. See the schema.
5. **When you are ready**, move to [Project 11: The Foreign Key](../11-foreign-key/).
6. **If anything is unclear**, do not proceed. The data layer is the foundation. It must be solid.

---

## A Note on the Bigger Picture

You now have a *real* database. The data is on disk. The auth flow is durable. From here, the path diverges:

- **Multiple entities** (project 11): `posts`, `comments`, etc., connected by foreign keys
- **Schema evolution** (project 12): add columns, add tables, safely
- **ORM** (project 13): cleaner database code
- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle unique constraint violations, etc.
- **Logging** (project 16): observe the database
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

Each adds a layer of *robustness* on top of the data layer. The data layer is solid. The auth flow is solid. The server is real.

The path continues. The HTTP substrate is done. The auth is done. The data layer is starting.
