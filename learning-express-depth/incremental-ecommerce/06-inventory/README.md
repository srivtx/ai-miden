# 06 — Inventory

Track stock. Reserve on order, release on cancel, commit on pay. Don't oversell.

**What's new:**
- `stock` and `reserved` columns on products
- `reserveStock()` — atomic check-and-decrement
- `releaseStock()` — give it back (on cancel)
- `commitStock()` — order paid, reserved becomes sold
- Rollback if any item is short on stock
- All reservations happen at order time, not pay time

**Why reserve?** Two users click "buy" on the last item. If we don't reserve, both think they got it. With reservation, only the first gets it. The second sees "out of stock."

**The flow:**
1. Order placed → stock reserved (decremented from available, added to reserved)
2. Order paid → reserved becomes sold (just removed from reserved)
3. Order cancelled → stock released (added back to available, removed from reserved)

## Run
```bash
npm install && node server.js
```

```bash
# See stock
curl http://localhost:3000/products
# Laptop: stock=10, reserved=0
# Phone:  stock=5,  reserved=0

# Try to order 6 phones (only 5 in stock)
curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "items": [{"product_id": 2, "quantity": 6}]}'
# 409 insufficient stock

# Order 3 phones
curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "items": [{"product_id": 2, "quantity": 3}]}'
# 201
# Phone: stock=2, reserved=3

# Cancel the order
curl -X POST http://localhost:3000/orders/ord_xxx/cancel
# Phone: stock=5, reserved=0 (back to original)

# Place a new order, pay it
curl -X POST http://localhost:3000/orders -H "Content-Type: application/json" \
  -d '{"user_id": "bob", "items": [{"product_id": 1, "quantity": 2}]}'
curl -X POST http://localhost:3000/orders/ord_yyy/pay
# Laptop: stock=8, reserved=0 (paid = sold)
```

## What this stage teaches
- Inventory state (available, reserved, sold)
- Atomic operations (check + decrement in one query)
- Rollback on partial failure
- Reserve vs commit vs release

## Next
**07-reviews** — let customers rate and review products. Aggregate ratings.
