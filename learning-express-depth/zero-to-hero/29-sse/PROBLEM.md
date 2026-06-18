# The Problem

> *"WebSocket is a phone call. SSE is a radio broadcast. Sometimes broadcast is enough."*

## Why WebSocket Is Overkill (Sometimes)

In project 28, we added WebSocket. It's bidirectional, persistent, and powerful. We use it for chat (server and client both send messages).

But for some use cases, WebSocket is overkill:

- **Notifications**: "you have a new comment." Server pushes; client doesn't reply.
- **Live updates**: stock prices, sports scores. Server pushes; client doesn't reply.
- **Progress**: file upload progress, build status. Server pushes; client doesn't reply.

For these, the client doesn't need to send anything. The server just talks. WebSocket still works (the client can ignore its send capability), but it's more complex than needed.

The fix: **Server-Sent Events (SSE)**. A simpler protocol for one-way push. The server pushes; the client receives. The connection is HTTP (not a separate protocol). The client uses the standard `EventSource` API.

## What Pain Is This Solving?

Imagine you want to show "X is typing..." in a chat. The server knows when a user is typing (it receives a `typing` event from WebSocket). It needs to push this to all other users in the channel.

With WebSocket, the client opens a connection, both sides send and receive. Simple.

But for "server status updates" or "build progress," the client never needs to send anything. Using WebSocket feels heavy. The protocol upgrade, the bidirectional framing, the `ws` library — all unnecessary.

With SSE:

```js
// Server
app.get('/build-status', (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream' });
  // ... send events as the build progresses
});

// Client
const events = new EventSource('/build-status');
events.addEventListener('progress', (e) => updateProgressBar(JSON.parse(e.data)));
```

That's it. The server pushes. The client listens. No protocol upgrade. No bidirectional framing. Standard HTTP.

## The Deeper Problem: One-Way vs Two-Way

HTTP is fundamentally *one-way* (request) plus *one-way* (response). It's not a conversation; it's an exchange. WebSocket is a conversation. SSE is a long-running response.

For one-way push, SSE is the right tool:

- It's HTTP (no protocol upgrade, no port)
- It works through proxies and CDNs
- It auto-reconnects (the browser reconnects when the connection drops)
- It has a standard browser API (`EventSource`)

For two-way, WebSocket is the right tool.

## What This Project Will Solve

This project will:

1. Add a `GET /events` endpoint that returns `text/event-stream`
2. Send a welcome event on connection
3. Send a heartbeat every 30 seconds (to keep the connection alive through proxies)
4. Handle disconnection (clear the interval)

By the end, the server can push one-way events to clients via SSE.

## What This Project Will *Not* Solve

- **Client-to-server messaging** — use WebSocket (project 28) for that.
- **Reconnection logic** — the browser handles this automatically with `EventSource`. We don't.
- **Authentication** — anyone can connect. We add auth in a future project.
- **Persistence** — events are not stored. We add persistence in a future project.
- **Multi-process with Redis** — for multi-process, use Redis pub/sub. We add this in project 30.

## The Question This Project Answers

> *"How do I push one-way events to clients without WebSocket?"*

If you can answer: "use SSE, the server keeps an HTTP connection open and sends `text/event-stream`, the client uses `EventSource`," you are ready for project 30.
