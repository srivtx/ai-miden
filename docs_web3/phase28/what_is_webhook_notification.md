# What is a Webhook Notification?

## Why It Exists

After a customer pays on-chain, the merchant needs to know immediately so they can ship a product, unlock content, or mark an order complete.
Polling the gateway API from the merchant's side is wasteful and slow.
Webhook notifications push the update to the merchant instantly and reliably.
Without webhooks, merchants would either poll constantly or miss payments entirely.
Polling creates unnecessary load and delays fulfillment.
Modern payment systems rely on event-driven architecture for real-time responsiveness.

## Definition

A webhook notification is an HTTP POST request sent by a payment gateway to a merchant's server when a payment reaches a specific status.
It delivers event data so the merchant can take action without continuously polling.
The merchant provides a URL, and the gateway calls it when something important happens.
It is the digital equivalent of a doorbell.
The gateway rings the bell; the merchant answers the door.
This simple model scales from small shops to global marketplaces.

## Real-Life Analogy

Imagine waiting for a package delivery.
Instead of refreshing the tracking page every minute, you sign up for text alerts.
The moment the driver drops the package on your porch, your phone buzzes.
Webhooks are those text alerts.
They push the news to you instantly so you can stop watching the door and start using what arrived.
Without alerts, you would waste hours staring at an unchanged tracking screen.

The alert is automatic and instant.
You do not need to ask for updates.
The system tells you exactly when something changes.
This is the core difference between push and pull communication.
Push is efficient; pull is wasteful.

## Tiny Numeric Example

A merchant processes 1,000 payments per day.

| Method | API Calls/Day | Avg Delay | Server Load |
|---|---|---|---|
| Polling every 10s | 8,640,000 | 5s | Very high |
| Polling every minute | 1,440,000 | 30s | High |
| Webhooks | 1,000 | 0.1s | Minimal |
| Savings | 99.99% | 50x faster | Massive |

With webhooks, the merchant's server receives exactly one request per event instead of millions of unnecessary polls.
The server can focus on business logic instead of wasting cycles on empty checks.
The efficiency gain is astronomical.
A small server can handle millions of webhooks but would crumble under millions of poll requests.
This architectural choice separates scalable systems from fragile ones.
Webhooks are the industry standard for reliable event delivery at scale.

## Common Confusion

- **"Is a webhook an API?"** It uses HTTP, but it is a push mechanism, not a pull mechanism. The gateway calls the merchant, not the other way around.
- **"What if my server is down when the webhook fires?"** Production gateways retry with exponential backoff and eventually mark the webhook as failed.
- **"How do I know the webhook is really from the gateway?"** Gateways sign payloads with HMAC signatures. Merchants verify the signature before trusting the data.
- **"Can't I just use websockets?"** Websockets work for real-time dashboards but require persistent connections. Webhooks are better for server-to-server notifications.
- **"What if I receive the same webhook twice?"** Idempotency keys in the webhook payload let merchants ignore duplicate notifications safely.
- **"Do all payment statuses trigger webhooks?"** Usually yes: created, pending, confirmed, failed, and expired. Merchants subscribe to the statuses they care about.
- **"What if the network is slow and confirmation takes minutes?"** The gateway waits for the configured confirmation level, then fires the webhook. The merchant does not need to track this themselves.
- **"Can I test webhooks?"** Yes. Most gateways provide test endpoints that simulate events without real payments.
- **"What is a webhook secret?"** A shared key used to sign payloads so the receiver can verify the sender's identity.

## Key Properties

- **Push Delivery:** Sends event data to merchant servers immediately upon status changes without requiring polling.
- **Retry Logic:** Automatically re-attempts failed deliveries with exponential backoff to ensure reliability.
- **Signature Verification:** Uses HMAC signatures so merchants can authenticate webhook origins and prevent spoofing.
- **Idempotency:** Includes unique keys per event so duplicate notifications can be detected and ignored safely.
- **Event Filtering:** Allows merchants to subscribe only to specific status changes they care about.
- **Observability:** Provides logging, metrics, and health checks for monitoring system behavior and debugging issues.
- **Composability:** Works seamlessly with other infrastructure components like load balancers, databases, and messaging queues.
- **Extensibility:** Supports plugins and middleware so developers can customize behavior without modifying core code.

## Key Properties
## Where It Appears in Our Code

`src_web3/phase28/payment_gateway.ts` implements `notifyMerchant` which POSTs signed webhook payloads to registered callback URLs when payments are confirmed.
