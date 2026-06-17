# 52 — Server-Sent Events (SSE)

**New concept:** one-way streaming from server to client. WebSocket is bidirectional. SSE is just server-to-client. Simpler.

Useful for: live updates, notifications, stock prices, progress bars.

## Run it

```bash
npm install
node server.js
```

```bash
# Watch ticks
curl -N http://localhost:3000/events
# event: tick
# data: {"n":1,"ts":1702656000000}
#
# event: tick
# data: {"n":2,"ts":1702656001000}
# ...

# Watch "stock prices" (simulated)
curl -N http://localhost:3000/stocks
# event: price
# data: {"symbol":"AAPL","price":"150.32"}
#
# event: price
# data: {"symbol":"GOOG","price":"100.18"}
```

**`curl -N`** disables buffering so you see each event as it arrives.

## How to think about it

WebSocket is like a phone call (both sides talk). SSE is like a radio (server broadcasts, client just listens). For things like notifications, you don't need the client to send anything. SSE is enough.

## How to build it (line by line)

```js
res.set({
  'Content-Type': 'text/event-stream',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
});
res.flushHeaders();
```

**Lines 10-16.** Set the right headers and flush them. This tells the client "the response is starting now, keep the connection open, more data is coming."

**`text/event-stream`** is the content type. It tells the client "this is an SSE stream."

```js
res.write(`event: tick\ndata: ${JSON.stringify({...})}\n\n`);
```

**Line 22.** Send an event. The format is:
- `event: <name>\n` — the event name
- `data: <json>\n` — the data
- `\n` — empty line marks the end of the event

```js
req.on('close', () => clearInterval(interval));
```

**Line 28.** When the client disconnects, stop the interval. Otherwise, we'd keep writing to a dead connection.

## What we learned

1. SSE = server-to-client streaming
2. Three headers: text/event-stream, no-cache, keep-alive
3. Event format: `event: name\ndata: json\n\n`
4. Clean up on disconnect (`req.on('close')`)
5. SSE is simpler than WebSocket for one-way updates

## What's next

In **53-redis-cache** we use Redis for caching instead of in-memory.
