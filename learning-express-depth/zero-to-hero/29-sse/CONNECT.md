# The Connect

> *"The server has two real-time channels. Now we need presence, co-editing, and voice."*

This project added SSE. The pain of "WebSocket is overkill for one-way push" is solved. The server can push events. The client receives them. Simpler than WebSocket for one-way use cases.

The server now has two real-time channels:

- **WebSocket** (project 28): bidirectional. Chat, collaborative editing.
- **SSE** (project 29): one-way. Notifications, live updates.

But the API is still missing:

1. **No presence** — we don't know who's online. The final artifact needs to show "Alice is online," "Bob is typing," etc.
2. **No co-editing** — we can't edit the same document simultaneously. The final artifact needs Notion-style co-editing.
3. **No voice/video** — we don't have voice channels. The final artifact needs "join a huddle."

Projects 30-32 (rest of Phase 5) will fix these. After Phase 5, the server is a real-time collaborative platform — the foundation of the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

## What Works

- SSE endpoint at `GET /events`
- Welcome event on connection
- Heartbeat every 30 seconds
- Disconnection handling (clears the interval)
- `EventSource` API on the client

## What Doesn't Work

### 1. No presence

We don't know who's online. The final artifact needs to show "Alice is online," "Bob is typing," etc.

**The pain**: Presence. Project 30.

### 2. No co-editing

We can't edit the same document simultaneously. The final artifact needs Notion-style co-editing.

**The pain**: CRDT. Project 31.

### 3. No voice/video

We don't have voice channels. The final artifact needs "join a huddle."

**The pain**: WebRTC. Project 32.

### 4. No RBAC

All authenticated users have the same permissions.

**The pain**: RBAC. Project 33.

### 5. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 6. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 7. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 8. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 9. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 10. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

---

## What This Project Forbids Us From Doing

This server can:

- Push one-way events via SSE
- Send heartbeats to keep connections alive
- Handle client disconnection

It cannot:

- Know who's online (presence)
- Co-edit documents
- Have voice/video
- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 30 | Presence | "I want to know who's online." |
| 31 | CRDT | "I want to co-edit documents." |
| 32 | WebRTC | "I want voice/video channels." |

Project 30 is the natural next step. We have WebSocket and SSE. Now we need to know who's connected.

---

## What You Should Do Now

1. **Read the code.** Notice the SSE endpoint, the heartbeats, the disconnection handling. The HTTP handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Open a browser console.** Use the `EventSource` API. See the welcome event and the heartbeats.
4. **Close the browser tab.** See the server log "SSE client disconnected."
5. **When you are ready**, move to [Project 30: Presence](../30-presence/).
6. **If anything is unclear**, do not proceed. SSE is the foundation of one-way real-time. It must be solid.

---

## A Note on the Bigger Picture

You now have a server with two real-time channels: WebSocket (bidirectional) and SSE (one-way). The right tool for each use case.

From here, the path diverges:

- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice

The server has two real-time channels. The path continues.
