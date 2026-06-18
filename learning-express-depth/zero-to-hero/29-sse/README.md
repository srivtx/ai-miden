# Project 29: The SSE Stream

> *"Sometimes the server only needs to talk. WebSocket is overkill. SSE is the answer."*

In project 28, we added WebSocket — bidirectional, persistent. The server and client can both send messages at any time. Perfect for chat, collaborative editing, multiplayer games.

But sometimes, the server only needs to *push* to the client. The client doesn't need to send anything back. Examples:

- **Notifications**: "you have a new comment"
- **Live updates**: stock prices, sports scores, server status
- **Progress**: file upload progress, build status

For these, WebSocket is overkill. We don't need bidirectional. We don't need the client to send messages.

**Server-Sent Events (SSE)** is a simpler protocol for one-way push. It's HTTP. The client opens a long-lived GET request. The server keeps the connection open and sends events as `text/event-stream`. The client listens with the `EventSource` API.

We use SSE for one-way push. The server can send events. The client receives them. The connection is persistent but one-way.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is WebSocket overkill for one-way push? What is SSE?
2. [The Thought](./THOUGHT.md) — How does SSE work? What is the EventSource API?
3. [The Build](./BUILD.md) — Line-by-line construction of the SSE endpoint
4. [The Decisions](./DECISIONS.md) — Why SSE? Why not WebSocket? Why not polling?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

SSE is a one-way push protocol over HTTP. The client opens a GET request. The server keeps the connection open and sends events as `text/event-stream`. The client listens with the `EventSource` API. We use SSE for notifications and live updates. It's simpler than WebSocket for one-way use cases.

---

## The Code

```js
app.get('/events', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  });
  res.flushHeaders();

  // Send a heartbeat every 30 seconds
  const interval = setInterval(() => {
    res.write(`event: heartbeat\ndata: {}\n\n`);
  }, 30000);

  // Send a welcome event
  res.write(`event: welcome\ndata: ${JSON.stringify({ message: 'Connected' })}\n\n`);

  req.on('close', () => {
    clearInterval(interval);
  });
});
```

Test it:

```javascript
// In a browser
const events = new EventSource('/events');
events.addEventListener('welcome', (e) => console.log(JSON.parse(e.data)));
events.addEventListener('heartbeat', () => console.log('heartbeat'));
```

The pain of "WebSocket is overkill for one-way push" is solved. The server pushes events. The client receives them.

---

## What You Will Have Learned

- What SSE is (a one-way push protocol over HTTP)
- The `EventSource` API in the browser
- The `text/event-stream` content type
- The event format (`event: name\ndata: payload\n\n`)
- How to send heartbeats to keep the connection alive
- When to use SSE vs WebSocket

These are the foundations of *one-way real-time*. From here, every project that needs server-push can use SSE.
