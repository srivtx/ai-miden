# The Build

> *"A page is a window. Don't load the whole table. Just load the window."*

We are going to add pagination to the list endpoints.

## The Code (Updated List Handlers)

### `GET /users` (paginated)

```js
app.get('/users', asyncHandler(async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const offset = parseInt(req.query.offset) || 0;

  const [users, [{ count }]] = await Promise.all([
    db('users').select('id', 'username', 'email', 'created_at').orderBy('created_at', 'desc').limit(limit).offset(offset),
    db('users').count('id as count'),
  ]);

  const total = count;
  res.json({
    data: users,
    meta: {
      total,
      limit,
      offset,
      page: Math.floor(offset / limit) + 1,
      totalPages: Math.ceil(total / limit),
    },
  });
}));
```

### `GET /posts` (paginated)

```js
app.get('/posts', asyncHandler(async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const offset = parseInt(req.query.offset) || 0;

  const [posts, [{ count }]] = await Promise.all([
    db('posts')
      .join('users', 'posts.user_id', 'users.id')
      .select('posts.*', 'users.username as author')
      .orderBy('posts.created_at', 'desc')
      .limit(limit)
      .offset(offset),
    db('posts').count('id as count'),
  ]);

  const total = count;
  res.json({
    data: posts,
    meta: {
      total,
      limit,
      offset,
      page: Math.floor(offset / limit) + 1,
      totalPages: Math.ceil(total / limit),
    },
  });
}));
```

### `GET /users/:id/posts` (paginated)

```js
app.get('/users/:id/posts', asyncHandler(async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  const offset = parseInt(req.query.offset) || 0;

  const [posts, [{ count }]] = await Promise.all([
    db('posts').where({ user_id: req.params.id }).orderBy('created_at', 'desc').limit(limit).offset(offset),
    db('posts').where({ user_id: req.params.id }).count('id as count'),
  ]);

  const total = count;
  res.json({
    data: posts,
    meta: {
      total,
      limit,
      offset,
      page: Math.floor(offset / limit) + 1,
      totalPages: Math.ceil(total / limit),
    },
  });
}));
```

## How It Works

### The Limit and Offset

```js
const limit = Math.min(parseInt(req.query.limit) || 20, 100);
const offset = parseInt(req.query.offset) || 0;
```

- `req.query.limit` is a string (or undefined). `parseInt(...)` converts to a number. `|| 20` defaults to 20 if undefined or `NaN` or `0`.
- `Math.min(limit, 100)` caps the limit at 100. A malicious client can't request 1M rows.
- `req.query.offset` is similar. Default 0.

### The Data Query

```js
db('posts')
  .join('users', 'posts.user_id', 'users.id')
  .select('posts.*', 'users.username as author')
  .orderBy('posts.created_at', 'desc')
  .limit(limit)
  .offset(offset)
```

Standard Knex query with `.limit(limit)` and `.offset(offset)`. The database returns only the requested page.

### The Count Query

```js
db('posts').count('id as count')
```

Returns an array with one row: `[{ count: 1234 }]`. The count is the total number of rows in the table (or filtered, for the nested resource).

### Promise.all

```js
const [posts, [{ count }]] = await Promise.all([
  /* data query */,
  /* count query */,
]);
```

Both queries run in parallel. We wait for both. Then destructure:
- `posts` is the array of post rows
- `[{ count }]` is an array with one object; we destructure `count` (the number)

### The Response

```js
res.json({
  data: posts,
  meta: {
    total,
    limit,
    offset,
    page: Math.floor(offset / limit) + 1,
    totalPages: Math.ceil(total / limit),
  },
});
```

- `data` is the array of rows
- `meta.total` is the total count
- `meta.limit` is the limit we used
- `meta.offset` is the offset we used
- `meta.page` is the current page (1-indexed): `Math.floor(offset / limit) + 1`
- `meta.totalPages` is the total number of pages: `Math.ceil(total / limit)`

## Run It

```bash
# First page (default 20)
curl http://localhost:3000/posts
# {"data":[...],"meta":{"total":10,"limit":20,"offset":0,"page":1,"totalPages":1}}

# Custom page size
curl 'http://localhost:3000/posts?limit=5&offset=0'
# {"data":[...],"meta":{"total":10,"limit":5,"offset":0,"page":1,"totalPages":2}}

# Second page
curl 'http://localhost:3000/posts?limit=5&offset=5'
# {"data":[...],"meta":{"total":10,"limit":5,"offset":5,"page":2,"totalPages":2}}

# Beyond the end
curl 'http://localhost:3000/posts?limit=5&offset=100'
# {"data":[],"meta":{"total":10,"limit":5,"offset":100,"page":21,"totalPages":2}}

# Capped at 100
curl 'http://localhost:3000/posts?limit=10000'
# {"data":[...],"meta":{"total":10,"limit":100,"offset":0,"page":1,"totalPages":1}}
```

The cap kicks in at 100. The offset can be anything (we return empty if beyond).

---

## Experiments

### Experiment 1: Try a large offset

```bash
curl 'http://localhost:3000/posts?limit=5&offset=1000000'
```

Empty data, but `meta` is correct. No error.

### Experiment 2: Negative offset

```bash
curl 'http://localhost:3000/posts?limit=5&offset=-5'
```

The database might error. We should validate. Out of scope for this project.

### Experiment 3: Zero limit

```bash
curl 'http://localhost:3000/posts?limit=0'
```

`parseInt('0') || 20` is `20` (because 0 is falsy). Good.

### Experiment 4: Float limit

```bash
curl 'http://localhost:3000/posts?limit=2.5'
```

`parseInt('2.5')` is `2`. Good.

### Experiment 5: Page-based on the client

The client computes the page from offset:
- Page 1: `offset = 0`
- Page 2: `offset = limit`
- Page 3: `offset = 2 * limit`

The server doesn't need a `page` parameter; the client can convert.

### Experiment 6: Cursor-based (alternative)

If you wanted cursor-based, you'd do:

```js
const cursor = req.query.cursor; // e.g., the id of the last row in the previous page
const posts = await db('posts')
  .where('id', '>', cursor)
  .orderBy('id', 'asc')
  .limit(limit);
```

The client gets a `nextCursor` in the response. Out of scope for this project.

---

## Summary

You now have pagination. List endpoints return a page at a time. The client can navigate pages. The server doesn't load the whole table.

This is the foundation of *every* list API. From here, every list endpoint paginates. The patterns (`limit`, `offset`, `meta`) are universal.

In project 19, we will add search. We will use SQLite FTS5 (full-text search) to find posts by relevance.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
