# The Problem

> *"A list of users is not an app. A list of users with their posts is an app."*

## Why Multiple Tables

In project 10, we had one table: `users`. Real apps have many tables, and the tables are *related*. A blog has `users` and `posts`. The `posts` table needs to know who wrote each post. A store has `users` and `orders`. The `orders` table needs to know who placed each order.

Without relations, we'd duplicate data. Imagine storing the author's username *inside* each post:

```json
{ "id": 1, "title": "Hello", "author": "alice", "body": "..." }
{ "id": 2, "title": "World", "author": "alice", "body": "..." }
{ "id": 3, "title": "Foo", "author": "bob", "body": "..." }
```

If alice changes her username, we have to update every post. If we miss one, the data is inconsistent. This is a *denormalized* design, and it causes bugs.

The solution: *normalize*. Store the username once (in `users`), and store just the *reference* (the user id) in `posts`. To get the username, *join* the two tables.

## What Pain Is This Solving?

Without foreign keys, we have no integrity. Without joins, we have no way to combine data from multiple tables. Without relations, we have a flat list of rows — not an app.

This project adds:

1. A `posts` table with a `user_id` foreign key
2. The `PRAGMA foreign_keys = ON` to enforce the constraint
3. `ON DELETE CASCADE` to clean up posts when a user is deleted
4. `JOIN` queries to combine posts with their authors
5. New routes: `POST /posts`, `GET /posts`, `GET /posts/:id`, `GET /users/:id/posts`

By the end, posts are connected to users. We can ask "all posts by user 1" or "all posts with their authors."

## The Deeper Problem: Referential Integrity

Without foreign keys, you can have orphan data. A post with `user_id = 99` but no user with id 99. The post exists; the user doesn't. The data is inconsistent.

With foreign keys, the database *enforces* the relationship. You can't insert a post with a `user_id` that doesn't exist. The database rejects it.

`ON DELETE CASCADE` adds another rule: if a user is deleted, all their posts are deleted too. This prevents orphans.

`PRAGMA foreign_keys = ON` is required because SQLite has foreign keys *off* by default for backwards compatibility. We turn them on.

## What This Project Will Solve

This project will:

1. Add a `posts` table with `user_id` foreign key
2. Enable foreign key enforcement
3. Add `ON DELETE CASCADE` for cleanup
4. Add 4 new routes for posts
5. Use `JOIN` to combine posts with users

By the end, we have a real relational data model. Users have many posts. Posts belong to a user. The relationship is enforced by the database.

## What This Project Will *Not* Solve

- **Schema evolution** — we have two `CREATE TABLE`s. If we add a column, we have to drop and recreate. Project 12.
- **ORM** — we hand-write SQL with joins. Project 13.
- **Many-to-many** — a post can have many tags; a tag can have many posts. That's a junction table. Out of scope for this project.
- **Validation** — we accept any `title` and `body`. Project 14.
- **Pagination** — `GET /posts` returns all posts. For 1M posts, that's huge. Project 18.
- **Search** — `GET /posts?search=hello` would be a `LIKE` query. Project 19.
- **Edit/delete posts** — we don't have `PATCH /posts/:id` or `DELETE /posts/:id`. Out of scope.
- **Comments** — a post can have many comments. That's a `comments` table with a `post_id` foreign key. Out of scope.

## The Question This Project Answers

> *"How do I connect two tables?"*

If you can answer: "foreign key column, `PRAGMA foreign_keys = ON`, `JOIN` to combine," you are ready for project 12.
