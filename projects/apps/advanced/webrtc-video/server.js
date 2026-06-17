// WebRTC Video Call — Signaling server (WebSocket) + peer connection management.
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const rooms = new Map(); // roomId -> Set of socket IDs

app.use(express.static('public'));

io.on('connection', (socket) => {
  console.log(`Connected: ${socket.id}`);

  // Join a room
  socket.on('join-room', (roomId) => {
    socket.join(roomId);
    if (!rooms.has(roomId)) rooms.set(roomId, new Set());
    rooms.get(roomId).add(socket.id);

    // Tell existing peers about the new peer
    socket.to(roomId).emit('user-joined', socket.id);

    // Tell the new peer about existing peers
    const others = [...rooms.get(roomId)].filter(id => id !== socket.id);
    socket.emit('existing-users', others);

    console.log(`${socket.id} joined room ${roomId} (${rooms.get(roomId).size} users)`);
  });

  // RELAY SIGNALING MESSAGES between peers (never inspect them)
  socket.on('signal', ({ to, from, data }) => {
    io.to(to).emit('signal', { from, data });
  });

  // Disconnect
  socket.on('disconnect', () => {
    rooms.forEach((members, roomId) => {
      if (members.has(socket.id)) {
        members.delete(socket.id);
        socket.to(roomId).emit('user-left', socket.id);
        if (members.size === 0) rooms.delete(roomId);
      }
    });
    console.log(`Disconnected: ${socket.id}`);
  });
});

// HTML client (browser-side WebRTC)
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html><head><title>WebRTC Video Call</title>
<style>body{font-family:monospace;background:#111;color:#0f0;padding:20px}
video{width:300px;background:#222;border-radius:8px;margin:10px}
#videos{display:flex;flex-wrap:wrap}
input,button{padding:8px;margin:5px;font:inherit;background:#333;color:#0f0;border:1px solid #555;border-radius:4px}
button:hover{background:#444}
</style></head><body>
<h2>WebRTC Video Call</h2>
<input id=room placeholder="Room name" value="test-room">
<button onclick=join()>Join Room</button>
<div id=videos></div>

<script src="/socket.io/socket.io.js"></script>
<script>
const socket = io();
let localStream;
const peers = new Map(); // remoteId -> RTCPeerConnection
const config = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };

async function join() {
  const room = document.getElementById('room').value;
  // Get camera
  localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  addVideo('local', localStream);

  socket.emit('join-room', room);

  // When another user joins, create a peer connection for them
  socket.on('user-joined', async (remoteId) => {
    console.log('User joined:', remoteId);
    const pc = createPeerConnection(remoteId);
    peers.set(remoteId, pc);

    // Add local stream tracks to this peer
    localStream.getTracks().forEach(track => pc.addTrack(track, localStream));

    // Create offer and send via signaling
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    socket.emit('signal', { to: remoteId, from: socket.id, data: offer });
  });

  // Handle incoming signaling
  socket.on('signal', async ({ from, data }) => {
    let pc = peers.get(from);
    if (!pc) {
      pc = createPeerConnection(from);
      peers.set(from, pc);
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
    }

    if (data.type === 'offer') {
      await pc.setRemoteDescription(data);
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      socket.emit('signal', { to: from, from: socket.id, data: answer });
    } else if (data.type === 'answer') {
      await pc.setRemoteDescription(data);
    } else if (data.candidate) {
      await pc.addIceCandidate(new RTCIceCandidate(data));
    }
  });

  // Handle existing users in the room
  socket.on('existing-users', async (userIds) => {
    userIds.forEach(async (remoteId) => {
      const pc = createPeerConnection(remoteId);
      peers.set(remoteId, pc);
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      socket.emit('signal', { to: remoteId, from: socket.id, data: offer });
    });
  });

  socket.on('user-left', (remoteId) => {
    if (peers.has(remoteId)) { peers.get(remoteId).close(); peers.delete(remoteId); }
    document.getElementById(remoteId)?.remove();
  });
}

function createPeerConnection(remoteId) {
  const pc = new RTCPeerConnection(config);
  pc.onicecandidate = (e) => {
    if (e.candidate) socket.emit('signal', { to: remoteId, from: socket.id, data: e.candidate });
  };
  pc.ontrack = (e) => addVideo(remoteId, e.streams[0]);
  return pc;
}

function addVideo(id, stream) {
  const existing = document.getElementById(id);
  if (existing) { existing.srcObject = stream; return; }
  const video = document.createElement('video');
  video.id = id;
  video.autoplay = true;
  video.playsinline = true;
  video.srcObject = stream;
  const label = document.createElement('div');
  label.textContent = id;
  document.getElementById('videos').appendChild(label);
  document.getElementById('videos').appendChild(video);
}
</script></body></html>`);
});

server.listen(3000, () => {
  console.log('WebRTC signaling server :3000');
  console.log('Open http://localhost:3000 in two browser tabs');
  console.log('Enter same room name in both. Video call starts.');
});
