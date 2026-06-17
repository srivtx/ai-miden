# 10 — Recommendations (final stage)

"Customers who bought X also bought Y." Two approaches: co-occurrence and popularity fallback.

**What's new:**
- `product_views` table: track what users look at
- Co-occurrence algorithm: find products that appear together in orders
- Popularity fallback: if no co-occurrence, return most popular
- `view_count` and `purchase_count` on products
- Trending endpoint
- Recently-viewed per user

**The algorithm:**
1. Find all orders containing the product
2. For each such order, find OTHER products in it
3. Count how often each other product appears
4. Sort by count
5. Return top N

**Why fallback to popularity?** New products have no co-occurrence data. For them, "most popular" is the best we can do.

## Run
```bash
npm install && node server.js
```

```bash
# Recommendations for the Laptop
curl http://localhost:3000/products/1/recommendations
# Returns: Laptop Bag (most co-occurring with Laptop)

# Recommendations for a new product with no orders
curl http://localhost:3000/products/999/recommendations
# Returns: most popular products

# Track a view
curl -X POST http://localhost:3000/track/view -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "product_id": 3}'

# Trending
curl http://localhost:3000/trending

# User's recently viewed
curl http://localhost:3000/users/alice/recently-viewed
```

## What this stage teaches
- Co-occurrence algorithm
- Popularity fallback
- View tracking
- Personalized recommendations
- SQL with JOIN + GROUP BY + ORDER BY

## 🎉 10 stages complete!

The full e-commerce app has:
- Products with categories ✓
- Shopping cart ✓
- Checkout with tax and shipping ✓
- Payments and refunds ✓
- Order lifecycle and tracking ✓
- Inventory management ✓
- Reviews and ratings ✓
- Coupons and discounts ✓
- Shipping zones and rates ✓
- Recommendations ✓

This is how Amazon, Shopify, and every e-commerce platform works. Same 10 patterns, different data.

## The 10 patterns from this app
1. **Catalog** — products, categories, search, filter
2. **Cart** — get-or-create, line items, total
3. **Checkout** — compute totals, persist order
4. **Payments** — intent, capture, refund
5. **Orders** — state machine, events
6. **Inventory** — reserve, commit, release
7. **Reviews** — verified purchases, aggregations
8. **Coupons** — validation, redemption
9. **Shipping** — zones, rates, tracking
10. **Recommendations** — co-occurrence, popularity

These 10 patterns are the building blocks of every e-commerce backend.
