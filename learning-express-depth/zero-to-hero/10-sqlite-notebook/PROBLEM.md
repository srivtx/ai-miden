# The Problem

> *"Memory forgets. Disk remembers. A real app remembers."*

## Why In-Memory Is Not Enough

In projects 06-09, we stored users and sessions in `Map`s. The auth flow was real, but the storage was ephemeral. Restart the server:

- All users are gone
- All sessions are gone
- All data is gone

This is acceptable for a demo. It is unacceptable for a real app. A real app must remember its data.

**The pain**: Volatility. We need disk-based storage. We need a database.

## What Pain Is This Solving?

Imagine you sign up for an app. You come back tomorrow. Your account is gone. You'd be furious.

Or you create a post. Refresh. The post is gone. Or you log in, the server restarts, you're logged out. Annoying.

Every real app has data that *persists*. Users, posts, comments, orders, messages, settings — all need to survive restarts. The data is the *value* of the app. Lose the data, lose the app.

## The Deeper Problem: Data Is Relational

In project 08-09, our data is just `{ username, hash, createdAt }`. One entity, no relations. We could store it in a file:

```json
{
  "alice": { "hash": "...", "createdAt": 1234567890 },
  "bob": { "hash": "...", "createdAt": 1234567891 }
}
```

But what about posts? Posts have an author (a user). Comments have a post and an author. Orders have a user and products. Likes have a user and a post.

We need *relations*. A post references a user. A user has many posts. This is a *relational* model. The natural data structure is a *table*. The natural query language is *SQL*.

We could build a relational model with files and JSON. We could. It would be a mess. SQL exists for exactly this reason. Let's use it.

## What This Project Will Solve

This project will:

1. Add `better-sqlite3` as a dependency
2. Create a `users` table with columns `id`, `username`, `hash`, `created_at`
3. Use prepared statements for insert and query
4. Replace the in-memory `USERS` Map with the database
5. Add a real numeric `id` to users

By the end, users persist. Sign up creates a row. Login queries it. Restart the server, the data is there.

## What This Project Will *Not* Solve

- **Relations** — we don't have a `posts` table yet. We can't have a post reference a user. Project 11 (Foreign Key).
- **Schema evolution** — if we add a column, we have to update every existing row by hand. Project 12 (Migration).
- **ORM** — we hand-write SQL. SQL injection is a real risk if we don't use prepared statements. Project 13 (ORM Detour) wraps this in a safer API.
- **Multiple processes** — SQLite locks the whole database file. Multiple processes writing at the same time will conflict. We don't have this problem yet (single server). Project 23 (Redis) and project 40 (Microservice Split) address scale.
- **Connection pooling** — `better-sqlite3` is synchronous, so no pool needed. For Postgres, we'd need a pool. Project 13+ (when we add Postgres).
- **Transactions** — multiple writes that must succeed or fail together. Project 27 (Transaction).

## The Question This Project Answers

> *"How do I store data so it survives restarts?"*

If you can answer: "use a database, create tables, insert with prepared statements, query with prepared statements, the database is a file on disk," you are ready for project 11.
