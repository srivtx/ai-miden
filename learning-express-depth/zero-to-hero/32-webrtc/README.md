# Project 32: The WebRTC Voice Channel

> *"WebSocket is for text. WebRTC is for voice and video. The browser becomes a phone."*

In projects 28-31, we have real-time text communication (WebSocket, SSE, Yjs). But the final artifact (Cove) needs *voice channels*: "join a huddle," talk to your team, like in Slack.

**WebRTC** (Web Real-Time Communication) is a browser API for peer-to-peer voice, video, and data. It establishes a direct connection between two browsers. The server's role is *signaling*: helping the two peers find each other and exchange the metadata needed to establish the connection. After that, the peers communicate directly (peer-to-peer), not through the server.

The flow:
1. User A and User B both join a "channel" (e.g., a voice channel)
2. The server signals User A about User B (and vice versa)
3. The browsers exchange *SDP offers/answers* and *ICE candidates* via the server
4. A direct peer-to-peer connection is established
5. Audio flows directly between A and B (the server is not in the audio path)

We use the browser's built-in `RTCPeerConnection` API. The server is just a signaling relay (via WebSocket or any other transport).

By the end, two users can join a voice channel and talk to each other, peer-to-peer, with the server only handling signaling.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is voice hard? What is WebRTC?
2. [The Thought](./THOUGHT.md) — How does WebRTC work? What is signaling? What are STUN/TURN?
3. [The Build](./BUILD.md) — Line-by-line construction of the signaling server
4. [The Decisions](./DECISIONS.md) — Why WebRTC? Why peer-to-peer? Why a separate server?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

WebRTC is a browser API for peer-to-peer voice, video, and data. The server's role is *signaling*: helping the two peers find each other and exchange the metadata (SDP and ICE candidates) needed to establish the direct connection. After signaling, the peers communicate directly (audio/video flows peer-to-peer, not through the server). The server is a relay for signaling messages; the actual media is peer-to-peer.

---

## The Code

The server is a signaling relay. We use WebSocket (project 28) to relay signaling messages.

```js
// Signaling server
const signaling = new Map(); // channel -> Set of WebSocket clients

wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const channel = url.pathname.slice(1); // e.g., 'general'

  if (!signaling.has(channel)) signaling.set(channel, new Set());
  signaling.get(channel).add(ws);

  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    // Relay to all other clients in the same channel
    for (const client of signaling.get(channel)) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    }
  });

  ws.on('close', () => {
    signaling.get(channel)?.delete(ws);
  });
});
```

The browser uses `RTCPeerConnection` to establish the peer-to-peer connection. The server is just a signaling relay.

The pain of "I can't talk to my team" is solved. The server signals. The peers connect. The audio flows.

---

## What You Will Have Learned

- What WebRTC is (peer-to-peer voice/video)
- The role of signaling (the server is just a relay for metadata)
- The `RTCPeerConnection` API
- SDP offers/answers and ICE candidates
- The difference between signaling and media (signaling goes through the server; media is peer-to-peer)

These are the foundations of *real-time voice/video*. From here, every project that needs voice or video can use WebRTC.
