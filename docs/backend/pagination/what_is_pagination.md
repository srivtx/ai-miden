## Why it exists (THE PROBLEM)

You have 1 million users. You need to display them. Naive: `SELECT * FROM users LIMIT 20 OFFSET 0`. Fine. User clicks "page 2": `OFFSET 20`. Fine. Page 5000: `OFFSET 100000`. The database has to read 100,020 rows and discard the first 100,000. Each subsequent page is SLOWER than the last. Page 50,000 takes 30 seconds. The user gives up.

**Cursor pagination** solves this. Instead of "skip N rows," it says "give me rows after this specific item." The database reads the index to find that item, then continues forward. Page 1 takes 5ms. Page 50,000 also takes 5ms. Constant speed.

Twitter, GitHub, Instagram, Facebook all use cursor pagination. They never show you "page 5000 of users." They show "load more" — which is cursor pagination in disguise.

## Definition (very simple)

**Offset pagination** = skip N rows then take M:
```sql
SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 100000;  -- page 5001
```
Database reads 100,020 rows, discards 100,000, returns 20. O(N) per page.

**Cursor pagination** = start from item X and take the next M:
```sql
SELECT * FROM users WHERE id > 100020 ORDER BY id LIMIT 20;  -- items after 100020
```
Database uses the index on `id`, finds 100020, reads next 20. O(1) per page.

The cursor = the ID (or timestamp, or composite key) of the LAST item from the previous page. Pass it back as `?cursor=100020`. Server returns `nextCursor: 100040`.

## Real-life analogy

**Offset pagination = a book with page numbers.** "Go to page 5001." You have to flip through 5000 pages. Each page is 200 pages of paper. Takes an hour.

**Cursor pagination = a Choose Your Own Adventure book.** "Turn to page 142 to continue." You jump directly. Always the same speed, regardless of which page you're on.

## Tiny numeric example

Same table, 1M users, page size 20:

| Page | Offset (ms) | Cursor (ms) |
|---|---|---|
| 1 | 5 | 5 |
| 100 | 50 | 5 |
| 1000 | 500 | 5 |
| 10,000 | 5000 | 5 |
| 50,000 | 30000 (timeout) | 5 |

Cursor is constant. Offset explodes.

## Common confusion (5+ bullet points)

1. **"I want page numbers, not cursors."** Page numbers come from offset. They break with concurrent inserts (a new user shifts everyone by 1). Cursors don't. The trade-off: stable infinite scroll (cursor) vs random access to page 50 (offset). Most APIs use cursor. If users NEED to bookmark page 50, use offset but only at small scales.

2. **"Cursor is hard with multi-column sort."** Use composite cursor. If sort is `(created_at DESC, id DESC)`, cursor = `"2024-01-15T10:30:00,42"`. Server uses both: `WHERE (created_at, id) < (?, ?)`. Slightly more complex but the same idea.

3. **"The user can skip ahead with cursors."** They can, by constructing cursors. But that's the same as direct API access — they're already API-aware. The trade-off favors performance and stability.

4. **"I need to jump to a specific page."** Use offset for small N (e.g., "first 100 pages of a forum thread"). For deeper pages, switch to "load more" (cursor). Combine: offset-based pagination for the first page (so URLs like `?page=5` work), then cursor for subsequent pages.

5. **"Cursor + sort direction matters."** If sort is `id DESC` (newest first), use `WHERE id < cursor`. If sort is `id ASC`, use `WHERE id > cursor`. Get this wrong and you paginate the same row repeatedly.

## Key properties

| Property | Offset | Cursor |
|---|---|---|
| Random access page N | Yes (just `OFFSET N*M`) | No (need to compute cursor) |
| Performance | O(N) per page | O(1) per page |
| Stable with concurrent inserts | No (rows shift) | Yes (anchored to a specific id) |
| "Load more" UX | Clumsy | Natural |
| "Jump to page 50" | Easy | Hard |
| Total count | Cheap (`SELECT COUNT(*)`) | Expensive or impossible |

## When to use which

- **Offset**: small N (< 10K rows total), users need to jump to specific pages, you need total count
- **Cursor**: large N, infinite scroll, real-time data, no total count needed

## Connection to our projects

Most of our 73 apps use `?page=N&limit=M` (offset). For dev demos with 10 rows, fine. For real use with 10K+ rows, switch the routes that list data to cursor:
- `GET /tasks?cursor=lastSeenId&limit=20` instead of `?page=N&limit=20`
- `GET /products?cursor=lastProductId&category=electronics`

The `cursor-pagination/` project in apps/level2 already shows the implementation. Copy that pattern to any list endpoint that might grow beyond dev scale.
