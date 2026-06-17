# 46 — Pub/Sub

**New concept:** publish/subscribe.

Imagine a radio station. The station broadcasts on a frequency. Anyone tuned in hears it. The station doesn't know who's listening. The listeners don't know about each other.

That's pub/sub. The publisher says "here's an event." Subscribers that care about that event get notified. They don't know about each other.

## Run it

```bash
npm install
node server.js
```

```bash
# Publish a user.created event
curl -X POST http://localhost:3000/publish/user.created \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'
# 202 { eventId: 123, subscriberCount: 2 }

# In server logs:
# [email] Sending welcome to alice@example.com
# [analytics] Recording signup: alice@example.com

# Publish an order.created event
curl -X POST http://localhost:3000/publish/order.created \
  -H "Content-Type: application/json" \
  -d '{"id": "ord_123"}'
# [inventory] Reserving stock for order ord_123

# See recent events
curl http://localhost:3000/events
```

## How to think about it

When you check out on Amazon, lots of things happen: payment processed, inventory updated, email sent, analytics recorded. These don't all happen in the checkout function. The checkout publishes an "order.created" event. Other services subscribe and do their thing.

This decouples the code. The checkout doesn't need to know about email, inventory, analytics. It just publishes. Each subscriber handles its own concern.

## How to build it (line by line)

```js
const subscribers = new Map();  // topic -> array of handlers
```

**Line 10.** A map from topic name to a list of handler functions.

```js
function subscribe(topic, handler) {
  if (!subscribers.has(topic)) subscribers.set(topic, []);
  subscribers.get(topic).push(handler);
  return () => { /* unsubscribe */ };
}
```

**Lines 12-19.** Add a handler to a topic. Returns a function to unsubscribe.

```js
async function publish(topic, data) {
  const handlers = subscribers.get(topic) || [];
  await Promise.all(handlers.map(h => h(event)));
}
```

**Lines 21-26.** Call all handlers for this topic, in parallel.

**`Promise.all`** — wait for all handlers to finish.

```js
subscribe('user.created', (event) => {
  console.log(`[email] Sending welcome to ${event.data.email}`);
});
```

**Lines 30-32.** Register a handler. The handler is just a function. It can do anything: send email, update DB, log.

## What we learned

1. Pub/sub decouples code: publishers don't know subscribers
2. A topic is a named channel
3. Subscribers register handlers for topics
4. `Promise.all` runs handlers in parallel
5. Real systems: Kafka, RabbitMQ, Redis Pub/Sub, AWS SNS

## What's next

In **47-job-queue** we build a queue for long-running tasks. The client submits a job, the server does the work in the background.
