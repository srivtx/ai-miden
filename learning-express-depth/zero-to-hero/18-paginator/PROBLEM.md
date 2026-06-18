# The Problem

> *"Returning 1 million rows is not an API. It's a denial of service."*

## Why Pagination Is Essential

In project 17, `GET /posts` returns all posts. For 10 posts, that's 5KB. For 1 million posts, that's 500MB. The consequences:

1. **Server memory spike** — the server has to load 1M rows into memory, build the JSON, send it. For 1M rows, that's 500MB of memory.
2. **Client freeze** — the client has to parse 500MB of JSON. Most browsers will OOM or freeze.
3. **Network timeout** — even on a fast network, 500MB takes seconds to transfer. The client times out.
4. **Database load** — the database has to scan the entire table, even if the client only wants 20 rows.
5. **Cascading failures** — one slow query can hold a connection, exhaust the connection pool, and take down the server.

This is not theoretical. Every large API has been bitten by this. The fix is *pagination*: never return more than N rows in one response.

## What Pain Is This Solving?

Imagine you have 1M users. A frontend wants to display "all users" in a table. Without pagination:

- The server tries to send 1M rows
- The frontend tries to render 1M DOM nodes
- The browser crashes
- The user sees a blank page
- The frontend team files a bug: "the users page is broken"

With pagination:

- The server sends 20 users
- The frontend renders 20 rows
- The browser is happy
- The user sees a table with a "Next" button
- The frontend team files a feature request: "add a Next button" (which we already have)

The user experience is better. The server load is lower. The network is faster. Everyone wins.

## The Deeper Problem: Memory and Time

Loading 1M rows into memory is *O(n)* in memory and *O(n)* in time. The client has to wait for all 1M rows. The server has to allocate memory for all 1M rows. The network has to transfer all 1M rows.

Loading 20 rows is *O(1)* in memory (constant — 20 rows, no matter the table size) and *O(log n)* in time (the database uses an index). The client waits for 20 rows. The server allocates memory for 20 rows. The network transfers 20 rows.

Pagination turns an *O(n)* operation into an *O(1)* operation. The cost is constant, regardless of the table size.

## What This Project Will Solve

This project will:

1. Add `limit` and `offset` query parameters to `GET /posts` and `GET /users`
2. Cap `limit` to a maximum (e.g., 100) to prevent abuse
3. Return `{ data, meta }` with `total`, `limit`, `offset`, `page`, `totalPages`
4. Use `Promise.all` to fetch the data and the count in parallel

By the end, list endpoints return a page at a time. The client can navigate pages.

## What This Project Will *Not* Solve

- **Cursor-based pagination** — for very large datasets, cursor is more efficient. Out of scope.
- **Sorting** — we hardcode `ORDER BY created_at DESC`. Out of scope.
- **Filtering** — `?author=42` is a simple addition. Out of scope.
- **Field selection** — `?fields=id,name` is a real feature. Out of scope.
- **Performance at scale** — for 100M rows, even paginated queries are slow without indexes. Out of scope.

## The Question This Project Answers

> *"How do I return a list without OOMing the server or the client?"*

If you can answer: "paginate — `?limit=20&offset=0`, return `{ data, meta }`, cap the limit," you are ready for project 19.
