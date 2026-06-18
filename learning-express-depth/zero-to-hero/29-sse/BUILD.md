# The Build

> *"SSE is a long-running HTTP response. The server writes events. The client reads events."*

We are going to add an SSE endpoint. The change from project 28: add a `GET /events` route that returns `text/event-stream` and sends events.

## The Code

### The SSE Endpoint

```js
app.get('/events', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no', // Disable buffering for nginx
  });
  res.flushHeaders();

  // Send a welcome event
  res.write(`event: welcome\ndata: ${JSON.stringify({ message: 'Connected' })}\n\n`);

  // Send a heartbeat every 30 seconds
  const interval = setInterval(() => {
    res.write(`event: heartbeat\ndata: ${}\n\n`);
  }, 30000);

  // Handle disconnection
  req.on('close', () => {
    logger.info('SSE client disconnected');
    clearInterval(interval);
  });

  logger.info('SSE client connected');
});
```

### What it does

1. Sets the headers for SSE
2. Flushes the headers (sends them immediately)
3. Sends a welcome event
4. Starts a heartbeat interval (every 30 seconds)
5. On client disconnect, clears the interval

### The event format

```js
res.write(`event: welcome\ndata: ${JSON.stringify({ message: 'Connected' })}\n\n`);
```

- `event: welcome` — the event name
- `data: { ... }` — the data (JSON-stringified)
- `\n\n` — blank line terminates the event

### Heartbeats

```js
setInterval(() => {
  res.write(`event: heartbeat\ndata: {}\n\n`);
}, 30000);
```

Every 30 seconds, send a heartbeat. This keeps the connection alive through proxies.

### Disconnection

```js
req.on('close', () => {
  clearInterval(interval);
});
```

When the client disconnects, the `req` object emits a `close` event. We clear the interval. Without this, the interval would keep running forever.

## Test It

In a browser, open DevTools console on `http://localhost:3000`:

```javascript
const events = new EventSource('/events');
events.addEventListener('welcome', (e) => console.log('welcome:', JSON.parse(e.data)));
events.addEventListener('heartbeat', () => console.log('heartbeat'));
```

You see:
- "welcome: { message: 'Connected' }" (immediately)
- "heartbeat" (every 30 seconds)

The pain of "WebSocket is overkill for one-way push" is solved. The server pushes events. The client receives them.

Or in Node:

```javascript
const { EventSource } = require('eventsource');
const events = new EventSource('http://localhost:3000/events');
events.addEventListener('welcome', (e) => console.log('welcome:', e.data));
events.addEventListener('heartbeat', () => console.log('heartbeat'));
```

---

## Experiments

### Experiment 1: Send a custom event

```js
app.post('/broadcast', (req, res) => {
  // Broadcast to all SSE clients
  for (const client of sseClients) {
    client.write(`event: broadcast\ndata: ${JSON.stringify(req.body)}\n\n`);
  }
  res.json({ message: 'Broadcast sent' });
});
```

Add a `POST /broadcast` endpoint that pushes a custom event to all SSE clients. Useful for notifications.

### Experiment 2: Track connected clients

```js
const sseClients = new Set();

app.get('/events', (req, res) => {
  // ... setup ...
  sseClients.add(res);
  req.on('close', () => {
    sseClients.delete(res);
    clearInterval(interval);
  });
});
```

Now you can broadcast to all connected clients. Useful for notifications.

### Experiment 3: Authenticate SSE

Pass a token as a query parameter: `/events?token=abc`. Verify the token in the handler. Reject if invalid.

```js
app.get('/events', (req, res) => {
  const token = req.query.token;
  if (!verifyToken(token)) {
    return res.status(401).end();
  }
  // ... setup ...
});
```

### Experiment 4: Use SSE for build progress

For a long-running task (e.g., image processing), use SSE to push progress updates:

```js
app.post('/process-image', async (req, res) => {
  const jobId = uuid();
  // Start the job in the background
  processImageInBackground(jobId, (progress) => {
    // Send SSE event with progress
  });
  res.json({ jobId });
});

app.get('/events/:jobId', (req, res) => {
  // SSE endpoint for this job's progress
  // ...
});
```

The client subscribes to the job's progress via SSE.

---

## Summary

You now have SSE. The server can push one-way events. The client receives them. The connection is persistent but one-way. Simpler than WebSocket for one-way use cases.

This is the foundation of *one-way real-time*. From here, every project that needs server-push can use SSE. The patterns (`text/event-stream`, `EventSource`, heartbeats) are universal.

In project 30, we will add **presence** — knowing who's online. We use Redis pub/sub so presence is shared across processes.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
