# 01 — Charges (Payments)

Charge a customer. Card number, amount, currency. Status tracking.

**What's here:**
- `charges` table with status (pending, succeeded, failed)
- `POST /charges` — create a charge
- Test card numbers: 4242... succeeds, 0002... declines, 9995... insufficient funds
- 402 Payment Required for declined cards
- Card validation (16 digits, last 4 stored)

**Why store last 4 only?** PCI compliance. Storing full card numbers is a security and legal nightmare. Last 4 is enough to display in the UI ("card ending in 4242").

**Why test cards?** Stripe-style test cards let you try success, decline, and insufficient funds scenarios without real money.

**Why 50 cents minimum?** Stripe and others have minimums. Below 50 cents, processing fees exceed the charge.

## Run
```bash
npm install && node server.js
```

```bash
# Successful charge
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{"customer_id": "cus_alice", "amount_cents": 5000, "card_number": "4242424242424242"}'
# 201 { id: "ch_xxx", status: "succeeded" }

# Declined
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{"customer_id": "cus_alice", "amount_cents": 5000, "card_number": "4000000000000002"}'
# 402 { error: "card_declined" }

# Insufficient funds
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{"customer_id": "cus_alice", "amount_cents": 5000, "card_number": "4000000000009995"}'
# 402 { error: "insufficient_funds" }
```

## What we learned
- Card processing simulation
- Decline codes
- 402 status for payment errors
- Last 4 storage (PCI compliance)
- Test card numbers

## Next
**02-customers** — save customer info. Cards, addresses, payment methods.
