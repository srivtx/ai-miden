## Why it exists (THE PROBLEM)

You make an API. The client wants to know when something happens. Three options:

**Option A: polling.** Client calls `GET /orders/new` every 30 seconds. Wasteful. 99% of calls return "nothing new." At 1000 clients, that's 2 million calls/day to "nothing new."

**Option B: long-polling.** Client calls `GET /orders/new?since=lastId`. Server holds the connection open until something happens, then responds. Better, but connections are stateful. If the server restarts, the client has to reconnect.

**Option C: webhooks.** Server calls the CLIENT when something happens. Client gives server a URL. Server POSTs to that URL. Zero idle traffic. Server doesn't need to track who's connected.

**Webhooks** = reverse API. The client provides a URL. The server calls that URL when events happen. Stripe, GitHub, Slack, Twilio all use webhooks for event delivery.

The trade-off: webhooks require the client to have a public URL (or use a tunnel like ngrok in dev). Polling works without that. For server-to-server, webhooks. For browser clients, polling or websockets.

## Definition (very simple)

**Webhook** = a URL that the client registers with the server. When an event happens, the server makes an HTTP POST to that URL with event data.

**Event** = something that happened. `order.created`, `payment.succeeded`, `user.signed_up`. Each has a name, a payload, a timestamp, an event ID.

**Event delivery** = the actual POST. Includes signature verification (HMAC) so the client knows it's from the server, not an attacker.

**Retry** = if the client's URL returns an error, the server retries. Exponential backoff: 1s, 5s, 30s, 5m, 30m, 2h. After 24h or 6 attempts, give up and put the event in a dead-letter queue.

**Dead-letter queue** = a place to store events that couldn't be delivered. The client can replay them later.

## Real-life analogy

**Polling = a kid asking "are we there yet?" every 30 seconds.** Parent is the server. Car trip is the work. "Are we there yet?" is the poll. Most of the time, answer is "no." Wasted breath.

**Webhook = a phone call from the parent.** "We're here." One call, one notification. The kid doesn't need to keep asking.

**Long-polling = leaving the line open and waiting for the parent's call.** The kid is on the phone, doesn't speak, just waits. When parent calls back, kid hears "we're here." Better than polling but the line is held.

## Tiny numeric example

Same scenario: 1000 clients want to know when an order is created.

| Approach | API calls when nothing happens | API calls when 1 event happens | Server state |
|---|---|---|---|
| Polling (every 30s) | 2 million/day | 2 million + 1 | None |
| Long-polling | 1000 (open) | 1000 (open) + 1 | 1000 connections |
| Webhooks | 0 | 1 per client that wants to know | None |

Webhooks are dramatically more efficient at scale. Stripe sends ~10 billion webhooks per year. Polling that would be impossible.

## Common confusion (5+ bullet points)

1. **"The client can just open a websocket."** They can, but it requires the client to have a stateful server. Webhooks don't — the client just needs a URL. For server-to-server, webhooks. For browser-to-server, websockets.

2. **"I'll just retry forever."** NO. If the client's URL is broken (typo, server down for days), your retry queue grows. You need a max retry count and a dead-letter queue. The client should be able to "replay" events from the dead-letter queue.

3. **"The signature isn't needed if the URL is secret."** The URL is in the request — it's not secret. Anyone who sees the URL can call it. Always sign with HMAC. The signature is in the `X-Signature` header. Client computes `HMAC-SHA256(secret, body)` and compares.

4. **"I should send the event in the URL."** Don't put data in the URL. It's logged, cached, and visible. Send it in the POST body (JSON).

5. **"Webhooks need real-time delivery."** They don't. If the client is down, the event queues. When the client comes back up, the queued events deliver. Webhooks are "eventually real-time" — within seconds usually, within minutes during incidents.

6. **"I'll just call the webhook directly from my code."** That ties your request to the webhook. If the webhook is slow, your request is slow. Use a queue: put the event in a queue, a worker dequeues and POSTs. Now your request is fast (just enqueue) and the webhook delivery is async.

## Key properties

| Property | Polling | Long-polling | Webhook |
|---|---|---|---|
| Idle traffic | High | Low | Zero |
| Real-time | 30s+ delay | Real-time | Real-time (when delivered) |
| Server state | None | Many connections | None |
| Client needs public URL | No | No | Yes |
| Failure recovery | Client retries | Reconnect | Server retries + DLQ |

## Webhook delivery pattern

```js
// When an event happens:
1. Save event to events table (id, type, payload, created_at)
2. Enqueue delivery job (event_id, target_url)
3. Worker:
   a. Look up event
   b. Compute signature: HMAC-SHA256(secret, body)
   c. POST to target_url with body + signature header
   d. If 2xx: mark delivered
   e. If 4xx (not 408/429): mark failed, no retry (client error)
   f. If 5xx or timeout: retry with backoff
   g. If max retries: move to dead-letter queue
```

## Signature verification (client side)

```js
const crypto = require('crypto');
const signature = req.headers['x-signature']; // sha256=...
const body = JSON.stringify(req.body);
const expected = 'sha256=' + crypto.createHmac('sha256', WEBHOOK_SECRET).update(body).digest('hex');
if (signature !== expected) return res.status(401).send('invalid signature');
```

## Connection to our projects

For our 73 apps, the `webhook-delivery/` project in apps/level3 is a complete webhook system. Copy that pattern to any service that needs to send events. Examples:
- `order-service` sends `order.created` to `notification-service`
- `payment-service` sends `payment.succeeded` to `fulfillment-service`
- `auth-service` sends `user.signed_up` to `email-service`

For CortexCode and logogen, the API server can emit webhooks too. "completion.finished" with the generated code. The user integrates it into their CI/CD. No polling.
