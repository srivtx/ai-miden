# The Connect

> *"The server pushes events. Now we need payments, tests, Docker, CI/CD, observability, and microservices."*

This project added webhooks. The pain of "the other service has to poll" is solved. The server can push events to external services. The receiver can verify the signature. Failed deliveries are retried.

The next 6 projects complete Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After these, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- Webhook registration (URL, events, secret)
- HMAC-SHA256 signing
- Queue delivery with retries
- Active/inactive flag
- Firing from handlers (e.g., post creation)

## What Doesn't Work

### 1. No payment

No Stripe integration. We can't charge for premium features.

**The pain**: Payment. Project 35.

### 2. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 3. No Docker

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 4. No CI/CD

We can't run tests automatically on every commit.

**The pain**: Pipeline. Project 38.

### 5. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 6. No microservices

One big monolith.

**The pain**: Microservices. Project 40.

### 7. No replay protection

A leaked signature can be replayed.

**The pain**: Replay protection. Out of scope.

### 8. No idempotency keys

A retried event might be processed twice.

**The pain**: Idempotency. Out of scope.

### 9. No webhook logs

We log to the application log, but no dedicated webhook log.

**The pain**: Webhook logs. Out of scope.

### 10. No encryption at rest

Webhook secrets are stored in plaintext.

**The pain**: Encryption. Out of scope (use KMS in production).

---

## What This Project Forbids Us From Doing

This server can:

- Push events to external services
- Sign payloads with HMAC
- Deliver via a queue with retries
- Support per-webhook events and secrets

It cannot:

- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Prevent replay attacks
- Guarantee exactly-once delivery
- Log every webhook delivery
- Encrypt webhook secrets at rest

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |

Project 35 is the natural next step. We have webhooks. Now we need to charge for premium features.

---

## What You Should Do Now

1. **Read the code.** Notice the `webhooks` table, the `fireWebhook` function, the HMAC signing. The HTTP handlers are extended.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Start a webhook receiver.** Register a webhook. Create a post. See the receiver log the request.
4. **Verify the signature.** Add receiver-side verification.
5. **When you are ready**, move to [Project 35: Payment](../35-payment/).
6. **If anything is unclear**, do not proceed. Webhooks are the foundation of outbound push. They must be solid.

---

## A Note on the Bigger Picture

You now have a server that can push events to other services. The integration is real-time, secure, and reliable.

From here, the path diverges into the final 6 projects of Phase 6 (Production):

- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server pushes events. The path continues.
