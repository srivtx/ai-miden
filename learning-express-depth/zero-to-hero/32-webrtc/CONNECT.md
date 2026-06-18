# The Connect

> *"The server has voice. Now we need RBAC, webhooks, payments, tests, Docker, CI/CD, observability, and microservices."*

This project added WebRTC for voice. The pain of "I can't talk to my team" is solved. The server signals. The peers connect. The audio flows directly between them. The server is not in the media path.

**Phase 5 (Real-Time) is now complete!** Projects 28-32 added: WebSocket, SSE, presence, CRDT, WebRTC. The server is a real-time collaborative platform — the foundation of the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

The next 8 projects begin Phase 6 (Production):

| # | Project | Pain Answered |
|---|---------|---------------|
| 33 | RBAC | "I want role-based permissions." |
| 34 | Webhook | "I want to push events to other services." |
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |
| 37 | Container | "I want to deploy reproducibly with Docker." |
| 38 | Pipeline | "I want CI/CD." |
| 39 | Observability | "I want to see metrics." |
| 40 | Microservice | "I want to split into services." |

After Phase 6, the server is a production-ready, real-time, role-based, tested, deployed, observed, distributed system. The complete backend for the final artifact.

## What Works

- WebSocket signaling server
- SDP and ICE relay between peers
- Peer-to-peer audio (no server in media path)
- STUN for NAT traversal
- Channels (different rooms)

## What Doesn't Work

### 1. No RBAC

All authenticated users have the same permissions. No "admin" role, no "owner" role, no "guest" role.

**The pain**: RBAC. Project 33.

### 2. No webhooks

We can't push events to other services.

**The pain**: Webhooks. Project 34.

### 3. No payment

No Stripe integration.

**The pain**: Payment. Project 35.

### 4. No tests

We can't verify anything works automatically.

**The pain**: Tests. Project 36.

### 5. No Docker / CI/CD

We can't deploy reproducibly.

**The pain**: Container. Project 37.

### 6. No observability

We can't see metrics.

**The pain**: Observability. Project 39.

### 7. No microservices

One big monolith. Hard to scale individual components.

**The pain**: Microservices. Project 40.

### 8. No TURN

For symmetric NAT or restrictive firewalls, we'd need a TURN server.

**The pain**: TURN. Out of scope.

### 9. No group calls (3+ peers)

WebRTC is 1:1. For 3+, you need an SFU.

**The pain**: SFU. Out of scope.

### 10. No recording

We don't record calls.

**The pain**: Recording. Out of scope.

---

## What This Project Forbids Us From Doing

This server can:

- Support voice (1:1, peer-to-peer)
- Signal peers via WebSocket
- Relay SDP and ICE
- Use STUN for NAT traversal

It cannot:

- Have role-based permissions
- Push events to other services
- Charge for premium features
- Be tested automatically
- Be deployed reproducibly
- Be observed in production
- Be split into microservices
- Handle 3+ peers in a call
- Record calls

Each is a future project.

---

## The Order of Subsequent Projects

| # | Project | Pain Answered |
|---|---------|---------------|
| 33 | RBAC | "I want role-based permissions." |
| 34 | Webhook | "I want to push events to other services." |
| 35 | Payment | "I want to charge for premium features." |
| 36 | Tests | "I want to verify everything works automatically." |

Project 33 is the natural next step. We have voice. Now we need permissions — who can do what.

---

## What You Should Do Now

1. **Read the code.** Notice the signaling server, the WebRTC flow. The HTTP handlers are unchanged.
2. **Run the experiments** in [BUILD.md](./BUILD.md). Predict the output before running.
3. **Open two browser tabs.** Join the same channel. Talk to each other.
4. **Open a different channel.** Confirm isolation.
5. **When you are ready**, move to [Project 33: RBAC](../33-rbac/).
6. **If anything is unclear**, do not proceed. WebRTC is the foundation of real-time voice. It must be solid.

---

## A Note on the Bigger Picture

**Phase 5 (Real-Time) is complete!** You now have a server that supports:

- Real-time text (WebSocket)
- One-way push (SSE)
- Presence (who's online)
- Co-editing (Yjs CRDT)
- Voice (WebRTC)

The server is a real-time collaborative platform. The foundation of the final artifact (Cove) is in place.

From here, the path diverges into Phase 6 (Production):

- **RBAC** (project 33): permissions
- **Webhook** (project 34): outbound push
- **Payment** (project 35): Stripe
- **Tests** (project 36): automated
- **Container** (project 37): Docker
- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The server is real-time. The path continues.
