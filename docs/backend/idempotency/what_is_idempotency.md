## Why it exists (THE PROBLEM)

A request comes in. The user posts a comment. Your server saves it. Before saving, the network glitches. The client doesn't know if the comment was saved. The client retries. Now you have the comment twice. Or, worse: the credit card was charged twice.

**Idempotency** = "doing the same thing twice has the same effect as doing it once." `POST /comments` is NOT idempotent (each call creates a new comment). `PUT /users/42` IS idempotent (setting the name to "Alice" twice has the same effect as once).

But what about `POST /payments`? It MUST be idempotent. You can't charge a card twice because of a network glitch. So you add an `Idempotency-Key` header. The client sends a unique key (UUID). The server remembers: "key X already used for this payment, return the same response." If the client retries with the same key, the server doesn't re-charge.

Stripe, PayPal, Square all use idempotency keys. The cost: store the key + response for some period (usually 24h). The benefit: safe retries.

## Definition (very simple)

**Idempotency key** = a unique string the client sends with a non-idempotent request. Server stores the key + result. Same key twice = same result.

**Idempotency window** = how long the server remembers the key. 24h is common. After that, the key can be reused (with a different result). Or the server returns 409 "key expired."

**Side effect** = a change to state. Charging a card is a side effect. Sending an email is a side effect. Updating a DB row is a side effect. Non-idempotent endpoints cause side effects.

**HTTP methods that should be idempotent by default**: `GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`. Methods that are NOT idempotent: `POST`, `PATCH` (debatable).

**At-most-once vs at-least-once**: at-most-once = "the operation might not happen, but it won't happen twice." at-least-once = "the operation will happen, might happen twice." Idempotency gives you effectively-once.

## Real-life analogy

**Without idempotency = the photocopier without a paper jam detector.** You press "copy" twice, you get two copies. Even if the first was already printing. Result: extra copies you didn't want.

**With idempotency = the photocopier with a "job ID" feature.** You press "copy" with job ID "abc123." Press again with same job ID. Photocopier says "I already did that, here's the same output." One copy, no matter how many times you press.

**In banking**: every transaction has a transaction ID. If the network drops, the bank sends the same transaction ID. The bank says "I already processed this, here's the receipt." No double charge.

## Tiny numeric example

```http
POST /payments
Idempotency-Key: 7c4e8a3b-2f1d-4e6a-9b8c-1a2b3c4d5e6f
Content-Type: application/json

{ "amount": 5000, "currency": "USD", "card": "tok_visa" }
```

First call:
- Server: check if key `7c4e8a3b-...` exists. No.
- Process payment. Return `{ id: "pay_42", status: "succeeded" }`.
- Store: `key: 7c4e8a3b-..., response: { id: "pay_42", status: "succeeded" }`

Network glitch. Client retries with same key.

Second call:
- Server: check if key `7c4e8a3b-...` exists. Yes.
- Return stored response: `{ id: "pay_42", status: "succeeded" }`.
- NO new payment. NO new charge.

## Common confusion (5+ bullet points)

1. **"PUT is always idempotent, POST is never."** Mostly, but not always. `PUT /counter` (incrementing a counter) is NOT idempotent — it has different effects each time. Idempotency is about the END STATE, not the HTTP method.

2. **"I'll just make my server more reliable so retries aren't needed."** Networks are inherently unreliable. TCP can drop a packet. The cloud can have a 30s hiccup. The client can crash and retry. You need idempotency regardless of server reliability.

3. **"The client can generate the idempotency key from the request."** If you hash the request body, then a different body gives a different key. But two requests with the same body SHOULD be idempotent. Use a UUID the client controls. If the client doesn't send a key, generate one and return it in the response.

4. **"I'll store idempotency keys forever."** Storage costs add up. 100M requests/day × 1KB per key × 365 days = 36TB. Store for 24h. Some compliance: 7 days. After that, the key is forgotten.

5. **"Idempotency conflicts are easy."** If the same key is used with a DIFFERENT request body, that's a conflict. Server returns 409. The client probably has a bug. Or two different users generated the same key (UUID collision is rare but possible).

6. **"Idempotency is just for payments."** It's for any state-changing operation: `POST /users`, `POST /orders`, `POST /comments`, `POST /messages`, `DELETE /users/42`. If a retry could cause a problem, you need an idempotency key.

## Key properties

| Property | Idempotent | Not idempotent |
|---|---|---|
| Repeat call | Same effect | Different effect |
| Example | `PUT /users/42 {name: "Alice"}` | `POST /users {name: "Alice"}` |
| Safe to retry | Yes | Only with idempotency key |
| HTTP method | GET, PUT, DELETE | POST |

## Implementing idempotency (simple pattern)

```js
// Middleware
function idempotencyMiddleware() {
  return async (req, res, next) => {
    const key = req.headers['idempotency-key'];
    if (!key) return next(); // No key, normal handling
    // Check if key already used
    const existing = db.prepare('SELECT response FROM idempotency WHERE key = ? AND created_at > ?').get(key, Date.now() - 24*60*60*1000);
    if (existing) return res.json(existing.response);
    // Capture response
    const originalJson = res.json.bind(res);
    res.json = (body) => {
      db.prepare('INSERT INTO idempotency (key, response, created_at) VALUES (?, ?, ?)').run(key, JSON.stringify(body), Date.now());
      return originalJson(body);
    };
    next();
  };
}
```

In production, use a fast KV store (Redis) for the key cache, not a SQL DB.

## Connection to our projects

For our 73 apps, add `Idempotency-Key` support to:
- `payment-service` (level3/advanced)
- `subscription-billing` (level2)
- `order-service` (level2 ecommerce)
- Any service that creates resources (POST /users, POST /orders)

Use a middleware. Store the key + response in Redis with a 24h TTL. Match against the key, return cached response if hit. The `idempotency-demo/` project shows the pattern.

For CortexCode and logogen: `POST /generate` could charge credits. With idempotency, retries are safe. `Idempotency-Key: <uuid>` from the client. Server: "already generated, here's the same code."
