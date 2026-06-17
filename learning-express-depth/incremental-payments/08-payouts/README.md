# 08 — Payouts (Payments)

Get your money. Stripe-style: balance → payout → bank account.

**What's new:**
- `balance` table: available + pending
- `payouts` table: amount, bank_account, status, arrival_date
- Payout flow: pending → in_transit → paid
- 2 business days arrival
- Minimum payout ($1)

**Why two balances?** "Available" is money you can pay out. "Pending" is money from charges that haven't fully cleared (cards take 1-7 days to clear). You can't pay out pending money yet.

**Why 2 days?** Bank transfers. ACH takes 1-3 business days. Wire is faster but more expensive. Stripe's default is 2 days.

**Why a minimum?** Bank fees per transfer. Below $1, the fee eats the payout. $1 minimum is standard.

## Run
```bash
npm install && node server.js
```

```bash
# Check balance
curl http://localhost:3000/balance
# { available_cents: 100000, pending_cents: 25000 }

# Create a payout
curl -X POST http://localhost:3000/payouts -H "Content-Type: application/json" \
  -d '{"amount_cents": 50000, "bank_account": "acct_xxx"}'
# 201 { status: "in_transit", arrival_date: "..." }

# Too much
curl -X POST http://localhost:3000/payouts -H "Content-Type: application/json" \
  -d '{"amount_cents": 200000, "bank_account": "acct_xxx"}'
# 422 insufficient balance

# List payouts
curl http://localhost:3000/payouts

# Mark as paid
curl -X POST http://localhost:3000/payouts/po_xxx/paid
```

## What we learned
- Balance tracking (available vs pending)
- Payout lifecycle
- Bank transfer timing
- Minimum payout
- The flow from charge to bank

## Next
**09-tax** — calculate tax correctly. Sales tax, VAT, GST. Per region.
