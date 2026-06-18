# The Decisions

> *"A key in Redis with a TTL. Refresh the TTL on heartbeat. The key dies if the heartbeat stops. The user is offline."*

## Decision 1: Redis TTL and not a database

**Alternative**: Store online status in a database column.

**Why Redis: Sub-millisecond updates. In-memory. The TTL is automatic (no cleanup job needed).

**Trade-off**: A database is more durable. We don't need durability for presence (we re-detect via heartbeat).

## Decision 2: 30-second TTL and 10-second heartbeat

**Alternative**: 60s TTL, 5s heartbeat, etc.

**Why 30s TTL, 10s heartbeat: 3x margin. The server has 30 seconds of grace period (3 missed heartbeats) before marking the user offline.

**Trade-off**: A network blip of >30s would mark a user offline, even if they come back. We accept this.

## Decision 3: Heartbeat from the server, not the client

**Alternative**: The client sends a heartbeat message periodically.

**Why server-side: The server is the source of truth for the connection. The client might be slow. The server controls the timing.

**Trade-off**: If the server is slow, the heartbeat is delayed. We accept this.

## Decision 4: Pub/sub for cross-process

**Alternative**: Each process has its own state. Clients connect to a specific process (sticky sessions).

**Why pub/sub: No sticky sessions. The client can connect to any process. The presence is shared.

**Trade-off**: Adds complexity (Redis pub/sub). For single-process, we could skip this.

## Decision 5: Token in query string for WebSocket auth

**Alternative**: Token in a message after connection. Or session ID.

**Why query string: Simple. The client opens `ws://...?token=abc`. The server verifies in the `connection` handler.

**Trade-off**: The token is in the URL. It could be logged. For sensitive apps, use a message-based auth.

## Decision 6: No per-room presence

**Alternative**: Track who's in each room separately.

**Why no: Out of scope. The final artifact has many features; presence is the foundation. Per-room presence is a future project.

**Trade-off**: Can't see "who's in this room." We accept this.

## Decision 7: No typing indicator

**Alternative**: Use a separate channel for typing events.

**Why no: Out of scope. The pattern is the same as presence.

**Trade-off**: Can't show "Bob is typing." We accept this.

## Decision 8: No last-seen

**Alternative**: Store the last disconnect time in the database.

**Why no: Out of scope. The pattern is "set the timestamp on disconnect."

**Trade-off**: Can't show "last seen 5 minutes ago." We accept this.

## Decision 9: No viewing counter

**Alternative**: Track who's viewing each document.

**Why no: Out of scope. Same pattern as presence, but per-document.

**Trade-off**: Can't show "3 people viewing this." We accept this.

## Decision 10: `redis.keys` for getting online users

`getOnlineUsers` uses `redis.keys('presence:*')` to find all online users.

**Alternative**: Maintain a Redis Set of online users.

**Why keys: Simpler. We don't need atomic operations on a Set. `KEYS` is O(n) but n is small (number of online users).

**Trade-off**: `KEYS` is O(n) and blocks Redis. For large numbers of online users, use a Set (`SADD` / `SMEMBERS`).

---

## What We Did Not Decide

- **Per-room presence** — out of scope
- **Typing indicator** — out of scope
- **Last seen** — out of scope
- **Viewing counter** — out of scope
- **Sticky sessions** — out of scope (we use pub/sub)
- **Cross-region** — out of scope
- **WebSocket auth via message** — out of scope (we use query string)
- **Atomic operations on a Set** — out of scope (we use KEYS)
- **Compression** — out of scope
- **Custom retry intervals** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Knows Who's Online

For 29 projects, we had real-time communication (WebSocket, SSE). But we didn't know who was connected.

Now the server knows. Redis stores the source of truth. Heartbeats detect crashes. Pub/sub shares across processes. Clients receive updates in real time.

This is the foundation of *real-time awareness*. From here, every project that needs to know who's connected can use presence. The patterns (Redis TTL, heartbeat, pub/sub) are universal.

The next 10 projects will assume presence exists. The path diverges:

- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server knows who's online. The path continues.
