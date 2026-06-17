# 05 — Refunds (Payments)

Refund a charge. Full or partial. Track the reason.

**What's new:**
- `refunds` table: charge_id, amount, reason, status
- `refunded_cents` on charges (running total)
- Charge status: succeeded → partially_refunded → refunded
- Default reason: `requested_by_customer`

**Why partial refunds?** You bought something for $100. Half the order arrived broken. The seller refunds $50, not the whole thing. Partial refunds let you give back the right amount.

**Why track refunded_cents?** You can refund multiple times. The total refunded goes up each time. Once it equals the charge amount, the status becomes `refunded`.

**Why a reason?** Compliance, analytics, fraud detection. "Customer requested" is the most common. "Duplicate charge" matters. "Fraud" triggers an investigation.

## Run
```bash
npm install && node server.js
```

```bash
# Full refund
curl -X POST http://localhost:3000/refunds -H "Content-Type: application/json" \
  -d '{"charge_id": "ch_seed", "reason": "requested_by_customer"}'
# 201 { amount_cents: 10000, new_charge_status: "refunded" }

# Re-create the charge and partial refund
curl -X POST http://localhost:3000/refunds -H "Content-Type: application/json" \
  -d '{"charge_id": "ch_seed", "amount_cents": 3000, "reason": "partial"}'
# 422 refund exceeds remaining (because the seed was already refunded)

# Check the charge
curl http://localhost:3000/charges/ch_seed
# { amount_cents: 10000, refunded_cents: 10000, status: "refunded", refunds: [...] }
```

## What we learned
- Refund patterns (full + partial)
- Running total of refunds
- Charge status transitions
- Reason tracking

## Next
**06-disputes** — when customers dispute a charge. The bank or card network gets involved.
