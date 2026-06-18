# The Build

> *"A key in Redis with a TTL. Refresh the TTL on heartbeat. The key dies if the heartbeat stops. The user is offline."*

We are going to add presence. The change from project 29: add presence tracking with Redis TTL, heartbeats, pub/sub for cross-process, and WebSocket auth.

## The Code

### The Presence Logic

```js
const PRESENCE_CHANNEL = 'presence:updates';
const PRESENCE_TTL = 30; // seconds
const HEARTBEAT_INTERVAL = 10; // seconds

async function setOnline(userId) {
  await redis.set(`presence:${userId}`, Date.now(), 'EX', PRESENCE_TTL);
  await redis.publish(PRESENCE_CHANNEL, JSON.stringify({ type: 'connect', userId }));
}

async function setOffline(userId) {
  await redis.del(`presence:${userId}`);
  await redis.publish(PRESENCE_CHANNEL, JSON.stringify({ type: 'disconnect', userId }));
}

async function refreshPresence(userId) {
  await redis.expire(`presence:${userId}`, PRESENCE_TTL);
}

async function getOnlineUsers() {
  const keys = await redis.keys('presence:*');
  return keys.map((k) => parseInt(k.split(':')[1]));
}
```

### The Pub/Sub Subscriber

```js
const subscriber = redis.duplicate();
subscriber.subscribe(PRESENCE_CHANNEL);
subscriber.on('message', (channel, message) => {
  const event = JSON.parse(message);
  // Broadcast to all WebSocket clients
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ type: 'presence', event }));
    }
  });
});
```

### The WebSocket Connection

```js
wss.on('connection', async (ws, req) => {
  // Authenticate via token in query string
  const url = new URL(req.url, 'http://localhost');
  const token = url.searchParams.get('token');
  let user;
  try {
    user = jwt.verify(token, SECRET);
  } catch (err) {
    ws.close(1008, 'Unauthorized');
    return;
  }

  logger.info({ userId: user.userId }, 'WebSocket authenticated');

  // Mark online and publish
  await setOnline(user.userId);

  // Send the current online users
  const online = await getOnlineUsers();
  ws.send(JSON.stringify({ type: 'presence:list', users: online }));

  // Heartbeat
  const heartbeat = setInterval(() => refreshPresence(user.userId), HEARTBEAT_INTERVAL * 1000);

  ws.on('close', async () => {
    clearInterval(heartbeat);
    await setOffline(user.userId);
  });
});
```

### The flow

1. Client connects with a token
2. Server verifies the token
3. Server marks the user online (Redis SET with TTL + publish)
4. Server sends the list of currently online users
5. Server starts a heartbeat (refresh TTL every 10 seconds)
6. On disconnect, server marks the user offline (Redis DEL + publish)
7. Other clients receive `presence:connect` and `presence:disconnect` events

## Test It

```javascript
// Client 1 (Alice)
const ws1 = new WebSocket(`ws://localhost:3000?token=${tokenForAlice}`);
ws1.onmessage = (e) => console.log(JSON.parse(e.data));

// Client 2 (Bob)
const ws2 = new WebSocket(`ws://localhost:3000?token=${tokenForBob}`);
ws2.onmessage = (e) => console.log(JSON.parse(e.data));
```

When Alice connects, Bob receives:
```json
{ "type": "presence", "event": { "type": "connect", "userId": 1 } }
```

When Bob connects, Alice receives:
```json
{ "type": "presence", "event": { "type": "connect", "userId": 2 } }
```

When Alice disconnects, Bob receives:
```json
{ "type": "presence", "event": { "type": "disconnect", "userId": 1 } }
```

The pain of "I don't know who's online" is solved. The server tracks presence. Clients receive real-time updates.

---

## Experiments

### Experiment 1: Simulate a crash

Connect a client. Kill the process. Wait 30 seconds. Check `redis-cli keys 'presence:*'`. The key is gone. The user is offline.

### Experiment 2: Multiple processes

Run two Node processes on different ports (e.g., 3000 and 3001). Connect a client to process 1. The presence event is published to Redis. Process 2's subscriber receives it. The local view on process 2 is updated.

### Experiment 3: Get the list of online users

```js
app.get('/online', authMiddleware, asyncHandler(async (req, res) => {
  const online = await getOnlineUsers();
  res.json({ online });
}));
```

### Experiment 4: Typing indicator

```js
// On typing
await redis.publish('typing', JSON.stringify({ userId, channel: 'general' }));

// Subscriber
const typingSub = redis.duplicate();
typingSub.subscribe('typing');
typingSub.on('message', (channel, message) => {
  // Broadcast to WebSocket clients in the same channel
});
```

A separate channel for typing. Clients subscribe to typing events for the channels they care about.

### Experiment 5: Last seen

When a user disconnects, store the timestamp:

```js
await setOffline(userId);
await db('users').where({ id: userId }).update({ last_seen: Date.now() });
```

Now `GET /users/:id` includes `last_seen`.

---

## Summary

You now have presence. The server tracks who's online. Clients receive real-time updates. Multi-process works via Redis pub/sub. Crashes are detected via TTL.

This is the foundation of *real-time awareness*. From here, every project that needs to know who's connected can use presence. The patterns (Redis TTL, heartbeat, pub/sub) are universal.

In project 31, we will add **CRDT** (Conflict-free Replicated Data Type) for co-editing documents. Two users can edit the same document simultaneously without conflicts.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
