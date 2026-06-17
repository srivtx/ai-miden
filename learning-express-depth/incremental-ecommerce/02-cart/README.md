# 02 — Cart

Add a shopping cart. Each user has a cart with line items.

**What's new:**
- `carts` and `cart_items` tables
- `X-User-Id` header identifies the user
- Add, update quantity, remove, clear
- Total is computed from line items
- Stock check before adding

**Why a separate cart table?** A user can have items in their cart without an order. The cart is "intent." The order is "commitment."

**Why "get or create"?** First time the user looks at their cart, there's no row. We create one on demand.

## Run
```bash
npm install && node server.js
```

```bash
# See your cart (empty)
curl -H "X-User-Id: alice" http://localhost:3000/cart

# Add items
curl -X POST http://localhost:3000/cart/items -H "Content-Type: application/json" \
  -H "X-User-Id: alice" -d '{"product_id": 1, "quantity": 2}'

curl -X POST http://localhost:3000/cart/items -H "Content-Type: application/json" \
  -H "X-User-Id: alice" -d '{"product_id": 2, "quantity": 1}'

# See the cart with total
curl -H "X-User-Id: alice" http://localhost:3000/cart
# { items: [...], total_cents: 249700, total: "2497.00" }

# Update quantity
curl -X PATCH http://localhost:3000/cart/items/1 -H "Content-Type: application/json" \
  -H "X-User-Id: alice" -d '{"quantity": 1}'

# Remove
curl -X DELETE -H "X-User-Id: alice" http://localhost:3000/cart/items/2

# Clear
curl -X DELETE -H "X-User-Id: alice" http://localhost:3000/cart
```

## What this stage teaches
- One-to-many (cart → items)
- Get-or-create pattern
- Computed totals
- Stock validation

## Next
**03-checkout** — turn the cart into an order. Calculate tax, shipping, total.
