# Pagination Demo — Offset vs Cursor with SQLite

500 seed items, indexed on `id`, `created_at`, `category`.

## Endpoints
```
GET /offset?limit=20&offset=0       # offset pagination (page N, M per page)
GET /cursor?limit=20&cursor=0       # cursor pagination (next 20 after cursor)
GET /cursor/category/electronics    # cursor + filter
GET /benchmark                      # compare speed: page 1 vs page 1000
```

## Run
```
node server.js
```

## What this teaches
1. Offset pagination: O(N) per page, slow at deep pages
2. Cursor pagination: O(1) per page, stable, infinite scroll
3. Pagination with filter (category)
4. The benchmark endpoint shows the speed difference in real time
5. Cursor format: just the last ID. Simple. No state.
