# The Thought

> *"Foreign keys say: 'this column points to that row.' JOINs say: 'follow the points and give me both.' CASCADE says: 'when the source goes, the targets go too.'"*

## What a Foreign Key Is

A *foreign key* is a column in one table that references the *primary key* of another. It creates a relationship.

```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

`posts.user_id` references `users.id`. Every `user_id` in `posts` must match an `id` in `users`. The database enforces this.

## Enabling Foreign Keys in SQLite

SQLite has foreign keys *off* by default. We turn them on:

```js
db.pragma('foreign_keys = ON');
```

This is a per-connection setting. We do it once, after opening the database.

Without this pragma, foreign keys are *not enforced*. You can insert a post with `user_id = 999` and SQLite won't complain. With the pragma, SQLite rejects the insert.

## ON DELETE CASCADE

```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

`ON DELETE CASCADE` says: "when the referenced user is deleted, also delete the rows that reference them." So if user 1 is deleted, all posts with `user_id = 1` are also deleted.

Other options:

- `ON DELETE RESTRICT` (default) — reject the delete if there are referencing rows
- `ON DELETE SET NULL` — set the foreign key to NULL (the column must allow NULL)
- `ON DELETE SET DEFAULT` — set the foreign key to a default value
- `ON DELETE NO ACTION` — like RESTRICT but checked at the end of the transaction
- `ON DELETE CASCADE` — delete the referencing rows

We use `CASCADE` because we want posts to be deleted with the user. The user owns the posts; when the user is gone, the posts are gone.

## What a JOIN Is

A *JOIN* combines rows from two tables based on a related column. The most common is `INNER JOIN`:

```sql
SELECT posts.*, users.username AS author
FROM posts
JOIN users ON posts.user_id = users.id
WHERE posts.id = ?;
```

This says: "give me the post plus the author's username." For each post, look up the user with the matching `id`, and include the user's `username` as `author`.

The result:

| id | user_id | title | body | created_at | author |
|----|---------|-------|------|------------|--------|
| 1  | 1       | Hello | ...  | 1234567890 | alice  |
| 2  | 2       | World | ...  | 1234567891 | bob    |

Each post is one row, but the row includes data from both tables. The `JOIN ... ON` clause is the bridge.

## Types of Joins

- **`INNER JOIN`** (or `JOIN`) — return only rows where the join condition matches. Posts with no user (shouldn't happen with foreign keys) are excluded.
- **`LEFT JOIN`** — return all rows from the left table, with matching rows from the right (or NULLs). Posts without a user would have NULL author.
- **`RIGHT JOIN`** — return all rows from the right table, with matching from the left.
- **`FULL OUTER JOIN`** — return all rows from both, with NULLs where there's no match.

We use `INNER JOIN` (the default). Posts always have a user (the foreign key enforces this).

## Path Parameters

```js
app.get('/posts/:id', (req, res) => { ... });
app.get('/users/:id/posts', (req, res) => { ... });
```

The `:id` is a *path parameter*. Express extracts it into `req.params.id`. So `GET /posts/42` gives `req.params.id = '42'` (a string).

In the prepared statement:

```js
const findPostById = db.prepare(`
  SELECT ... FROM posts JOIN users ON ... WHERE posts.id = ?
`);
findPostById.get(req.params.id);
```

The `?` is filled with `req.params.id`. SQLite does the type coercion (string `'42'` becomes integer `42` for the comparison).

## Common Confusions (read these)

**Confusion 1: "Why use a foreign key? Why not just store the username?"**
If you store the username, and the user changes their username, every post has the old username. With a foreign key, you store the user *id*. The username can change in `users`; the post still references the same user (by id). The JOIN gets the current username.

**Confusion 2: "What's the difference between `CASCADE` and `RESTRICT`?"**
`CASCADE` deletes the children when the parent is deleted. `RESTRICT` prevents the parent from being deleted if it has children. We use `CASCADE` for posts (they belong to the user).

**Confusion 3: "Why is `PRAGMA foreign_keys = ON` needed?"**
SQLite has it off by default for backwards compatibility. Always turn it on. We do it right after opening the database.

**Confusion 4: "What if I forget `PRAGMA foreign_keys = ON`?"**
Foreign keys are not enforced. You can insert orphan data. The constraint is still in the schema, but it's not checked. Always turn on the pragma.

**Confusion 5: "What is `ON UPDATE`?"**
Like `ON DELETE` but for updates. If the parent's primary key changes (rare, but possible), what happens to the children? `ON UPDATE CASCADE` would update the children's foreign key to match. We don't need this because we use AUTOINCREMENT IDs that never change.

**Confusion 6: "Why `ORDER BY created_at DESC`?"**
To get the newest posts first. `DESC` is descending (newest to oldest). Default is `ASC` (ascending, oldest to newest).

**Confusion 7: "What is `AS author`?"**
A column alias. The `users.username` column is renamed to `author` in the result. Makes the response more readable.

## What We Are About to Build

A ~90-line Express app that:

1. Has the same auth flow as project 10
2. Has a new `posts` table with a foreign key to `users`
3. Has 4 new post routes: create, list all, get one, list by user
4. Uses `JOIN` to include the author in the response

The auth flow is unchanged. The new pieces are the `posts` table, the foreign key, the JOIN queries, and the path parameters.

In [BUILD.md](./BUILD.md) we will go line by line.
