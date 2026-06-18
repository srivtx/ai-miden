# The Thought

> *"A key in Redis with a TTL. Refresh the TTL on heartbeat. The key dies if the heartbeat stops. The user is offline."*

## How Presence Works

Presence is a *distributed* state machine. Each process has a local view of who's online. The local view is updated via Redis pub/sub. The source of truth is Redis (via TTL).

The lifecycle:

1. **Client connects**: server sets `presence:<userId>` with TTL 30 seconds. Publishes `presence:connect`.
2. **Heartbeat**: every 10 seconds, server refreshes the TTL (`EXPIRE presence:<userId> 30`).
3. **Client disconnects normally**: server deletes the key, publishes `presence:disconnect`.
4. **Client crashes**: no more heartbeats. TTL expires. Redis deletes the key. The user is offline.
5. **Process restart**: no impact. Redis still has the TTL. Other processes see the same state.

## Redis TTL as a "Last Seen" Mechanism

Redis `SET key value EX seconds` sets a key with a TTL. After `seconds`, the key is automatically deleted.

```
SET presence:42 1700000000 EX 30
```

This means: "user 42 is online, expires in 30 seconds."

If we don't refresh the TTL, the key expires. The user is offline. The TTL is the "liveness" signal.

## Heartbeat

A heartbeat is a periodic refresh of the TTL:

```js
setInterval(() => {
  redis.expire(`presence:${userId}`, 30);
}, 10000); // every 10 seconds
```

Every 10 seconds, we refresh the TTL to 30 seconds. This means:

- If the client is alive, the TTL is always between 10 and 30 seconds.
- If the client dies, no more refreshes. The TTL expires. The user is offline.

The relationship between heartbeat interval and TTL:

- `heartbeat_interval < TTL` — the heartbeat is more frequent than the TTL
- If `heartbeat_interval = 10s` and `TTL = 30s`, the server has 30s of grace period (3 missed heartbeats) before marking the user offline.

## Pub/Sub for Cross-Process

If you have 3 Node processes behind a load balancer, a user might be connected to process 1. Processes 2 and 3 don't know.

The fix: pub/sub. When a process changes presence (connect, disconnect, refresh), it publishes to Redis. All processes subscribe and update their local view.

```js
// Publisher (process 1)
await redis.publish('presence:updates', JSON.stringify({ type: 'connect', userId: 42 }));

// Subscriber (process 1, 2, 3)
const subscriber = redis.duplicate();
subscriber.subscribe('presence:updates');
subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  // Update local view, broadcast to WebSocket clients
});
```

Every process sees every presence event. The local view is consistent.

## WebSocket Authentication

The WebSocket endpoint at `ws://localhost:3000` is unauthenticated in project 28. For presence, we need to know *who* is connecting. We authenticate via a token in the query string:

```js
const url = new URL(req.url, 'http://localhost');
const token = url.searchParams.get('token');
const user = jwt.verify(token, SECRET);
```

If the token is invalid, we close the connection with code 1008 (policy violation).

The client includes the token in the URL:

```javascript
const ws = new WebSocket(`ws://localhost:3000?token=${token}`);
```

## The Broadcast to Clients

When a presence event arrives (from Redis pub/sub), we broadcast to all WebSocket clients:

```js
subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ type: 'presence', event }));
    }
  });
});
```

Clients receive `presence` events. They update their UI: green dot, gray dot, etc.

## Common Confusions (read these)

**Confusion 1: "Why not just use a database?"**
A database is too slow. We need sub-millisecond updates. Redis is in-memory.

**Confusion 2: "Why not use WebSocket directly (no Redis)?"**
For single process, yes. For multi-process, we need a shared state. Redis is that shared state.

**Confusion 3: "Why TTL instead of explicit disconnect?"**
Crash detection. If the client crashes, there's no disconnect message. The TTL handles it.

**Confusion 4: "Why heartbeat from the server, not the client?"**
The server is the source of truth for the connection. The client might be slow. The server is faster.

**Confusion 5: "What if Redis is down?"**
The local view is stale. The WebSocket connections still work. When Redis comes back, the state is rebuilt (new connections publish events, refresh TTLs).

**Confusion 6: "What about per-room presence?"**
Out of scope. We have global presence. For per-room, you'd use a different key per room (e.g., `presence:room:general:42`).

**Confusion 7: "Why 30-second TTL and 10-second heartbeat?"**
3x margin. If the client misses 2 heartbeats, the user is still online. After 3 missed, offline. Tunable.

**Confusion 8: "What about WebSocket auth?"**
We use a token in the query string. Other options: token in a message after connection, or a session ID.

## What We Are About to Build

A ~600-line Express app that:

1. Has a WebSocket server with token-based auth
2. Tracks presence with Redis TTL
3. Sends heartbeats every 10 seconds
4. Uses Redis pub/sub for cross-process presence
5. Broadcasts presence events to WebSocket clients

The handlers are unchanged. The new pieces are the presence logic and the WebSocket auth.

In [BUILD.md](./BUILD.md) we will go line by line.
