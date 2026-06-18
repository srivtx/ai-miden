# The Thought

> *"WebRTC is peer-to-peer. The server signals. The media flows directly."*

## How WebRTC Works

WebRTC establishes a peer-to-peer connection. The steps:

1. **Both peers create an `RTCPeerConnection`**. This is the browser's API for the connection.

2. **Peer A creates an SDP offer**. SDP (Session Description Protocol) describes what A can do: audio codec (Opus), video codec (VP8), network info, etc.

3. **Peer A sends the SDP offer to Peer B via the signaling server**. The server relays. The server doesn't process the SDP.

4. **Peer B creates an SDP answer**. B's answer says what B can do. It's a *response* to A's offer.

5. **Peer B sends the SDP answer to Peer A via the signaling server**. The server relays.

6. **Both peers exchange ICE candidates**. ICE (Interactive Connectivity Establishment) finds the network path. Each peer discovers its public IP (via STUN) and the possible routes. The candidates are exchanged via the signaling server.

7. **The connection is established**. The peers have negotiated. The browser knows the path, the codec, everything.

8. **Media flows directly**. Audio (and video) flow from A's microphone to A's browser, through the peer-to-peer connection, to B's browser, to B's speakers. The server is not involved.

## The Signaling Server

The server's only job is to relay signaling messages. It doesn't process them. It doesn't even know what they are (SDP, ICE, etc.). It just forwards them.

In this project, we use WebSocket (project 28) for signaling. Each peer connects to the server with a channel name. The server relays messages between peers in the same channel.

```js
const signaling = new Map(); // channel -> Set of WebSocket clients

wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const channel = url.pathname.slice(1);

  if (!signaling.has(channel)) signaling.set(channel, new Set());
  signaling.get(channel).add(ws);

  ws.on('message', (data) => {
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

The server is a *relay*. It doesn't understand the messages. It just forwards them.

## The Browser

The browser uses `RTCPeerConnection` to establish the connection. The flow:

```javascript
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
});

// Add the local audio stream (from the user's microphone)
const localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

// When a remote track arrives, play it
pc.ontrack = (event) => {
  const remoteAudio = new Audio();
  remoteAudio.srcObject = event.streams[0];
  remoteAudio.play();
};

// Signaling: send ICE candidates
pc.onicecandidate = (event) => {
  if (event.candidate) {
    ws.send(JSON.stringify({ type: 'ice', candidate: event.candidate }));
  }
};

// Signaling: receive an offer, create an answer
ws.onmessage = async (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'offer') {
    await pc.setRemoteDescription(message.offer);
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    ws.send(JSON.stringify({ type: 'answer', answer }));
  } else if (message.type === 'answer') {
    await pc.setRemoteDescription(message.answer);
  } else if (message.type === 'ice') {
    await pc.addIceCandidate(message.candidate);
  }
};

// The "first" peer creates the offer
if (isFirstPeer) {
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  ws.send(JSON.stringify({ type: 'offer', offer }));
}
```

The browser handles the WebRTC details. The server is just a relay.

## STUN and TURN

For ICE to find the network path, it uses STUN and TURN:

- **STUN**: tells the peer its public IP. The peer uses this to know how it's seen from the internet. Google's public STUN server is `stun.l.google.com:19302`.
- **TURN**: relays media when a direct connection is impossible. Costs bandwidth.

For our use case, STUN is enough. TURN is for production.

## Common Confusions (read these)

**Confusion 1: "Why not just stream audio through WebSocket?"**
WebSocket is text. Audio is binary and continuous. WebSocket is not optimized for low-latency streaming. WebRTC is.

**Confusion 2: "Why peer-to-peer? Why not through the server?"**
Latency. Server is in the middle → 2x latency. Peer-to-peer → 1x latency. Also bandwidth: server doesn't process the media.

**Confusion 3: "Why does the server need to know about the channel?"**
For routing. The server is a relay; it needs to know which peers are in the same channel to relay messages between them.

**Confusion 4: "What if 3+ peers are in a channel?"**
WebRTC is 1:1. For 3+, you need an SFU (Selective Forwarding Unit), like Janus, mediasoup, or LiveKit. Or you can do a mesh (each peer connects to every other peer) — works for 3-4 peers, doesn't scale.

**Confusion 5: "Why is the server 'dumb'?"**
Because the protocol is peer-to-peer. The server has no role in the media path. It just helps the peers find each other.

**Confusion 6: "What about authentication?"**
Anyone with the channel name can connect. For auth, you'd verify a token in the WebSocket handshake. We add this in project 33 (RBAC).

**Confusion 7: "What about recording?"**
Out of scope. For recording, you'd use an SFU that records the media as it forwards.

**Confusion 8: "What about screen sharing?"**
WebRTC supports it. The browser uses `getDisplayMedia()`. Out of scope for this project.

## What We Are About to Build

A ~650-line Express app that:

1. Has a WebSocket-based signaling server
2. The server relays SDP and ICE messages between peers
3. The browser uses `RTCPeerConnection` to establish the connection
4. Audio flows peer-to-peer

The HTTP handlers are unchanged. The new piece is the WebRTC signaling WebSocket.

In [BUILD.md](./BUILD.md) we will go line by line.
