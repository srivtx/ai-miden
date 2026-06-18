# Project 18: The Paginator

> *"Don't ship the whole table. Ship a page. The client can ask for more."*

In project 17, `GET /posts` returns *all* posts. For 10 posts, that's fine. For 1 million posts, the response is 100MB. The server's memory spikes. The client's browser freezes. The network times out.

This project adds **pagination**. We split the list into *pages*. The client requests a specific page. The server returns just that page (plus metadata about the total count, the current page, the total pages, etc.).

The most common pagination styles are:

- **Offset-based**: `?limit=20&offset=0` (skip 0, take 20)
- **Page-based**: `?page=1&per_page=20` (page 1, 20 per page)
- **Cursor-based**: `?cursor=abc&limit=20` (give me 20 starting after cursor abc)

We use **offset-based** for its simplicity. Cursor-based is better for very large datasets (no skip cost), but offset is fine for our scale.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is returning all rows bad? What is pagination?
2. [The Thought](./THOUGHT.md) — Offset vs. cursor. How to compute total pages.
3. [The Build](./BUILD.md) — Line-by-line construction of the paginator
4. [The Decisions](./DECISIONS.md) — Why offset? Why not cursor? Why a meta object?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Pagination splits a list into chunks. The client sends `?limit=20&offset=0` (or `?page=1&per_page=20`). The server returns `{ data: [...], meta: { total, limit, offset, page, totalPages } }`. The client can request more pages. The server doesn't load the whole table into memory.

---

## The Code

```js
// In the list handler
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

Test it:

```bash
# First page
curl 'http://localhost:3000/posts?limit=2&offset=0'
# {"data":[...],"meta":{"total":10,"limit":2,"offset":0,"page":1,"totalPages":5}}

# Second page
curl 'http://localhost:3000/posts?limit=2&offset=2'
# {"data":[...],"meta":{"total":10,"limit":2,"offset":2,"page":2,"totalPages":5}}

# Last page
curl 'http://localhost:3000/posts?limit=2&offset=8'
# {"data":[...],"meta":{"total":10,"limit":2,"offset":8,"page":5,"totalPages":5}}
```

The pain of "GET /posts returns 1M rows" is solved. The client gets a page at a time.

---

## What You Will Have Learned

- Why pagination is essential for large lists
- Offset-based vs. cursor-based pagination
- The `limit` and `offset` query parameters
- The `meta` object with `total`, `limit`, `offset`, `page`, `totalPages`
- Why we cap `limit` (security)
- How to compute total count efficiently

These are the foundations of *every* list API. From here, every list endpoint paginates.
