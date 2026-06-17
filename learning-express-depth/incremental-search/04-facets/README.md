# 04 — Facets (Search)

Show counts per category/brand for the current results.

**What's new:**
- `facets` field in the response: counts per category, per brand
- Facets reflect the CURRENT filtered set (not the whole table)

**Why facets?** When searching "phone", show: "12 in electronics, 5 in computers". The user clicks "electronics" to filter. Without facets, they'd have to know what categories exist.

**Why on the current set?** When you click "Apple" brand, the category counts should update too. "5 Apple products: 3 electronics, 2 computers." Facets always reflect what's currently visible.

**The pattern:** one query, one count, two groupings. We loop over the results once and count per field.

## Run
```bash
npm install && node server.js
```

```bash
# All products
curl 'http://localhost:3000/search'
# { count: 5, results: [...], facets: { category: [{ electronics: 3 }, { computers: 2 }], brand: [...] } }

# Filter by Apple
curl 'http://localhost:3000/search?brand=apple'
# { count: 2, results: [iPhone, MacBook], facets: { category: [{ electronics: 1 }, { computers: 1 }] } }
```

## What we learned
- Faceted search
- Counts per field on the current result set
- The "show me what I can filter by" pattern
- One query, multiple aggregations

## Next
**05-autocomplete** — as the user types, suggest completions.
