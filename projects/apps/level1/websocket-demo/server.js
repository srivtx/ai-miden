// WebSocket Demo — Real-time bidirectional communication over a single TCP connection.
const express = require('express');
const http = require('http');
const crypto = require('crypto');
const { WebSocketServer } = require('ws');

const app = express();
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

const rooms = new Map(); // room -> Set<ws>
const clients = new Map(); // ws -> {id, username, room}

function broadcast(room, message, excludeWs = null) {
  const members = rooms.get(room) || new Set();
  const data = JSON.stringify(message);
  for (const ws of members) {
    if (ws !== excludeWs && ws.readyState === 1) ws.send(data);
  }
}

wss.on('connection', (ws) => {
  const id = crypto.randomBytes(4).toString('hex');
  clients.set(ws, { id, username: 'anon_' + id, room: null });
  ws.send(JSON.stringify({ type: 'welcome', id, msg: 'Send {type: "join", room: "lobby", username: "alice"} to start' }));

  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return ws.send(JSON.stringify({ type: 'error', error: 'invalid_json' })); }
    const client = clients.get(ws);
    if (!client) return;

    if (msg.type === 'join') {
      // Leave old room
      if (client.room) rooms.get(client.room)?.delete(ws);
      client.room = msg.room || 'lobby';
      client.username = msg.username || client.username;
      if (!rooms.has(client.room)) rooms.set(client.room, new Set());
      rooms.get(client.room).add(ws);
      broadcast(client.room, { type: 'system', msg: `${client.username} joined ${client.room}` }, ws);
      ws.send(JSON.stringify({ type: 'joined', room: client.room, members: rooms.get(client.room).size }));
    } else if (msg.type === 'chat' && client.room) {
      broadcast(client.room, { type: 'chat', from: client.username, text: msg.text, ts: Date.now() });
    } else if (msg.type === 'ping') {
      ws.send(JSON.stringify({ type: 'pong', ts: Date.now() }));
    } else if (msg.type === 'leave' && client.room) {
      rooms.get(client.room).delete(ws);
      broadcast(client.room, { type: 'system', msg: `${client.username} left` });
      client.room = null;
    }
  });

  ws.on('close', () => {
    const client = clients.get(ws);
    if (client?.room) {
      rooms.get(client.room)?.delete(ws);
      broadcast(client.room, { type: 'system', msg: `${client.username} disconnected` });
    }
    clients.delete(ws);
  });
});

app.get('/', (req, res) => res.json({ type: 'websocket', endpoint: '/ws', protocol: 'ws:// or wss://' }));
app.get('/admin/rooms', (req, res) => {
  const data = {};
  for (const [room, members] of rooms) data[room] = members.size;
  res.json({ rooms: data, totalClients: clients.size });
});

const PORT = 3000;
server.listen(PORT, () => console.log(`WebSocket demo on :${PORT} (ws://localhost:${PORT}/ws)`));
module.exports = app;
