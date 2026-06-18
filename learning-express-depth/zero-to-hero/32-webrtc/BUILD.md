# The Build

> *"WebRTC is peer-to-peer. The server signals. The media flows directly."*

We are going to add WebRTC for voice. The change from project 31: add a WebSocket-based signaling server.

## The Code

### The Signaling Server

```js
const signaling = new Map(); // channel -> Set of WebSocket clients

wss.on('connection', (ws, req) => {
  // Extract channel from URL path
  const url = new URL(req.url, 'http://localhost');
  const channel = url.pathname.slice(1); // e.g., 'general' from '/general'

  // Add to the channel's set
  if (!signaling.has(channel)) signaling.set(channel, new Set());
  signaling.get(channel).add(ws);

  logger.info({ channel, clientCount: signaling.get(channel).size }, 'Peer joined channel');

  // Relay signaling messages to other peers in the same channel
  ws.on('message', (data) => {
    for (const client of signaling.get(channel)) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(data.toString());
      }
    }
  });

  // Remove on disconnect
  ws.on('close', () => {
    signaling.get(channel)?.delete(ws);
    logger.info({ channel }, 'Peer left channel');
  });
});
```

The server is a *relay*. It doesn't understand the messages. It just forwards them between peers in the same channel.

### The Browser

```html
<!DOCTYPE html>
<html>
<head>
  <title>WebRTC Voice</title>
</head>
<body>
  <h1>Voice Channel: <span id="channel"></span></h1>
  <button id="join">Join Channel</button>
  <button id="leave" disabled>Leave</button>
  <audio id="remoteAudio" autoplay></audio>
  <script>
    const channel = window.location.pathname.slice(1);
    document.getElementById('channel').textContent = channel;

    let pc, ws, localStream;

    document.getElementById('join').onclick = async () => {
      // Connect to signaling server
      ws = new WebSocket(`ws://${window.location.host}/${channel}`);

      // Get the local audio stream
      localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Create the peer connection
      pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
      });

      // Add the local audio track
      localStream.getTracks().forEach((track) => pc.addTrack(track, localStream));

      // When a remote track arrives, play it
      pc.ontrack = (event) => {
        const remoteAudio = document.getElementById('remoteAudio');
        remoteAudio.srcObject = event.streams[0];
      };

      // Send ICE candidates
      pc.onicecandidate = (event) => {
        if (event.candidate) {
          ws.send(JSON.stringify({ type: 'ice', candidate: event.candidate }));
        }
      };

      // Handle signaling messages
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

      ws.onopen = async () => {
        // The first peer creates the offer
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        ws.send(JSON.stringify({ type: 'offer', offer }));
        document.getElementById('join').disabled = true;
        document.getElementById('leave').disabled = false;
      };
    };

    document.getElementById('leave').onclick = () => {
      pc?.close();
      ws?.close();
      localStream?.getTracks().forEach((track) => track.stop());
      document.getElementById('join').disabled = false;
      document.getElementById('leave').disabled = true;
    };
  </script>
</body>
</html>
```

The browser uses `RTCPeerConnection` to establish the connection. The server is just a signaling relay.

## Test It

1. Open `http://localhost:3000/general` in two browser tabs.
2. Click "Join Channel" in both.
3. Allow microphone access.
4. Speak into the microphone. The other tab should hear the audio.

The pain of "I can't talk to my team" is solved. The server signals. The peers connect. The audio flows directly between them.

---

## Experiments

### Experiment 1: Use a TURN server

For production, you'd run a TURN server. For dev, STUN is enough. Try adding a TURN:

```js
const pc = new RTCPeerConnection({
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'turn:turn.example.com:3478', username: 'user', credential: 'pass' },
  ],
});
```

### Experiment 2: Multiple channels

```bash
# Tab 1
http://localhost:3000/channel1

# Tab 2
http://localhost:3000/channel1

# Tab 3
http://localhost:3000/channel2
```

Tabs 1 and 2 are in the same channel. Tab 3 is in a different channel. Tabs 1 and 2 can talk; Tab 3 is isolated.

### Experiment 3: Add video

```js
const localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
```

Add video to the stream. Add a `<video>` element to display the remote video.

### Experiment 4: Use an SFU for 3+ peers

For 3+ peers, you need an SFU (Selective Forwarding Unit). Examples: Janus, mediasoup, LiveKit. The SFU forwards media between peers, so the server is in the media path (but it's optimized for forwarding).

### Experiment 5: Add screen sharing

```js
const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
displayStream.getTracks().forEach((track) => pc.addTrack(track, displayStream));
```

Add screen sharing via `getDisplayMedia`.

---

### Combined WebSocket Relay (Cove Editor)

The chat WebSocket now relays **all** message types, not just `chat`:

```
Message types forwarded: chat, draw, doc-sync, webrtc-offer, ice-candidate
```

**Draw history replay**: the server keeps the last 200 draw operations in memory. When a new client connects, it replays the full history so the refreshed tab sees existing drawings.

```js
const drawHistory = [];
ws.on("message", (data) => {
  const msg = JSON.parse(data);
  if (msg.type === "draw") {
    drawHistory.push(msg);
    if (drawHistory.length > 200) drawHistory.shift();
  }
});
// On new connection: ws.send({ type: "draw:history", ops: drawHistory });
```

**Doc content sync**: the server stores the latest collaborative doc content. New clients receive it on connect.

```js
let docContent = "";
if (msg.type === "doc-sync") docContent = msg.content;
// On new connection: ws.send({ type: "doc-sync", content: docContent });
```

**CORS**: manually added (not a library) so the Cove editor at `file://` or served statically can call the API. Also serves the editor at `/cove/editor.html` via `express.static`.

```js
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  if (req.method === "OPTIONS") return res.sendStatus(200);
  next();
});
app.use("/cove", express.static(path.join(__dirname, "../../cove")));
```

---

## Summary

You now have WebRTC for voice. The server signals. The peers connect. The audio flows directly between them. The server is not in the media path.

This is the foundation of *real-time voice/video*. From here, every project that needs voice or video can use WebRTC. The patterns (signaling, SDP, ICE, peer-to-peer) are universal.

**Phase 5 (Real-Time) is now complete!** Projects 28-32 added: WebSocket, SSE, presence, CRDT, WebRTC. The server is a real-time collaborative platform — the foundation of the final artifact (Cove, the Slack × Notion × Figma-lite hybrid).

The next 8 projects begin Phase 6 (Production): RBAC, webhooks, payments, tests, Docker, CI/CD, observability, microservices.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
