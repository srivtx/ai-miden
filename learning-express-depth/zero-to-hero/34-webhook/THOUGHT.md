# The Thought

> *"Register a URL. Sign the payload. POST. Retry on failure. That's the whole pattern."*

## The Webhook Lifecycle

1. **Registration**: the receiver registers a URL with our service. They provide:
   - `url`: the URL to POST to (e.g., `https://their-app.com/webhooks/cove`)
   - `events`: array of event types they care about (e.g., `['post.created', 'user.updated']`)
   - We generate a `secret` and return it (or they generate it; either way, they store it)

2. **Event**: when an event happens in our app, we call `fireWebhook(event, data, userId)`.

3. **Delivery**: `fireWebhook` looks up the user's webhooks. For each webhook that cares about the event, it:
   - Builds the payload: `{ event, data, timestamp }`
   - Signs with HMAC-SHA256: `signature = HMAC(secret, payload)`
   - Adds a job to the queue: `webhookQueue.add('deliver', { url, payload, signature })`

4. **Worker**: the queue worker picks up the job. It POSTs to the URL with the payload and signature. On failure, it's retried (BullMQ handles this).

5. **Receiver**: the receiver receives the POST. They:
   - Read the `X-Webhook-Signature` header
   - Compute the expected signature: `HMAC(their_secret, request_body)`
   - Compare. If match, process. If not, reject.

## The Signature

```js
const crypto = require('node:crypto');

const payload = JSON.stringify({ event: 'post.created', data: { id: 42 }, timestamp: 1700000000 });
const signature = crypto.createHmac('sha256', secret).update(payload).digest('hex');

// Send in header
fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Webhook-Signature': signature,
  },
  body: payload,
});
```

The signature is `hex(HMAC-SHA256(secret, payload))`. The receiver has the same `secret` and computes the same hash. If the hashes match, the payload is authentic.

## The Queue

We use the queue from project 26. The webhook delivery is a job:

```js
const webhookQueue = new Queue('webhook', { connection: redis });
const webhookWorker = new Worker('webhook', async (job) => {
  if (job.name === 'deliver') {
    const { url, payload, signature } = job.data;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature,
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error(`Webhook delivery failed: ${response.status}`);
  }
}, { connection: redis });
```

BullMQ retries on failure (with the same `attempts` and `backoff` options from project 26). After N failures, the job is in the failed set.

## The Endpoints

```js
const webhookCreateSchema = z.object({
  url: z.string().url(),
  events: z.array(z.string()).min(1),
});

app.post('/webhooks', authMiddleware, validate(webhookCreateSchema), asyncHandler(async (req, res) => {
  const { url, events } = req.validated;
  const secret = crypto.randomBytes(32).toString('hex');
  const [id] = await db('webhooks').insert({
    user_id: req.user.userId,
    url,
    events: JSON.stringify(events),
    secret,
    created_at: Date.now(),
  });
  res.status(201).json({ id, url, events, secret });
}));

app.get('/webhooks', authMiddleware, asyncHandler(async (req, res) => {
  const webhooks = await db('webhooks').where({ user_id: req.user.userId }).select('id', 'url', 'events', 'created_at', 'last_triggered_at', 'active');
  res.json({ data: webhooks });
}));

app.delete('/webhooks/:id', authMiddleware, asyncHandler(async (req, res) => {
  await db('webhooks').where({ id: req.params.id, user_id: req.user.userId }).delete();
  res.status(204).end();
}));
```

The endpoints let users register, list, and delete their webhooks. The `secret` is returned only once (on creation). The user must store it.

## Firing the Webhook

In the relevant handler (e.g., `POST /posts`):

```js
app.post('/posts', authMiddleware, validate(postCreateSchema), asyncHandler(async (req, res) => {
  // ... create the post ...
  const [id] = await db('posts').insert({...});
  // Fire the webhook
  await fireWebhook('post.created', { id, title, author: req.user.username }, req.user.userId);
  res.status(201).json({...});
}));
```

After creating the post, we fire a `post.created` webhook for the user. The webhook includes the post data.

## Common Confusions (read these)

**Confusion 1: "Why sign? Why not just HTTPS?"**
HTTPS encrypts the connection. It doesn't *authenticate* the sender. An attacker could still POST to the URL. The signature proves the sender is us.

**Confusion 2: "Why not just use an API key in the URL?"**
An API key can be leaked. A signature is computed per request, so leaking one doesn't compromise others.

**Confusion 3: "What if the receiver's server is down?"**
The queue retries. After N failures, the job is in the failed set. The user can manually retry.

**Confusion 4: "What if the secret is leaked?"**
Rotate the secret. Generate a new one. Update the receiver. Old signatures are invalid.

**Confusion 5: "What about replay attacks?"**
Add a timestamp to the payload. The receiver rejects signatures older than 5 minutes. Out of scope for this project.

**Confusion 6: "What about idempotency?"**
Add an event ID. The receiver deduplicates. Out of scope for this project.

**Confusion 7: "What about ordering?"**
Out of scope. We don't guarantee order. If the receiver needs order, they should use the timestamp to sort.

**Confusion 8: "What about large payloads?"**
Keep payloads small. Send IDs, not full objects. The receiver can fetch the full object via the API.

## What We Are About to Build

A ~750-line Express app that:

1. Has a `webhooks` table
2. Has endpoints to register, list, and delete webhooks
3. Has a `fireWebhook(event, data, userId)` function
4. Signs the payload with HMAC-SHA256
5. Delivers via the queue (with retries)
6. Calls `fireWebhook` from relevant handlers

The handlers are extended. The new piece is the webhook system.

In [BUILD.md](./BUILD.md) we will go line by line.
