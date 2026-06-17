# 07 — Reviews

Customers rate and review products. Only verified purchasers (bought + delivered). Aggregate ratings.

**What's new:**
- `reviews` table with rating, title, body, verified flag
- Verified purchase check: only users who actually bought the product can review
- One review per user per product (can update)
- Aggregate stats: average rating, distribution

**Why verified only?** Without it, anyone can post fake reviews. Competitors could give 1-stars. Users could game the system. Limiting reviews to verified buyers keeps it honest.

**The aggregate:** the most useful single number for a product. The distribution (5 stars: 100, 4 stars: 30, etc.) is also useful — average can be misleading.

## Run
```bash
npm install && node server.js
```

```bash
# Alice reviews the laptop (she bought it)
curl -X POST http://localhost:3000/products/1/reviews -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "rating": 5, "title": "Great laptop!", "body": "Fast and reliable"}'
# 201 (verified: true)

# Bob tries to review without buying
curl -X POST http://localhost:3000/products/1/reviews -H "Content-Type: application/json" \
  -d '{"user_id": "bob", "rating": 1, "body": "bad"}'
# 403 only verified purchasers

# Add more reviews
curl -X POST http://localhost:3000/products/1/reviews -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "rating": 4, "title": "good", "body": ""}'

# See the aggregate
curl http://localhost:3000/products/1/rating
# { count: 2, average: 4.5, distribution: { 5: 1, 4: 1, 3: 0, 2: 0, 1: 0 } }
```

## What this stage teaches
- Verified purchase pattern
- One review per user (upsert)
- Aggregations: average, count, distribution
- "trusted" data through validation

## Next
**08-coupons** — discount codes. Apply at checkout. Track usage.
