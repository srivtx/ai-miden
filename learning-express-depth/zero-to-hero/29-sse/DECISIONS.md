# The Decisions

> *"SSE is a long-running HTTP response. The server writes events. The client reads events."*

## Decision 1: SSE and not WebSocket for one-way push

**Alternative**: WebSocket (project 28) for everything.

**Why SSE for one-way: Simpler. Less protocol overhead. Standard HTTP. Auto-reconnect in the browser. No `ws` library on the client.

**Trade-off**: SSE is one-way. For two-way, use WebSocket.

## Decision 2: 30-second heartbeat

**Alternative**: 60-second, 5-second, no heartbeat.

**Why 30 seconds: A balance between keeping the connection alive and not spamming the client. Most proxies time out idle connections at 60 seconds. 30s is well within that.

**Trade-off**: A heartbeat every 30s adds traffic. Negligible.

## Decision 3: No authentication

**Alternative**: Verify a token in the query string.

**Why no: Out of scope. We add auth in a future project.

**Trade-off**: Anyone can connect. We accept this for the demo.

## Decision 4: No client-to-server messaging

**Alternative**: Use WebSocket for two-way.

**Why no: SSE is one-way. For two-way, use WebSocket. We don't want to add a fake "send" mechanism via POST.

**Trade-off**: A client can't send events. We accept this.

## Decision 5: `text/event-stream`

The standard content type for SSE.

**Alternative**: Custom content type.

**Why standard: The browser's `EventSource` API knows how to handle `text/event-stream`. Custom types would require custom client code.

**Trade-off**: None. Use the standard.

## Decision 6: No compression

**Alternative**: Use gzip or other compression.

**Why no: SSE messages are small. Compression adds complexity.

**Trade-off**: Larger messages use more bandwidth. We accept this.

## Decision 7: `flushHeaders()` immediately

We call `res.flushHeaders()` to send the headers immediately. This is important for SSE — we want the client to know the connection is open.

**Alternative**: Wait for the first event.

**Why flush: The client connects. We send headers (200 OK, text/event-stream). The client knows the connection is open. We send events as they happen.

**Trade-off**: None. Always flush.

## Decision 8: No `Last-Event-ID` handling

The browser sends `Last-Event-ID` on reconnection. We could use this to send missed events. We don't.

**Why no: Out of scope. The client doesn't need to replay events. If it does, we'd persist events to a database and replay on reconnect.

**Trade-off**: A disconnected client misses events. We accept this.

## Decision 9: No client tracking

We don't track connected clients in a Set. We could.

**Why no: For the demo, we don't need to broadcast to specific clients. We just send events to the current client. If we need broadcast, we'd add tracking.

**Trade-off**: Can't broadcast. We accept this.

## Decision 10: Same port as HTTP

**Alternative**: SSE on a separate port.

**Why same port: Simpler. One server. No CORS issues.

**Trade-off**: HTTP traffic could affect SSE throughput. For high scale, separate.

---

## What We Did Not Decide

- **Authentication** — out of scope
- **Persistence** — events are not stored
- **Multi-process with Redis** — out of scope (project 30)
- **Compression** — out of scope
- **Client tracking** — out of scope
- **Broadcast** — out of scope
- **`Last-Event-ID`** — out of scope
- **CORS** — out of scope (same origin for now)
- **Binary events** — out of scope (use WebSocket)
- **Custom retry intervals** — out of scope (browser default)

Each is a future decision.

---

## The Meta-Decision: The Server Has Two Real-Time Channels

For 28 projects, every interaction was HTTP. The server couldn't push.

Now the server has two real-time channels:

- **WebSocket** (project 28): bidirectional. Chat, collaborative editing.
- **SSE** (project 29): one-way. Notifications, live updates.

The right tool for each use case. Simple where possible.

This is the foundation of *real-time communication*. The patterns (`ws`, `text/event-stream`, `EventSource`) are universal.

The next 11 projects will assume both WebSocket and SSE exist. The path diverges:

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

The server has two real-time channels. The path continues.
