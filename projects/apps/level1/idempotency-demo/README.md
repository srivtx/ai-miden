# Idempotency Demo — Safe retries with idempotency keys

When a network glitches and a client retries, you don't want to double-charge. With `Idempotency-Key` header, the server remembers: "I already processed this key, return the same response."

## Endpoints
```
POST /charge  { amount, currency, card }     # payment, with idempotency
POST /users   { name, email }                # user creation, with idempotency
GET /admin/idempotency                       # all stored keys
GET /admin/charges                           # all charges
```

## Try
```bash
# First call: creates charge
curl -X POST http://localhost:3000/charge \
  -H "Idempotency-Key: 7c4e8a3b-2f1d-4e6a-9b8c-1a2b3c4d5e6f" \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "currency": "USD", "card": "tok_visa"}'
# Response: { id: "ch_abc...", status: "succeeded", ... }
# Header: Idempotent-Replay: false

# Same call again (simulating retry): returns same charge
# Response: { id: "ch_abc...", status: "succeeded", ... }
# Header: Idempotent-Replay: true

# Same key, different body: 409 Conflict
curl -X POST http://localhost:3000/charge \
  -H "Idempotency-Key: 7c4e8a3b-2f1d-4e6a-9b8c-1a2b3c4d5e6f" \
  -H "Content-Type: application/json" \
  -d '{"amount": 9999, "currency": "USD", "card": "tok_visa"}'
# Response: 409 { error: "Idempotency key reused with different request body" }
```

## What this teaches
1. **Why idempotency keys**: safe retries for non-idempotent endpoints
2. **TTL**: keys expire after 24h (configurable)
3. **Conflict detection**: same key + different body = 409
4. **Idempotent-Replay header**: tells the client this was a cached response
5. **Storage**: in this demo SQLite; in production Redis
