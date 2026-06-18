# The Thought

> *"A page is a window. The window is small. The client can move the window. The server stays calm."*

## Offset-Based Pagination

The simplest form of pagination. The client sends:

```
?limit=20&offset=0
```

- `limit` — how many rows to return (e.g., 20)
- `offset` — how many rows to skip (e.g., 0)

The server runs:

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 0;
```

This returns rows 1-20 (the first page).

For the second page:

```
?limit=20&offset=20
```

The server runs:

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 20;
```

This returns rows 21-40.

### Pros

- Simple
- Easy to understand
- Works with any database
- The client can jump to any page

### Cons

- **Slow for large offsets** — `OFFSET 1000000` requires the database to scan and discard 1M rows. The query gets slower as the offset grows.
- **Inconsistent under writes** — if rows are inserted or deleted during pagination, the client might see duplicates or skip rows.

For our scale (1M users max), offset is fine. For 100M rows, cursor is better.

## Cursor-Based Pagination

The client sends:

```
?cursor=abc&limit=20
```

The cursor is an opaque token (e.g., the ID of the last row in the previous page). The server returns:

- The 20 rows after the cursor
- A new cursor for the next page

### Pros

- **Fast for any page** — the database uses the index on the cursor column. No skip cost.
- **Consistent under writes** — new rows don't shift the cursor.

### Cons

- The client can't jump to page 5 directly (no random access)
- The cursor format is opaque (the client doesn't know what it means)
- More complex to implement

We use offset for simplicity. Cursor is a future project (or a future optimization).

## Page-Based vs. Offset-Based

Some APIs use page-based:

```
?page=1&per_page=20
```

This is equivalent to offset-based with `offset = (page - 1) * per_page`. It's more user-friendly (the client thinks in pages) but less flexible (you can't easily say "give me rows 100-110").

We use offset-based. The client can compute the page if they want.

## The `meta` Object

The response shape is:

```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "page": 1,
    "totalPages": 5
  }
}
```

`data` is the array of rows. `meta` has the metadata:

- `total` — total number of rows in the table
- `limit` — how many were requested (and returned)
- `offset` — how many were skipped
- `page` — current page (1-indexed)
- `totalPages` — total number of pages

The client uses `meta` to render "Page 1 of 5" or "Showing 1-20 of 100".

## Capping the Limit

`?limit=1000000` would let the client request a million rows. We don't allow that. We cap:

```js
const limit = Math.min(parseInt(req.query.limit) || 20, 100);
```

- Default: 20
- Max: 100

The cap is a security measure. Without it, a malicious client could request 1M rows and OOM the server.

## Computing the Total

We need the total count for `meta.total`. We compute it with a separate query:

```js
const [posts, [{ count }]] = await Promise.all([
  db('posts').select(...).limit(limit).offset(offset),
  db('posts').count('id as count'),
]);
```

`Promise.all` runs both queries in parallel. The data query and the count query don't depend on each other.

For very large tables, the count query is slow (it has to scan the table or use an index). For SQLite, it's fast. For Postgres, it's fast with an index. We don't optimize further.

## Common Confusions (read these)

**Confusion 1: "Why not just return all rows? The client can paginate."**
The server still has to load all rows into memory. The network still has to transfer all rows. The client still has to parse all rows. The waste is at every layer.

**Confusion 2: "Why cap the limit?"**
Security. A malicious client could request 1M rows and OOM the server. The cap is a safety net.

**Confusion 3: "Why not use the page parameter?"**
You can. It's equivalent. We use offset because it's more flexible (you can do `?offset=15&limit=5` to get rows 15-19, which you can't do with page-based).

**Confusion 4: "What if the offset is larger than the total?"**
The database returns an empty array. The client gets `{ data: [], meta: { total: 100, offset: 200, ... } }`. The client knows they overshot.

**Confusion 5: "What if the offset is negative?"**
`parseInt('-5')` is `-5`. The database might error. We should validate (positive integer). Out of scope for now.

**Confusion 6: "What if `limit` is not a number?"**
`parseInt('abc')` is `NaN`. `NaN || 20` is `20` (because NaN is falsy). So we default to 20. Good.

**Confusion 7: "What about the count query? Is it expensive?"**
For SQLite, `COUNT(*)` is fast (the table is small). For Postgres, `COUNT(*)` is fast with an index. For very large tables, you'd use an estimate (`pg_class.reltuples`). We don't optimize.

**Confusion 8: "Why not include `nextPage` and `prevPage` URLs in the response?"**
HATEOAS-style pagination. The client doesn't have to construct the URL. We don't do this (most APIs don't).

## What We Are About to Build

A ~250-line Express app that:

1. Paginates `GET /users` with `?limit=&offset=`
2. Paginates `GET /posts` with `?limit=&offset=`
3. Paginates `GET /users/:id/posts` with `?limit=&offset=`
4. Caps the limit at 100
5. Returns `{ data, meta }` with full metadata
6. Uses `Promise.all` for the data + count queries

The handlers are slightly updated. The schema (validation) is unchanged. The error wall is unchanged.

In [BUILD.md](./BUILD.md) we will go line by line.
