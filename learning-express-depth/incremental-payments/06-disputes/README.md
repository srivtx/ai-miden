# 06 — Disputes (Payments)

Customer disputes a charge with their bank. We track the dispute, submit evidence, win or lose.

**What's new:**
- `disputes` table: charge_id, reason, status, evidence_due_by
- 7-day deadline to respond
- `dispute_evidence` table: proof we provide
- Status flow: needs_response → under_review → won/lost

**Why disputes happen:** Customer calls their bank and says "I didn't make this charge." Bank reverses it. You have to provide evidence (receipt, shipping tracking, etc.) to win it back.

**Why 7 days?** Card networks (Visa, Mastercard) give a window to respond. Miss it and you automatically lose.

**The state machine:**
- `needs_response` — you must submit evidence
- `under_review` — bank is deciding
- `won` — you keep the money
- `lost` — you refund the money

**Why track evidence?** The bank needs proof: order confirmation, shipping receipt, customer communication. We store it all in `dispute_evidence`.

## Run
```bash
npm install && node server.js
```

```bash
# Open a dispute
curl -X POST http://localhost:3000/disputes -H "Content-Type: application/json" \
  -d '{"charge_id": "ch_seed", "reason": "fraudulent", "amount_cents": 10000}'
# 201 { status: "needs_response", evidence_due_by: "..." }

# Submit evidence
curl -X POST http://localhost:3000/disputes/dp_xxx/evidence -H "Content-Type: application/json" \
  -d '{"type": "shipping_tracking", "content": "Tracking #1Z999AA10123456784"}'

# Mark as submitted
curl -X POST http://localhost:3000/disputes/dp_xxx/submit
# { submitted: true }

# Resolve
curl -X POST http://localhost:3000/disputes/dp_xxx/resolve -H "Content-Type: application/json" \
  -d '{"outcome": "won"}'
# { status: "won" }
```

## What we learned
- Dispute state machine
- Evidence collection
- Time-bound responses (7 days)
- Won/lost resolution

## Next
**07-webhooks** — Stripe-style webhooks for payment events. Notify your system.
