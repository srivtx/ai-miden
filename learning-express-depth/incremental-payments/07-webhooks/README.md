# 07 — Webhooks (Payments)

Stripe-style webhooks. Subscribe to payment events, get notified.

**What's new:**
- `webhook_endpoints` table: URL, secret, events
- `webhook_deliveries` table: every attempt
- HMAC signing for verification
- Per-event filtering (only get events you care about)

**Why webhooks?** When a payment succeeds, you want to know immediately. Without webhooks, you'd have to poll ("did anything happen yet?"). With webhooks, the system tells you.

**Why signing?** The receiver needs to verify the webhook actually came from you. HMAC signature in the `X-Signature` header. They compute the same signature with your shared secret. If it matches, it's real.

**Why per-event filtering?** You might only care about `charge.succeeded`, not `customer.created`. Subscribe only to what you need.

## Run
```bash
npm install && node server.js
```

```bash
# Register
curl -X POST http://localhost:3000/webhooks -H "Content-Type: application/json" \
  -d '{"url": "https://myapp.com/hook", "events": ["charge.succeeded", "charge.failed"]}'
# 201 { id, url, events, secret }

# Fire a test event
curl -X POST http://localhost:3000/test/fire -H "Content-Type: application/json" \
  -d '{"event": "charge.succeeded", "data": {"amount_cents": 5000}}'
# Server logs: [webhook] Would POST to https://myapp.com/hook: X-Signature: sha256=...

# See deliveries
curl http://localhost:3000/webhooks/wh_xxx/deliveries
```

## What we learned
- Webhook subscriptions
- HMAC signing for verification
- Per-event filtering
- Delivery log
- The "tell me when" pattern

## Next
**08-payouts** — money comes in. How does it get to your bank?
