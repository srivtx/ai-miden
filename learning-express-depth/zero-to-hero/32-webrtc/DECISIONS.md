# The Decisions

> *"WebRTC is peer-to-peer. The server signals. The media flows directly."*

## Decision 1: WebRTC and not a media server

**Alternatives**:
- **Janus** — media server, supports many features
- **mediasoup** — SFU library
- **LiveKit** — full WebRTC platform
- **Twilio** — hosted WebRTC
- **Agora** — hosted WebRTC

**Why WebRTC: Peer-to-peer is simpler for 1:1. No media server to run. The browser has the API built-in.

**Trade-off**: For 3+ peers, you need an SFU. For production, you'd use a media server (Janus, mediasoup, LiveKit).

## Decision 2: STUN and not TURN

**Alternative**: TURN server.

**Why STUN: Free public servers. Works for most cases. No infrastructure.

**Trade-off**: For symmetric NAT or restrictive firewalls, you'd need TURN.

## Decision 3: 1:1 and not group

**Alternative**: Mesh network (each peer connects to every other).

**Why 1:1: Simpler. The mesh approach works for 3-4 peers, but doesn't scale.

**Trade-off**: For 3+ peers, you'd use an SFU.

## Decision 4: WebSocket signaling

**Alternative**: SSE, HTTP, any transport.

**Why WebSocket: We already have it (project 28). It's bidirectional. The signaling messages are small.

**Trade-off**: None. WebSocket is the right tool.

## Decision 5: The server is dumb

The server doesn't process the media. It just relays signaling messages.

**Why: Peer-to-peer. The server has no role in the media path. This is the whole point of WebRTC.

**Trade-off**: For 3+ peers, the server needs to be in the media path (SFU). For 1:1, it's not.

## Decision 6: Audio only and not video

**Alternative**: Video.

**Why audio: Simpler. The pattern is the same for video. The bandwidth is lower. The latency requirement is similar.

**Trade-off**: No video. We accept this for the demo.

## Decision 7: No recording

**Alternative**: Record the media as it flows.

**Why no: Out of scope. For recording, you'd use an SFU or a media server.

**Trade-off**: Can't record calls. We accept this.

## Decision 8: No authentication

**Alternative**: Verify a token in the WebSocket handshake.

**Why no: Out of scope. We add auth in project 33 (RBAC).

**Trade-off**: Anyone with the channel name can join. We accept this.

## Decision 9: No group chat (3+ peers)

**Alternative**: SFU for group calls.

**Why no: Out of scope. We'd need a media server.

**Trade-off**: 1:1 only. We accept this.

## Decision 10: No screen sharing

**Alternative**: Use `getDisplayMedia` for screen sharing.

**Why no: Out of scope. Same pattern as audio/video.

**Trade-off**: No screen sharing. We accept this.

---

## What We Did Not Decide

- **TURN server** — out of scope
- **Group calls (3+ peers)** — out of scope (need SFU)
- **Recording** — out of scope
- **Video** — out of scope
- **Authentication** — out of scope
- **Permissions (who can join)** — out of scope
- **Screen sharing** — out of scope
- **Noise suppression** — out of scope (browser default)
- **Custom codec selection** — out of scope (browser default)
- **TURN credentials** — out of scope

Each is a future decision.

---

## The Meta-Decision: The Server Has Voice

For 31 projects, we had real-time text. We couldn't talk to each other.

Now the server has voice. WebRTC establishes a peer-to-peer connection. The server signals. The audio flows directly between peers. The server is not in the media path.

**Phase 5 (Real-Time) is now complete!** Projects 28-32 added: WebSocket, SSE, presence, CRDT, WebRTC. The server is a real-time collaborative platform — the foundation of the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

The next 8 projects begin Phase 6 (Production): RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices.

The server has voice. The path continues.
