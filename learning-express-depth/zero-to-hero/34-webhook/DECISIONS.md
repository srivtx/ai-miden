# The Decisions

> *"Register a URL. Sign the payload. POST. Retry on failure."*

## Decision 1: Webhooks and not polling

**Alternative**: Provide a "list events" API. The receiver polls.

**Why webhooks: Real-time. Efficient. Standard. Most modern APIs use them.

**Trade-off**: The receiver must implement an HTTP endpoint. We accept this.

## Decision 2: HMAC-SHA256 and not other algorithms

**Alternative**: HMAC-SHA512, RSA signatures, etc.

**Why HMAC-SHA256: Standard. Widely supported. Fast. Sufficient security.

**Trade-off**: For higher security, use HMAC-SHA512. We use SHA256.

## Decision 3: Per-webhook secret

**Alternative**: One global secret.

**Why per-webhook: Compromise isolation. If one webhook's secret leaks, only that webhook is affected.

**Trade-off**: The user has to manage multiple secrets. We accept this.

## Decision 4: Queue delivery (not inline)

**Alternative**: Deliver inline (in the request handler).

**Why queue: Reliability. If the receiver is down, the job is retried. If the server crashes, the job is persisted in Redis.

**Trade-off**: More complex. We accept it.

## Decision 5: 5 retries with exponential backoff

**Alternative**: No retries. Or more retries.

**Why 5: A reasonable default. Most failures are transient. After 5 retries, give up (manual review).

**Trade-off**: A persistent failure is lost. We accept this.

## Decision 6: Secret returned only once

The secret is returned in the `POST /webhooks` response. The user must store it. We don't store it in plaintext (we do, actually, because we need it to sign). But we could encrypt it.

**Alternative**: Encrypt the secret at rest.

**Why not: For this project, we store it as-is. In production, you'd encrypt with a KMS.

**Trade-off**: If the database is leaked, all webhook secrets are leaked. We accept this for now.

## Decision 7: No replay protection

**Alternative**: Add a timestamp to the payload. The receiver rejects signatures older than 5 minutes.

**Why no: Out of scope. For high-security apps, you'd add this.

**Trade-off**: A leaked signature can be replayed. We accept this.

## Decision 8: No idempotency keys

**Alternative**: Add an event ID. The receiver deduplicates.

**Why no: Out of scope. The receiver can use the timestamp + payload to dedupe.

**Trade-off**: A retried event might be processed twice. We accept this.

## Decision 9: No webhook logs

**Alternative**: Log every delivery attempt (success, failure, retry).

**Why no: Out of scope. The queue worker logs to the application log. For a dedicated webhook log, you'd add a `webhook_deliveries` table.

**Trade-off**: Hard to debug webhook issues. We accept this.

## Decision 10: Active/inactive flag

The `webhooks` table has an `active` column. The user can deactivate a webhook (instead of deleting it).

**Why: Useful for debugging. "Is the webhook active?" is a common question.

**Trade-off**: Slightly more complex. We accept it.

---

## What We Did Not Decide

- **Replay protection** — out of scope
- **Idempotency keys** — out of scope
- **Webhook logs** — out of scope
- **Per-event URLs** — out of scope
- **Rate limiting on webhooks** — out of scope
- **Encryption at rest** — out of scope (use KMS in production)
- **Multiple secrets per webhook (rotation)** — out of scope
- **Subscription filters (advanced)** — out of scope
- **Per-receiver retry policies** — out of scope
- **Webhook marketplace** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Pushes Events

For 33 projects, the server could only *receive* events (HTTP requests). It couldn't *push* events to other services.

Now the server pushes. Webhooks are registered. Events are signed with HMAC. Delivery is via a queue with retries. The receiver can verify the signature.

This is the foundation of *outbound push*. From here, every project that needs to notify external services can use webhooks. The patterns (HMAC signing, queue delivery, retries) are universal.

The next 6 projects will assume webhooks exist. The path diverges:

- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server pushes events. The path continues.
