# The Decisions

> *"A page is a window. The client moves the window. The server stays calm."*

## Decision 1: Offset-based and not cursor-based

**Alternatives**:
- **Cursor-based** — `?cursor=abc&limit=20`. Fast for any page, no skip cost.
- **Page-based** — `?page=1&per_page=20`. User-friendly, but less flexible.

**Why offset: Simple. Easy to understand. Works with any database. Fine for our scale (1M rows max).

**Trade-off**: Slow for large offsets. Inconsistent under writes. For 100M rows, cursor is better.

## Decision 2: Cap the limit at 100

**Alternative**: No cap. Or a higher cap (e.g., 1000).

**Why 100: A balance between flexibility and security. Most clients don't need more than 100 rows at a time. A cap of 100 prevents accidental OOM (a client requests 1M rows) and intentional abuse (a malicious client requests 1M rows).

**Trade-off**: A client that wants 200 rows has to make 2 requests. We accept this.

## Decision 3: Default limit of 20

**Alternative**: Default 10, 50, 100, etc.

**Why 20: A reasonable default. Most UIs render 10-20 rows per page. 20 is the sweet spot.

**Trade-off**: A client that doesn't specify `limit` gets 20 rows. They might want more. They can specify.

## Decision 4: `{ data, meta }` response shape

**Alternative**: Just an array. Or array with headers (X-Total-Count).

**Why `{ data, meta }`**: The client gets the metadata in the response body. They don't have to read headers. The shape is consistent across endpoints.

**Trade-off**: A bit more verbose. We accept it for clarity.

## Decision 5: `meta.page` and `meta.totalPages`

**Alternative**: Just `meta.offset` and `meta.limit`. The client computes the page.

**Why include page: Most clients think in pages, not offsets. Computing the page in the handler is trivial (`Math.floor(offset / limit) + 1`). The client gets a more user-friendly response.

**Trade-off**: Redundant with `offset` and `limit`. We accept it for usability.

## Decision 6: `Promise.all` for data + count

**Alternative**: Run the data query, then the count query. Or run them sequentially.

**Why `Promise.all`: Both queries are independent. Running them in parallel is faster (they execute concurrently).

**Trade-off**: Slightly more complex code. We accept it for performance.

## Decision 7: No validation of `limit` and `offset`

**Alternative**: Validate with Zod. `limit` must be a positive integer, `offset` must be a non-negative integer.

**Why no validation: We're using `parseInt` which returns `NaN` for invalid input, and `|| 20` defaults. Negative offsets are passed to the database (which might error or return empty). For now, this is acceptable.

**Trade-off**: A malicious client could send `?offset=-1`. The database might error. We should validate in a future project.

## Decision 8: No HATEOAS pagination links

**Alternative**: Include `nextPage` and `prevPage` URLs in the response. The client doesn't have to construct the URL.

**Why no: Most APIs don't do this. The client can construct the URL from `meta`.

**Trade-off**: Slightly more work for the client. We accept it for simplicity.

## Decision 9: Same pagination for nested resources

`GET /users/:id/posts` is paginated the same way as `GET /posts`. The count is filtered (only posts by this user).

**Why consistent: The patterns are the same. The client uses the same code to paginate.

**Trade-off**: None.

## Decision 10: No total count optimization

**Alternative**: Estimate the count (`pg_class.reltuples` in Postgres). Cache the count.

**Why no optimization: For our scale, the count is fast (SQLite, small table). We don't optimize until we measure a problem.

**Trade-off**: For very large tables, the count is slow. We accept this.

---

## What We Did Not Decide

- **Cursor-based pagination** — out of scope (future optimization)
- **Field selection** (`?fields=id,name`) — out of scope
- **Sorting** (`?sort=name`) — out of scope
- **Filtering** (`?author=42`) — out of scope
- **HATEOAS pagination links** — out of scope
- **Count caching** — out of scope
- **Count estimation** — out of scope
- **Negative offset validation** — out of scope

Each is a future decision.

---

## The Meta-Decision: The API Scales to Lists

For 17 projects, list endpoints returned everything. For 1M rows, the server OOMed. The client froze. The network timed out.

Now list endpoints return a page at a time. The client gets 20 rows. The server loads 20 rows. The network transfers 20 rows. The cost is *constant*, regardless of the table size.

This is the foundation of *every* large-scale API. Pagination is non-negotiable. The patterns (`limit`, `offset`, `meta`) are universal.

The next 22 projects will assume pagination. The path diverges:

- **Search** (project 19): find with relevance
- **File upload** (project 20): accept files
- **Email** (project 21): send notifications
- **Caching** (project 22): reduce DB load
- **Redis** (project 23): shared state
- **Rate limiting** (project 24): throttle abuse
- **Cron** (project 25): scheduled jobs
- **Queue** (project 26): move slow work off the request
- **Transactions** (project 27): atomic multi-write operations

The API scales. The path continues.
