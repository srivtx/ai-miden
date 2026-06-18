# The Connect

> *"The server is real-time. Now we need SSE, presence, and the rest of the real-time stack."*

This project added WebSocket. The pain of "the server can't push to the client" is solved. The server can broadcast anytime. The clients receive in real time. The chat example is the foundation for notifications, presence, and co-editing.

But the API is still missing:

1. **No SSE** — for simpler one-way push (server to client), SSE is a lighter alternative.
2. **No presence** — we don't know who's online.
3. **No co-editing** — we can't edit the same document simultaneously.
4. **No voice/video** — we don't have WebRTC.

Projects 29-32 (rest of Phase 5) will fix these. After Phase 5, the server is a real-time collaborative platform — the foundation of the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

## What Works

- WebSocket server attached to the HTTP server
- Connection, message, close, error events
- Broadcast to all clients
- Welcome message on connection
- JSON text frames

## What Doesn't Work

### 1. No SSE

For one-way push (server to client), SSE is a lighter alternative. Out of scope for this project; project 29.

**The pain**: SSE. Project 29.

### 2. No presence

We don't know who's online. The final artifact needs to show "Alice is online," "Bob is typing," etc.

**The pain**: Presence. Project 30.

### 3. No co-editing

We can't edit the same document simultaneously. The final artifact needs Notion-style co-editing.

**The pain**: CRDT. Project 31.

### 4. No voice/video

We don't have voice channels. The final artifact needs "join a huddle."

**The pain**: WebRTC. Project 32.

### 5. No RBAC

All authenticated users have the same permissions.

**The pain**: RBAC. Project 33.

### 6. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 7. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 8. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 9. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 10. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

---

## What This Project Forbids Us From Doing

This server can:

- Push updates to clients in real time
- Accept messages from clients
- Broadcast to all connected clients

It cannot:

- Push one-way (without WebSocket overhead)
- Know who's online
- Co-edit documents
- Have voice/video
- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 29 | SSE | "I want simpler one-way push." |
| 30 | Presence | "I want to know who's online." |
| 31 | CRDT | "I want to co-edit documents." |
| 32 | WebRTC | "I want voice/video channels." |

Project 29 is the natural next step. WebSocket is bidirectional. SSE is one-way. For notifications, SSE is simpler.

---

## What You Should Do Now

1. **Read the code.** Notice the WebSocket server, the connection event, the broadcast. The HTTP handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Connect a client.** Send a message. See the broadcast.
4. **Connect two clients.** See both receive.
5. **When you are ready**, move to [Project 29: SSE](../29-sse/).
6. **If anything is unclear**, do not proceed. WebSocket is the foundation of every real-time app. It must be solid.

---

## A Note on the Bigger Picture

You now have a *real-time* server. The server can push to clients. Clients can send messages. The conversation is bidirectional.

From here, the path diverges:

- **SSE** (project 29): simpler one-way push
- **Presence** (project 30): who's online
- **CRDT** (project 31): co-editing
- **WebRTC** (project 32): voice

The server is real-time. The path continues.
