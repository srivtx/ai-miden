# The Connect

> *"The server has no state. The token is the session. Now we need persistence, foreign keys, and a real schema."*

This project replaced sessions with JWT. The pain of "I need to scale to multiple servers" is solved. The token is self-contained. Any server with the secret can verify it. The server has zero session state.

But the auth flow still has two pain points:

1. **Users are in memory** — `USERS` is a Map. Restart the server, all users are gone. We can't actually *create* users that survive a restart.
2. **No foreign keys** — we don't have entities that reference each other. We don't have a `users` table, a `posts` table, etc. We just have usernames and hashes.

Project 10 (SQLite) will solve the first. Project 11 (Foreign Key) will solve the second. Project 12 (Migration) will make the schema evolve safely. Project 13 (ORM) will make the database code clean.

## What Works

- Stateless authentication with JWT
- Tokens contain user identity, signed
- `authMiddleware` verifies tokens
- `req.user` is the authenticated user
- Server has zero session state
- Multi-process, multi-region safe
- Restart-safe

## What Doesn't Work

### 1. Users are in memory

`USERS` is a Map. Restart, users are gone. The signup flow is essentially a demo.

**The pain**: Persistence. We need a database. Project 10 (SQLite).

### 2. No user IDs

We use `username` as the primary key. Can't change usernames. Can't have multiple users with the same display name.

**The pain**: Proper user model. Project 11 (Foreign Key).

### 3. No other entities

We don't have posts, comments, orders, etc. We just have users. A real app has many entity types, related to each other.

**The pain**: Multiple entities with relations. Project 11 (Foreign Key).

### 4. No schema evolution

If we add a column to the users table, we have to manually update every existing row, every existing backup, etc.

**The pain**: Schema migrations. Project 12 (Migration).

### 5. We hand-write SQL

`db.exec(\`SELECT * FROM users WHERE id = ${id}\`)` is a SQL injection time bomb. We need prepared statements or an ORM.

**The pain**: SQL injection. Project 13 (ORM Detour).

### 6. We don't validate input

`POST /signup` accepts any `username` and any `password`. No length, no format, no strength.

**The pain**: Validation. Project 14 (Validator).

### 7. We have no error handling

If `bcrypt.compare` throws (it won't, but if some handler throws), the default error handler returns 500.

**The pain**: Error handling. Project 15 (Error Wall).

### 8. We have no logging

We don't log signups, logins, or token verifications.

**The pain**: Observability. Project 16 (Logger).

### 9. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 10. We have no security headers

We don't set `helmet` headers.

**The pain**: Helmet. Project 58.

---

## What This Project Forbids Us From Doing

This server can:

- Authenticate users with passwords
- Issue stateless JWTs
- Verify JWTs on protected routes
- Scale to multiple servers

It cannot:

- Persist users across restarts (no DB)
- Have changing usernames (no ID model)
- Have multiple entity types with relations (no FK)
- Evolve the schema safely (no migrations)
- Avoid SQL injection (no prepared statements)
- Validate input strictly
- Handle errors gracefully
- Log requests
- Be called from a browser on a different origin
- Be protected by security headers

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 10 | The SQLite Notebook | "I want to persist users and sessions on disk." |
| 11 | The Foreign Key | "I want users with proper IDs and connected entities." |
| 12 | The Migration | "I want to evolve the schema safely." |
| 13 | The ORM Detour | "I want to stop concatenating SQL strings." |

Project 10 (SQLite) is the natural next step. Users are in memory. We need them on disk. SQLite is the simplest database — a single file, no server. Perfect for the next step.

---

## What You Should Do Now

1. **Read the code.** Notice the session middleware is gone. The `authMiddleware` is custom. The `req.user` is set by the middleware.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try logging in twice and using the same token.** See how it's stateless.
4. **Try tampering with the token.** See how the signature catches it.
5. **Restart the server.** Notice the users are gone, but the token still works (because it's signed and the data is in the token). The user is "logged in" but the user record is gone. Feel the pain of "no persistence."
6. **When you are ready**, move to [Project 10: The SQLite Notebook](../10-sqlite-notebook/).
7. **If anything is unclear**, do not proceed. JWT is the foundation of every modern API. It must be solid.

---

## A Note on the Bigger Picture

You now have a *stateless* server. The token is the credential. The server has no state. Any server can verify any token.

This is the foundation of scale. From here, the path diverges:

- **Persistence** (project 10): users on disk
- **Proper user model** (project 11): numeric IDs, foreign keys
- **Schema evolution** (project 12): migrations
- **ORM** (project 13): clean database code
- **Validation** (project 14): reject bad input

Each adds a layer of *robustness* on top of the auth flow. The auth flow itself is solid. The token is the credential. The server is stateless.

The path continues. The HTTP substrate is done. The auth is done. Now we build the data layer.
