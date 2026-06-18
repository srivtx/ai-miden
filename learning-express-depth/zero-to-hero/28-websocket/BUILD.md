# The Build

> *"The HTTP connection upgrades. The protocol switches. The conversation begins."*

We are going to add a WebSocket server. The change from project 27: add `ws`, create a WebSocket server attached to the HTTP server, handle connections and messages.

## Setup

```bash
npm install ws
```

## The Code

### Imports

```js
const { WebSocketServer, WebSocket } = require('ws');
```

### Create the HTTP Server and the WebSocket Server

```js
const server = app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));

const wss = new WebSocketServer({ server });
```

`app.listen(...)` returns an HTTP server. We pass it to `WebSocketServer({ server })`. The WebSocket server is attached to the same HTTP server.

The WebSocket endpoint is at `ws://localhost:3000/ws` (or any path; the default is no path, but we can specify `path: '/ws'` if we want).

### Handle Connections

```js
wss.on('connection', (ws, req) => {
  logger.info({ ip: req.socket.remoteAddress }, 'WebSocket client connected');

  // Send a welcome message
  ws.send(JSON.stringify({ type: 'welcome', message: 'Connected to the chat' }));

  // Handle messages from this client
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      logger.info({ type: message.type }, 'Received message');

      if (message.type === 'chat') {
        // Broadcast to all clients
        wss.clients.forEach((client) => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify({
              type: 'chat',
              user: message.user,
              text: message.text,
              timestamp: Date.now(),
            }));
          }
        });
      }
    } catch (err) {
      logger.error({ err: err.message }, 'Failed to parse WebSocket message');
    }
  });

  // Handle disconnection
  ws.on('close', () => {
    logger.info('WebSocket client disconnected');
  });

  // Handle errors
  ws.on('error', (err) => {
    logger.error({ err: err.message }, 'WebSocket error');
  });
});
```

The flow:
- Connection event: a new client connected. Send a welcome message. Register handlers.
- Message event: a client sent a message. Parse it. If it's a chat message, broadcast to all clients.
- Close event: a client disconnected. Log.
- Error event: a WebSocket error. Log.

### The Broadcast

```js
wss.clients.forEach((client) => {
  if (client.readyState === WebSocket.OPEN) {
    client.send(JSON.stringify({ ... }));
  }
});
```

`wss.clients` is a `Set` of all connected clients. We iterate and send. We check `readyState === OPEN` to skip clients that are closing or closed.

## Test It

You need a WebSocket client. Here's a Node.js client:

```javascript
// client.js
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:3000');

ws.on('open', () => {
  console.log('Connected');
  ws.send(JSON.stringify({ type: 'chat', user: 'alice', text: 'Hello!' }));
});

ws.on('message', (data) => {
  console.log('Received:', JSON.parse(data.toString()));
});

ws.on('close', () => {
  console.log('Disconnected');
});
```

Run it in two terminals. Both clients connect. When one sends a chat message, both receive it (the sender and the other).

Or use a browser console:

```javascript
const ws = new WebSocket('ws://localhost:3000');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.onopen = () => ws.send(JSON.stringify({ type: 'chat', user: 'browser', text: 'Hello from the browser!' }));
```

The pain of "the server can't push to the client" is solved. The server broadcasts. The clients receive.

---

## Experiments

### Experiment 1: Use a browser client

Open DevTools console on `http://localhost:3000` and use the WebSocket API to connect and send messages.

### Experiment 2: Multiple clients

Open multiple browser tabs. Connect each. Send a message from one. All receive.

### Experiment 3: Persist messages

In production, you'd store messages in a database. Add a `messages` table; insert on chat, query on connect (send the last 50 messages to the new client).

### Experiment 4: Add rooms

A room is a subset of clients. "chat:general" or "chat:random". Broadcast only to clients in the same room. Out of scope for this project.

### Experiment 5: Auth

Add a token in the query string: `ws://localhost:3000?token=abc`. Verify the token in the `connection` handler. Reject if invalid.

```js
wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const token = url.searchParams.get('token');
  if (!verifyToken(token)) {
    ws.close(1008, 'Unauthorized');
  }
});
```

---

## Summary

You now have WebSocket. The server can push updates. Clients receive in real time. The chat example is the foundation for notifications, presence, and co-editing.

This is the foundation of *real-time communication*. From here, every project that needs bidirectional communication can use WebSocket. The patterns (`ws`, broadcast, message handling) are universal.

In project 29, we will add **SSE (Server-Sent Events)** — a simpler alternative for one-way push (server to client only). Useful for notifications, live updates, etc.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
