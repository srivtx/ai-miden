# Products API — Step 4 in the learning path

Builds on Blog. Adds: categories, prices (in cents), inventory, search, sort, filter, stock management.

## Endpoints
```
GET    /products                    # search/filter: ?q=laptop&category=electronics&min_price=10000&max_price=200000&in_stock=true&sort=price_cents&order=asc
GET    /products/:id                # by id OR sku
POST   /products                    # create
PATCH  /products/:id                # update
PATCH  /products/:id/stock          # { delta: +5 } or { delta: -3 } to adjust stock
DELETE /products/:id
GET    /categories                  # all categories with product counts
```

## Try
```bash
# Search
curl 'http://localhost:3000/products?q=laptop'
# { count: 1, items: [{ name: "Laptop Pro", price: "1299.00", ... }] }

# Filter by category
curl 'http://localhost:3000/products?category=electronics'

# Filter by price range
curl 'http://localhost:3000/products?min_price=50000&max_price=100000'

# In stock only
curl 'http://localhost:3000/products?in_stock=true'

# Sort by price ascending
curl 'http://localhost:3000/products?sort=price_cents&order=asc'

# Adjust stock (e.g., sold 3 units)
curl -X PATCH http://localhost:3000/products/<id>/stock \
  -H "Content-Type: application/json" -d '{"delta": -3}'
```

## What this teaches
1. **Money handling**: store in cents (integers), never floats
2. **Multi-field search**: search across name, description, SKU
3. **Filter combinations**: query params combined with AND
4. **Sort with whitelist**: never allow user-supplied column names directly
5. **Stock management**: atomic increment/decrement
6. **Categories as separate table**: normalization
7. **Lookups by slug OR id**: dual primary key

## Next project
→ **weather-api** — adds: external API calls, caching, time-series data
