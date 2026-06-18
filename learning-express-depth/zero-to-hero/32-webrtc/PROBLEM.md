# The Problem

> *"WebSocket is for text. WebRTC is for voice. The browser becomes a phone."*

## Why Voice Is Hard

In projects 28-31, we have real-time *text* communication. But the final artifact (Cove) needs voice. "Join a huddle" — like in Slack or Discord.

Voice has different requirements than text:

- **Low latency**: 100ms is acceptable. 500ms is annoying. 1s is unusable.
- **Continuous stream**: not discrete messages like chat. A continuous audio stream.
- **Bandwidth**: ~30-100 kbps for voice, ~1-5 Mbps for video. More than text.
- **Synchronization**: both peers must agree on codec, format, network path.

Text WebSocket doesn't fit. We need a different protocol.

## What Pain Is This Solving?

Imagine building a voice chat like Discord. The server needs to:

1. **Find peers**: User A and User B are in the same channel. The server tells them about each other.
2. **Negotiate the connection**: A and B need to agree on codec, network path, etc. This is the *signaling*.
3. **Stream the audio**: once the connection is established, audio flows. Where does it flow?

For (1) and (2), the server is in the middle. The server knows who's in the channel. The server helps A and B find each other.

For (3), the server is *not* in the middle. The audio flows directly between A and B (peer-to-peer). The server doesn't process the audio. This is critical for low latency and bandwidth.

The protocol that does this is **WebRTC**.

## What WebRTC Is

WebRTC (Web Real-Time Communication) is a browser API for peer-to-peer voice, video, and data. The key property: **peer-to-peer**. The server is not in the media path.

WebRTC has three parts:

1. **Signaling**: how peers find each other. The server's role. Any protocol works (WebSocket, SSE, HTTP, etc.).
2. **SDP (Session Description Protocol)**: describes the media (codec, format, etc.). Peers exchange SDP offers and answers.
3. **ICE (Interactive Connectivity Establishment)**: finds the network path between peers. Uses STUN and TURN servers.

The flow:

1. Both peers create an `RTCPeerConnection`.
2. Peer A creates an SDP offer ("here's what I can do").
3. Peer A sends the offer to Peer B via the signaling server.
4. Peer B creates an SDP answer ("here's what I can do").
5. Peer B sends the answer to Peer A via the signaling server.
6. Both peers exchange ICE candidates (network paths).
7. The connection is established. Media flows directly between A and B.

The server's role is *just signaling*. It relays SDP and ICE messages. It doesn't process the media.

## STUN and TURN

For ICE to find the network path, it needs to know the peer's public IP. Most peers are behind NAT (home router, corporate firewall). A **STUN server** helps: it tells the peer its public IP. Google's public STUN server is `stun.l.google.com:19302`.

Sometimes, a direct connection is impossible (symmetric NAT, firewall). A **TURN server** relays the media as a fallback. TURN is a real media server; it costs bandwidth.

For most cases, STUN is enough. TURN is for edge cases.

## What This Project Will Solve

This project will:

1. Add a WebSocket-based signaling server
2. The server relays SDP and ICE messages between peers in the same channel
3. The browser uses `RTCPeerConnection` to establish the peer-to-peer connection
4. Audio (and optionally video) flows directly between peers

By the end, two users can join a voice channel and talk. The server is just a signaling relay; the media is peer-to-peer.

## What This Project Will *Not* Solve

- **TURN server** — we use a public STUN server. For production, you'd run your own TURN.
- **Group calls** (3+ peers) — we do 1:1. For 3+, you'd use an SFU (Selective Forwarding Unit).
- **Recording** — we don't record. For recording, you'd use an SFU or a media server.
- **Noise suppression / echo cancellation** — the browser does this. We don't customize.
- **Mobile push** — we use WebRTC in the browser. For mobile, you'd use a native SDK.

## The Question This Project Answers

> *"How do two browsers talk to each other in real time with low latency?"*

If you can answer: "use WebRTC, the server is just a signaling relay, the peers exchange SDP and ICE, the media flows peer-to-peer," you are ready for project 33.
