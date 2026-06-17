# 04 — Payments

Simulated payment gateway. Charge, refund, status.

**What's new:**
- `payments` table: id, order_id, amount, status, method
- Simulated gateway (`processPayment`) — in real life this is Stripe/PayPal
- `POST /orders/:id/pay` charges the order
- `POST /payments/:id/refund` refunds a payment
- Status flow: `pending` → `paid` (or `failed`)
- 402 Payment Required for declined cards
- 409 Conflict for already-paid or cancelled orders

**Why a separate `payments` table?** An order can have multiple payment attempts. The first might fail, the second might succeed. We want the history.

**Why simulate?** In a real app, you'd call Stripe. We're simulating so the demo runs offline. Replace `processPayment` with `stripe.charges.create()`.

## Run
```bash
npm install && node server.js
```

```bash
# Pay an order (success)
curl -X POST http://localhost:3000/orders/ord_001/pay -H "Content-Type: application/json" \
  -d '{"card_number": "4242424242424242"}'
# { order_id: "ord_001", status: "paid", payment_id: "pay_..." }

# Pay again (fails, already paid)
curl -X POST http://localhost:3000/orders/ord_001/pay -H "Content-Type: application/json" \
  -d '{"card_number": "4242424242424242"}'
# 409 already paid

# Try a card that declines
curl -X POST http://localhost:3000/orders/ord_002/pay -H "Content-Type: application/json" \
  -d '{"card_number": "4242424242420000"}'
# 402 card_declined

# Refund
curl -X POST http://localhost:3000/payments/pay_xxx/refund
# { status: "refunded" }

# See payment history
curl http://localhost:3000/orders/ord_001/payments
```

## What this stage teaches
- Payment intent and capture
- Multiple payment attempts
- Refund flow
- 402 status code

## Next
**05-orders** — full order management. Status transitions (pending → paid → shipped → delivered), tracking.
