# 03 — Filters (Search)

Combine search with filters. Search + category, brand, price range.

**What's new:**
- Search by `q` (substring match)
- Filter by `category`, `brand`, `min_price`, `max_price`
- Filters combine with search (AND)
- Results sorted by price

**Why filters?** Search alone isn't enough. A user searching "phone" might want only phones under $500. Search + filters: "phones under $500" with two clicks instead of complex query syntax.

**Why combine with AND?** "Phones" AND "category:electronics" AND "min_price:10000" — the user wants ALL of these.

**Why query params?** Standard. URL-shareable. `?q=phone&category=electronics&max_price=50000`.

## Run
```bash
npm install && node server.js
```

```bash
# Search for phone
curl 'http://localhost:3000/search?q=phone'
# Returns: iPhone, Galaxy, Pixel

# Filter by category
curl 'http://localhost:3000/search?category=electronics'
# Returns: only electronics

# Combine
curl 'http://localhost:3000/search?q=phone&category=electronics'
# Both filters

# Price range
curl 'http://localhost:3000/search?min_price=80000&max_price=100000'
# Phones in that range
```

## What we learned
- Combining search with filters
- Dynamic SQL building
- Multiple AND conditions
- Query params for shareable URLs

## Next
**04-facets** — show counts per category. "12 in electronics, 5 in computers."
