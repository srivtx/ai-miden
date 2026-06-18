# The Decisions

> *"One table is a list. Two tables connected is a graph. The graph is the app."*

## Decision 1: A separate `posts` table, not a JSON column in `users`

**Alternative**: `users.posts = '[{"title":...}]'` (a JSON array on the user).

**Why a separate table**: Foreign keys, JOINs, indexing, CASCADE — all of these require a separate table. A JSON column can't have a foreign key. You can't efficiently query "all posts by user X." You can't cascade delete. Separate table is the right answer.

**Trade-off**: An extra table, an extra JOIN. We accept this for the integrity.

## Decision 2: `ON DELETE CASCADE`

**Alternative**: `ON DELETE RESTRICT` (prevent user deletion if they have posts), `ON DELETE SET NULL` (set the foreign key to null on user delete).

**Why CASCADE**: A post "belongs to" a user. When the user is deleted, the posts are deleted too. The user "owns" the posts. CASCADE is the natural choice.

**Trade-off**: Deleting a user deletes their posts. For some apps, you'd want to keep the posts (set the foreign key to NULL and show "deleted user"). It depends on the use case. We use CASCADE.

## Decision 3: `PRAGMA foreign_keys = ON`

**Alternative**: Leave it off (SQLite's default).

**Why ON**: We need the constraint enforced. Without it, we can insert orphan data.

**Trade-off**: Slightly slower writes (the database checks the constraint). Negligible. We always turn it on.

## Decision 4: `INNER JOIN` (the default `JOIN`)

**Alternative**: `LEFT JOIN`.

**Why INNER**: Posts always have a user (the foreign key enforces this). There's no need to return posts with NULL authors.

**Trade-off**: If we ever have orphan data (e.g., from a manual SQL fix), `LEFT JOIN` would return it with NULL author. `INNER JOIN` excludes it. We use INNER.

## Decision 5: `ORDER BY created_at DESC`

**Alternative**: `ORDER BY id DESC`, no order, ascending.

**Why `created_at DESC`: Newest first. This is the standard "feed" order.

**Trade-off**: For very large tables, ordering can be slow without an index. We don't have an index on `created_at`. We could add one (`CREATE INDEX idx_posts_created_at ON posts(created_at)`). We don't, because we don't have scale yet. Project 22 (Cache) and project 23 (Redis) discuss scale.

## Decision 6: `users.username AS author`

**Alternative**: `users.username` (no alias).

**Why alias: The response has `author: "alice"`, not `username: "alice"`. The alias makes the response more readable.

**Trade-off**: A bit more verbose in the SQL. We accept this for clarity.

## Decision 7: Numeric `user_id` (not `username`)

**Alternative**: `user_username` (a string).

**Why numeric ID**: Stable (usernames can change). Faster joins. Standard. Aligns with the foreign key reference (`users.id`).

**Trade-off**: A JOIN is required to get the username. We accept this for stability.

## Decision 8: No `updated_at`

**Alternative**: Add `updated_at` for tracking modifications.

**Why not: We don't have edit routes (`PATCH /posts/:id`). When we add them (future project), we'll add `updated_at`.

## Decision 9: No `deleted_at` (soft delete)

**Alternative**: Add `deleted_at` to support soft delete (mark as deleted, don't actually delete).

**Why not: Out of scope. We'll add it when we need it.

## Decision 10: No indexes beyond the primary key and `UNIQUE`

**Alternative**: Add `INDEX idx_posts_user_id` for faster `WHERE user_id = ?` queries.

**Why not: We don't have scale yet. For 1000 posts, the index is overkill. We'll add indexes when we feel the slowness. Project 22.

---

## What We Did Not Decide

- **Many-to-many** (e.g., posts ↔ tags) — out of scope. Would need a junction table.
- **Polymorphic associations** (e.g., comments on posts AND on users) — out of scope.
- **Schema evolution** — we have two `CREATE TABLE`s. If we add a column, we have to drop and recreate. Project 12.
- **ORM** — we hand-write SQL. Project 13.
- **Validation** — we accept any `title` and `body`. Project 14.
- **Edit/delete posts** — out of scope. Would need `PATCH /posts/:id` and `DELETE /posts/:id`.
- **Comments** — out of scope. Would need a `comments` table with `post_id` foreign key.
- **Pagination** — `GET /posts` returns all posts. Project 18.
- **Search** — out of scope. Project 19.

Each is a future decision.

---

## The Meta-Decision: The Data Model Is a Graph

For 11 projects, our data was flat: a list of users, a list of sessions. Now we have a graph:

```
users ─┬─< posts
       │
       └─< (future: comments, likes, etc.)
```

A user has many posts. A post belongs to a user. The relationship is enforced by the database (foreign key). The relationship can be traversed in both directions:

- `users → posts` (all posts by a user)
- `posts → users` (the author of a post)

This is the foundation of *every* real app. Slack has users and messages. Notion has users and pages. Figma has users and designs. The shapes are different, but the pattern is the same: tables, foreign keys, JOINs.

The next 29 projects will keep extending this graph. We'll add `comments`, `likes`, `messages`, `channels`, `pages`, `workspaces`. Each will be a new table, with a foreign key to another table. The pattern is stable. The graph grows.

This is the inflection point of data modeling. The graph is the app.
