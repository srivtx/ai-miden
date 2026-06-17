# 01 — Products

The foundation. Products with categories, search, filter, sort.

**What's here:**
- Categories and products
- Search by name, description, SKU
- Filter by category, price range, in-stock
- Sort by created_at, price, name
- Stock management (delta operations)

**Schema:**
```
categories:  id, name, slug
products:    id, sku, name, description, price_cents, category_id, stock
```

**Why `price_cents`?** Never store money as floats. Always as integer cents. `(price_cents / 100).toFixed(2)` for display.

**Why SKU?** A unique identifier for inventory. Manufacturers have SKUs. We can sync with suppliers by SKU.

## Run
```bash
npm install && node server.js
```

```bash
# Create a category
curl -X POST http://localhost:3000/categories -H "Content-Type: application/json" -d '{"name": "Electronics", "slug": "electronics"}'

# Add products
curl -X POST http://localhost:3000/products -H "Content-Type: application/json" \
  -d '{"sku": "LP-001", "name": "Laptop", "description": "Powerful laptop", "price_cents": 99900, "category_id": 1, "stock": 50}'

# Search
curl 'http://localhost:3000/products?q=laptop'

# Filter
curl 'http://localhost:3000/products?category=electronics&min_price=50000'

# Adjust stock
curl -X PATCH http://localhost:3000/products/1/stock -H "Content-Type: application/json" -d '{"delta": -3}'
# 3 sold, stock went from 50 to 47
```

## What this stage teaches
- Product/category schema
- Money in cents
- Stock management (delta)
- Search/filter/sort

## Next
**02-cart** — add a shopping cart. Items in the cart, add/remove, total.
