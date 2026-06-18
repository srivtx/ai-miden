# Project 30: The Presence

> *"Who's online? Who's typing? The server knows. The clients should too."*

In projects 28-29, we have real-time communication (WebSocket for chat, SSE for notifications). But we don't know *who* is connected. The final artifact needs:

- "Alice is online" (green dot)
- "Bob is typing..." (animated dots)
- "3 people viewing this document" (avatar stack)
- "Carol went offline" (gray dot)

This is **presence**. The server tracks who's connected. It broadcasts presence updates when someone connects, disconnects, or changes state (e.g., starts typing).

We use **Redis pub/sub** to share presence across processes. Each server process publishes presence events to Redis. All processes (including itself) subscribe and update their local view.

The flow:
1. Client connects to WebSocket
2. Server publishes `presence:connect` with the user ID
3. All processes receive the event; they mark the user as online
4. Other clients receive a `presence:update` event via WebSocket
5. Client disconnects
6. Server publishes `presence:disconnect`
7. After a TTL (e.g., 30 seconds), the user is marked offline (heartbeat expires)

By the end, the server knows who's online, and clients receive real-time presence updates.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is presence needed? What is the heartbeat pattern?
2. [The Thought](./THOUGHT.md) — How does presence work? What is Redis pub/sub for this?
3. [The Build](./BUILD.md) — Line-by-line construction of presence
4. [The Decisions](./DECISIONS.md) — Why Redis pub/sub? Why TTL? Why not sticky sessions?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

Presence tracks who's connected. We use Redis to store a "user is online" key with a TTL (e.g., 30 seconds). When a client connects, we set the key. When the client disconnects, we delete the key. To keep the key alive while the client is connected, we refresh the TTL every 10 seconds (heartbeat). If the client crashes or the network drops, the TTL expires and the user is marked offline. We use Redis pub/sub to broadcast presence updates across processes.

---

## The Code

```js
const presenceChannel = 'presence:updates';

async function setOnline(userId) {
  await redis.set(`presence:${userId}`, Date.now(), 'EX', 30);
  await redis.publish(presenceChannel, JSON.stringify({ type: 'connect', userId }));
}

async function setOffline(userId) {
  await redis.del(`presence:${userId}`);
  await redis.publish(presenceChannel, JSON.stringify({ type: 'disconnect', userId }));
}

async function refreshPresence(userId) {
  await redis.expire(`presence:${userId}`, 30);
}

async function getOnlineUsers() {
  const keys = await redis.keys('presence:*');
  return keys.map((k) => parseInt(k.split(':')[1]));
}

// Subscribe to presence updates
const subscriber = redis.duplicate();
subscriber.subscribe(presenceChannel);
subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  // Broadcast to all WebSocket clients
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ type: 'presence', event }));
    }
  });
});

// On WebSocket connection
wss.on('connection', async (ws, req) => {
  // Authenticate (from query string)
  const token = new URL(req.url, 'http://localhost').searchParams.get('token');
  let user;
  try {
    user = jwt.verify(token, SECRET);
  } catch (err) {
    ws.close(1008, 'Unauthorized');
    return;
  }

  await setOnline(user.userId);

  // Heartbeat every 10 seconds
  const heartbeat = setInterval(() => refreshPresence(user.userId), 10000);

  ws.on('close', async () => {
    clearInterval(heartbeat);
    await setOffline(user.userId);
  });
});
```

The pain of "I don't know who's online" is solved. The server tracks presence. Clients receive updates in real time.

---

## What You Will Have Learned

- What presence is (tracking who's connected)
- The heartbeat pattern (refresh TTL while connected)
- Redis pub/sub for cross-process presence
- The TTL fallback (if the client crashes, the user is marked offline)
- Authentication for WebSocket (token in query string)

These are the foundations of *real-time awareness*. From here, every project that needs to know who's connected can use presence.
