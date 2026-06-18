# The Connect

> *"The server knows who's online. Now we need co-editing, voice, and the rest of the real-time stack."*

This project added presence. The pain of "I don't know who's online" is solved. The server tracks who's connected with Redis TTL, heartbeats detect crashes, and pub/sub shares across processes. Clients receive real-time presence updates.

But the API is still missing:

1. **No co-editing** — we can't edit the same document simultaneously. The final artifact needs Notion-style co-editing.
2. **No voice/video** — we don't have voice channels. The final artifact needs "join a huddle."

Projects 31-32 (rest of Phase 5) will fix these. After Phase 5, the server is a real-time collaborative platform — the foundation of the final artifact (Cove).

## What Works

- Presence tracking with Redis TTL
- 30-second TTL, 10-second heartbeat
- Pub/sub for cross-process presence
- WebSocket auth via query string token
- Broadcast presence events to WebSocket clients
- Initial presence list on connection

## What Doesn't Work

### 1. No co-editing

We can't edit the same document simultaneously. The final artifact needs Notion-style co-editing.

**The pain**: CRDT. Project 31.

### 2. No voice/video

We don't have voice channels. The final artifact needs "join a huddle."

**The pain**: WebRTC. Project 32.

### 3. No RBAC

All authenticated users have the same permissions.

**The pain**: RBAC. Project 33.

### 4. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 5. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 6. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 7. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 8. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 9. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 10. No per-room presence

We have global presence, not per-channel/per-document.

**The pain**: Per-room presence. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Track who's online
- Detect crashes via TTL
- Share presence across processes
- Broadcast presence events to WebSocket clients

It cannot:

- Co-edit documents
- Have voice/video
- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Show per-room presence

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 31 | CRDT | "I want to co-edit documents." |
| 32 | WebRTC | "I want voice/video channels." |

Project 31 is the natural next step. We have presence. Now we need co-editing for the final artifact.

---

## What You Should Do Now

1. **Read the code.** Notice the presence functions, the pub/sub, the WebSocket auth, the heartbeat. The HTTP handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Connect two clients** with different tokens. See the presence events.
4. **Kill one client.** See the disconnect event.
5. **When you are ready**, move to [Project 31: CRDT](../31-crdt/).
6. **If anything is unclear**, do not proceed. Presence is the foundation of real-time awareness. It must be solid.

---

## A Note on the Bigger Picture

You now have a server that knows who's online. Clients receive real-time presence updates. Multi-process works via Redis pub/sub. Crashes are detected via TTL.

From here, the path diverges:

- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice

The server knows who's online. The path continues.
