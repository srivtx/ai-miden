# The Decisions

> *"Add the job. Return. The worker picks it up. The user doesn't wait."*

## Decision 1: BullMQ and not Bee-Queue, Kue, or agenda

**Alternatives**:
- **Bee-Queue** — simpler, less featureful
- **Kue** — older, less maintained
- **agenda** — MongoDB-backed
- **RabbitMQ** — separate service, more complex
- **AWS SQS** — AWS-specific

**Why BullMQ: Modern, actively maintained, Redis-backed (we already have Redis), featureful (retries, backoff, priority, delayed jobs).

**Trade-off**: Lock-in to BullMQ's API. We accept it.

## Decision 2: Redis and not RabbitMQ / SQS

**Alternative**: RabbitMQ, SQS.

**Why Redis: Simpler. We already have Redis. For our scale, Redis is enough.

**Trade-off**: For high scale, use RabbitMQ or SQS. They have better queue semantics, dead letter queues, etc.

## Decision 3: Worker in the same process

**Alternative**: Worker in a separate process.

**Why same process: Simpler. One deployment. No extra process to manage.

**Trade-off**: For scale, run the worker in a separate process. The web server can scale independently of the worker.

## Decision 4: 3 retries with exponential backoff

**Alternative**: No retries. Or more retries.

**Why 3: A reasonable default. Most failures are transient (SMTP timeout, network glitch). 3 retries with backoff covers most cases.

**Trade-off**: A persistent failure (SMTP server down) is retried 3 times before giving up. We accept this.

## Decision 5: Inline worker (not a separate process)

We start the worker in the same file as the server.

**Why: Simpler. One process to start. The worker and the server share the same Redis.

**Trade-off**: In a real app, run the worker separately. The web server can crash and the worker keeps processing. Or vice versa.

## Decision 6: No dead letter queue

BullMQ has a "failed" set for jobs that fail after all retries. We don't customize this.

**Why: Out of scope. We log the failures. An admin can inspect the failed set in the BullMQ UI.

**Trade-off**: A persistent failure might go unnoticed. For critical jobs, add alerting.

## Decision 7: No job priority

BullMQ supports priorities. We don't use them.

**Why: Out of scope. Our queue is small. All jobs are equally important.

**Trade-off**: A high-priority job (e.g., password reset email) is queued behind a low-priority job (e.g., digest email). For most apps, this is fine.

## Decision 8: No job dependencies

BullMQ supports "do B after A finishes." We don't use them.

**Why: Out of scope. Our jobs are independent.

**Trade-off**: For complex workflows, you'd use dependencies or a workflow engine.

## Decision 9: No delayed jobs

BullMQ supports delayed jobs (e.g., send in 1 hour). We don't use them.

**Why: Out of scope. We process jobs immediately.

**Trade-off**: For scheduled work, use cron (project 25) or BullMQ's delayed jobs.

## Decision 10: Same handler pattern

The worker is just an async function. We use the same error handling as handlers.

**Why: Consistency. The same `try/catch` patterns work.

**Trade-off**: None.

---

## What We Did Not Decide

- **Separate worker process** — out of scope
- **Dead letter queue customization** — out of scope
- **Job priority** — out of scope
- **Job dependencies** — out of scope
- **Delayed jobs** — out of scope
- **Multiple worker types** — out of scope
- **BullMQ UI** — out of scope (separate project)
- **Idempotency checks** — out of scope
- **Job progress tracking** — out of scope
- **Worker scaling** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Has a Queue

For 25 projects, slow work was inline. The user waited for the email. The user waited for the image processing. The user waited for the report.

Now the server has a queue. Slow work is moved off the request. The user gets a fast response. The work is done reliably in the background.

This is the foundation of *every* production app. Queues are non-negotiable for any non-trivial work. The patterns (BullMQ, Redis-backed, retries, backoff) are universal.

The next 14 projects will assume queues exist. The path diverges:

- **Transactions** (project 27): atomic multi-write operations
- **WebSocket** (project 28): bidirectional channel
- **SSE** (project 29): server-push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server has a queue. The path continues.
