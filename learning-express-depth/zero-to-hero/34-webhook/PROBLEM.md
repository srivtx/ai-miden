# The Problem

> *"Don't make your customers poll. Tell them when something happens."*

## Why Polling Is Bad

Imagine you're building a Slack integration for Cove. You want to notify a Slack channel when a new post is created in a workspace. Two options:

**Option 1: Polling.** Slack asks Cove every 30 seconds: "any new posts?". Cove checks and responds. Most responses are "no." Wasteful and laggy.

**Option 2: Webhook.** Cove tells Slack: "here's my URL. Send me a POST when a new post is created." Slack registers the URL. When a new post is created, Cove POSTs to Slack. Slack receives it in real time.

Webhooks are how modern APIs integrate. Stripe, GitHub, Slack, Twilio — all use webhooks.

## What Pain Is This Solving?

Webhooks solve the *push* problem:

- **Real-time**: events are delivered in milliseconds, not on a poll interval.
- **Efficient**: no wasted requests. The sender only sends when there's something to send.
- **Decoupled**: the sender doesn't need to know how the receiver works. Just POST JSON.
- **Standard**: HTTP POST + JSON is universal. Any language can receive.

Without webhooks:
- The receiver has to poll (wasteful, laggy)
- The sender has to provide a "list events" API (more code, more attack surface)

With webhooks:
- The sender pushes events to registered URLs
- The receiver verifies the signature and processes the event
- Both sides are loosely coupled

## The Deeper Problem: Trust

When you POST to a URL, how does the receiver know it's from you (and not an attacker)?

The answer: **HMAC signing**. The sender signs the payload with a shared secret. The receiver verifies the signature.

```
Sender:  payload = { event: 'post.created', data: {...} }
         signature = HMAC-SHA256(secret, payload)
         POST: { body: payload, headers: { 'X-Signature': signature } }

Receiver: signature = request.headers['X-Signature']
         expected = HMAC-SHA256(secret, request.body)
         if signature === expected: process the event
         else: reject (it's not from us)
```

The receiver has the same `secret`. They compute the expected signature. If it matches, the event is from us. If not, it's an attacker (or a bug).

The secret is shared at registration time. The receiver stores it. The sender uses it to sign. Both sides keep it secret.

## The Reliability Problem

What if the receiver is down? The POST fails. The event is lost.

The fix: **retries with exponential backoff**. We use a queue (project 26). The webhook delivery is a job. If the job fails, it's retried. After N failures, it's marked as failed (for manual review).

This is the same pattern as the email queue (project 26). Webhook delivery is a job. The job is retried on failure. The receiver doesn't need to be 100% reliable.

## What This Project Will Solve

This project will:

1. Add a `webhooks` table
2. Add endpoints to register, list, and delete webhooks
3. Add a `fireWebhook(event, data, userId)` function
4. Sign the payload with HMAC-SHA256
5. Deliver via the queue (with retries)
6. Call `fireWebhook` from relevant handlers (e.g., post creation)

By the end, the server can push events to external services. The receiver can verify the signature.

## What This Project Will *Not* Solve

- **Receiver-side verification** — the receiver must verify the signature. We provide the secret; they verify.
- **Subscription filters** — the receiver subscribes to specific events. We support an array of event types per webhook.
- **Replay protection** — a timestamp in the payload prevents replay. We add a timestamp.
- **Rate limiting** — too many webhooks in a short time. Out of scope.
- **Per-event URLs** — one URL per event. We have one URL per webhook (with an array of events).
- **Webhook logs** — record every delivery attempt. Out of scope.

## The Question This Project Answers

> *"How do I push events to other services in real time?"*

If you can answer: "register a webhook URL, sign the payload with HMAC, deliver via a queue with retries, the receiver verifies the signature," you are ready for project 35.
