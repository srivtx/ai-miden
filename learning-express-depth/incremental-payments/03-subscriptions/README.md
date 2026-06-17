# 03 — Subscriptions (Payments)

Recurring charges. Monthly or yearly. Auto-bill.

**What's new:**
- `subscriptions` table: customer, plan, amount, interval, current_period
- `invoices` table: linked to subscriptions
- `POST /subscriptions` — create
- `DELETE /subscriptions/:id` — cancel
- `POST /subscriptions/:id/renew` — bill the next period
- Period-based: monthly (30 days) or yearly (365 days)

**Why subscriptions?** SaaS. Netflix. Spotify. Anything where you pay regularly for ongoing access. Without subscriptions, every customer would have to remember to pay every month.

**Why intervals?** Different plans have different cycles. Monthly is most common. Yearly often has a discount.

**The cron:** every day, a job runs and renews subscriptions whose `current_period_end` is in the past. The `POST /renew` endpoint simulates one renewal.

## Run
```bash
npm install && node server.js
```

```bash
# Create
curl -X POST http://localhost:3000/subscriptions -H "Content-Type: application/json" \
  -d '{"customer_id": "cus_alice", "plan": "pro", "amount_cents": 1999, "interval": "monthly"}'
# 201

# Cancel
curl -X DELETE http://localhost:3000/subscriptions/sub_xxx
# { cancelled: true }

# Renew (manual for demo)
curl -X POST http://localhost:3000/subscriptions/sub_xxx/renew
# { renewed: true, invoice_id: "inv_..." }

# See the subscription
curl http://localhost:3000/subscriptions/sub_xxx
# { ... invoices: [...] }
```

## What we learned
- Subscription state machine (active, cancelled)
- Period-based billing
- Auto-renewal via cron
- Invoices linked to subscriptions

## Next
**04-invoices** — generate invoices for one-off purchases. PDF, line items, totals.
