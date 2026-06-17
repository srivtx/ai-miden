# 03 — Checkout

Turn the cart into an order. Calculate subtotal, tax, shipping, total. Clear the cart.

**What's new:**
- `orders` table: id, user_id, totals, status, shipping_address
- `order_items` table: line items
- `POST /checkout` creates an order from the cart
- Tax: 8% of subtotal
- Shipping: $9.99 flat, or free if subtotal >= $50
- Cart is cleared after checkout

**The flow:**
1. User has items in their cart
2. User clicks "checkout"
3. We calculate subtotal, tax, shipping, total
4. We create an order
5. We save the line items
6. We clear the cart
7. We return the order

**Status:** `pending` — the order exists but hasn't been paid yet. Next stage: payments.

## Run
```bash
npm install && node server.js
```

```bash
# Add to cart
curl -X POST http://localhost:3000/cart/items -H "Content-Type: application/json" \
  -H "X-User-Id: alice" -d '{"product_id": 1, "quantity": 1}'

# Checkout
curl -X POST http://localhost:3000/checkout -H "Content-Type: application/json" \
  -H "X-User-Id: alice" \
  -d '{"shipping_address": "123 Main St"}'
# 201 { order_id: "ord_...", total: "1078.91", ... }

# See the order
curl http://localhost:3000/orders/ord_...
```

## What this stage teaches
- The order lifecycle (cart → order)
- Computed totals (subtotal + tax + shipping)
- Free shipping threshold
- Order persistence

## Next
**04-payments** — accept a payment, mark the order as paid, simulate the gateway.
