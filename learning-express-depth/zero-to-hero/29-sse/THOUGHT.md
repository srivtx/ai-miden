# The Thought

> *"SSE is a long-running HTTP response. The server writes events. The client reads events. The connection stays open."*

## What SSE Is

SSE is a standard for one-way server-to-client streaming over HTTP. The server keeps a response open and writes events. The client receives them.

The Content-Type is `text/event-stream`. The response never "ends" — the server keeps the connection open and writes events as they happen.

The protocol:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: welcome
data: {"message": "Connected"}

event: heartbeat
data: {}

```

Each event is:

```
event: <name>
data: <payload>
<blank line>
```

The blank line terminates the event. The browser fires an event listener for `event: <name>` with the `data` as the payload.

## How the Server Sends Events

```js
res.set({
  'Content-Type': 'text/event-stream',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
});
res.flushHeaders();

// Send an event
res.write(`event: welcome\ndata: ${JSON.stringify({ message: 'Connected' })}\n\n`);
```

The format:

- `event: <name>\n` — the event name
- `data: <payload>\n` — the data (can be multiple `data:` lines for multi-line data)
- `\n` — a blank line terminates the event

We use `res.write` to send data without closing the response. The connection stays open.

## How the Client Receives Events

In the browser:

```javascript
const events = new EventSource('/events');

events.addEventListener('welcome', (e) => {
  console.log(JSON.parse(e.data));
});

events.addEventListener('heartbeat', () => {
  console.log('heartbeat');
});
```

The `EventSource` API is built into browsers. It auto-reconnects on disconnection. It fires events for each `event: <name>` it receives.

In Node, you can use the `eventsource` npm package.

## Heartbeats

Proxies and load balancers often close idle connections. To prevent this, we send a heartbeat every 30 seconds:

```js
const interval = setInterval(() => {
  res.write(`event: heartbeat\ndata: {}\n\n`);
}, 30000);
```

The client can listen for `heartbeat` events to know the connection is alive. Or it can ignore them; the browser's `EventSource` will keep the connection open.

## Disconnection

When the client disconnects, the `req` object emits a `close` event. We clear the interval:

```js
req.on('close', () => {
  clearInterval(interval);
});
```

Without this, the interval would keep running forever, even after the client disconnects. Memory leak.

## Common Confusions (read these)

**Confusion 1: "Why not WebSocket?"**
WebSocket is bidirectional. SSE is one-way. If you only need server-to-client, SSE is simpler. Less code, less protocol overhead, standard HTTP.

**Confusion 2: "Why not long polling?"**
Long polling works but uses a new HTTP request per poll. SSE uses one persistent connection.

**Confusion 3: "Why not just regular polling with `fetch`?"**
You can. But it's wasteful (1 request per second per user). SSE uses 1 connection per user, persistent.

**Confusion 4: "What if the connection drops?"**
The browser's `EventSource` auto-reconnects. The server doesn't need to do anything.

**Confusion 5: "What about authentication?"**
Anyone can connect. For auth, you'd verify a token (e.g., as a query parameter or cookie). We add auth in a future project.

**Confusion 6: "What about CORS?"**
SSE has CORS. The server must send the right `Access-Control-Allow-Origin` header. The browser enforces it.

**Confusion 7: "What about buffering?"**
Some proxies buffer responses. Nginx, for example, buffers by default. You may need to disable buffering (`X-Accel-Buffering: no`).

**Confusion 8: "Can I send binary?"**
No. SSE is text only. For binary, use WebSocket.

## What We Are About to Build

A ~550-line Express app that:

1. Has a `GET /events` endpoint that returns `text/event-stream`
2. Sends a welcome event on connection
3. Sends a heartbeat every 30 seconds
4. Handles disconnection (clears the interval)
5. Logs connections and disconnections

The handlers are unchanged. The new piece is the SSE endpoint.

In [BUILD.md](./BUILD.md) we will go line by line.
