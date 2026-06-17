# WebRTC — Peer-to-peer video, audio, and data

## Why it exists (THE PROBLEM)

You want two browsers to talk directly — video call, screen share, file transfer. Going through a server is slow (browser → server → browser). The server sees everything. You pay for server bandwidth for every byte of video. For a 10-minute HD call between 2 people, that's ~300MB of server bandwidth.

**WebRTC** lets browsers talk DIRECTLY to each other. Video goes browser → browser. The server only handles the initial handshake (signaling). After connection, 99.9% of data bypasses the server entirely. Zero server bandwidth for video. Zero server visibility into the call content.

## Definition (very simple)

WebRTC = browser-to-browser real-time communication. Three APIs:
1. **getUserMedia()** — access camera/microphone
2. **RTCPeerConnection** — establish direct P2P connection
3. **RTCDataChannel** — send arbitrary data (text, files, game state)

Two servers are needed only for SETUP:
- **Signaling server** (WebSocket) — exchange connection info (SDP offers/answers, ICE candidates). ~50 lines.
- **STUN/TURN server** — help peers discover their public IP (free Google STUN servers exist). TURN relay is fallback for restrictive networks.

After connection: zero server involvement.

## Real-life analogy

**Without WebRTC (server relay):** You want to tell your friend a secret across a crowded room. Instead of walking over and whispering, you hand a note to a waiter, who walks to your friend and hands them the note. The waiter reads it. You pay the waiter per word.

**With WebRTC (direct connection):** You ask the waiter for your friend's table number. The waiter points. You walk over and whisper directly. The waiter never hears the secret. Free.

**The signaling server is the waiter.** It only does introductions. The actual conversation is P2P.

## The connection flow

```
Browser A                          Signaling Server (WS)                Browser B
   |                                       |                                |
   |-- createOffer() -->                   |                                |
   |   setLocalDescription(offer)          |                                |
   |--- send offer via WS --------------->|--- forward offer ------------>|
   |                                       |                setRemoteDescription(offer)
   |                                       |                createAnswer()
   |                                       |                setLocalDescription(answer)
   |<-- receive answer via WS -----------|<--- forward answer ------------|
   |   setRemoteDescription(answer)        |                                |
   |                                       |                                |
   |==== ICE candidates exchanged via WS ====|==== (discover network paths) ====|
   |                                       |                                |
   |<============ DIRECT P2P CONNECTION ESTABLISHED ======================>|
   |              (video, audio, data flow directly, no server)             |
```

## Key properties

| Property | Server relay | WebRTC |
|---|---|---|
| Video path | Client → Server → Client | Client ↔ Client (direct) |
| Server bandwidth | Every byte × 2 | ~0 (only signaling) |
| Latency | Server hop adds 50-100ms | Direct (lowest possible) |
| Privacy | Server can see/hear | End-to-end encrypted (DTLS-SRTP) |
| Scale limit | Server bottleneck | No server bottleneck for media |
| Fallback | Always works | TURN relay if direct fails (~5% of users) |

## Common confusion

1. **"WebRTC needs a server."** Only for signaling (the initial handshake). After that, zero server. You CAN add a TURN relay for users behind restrictive firewalls (~5% of users), but 95% of connections are truly P2P.

2. **"WebRTC is just for video calls."** DataChannel sends arbitrary data at low latency. Used for: file sharing (Snapdrop), gaming (low-latency game state), collaborative editing (Figma uses WebRTC for cursor sync), torrent-like P2P CDN.

3. **"WebRTC is complex."** The API is verbose (~100 lines for a basic video call) but the concepts are simple: create offer, exchange via signaling, create answer, connect. Libraries like simple-peer reduce it to ~20 lines.

4. **"STUN/TURN servers cost money."** Google provides free STUN servers (`stun:stun.l.google.com:19302`). TURN relay costs money (bandwidth), but you only need it for ~5% of users, and free tiers exist (Twilio, Xirsys).

## Connection to our projects

A WebRTC-based code collaboration feature: two users editing the same file, seeing each other's cursor in real-time via DataChannel. Or: a video call embed in the chat app (level 3, project 22). The signaling server is just our WebSocket chat server with one extra message type (`signal`).
