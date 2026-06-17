# 10 — Fraud (Payments, final stage)

Detect and prevent fraudulent charges. Risk scoring based on multiple signals.

**What's new:**
- AVS check (Address Verification System)
- CVV check
- Velocity (too many charges from one user or IP)
- Amount check (unusual amounts)
- Country check (high-risk regions)
- Risk score 0-100
- Auto-block at 75+, review at 40+

**Why risk scoring?** Every signal is a hint, not proof. AVS mismatch alone might be a typo. High velocity + high amount + foreign IP = definitely fraud. Combine signals: 10 + 25 + 50 = 85, block.

**Why AVS, CVV?** These are the basic checks the card networks do. AVS: does the billing zip match the bank's records? CVV: do they have the security code? Both add friction to fraud.

**Why velocity checks?** Fraudsters test stolen cards with small charges first. If 5 charges in 5 minutes, they're testing. Block before they get to a real purchase.

**Why risk-based instead of rules?** A new card with no history + first big purchase = suspicious. A regular customer buying the same thing every month = not suspicious. Risk scoring captures this nuance.

## Run
```bash
npm install && node server.js
```

```bash
# Low risk: regular purchase
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_alice",
    "amount_cents": 5000,
    "card": {"number": "4242424242424242", "cvv": "123", "zip": "12345"},
    "ip": "1.2.3.4",
    "country": "US"
  }'
# 201 { risk_score: 0, status: "succeeded" }

# High risk: missing CVV, high amount, no zip
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_new",
    "amount_cents": 200000,
    "card": {"number": "4242424242424242"},
    "ip": "1.2.3.4",
    "country": "US"
  }'
# 201 { risk_score: 35, status: "succeeded" }

# Very high: bad country + high amount + no AVS
curl -X POST http://localhost:3000/charges -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_new",
    "amount_cents": 500000,
    "card": {"number": "4242424242424242"},
    "ip": "1.2.3.4",
    "country": "XX"
  }'
# 201 { risk_score: 75, status: "blocked" }

# See flagged charges
curl http://localhost:3000/admin/charges/flagged
```

## What we learned
- Risk scoring (combine signals)
- AVS, CVV, velocity, amount, country checks
- Auto-block vs review thresholds
- The "many signals" approach to fraud

## 🎉 10 stages complete!

The full payments system has:
- Charges ✓
- Customers ✓
- Subscriptions ✓
- Invoices ✓
- Refunds ✓
- Disputes ✓
- Webhooks ✓
- Payouts ✓
- Tax ✓
- Fraud ✓

This is how Stripe, PayPal, Square, Adyen all work. Same 10 patterns, different code.

## The 10 patterns
1. **Charges** — card processing, test cards
2. **Customers** — saved payment methods, brand detection
3. **Subscriptions** — recurring billing, periods
4. **Invoices** — line items, tax, auto-numbering
5. **Refunds** — full + partial, running total
6. **Disputes** — chargebacks, evidence, win/lose
7. **Webhooks** — event delivery, HMAC signing
8. **Payouts** — balance to bank, 2-day arrival
9. **Tax** — per-region rates
10. **Fraud** — risk scoring, multi-signal

These 10 patterns are the building blocks of every payment system.
