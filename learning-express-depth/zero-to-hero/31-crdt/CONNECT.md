# The Connect

> *"The server supports co-editing. Now we need voice, RBAC, and the rest of the production stack."*

This project added Yjs for co-editing. The pain of "two users editing the same document" is solved. Yjs handles the merging. The server is a relay. The CRDT does the work.

But the API is still missing:

1. **No voice/video** — we don't have voice channels. The final artifact needs "join a huddle."
2. **No RBAC** — all authenticated users have the same permissions. No "admin" role, no "owner" role, no "guest" role.

Projects 32-33 will fix these. After project 32, Phase 5 (Real-Time) is complete. Project 33 starts Phase 6 (Production).

## What Works

- Yjs WebSocket server (relay)
- Two clients can edit the same document
- Yjs handles the merging (commutative operations)
- Plain text (no rich text)
- No persistence (in-memory)

## What Doesn't Work

### 1. No voice/video

We don't have voice channels. The final artifact needs "join a huddle."

**The pain**: WebRTC. Project 32.

### 2. No RBAC

All authenticated users have the same permissions. No "admin" role, no "owner" role, no "guest" role.

**The pain**: RBAC. Project 33.

### 3. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 4. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 5. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 6. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 7. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 8. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 9. No persistence for Yjs

Restart the server, the document is gone.

**The pain**: Persistence. Out of scope.

### 10. No awareness

Can't see other users' cursors.

**The pain**: Awareness. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Support co-editing (two users editing the same document)
- Merge changes automatically (Yjs CRDT)
- Relay Yjs updates between clients

It cannot:

- Have voice/video
- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Persist the document across restarts
- Show other users' cursors

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 32 | WebRTC | "I want voice/video channels." |
| 33 | RBAC | "I want role-based permissions." |

Project 32 is the natural next step. We have co-editing. Now we need voice for the final artifact.

---

## What You Should Do Now

1. **Read the code.** Notice the Yjs WebSocket server, the `setupWSConnection` call, the `handleUpgrade` for the HTTP server. The HTTP handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Connect two Yjs clients.** Type in one. See the change in the other.
4. **Connect in two browsers.** See the real-time co-editing.
5. **When you are ready**, move to [Project 32: WebRTC](../32-webrtc/).
6. **If anything is unclear**, do not proceed. CRDTs are the foundation of co-editing. They must be solid.

---

## A Note on the Bigger Picture

You now have a server that supports *co-editing*. Two users can edit the same document in real time. Yjs handles the merging. The server is a relay. The CRDT does the work.

From here, the path diverges:

- **WebRTC** (project 32): voice
- **RBAC** (project 33): permissions

The server supports co-editing. The path continues.
