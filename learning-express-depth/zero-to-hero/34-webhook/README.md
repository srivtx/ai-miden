# Project 34: The Webhook

> *"Don't make your customers poll. Tell them when something happens."*

In projects 21-33, our server can *receive* events (HTTP requests). But what if another service wants to *know* when something happens in our app? Examples:

- "Tell Slack when a new post is created in workspace X"
- "Tell Zapier when a user upgrades to premium"
- "Tell our analytics service when a payment is processed"

The other service doesn't want to poll. They want a **push notification**: "Hey, this happened in our app. Here's the data."

**Webhooks** are the standard. You register a URL with our service. When an event happens, we send an HTTP POST to that URL with the event data. The other service receives it in real time.

We add a `webhooks` table, an endpoint to register a webhook, and a function to fire webhooks when events happen. The webhooks are signed with HMAC so the receiver can verify they're from us.

By the end, our server can push events to other services. The integration is real-time, secure, and reliable (with retries).

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is polling bad? What is a webhook?
2. [The Thought](./THOUGHT.md) — How do webhooks work? What is HMAC signing?
3. [The Build](./BUILD.md) — Line-by-line construction of the webhook system
4. [The Decisions](./DECISIONS.md) — Why webhooks? Why HMAC? Why retries?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A webhook is an HTTP callback. The receiver registers a URL. The sender POSTs to that URL when an event happens. The receiver verifies the signature (HMAC) and processes the event. Failed deliveries are retried with exponential backoff. We add a `webhooks` table, an endpoint to register, and a `fireWebhook(event, data)` function that's called from our handlers.

---

## The Code

```js
// Migration
{
  version: 8,
  up: `
    CREATE TABLE IF NOT EXISTS webhooks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      url TEXT NOT NULL,
      events TEXT NOT NULL, -- JSON array of event types
      secret TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      last_triggered_at INTEGER,
      active INTEGER NOT NULL DEFAULT 1
    );
  `,
},

// Fire a webhook
async function fireWebhook(event, data, userId) {
  const webhooks = await db('webhooks').where({ user_id: userId, active: 1 });
  for (const wh of webhooks) {
    const events = JSON.parse(wh.events);
    if (!events.includes(event) && !events.includes('*')) continue;
    const payload = { event, data, timestamp: Date.now() };
    const signature = crypto.createHmac('sha256', wh.secret).update(JSON.stringify(payload)).digest('hex');
    // Push to queue (project 26) for retry
    await webhookQueue.add('deliver', { url: wh.url, payload, signature });
  }
}

// Worker
const webhookWorker = new Worker('webhook', async (job) => {
  if (job.name === 'deliver') {
    const { url, payload, signature } = job.data;
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature,
      },
      body: JSON.stringify(payload),
    });
  }
}, { connection: redis });
```

The pain of "the other service has to poll" is solved. We push. They receive.

---

## What You Will Have Learned

- What a webhook is (HTTP callback for events)
- How to register a webhook (URL, events, secret)
- How to sign a webhook (HMAC-SHA256)
- How to deliver via a queue (with retries)
- The receiver can verify the signature

These are the foundations of *outbound push*. From here, every project that needs to notify external services can use webhooks.
