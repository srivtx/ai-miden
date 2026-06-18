# The Decisions

> *"The HTTP connection upgrades. The protocol switches. The conversation begins."*

## Decision 1: ws and not Socket.IO

**Alternatives**:
- **Socket.IO** — higher-level, with rooms, namespaces, fallback to long polling
- **uWebSockets.js** — faster, lower-level
- **Engine.IO** — Socket.IO's underlying engine

**Why ws: It's the de-facto WebSocket library. Simple. Standard. We can learn the WebSocket protocol directly. We use it.

**Trade-off**: No rooms, no namespaces, no fallback. We add those in future projects.

## Decision 2: WebSocket on the same HTTP server

**Alternative**: WebSocket on a separate port (e.g., 3001).

**Why same server: Simpler. One process. The WebSocket endpoint is at the same origin. CORS doesn't apply.

**Trade-off**: The HTTP and WebSocket share the same event loop. Heavy HTTP traffic could slow down WebSocket. For high scale, separate.

## Decision 3: JSON text frames

**Alternative**: Binary frames (Buffers).

**Why JSON: Standard. Readable. Easy to debug. Most APIs use JSON.

**Trade-off**: JSON is larger than binary. For high-throughput, use binary.

## Decision 4: Broadcast to all clients

**Alternative**: Broadcast to specific clients (rooms, direct messages).

**Why all: Simple. The demo is a global chat. We add rooms in a future project.

**Trade-off**: A private message can't be sent. We accept this.

## Decision 5: No authentication

**Alternative**: Verify a token in the handshake.

**Why no: Out of scope. We add auth in a future project.

**Trade-off**: Anyone can connect. The chat is open. We accept this for the demo.

## Decision 6: No persistence

**Alternative**: Store messages in a database. Send the last N to new clients on connect.

**Why no: Out of scope. The demo is a real-time chat without history. We add persistence in a future project.

**Trade-off**: When a client connects, they don't see past messages. We accept this.

## Decision 7: No reconnection handling

**Alternative**: Auto-reconnect on the client. Resync state on reconnect.

**Why no: Out of scope. The client should handle this (with a library like `reconnecting-websocket`).

**Trade-off**: A dropped connection loses messages. We accept this.

## Decision 8: Single process, no Redis

**Alternative**: Use Redis pub/sub to broadcast across processes.

**Why no: We run in a single process. For multi-process, we'd add Redis. We add this in project 30 (presence).

**Trade-off**: Multi-process scaling requires Redis. We accept this.

## Decision 9: No ping/pong

**Alternative**: Periodically send ping frames to detect dead connections.

**Why no: Out of scope. The client should ping. Or the OS will detect dead connections via TCP keepalive.

**Trade-off**: Dead connections stay open until the OS times out. We accept this.

## Decision 10: No compression

**Alternative**: Use permessage-deflate extension to compress messages.

**Why no: Out of scope. For large messages, this would help. Our messages are small.

**Trade-off**: Larger messages use more bandwidth. We accept this.

---

## What We Did Not Decide

- **Socket.IO** — out of scope
- **uWebSockets.js** — out of scope
- **Authentication** — out of scope
- **Persistence** — out of scope
- **Reconnection** — out of scope (client concern)
- **Multi-process with Redis** — out of scope (project 30)
- **Rooms / namespaces** — out of scope
- **Ping / pong** — out of scope
- **Compression** — out of scope
- **Binary frames** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Is Real-Time

For 27 projects, every interaction was HTTP. The client asked; the server answered. The connection closed. The server couldn't push.

Now the server is real-time. WebSocket is established. The server can push anytime. The client receives instantly. The conversation is bidirectional.

This is the foundation of *real-time communication*. WebSocket is non-negotiable for any app that needs live updates. The patterns (`ws`, broadcast, message handling) are universal.

The next 12 projects will assume WebSocket exists. The path diverges:

- **SSE** (project 29): simpler one-way push
- **Presence** (project 30): who's online (with Redis pub/sub)
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

The server is real-time. The path continues.
