# The Connect

> *"The graph is the app. Now we need to evolve it, query it, validate it, and secure it."*

This project added a `posts` table with a foreign key to `users`. The pain of "I can't connect entities" is solved. We have two tables, related. The relationship is enforced by the database.

The data model is now a *graph*:

```
users ─< posts
```

Users have many posts. Posts belong to a user. The relationship is real (foreign key, not just a JSON column). The relationship is enforced (CASCADE on delete). The relationship is queryable (JOIN).

## What Works

- Two tables: `users` and `posts`
- Foreign key with `ON DELETE CASCADE`
- `PRAGMA foreign_keys = ON` enforces the constraint
- 4 post routes: create, list all, get one, list by user
- JOIN queries combine posts with author info
- Path parameters (`req.params.id`)
- Auth flow unchanged

## What Doesn't Work

### 1. We can't evolve the schema

If we want to add an `email` column to `users`, we have to drop the table and recreate it. All data is lost. We can't migrate.

**The pain**: Schema evolution. Project 12 (Migration).

### 2. We hand-write SQL with joins

`SELECT posts.*, users.username AS author FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = ?` is a lot of SQL. As the app grows, this becomes repetitive.

**The pain**: ORM. Project 13.

### 3. We don't validate input

`POST /posts` accepts any `title` and `body`. Empty strings, 1MB strings, weird unicode.

**The pain**: Validation. Project 14.

### 4. We have no error handling

If the foreign key constraint fails (e.g., user deleted after token issued), we get a generic 500.

**The pain**: Error handling. Project 15.

### 5. We have no logging

We don't log post creation or queries.

**The pain**: Observability. Project 16.

### 6. We don't have edit/delete

Once a post is created, it can't be edited or deleted.

**The pain**: CRUD completeness. Out of scope for the learning path; we'll cover it briefly in a future project.

### 7. We have no pagination

`GET /posts` returns all posts. For 1M posts, the response is huge.

**The pain**: Pagination. Project 18.

### 8. We have no search

`GET /posts?search=hello` would be a `LIKE` query. Slow, no relevance.

**The pain**: Search. Project 19.

### 9. We have no CORS

A browser on a different origin cannot call our server.

**The pain**: CORS. Project 57.

### 10. We have no comments

A post can have comments. We need a `comments` table with a `post_id` foreign key.

**The pain**: More relations. Out of scope (this is the path, not a real app).

---

## What This Project Forbids Us From Doing

This server can:

- Have multiple tables with relations
- Enforce foreign keys
- Cascade deletes
- Join tables
- Use path parameters

It cannot:

- Evolve the schema without data loss (no migrations)
- Hide the SQL behind a clean API (no ORM)
- Validate input strictly
- Handle errors gracefully
- Log requests
- Edit or delete posts
- Paginate large lists
- Search with relevance
- Be called from a browser on a different origin
- Have comments on posts

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 12 | The Migration | "I want to evolve the schema safely." |
| 13 | The ORM Detour | "I want to stop hand-writing SQL." |
| 14 | The Validator | "I want to reject bad input." |
| 15 | The Error Wall | "I want to handle errors with proper status codes." |

Project 12 is the natural next step. We have two tables. We need to add a third (e.g., `comments`). We can't just drop and recreate — we need migrations.

---

## What You Should Do Now

1. **Read the code.** Notice the new `posts` table, the foreign key, the JOIN queries, the path parameters. The auth flow is unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Try to insert a post with an invalid user_id.** See the constraint error.
4. **Try to delete a user.** See the cascade.
5. **Try to add a new column** to the schema. See how you have to drop the table. Feel the pain of "no migrations."
6. **When you are ready**, move to [Project 12: The Migration](../12-migration/).
7. **If anything is unclear**, do not proceed. Foreign keys and JOINs are the foundation of relational databases. They must be solid.

---

## A Note on the Bigger Picture

You now have a *relational* database. Two tables, connected. The graph is starting.

From here, the path diverges:

- **Schema evolution** (project 12): add columns, add tables, safely
- **ORM** (project 13): cleaner database code
- **Validation** (project 14): reject bad input
- **Error handling** (project 15): handle constraint violations
- **Logging** (project 16): observe the database
- **Pagination** (project 18): handle large lists
- **Search** (project 19): find with relevance

The data layer is solid. The graph is the app. The path continues.
