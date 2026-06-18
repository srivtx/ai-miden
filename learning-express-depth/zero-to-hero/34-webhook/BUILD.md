# The Build

> *"Register a URL. Sign the payload. POST. Retry on failure."*

We are going to add webhooks. The change from project 33: add a `webhooks` table, an HMAC signing helper, and a delivery queue.

## The Code

### The Migration

```js
{
  version: 8,
  up: `
    CREATE TABLE IF NOT EXISTS webhooks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      url TEXT NOT NULL,
      events TEXT NOT NULL,
      secret TEXT NOT NULL,
      created_at INTEGER NOT NULL,
      last_triggered_at INTEGER,
      active INTEGER NOT NULL DEFAULT 1
    );
  `,
},
```

### The Queue and Worker

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
        'X-Webhook-Event': payload.event,
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Webhook delivery failed: ${response.status}`);
    }
  }
}, { connection: redis, attempts: 5, backoff: { type: 'exponential', delay: 1000 } });
```

### The `fireWebhook` Function

```js
async function fireWebhook(event, data, userId) {
  const webhooks = await db('webhooks').where({ user_id: userId, active: 1 });
  for (const wh of webhooks) {
    const events = JSON.parse(wh.events);
    if (events.length > 0 && !events.includes('*') && !events.includes(event)) continue;
    const payload = { event, data, timestamp: Date.now() };
    const signature = crypto.createHmac('sha256', wh.secret).update(JSON.stringify(payload)).digest('hex');
    await webhookQueue.add('deliver', { url: wh.url, payload, signature });
    await db('webhooks').where({ id: wh.id }).update({ last_triggered_at: Date.now() });
  }
}
```

### The Endpoints

```js
const webhookCreateSchema = z.object({
  url: z.string().url(),
  events: z.array(z.string()).min(1),
});

app.post('/webhooks', authMiddleware, validate(webhookCreateSchema), asyncHandler(async (req, res) => {
  const { url, events } = req.validated;
  const secret = crypto.randomBytes(32).toString('hex');
  const [id] = await db('webhooks').insert({ user_id: req.user.userId, url, events: JSON.stringify(events), secret, created_at: Date.now() });
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

### Firing the Webhook

In the post creation handler:

```js
app.post('/posts', authMiddleware, validate(postCreateSchema), asyncHandler(async (req, res) => {
  const { title, body } = req.validated;
  const [id] = await db('posts').insert({ user_id: req.user.userId, title, body, created_at: Date.now() });
  // Fire the webhook
  await fireWebhook('post.created', { id, title, author: req.user.username }, req.user.userId);
  res.status(201).json({ id, userId: req.user.userId, title, body });
}));
```

After creating the post, we fire a `post.created` webhook.

## Run It

```bash
# Start a simple webhook receiver
node -e "
  const http = require('http');
  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (chunk) => body += chunk);
    req.on('end', () => {
      console.log('Received:', body);
      console.log('Signature:', req.headers['x-webhook-signature']);
      res.writeHead(200);
      res.end('OK');
    });
  });
  server.listen(4000, () => console.log('Webhook receiver on :4000'));
"

# Register a webhook
curl -X POST http://localhost:3000/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:4000","events":["post.created"]}'
# {"id":1,"url":"http://localhost:4000","events":["post.created"],"secret":"..."}

# Create a post (triggers the webhook)
curl -X POST http://localhost:3000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","body":"World"}'

# The webhook receiver logs the request
# "Received: {\"event\":\"post.created\",\"data\":{...},\"timestamp\":...}"
# "Signature: <hmac>"
```

The pain of "the other service has to poll" is solved. We push. They receive.

---

## Experiments

### Experiment 1: Receiver-side verification

```js
const http = require('http');
const crypto = require('crypto');

const server = http.createServer((req, res) => {
  let body = '';
  req.on('data', (chunk) => body += chunk);
  req.on('end', () => {
    const signature = req.headers['x-webhook-signature'];
    const secret = '<your-webhook-secret>';
    const expected = crypto.createHmac('sha256', secret).update(body).digest('hex');
    if (signature === expected) {
      console.log('Valid webhook:', body);
    } else {
      console.log('Invalid signature!');
    }
    res.writeHead(200);
    res.end('OK');
  });
});
server.listen(4000);
```

### Experiment 2: Test retries

Stop the receiver. Create a post. The webhook fails. The queue retries (5 times with exponential backoff). After 5 failures, the job is in the failed set. Restart the receiver. Manually retry the failed jobs.

### Experiment 3: Webhook logs

Add a `webhook_deliveries` table to record every delivery attempt. Out of scope for this project, but a good practice.

### Experiment 4: Subscription filters

The receiver subscribes to specific events. We support an array of events. They can also subscribe to `*` for all events.

---

## Summary

You now have webhooks. The server can push events to external services. The receiver can verify the signature. Failed deliveries are retried.

This is the foundation of *outbound push*. From here, every project that needs to notify external services can use webhooks. The patterns (HMAC signing, queue delivery, retries) are universal.

In project 35, we will add **payments** with Stripe. Users can upgrade to a premium plan. The server charges their card. The webhook from project 34 is used to receive payment events from Stripe.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
