// Chat API — Step 6. Adds: WebSockets, rooms, real-time messaging, history.
const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const Database = require('better-sqlite3');
const crypto = require('crypto');

const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE rooms (id TEXT PRIMARY KEY, name TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE TABLE messages (id TEXT PRIMARY KEY, room_id TEXT, user_id TEXT, text TEXT, created_at TEXT DEFAULT (datetime('now')))`);
db.exec(`CREATE INDEX idx_messages_room ON messages(room_id, created_at)`);

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });
const clients = new Map(); // ws -> { userId, roomId }
const roomMembers = new Map(); // roomId -> Set<ws>

wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'welcome', msg: 'Send {type: "join", userId, roomId} to start' }));
  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    const client = clients.get(ws) || {};
    if (msg.type === 'join') {
      if (client.roomId) roomMembers.get(client.roomId)?.delete(ws);
      client.userId = msg.userId || 'anon';
      client.roomId = msg.roomId;
      clients.set(ws, client);
      if (!roomMembers.has(msg.roomId)) roomMembers.set(msg.roomId, new Set());
      roomMembers.get(msg.roomId).add(ws);
      const history = db.prepare('SELECT id, user_id, text, created_at FROM messages WHERE room_id = ? ORDER BY created_at DESC LIMIT 50').all(msg.roomId).reverse();
      ws.send(JSON.stringify({ type: 'joined', roomId: msg.roomId, history, members: roomMembers.get(msg.roomId).size }));
      broadcast(msg.roomId, { type: 'user_joined', userId: client.userId, members: roomMembers.get(msg.roomId).size }, ws);
    } else if (msg.type === 'message' && client.roomId) {
      const id = 'm_' + crypto.randomBytes(4).toString('hex');
      db.prepare('INSERT INTO messages (id, room_id, user_id, text) VALUES (?, ?, ?, ?)').run(id, client.roomId, client.userId, msg.text);
      broadcast(client.roomId, { type: 'message', id, userId: client.userId, text: msg.text, created_at: new Date().toISOString() });
    }
  });
  ws.on('close', () => {
    const client = clients.get(ws);
    if (client?.roomId) { roomMembers.get(client.roomId)?.delete(ws); broadcast(client.roomId, { type: 'user_left', userId: client.userId }); }
    clients.delete(ws);
  });
});

function broadcast(roomId, message, excludeWs = null) {
  const data = JSON.stringify(message);
  for (const ws of roomMembers.get(roomId) || []) if (ws !== excludeWs && ws.readyState === 1) ws.send(data);
}

app.get('/rooms', (req, res) => {
  const rooms = db.prepare('SELECT r.*, COUNT(m.id) as message_count FROM rooms r LEFT JOIN messages m ON m.room_id = r.id GROUP BY r.id').all();
  res.json({ rooms });
});

app.post('/rooms', (req, res) => {
  if (!req.body.name) return res.status(422).json({ error: 'missing_name' });
  const id = 'r_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO rooms (id, name) VALUES (?, ?)').run(id, req.body.name);
  res.status(201).json({ id, name: req.body.name });
});

app.get('/rooms/:id/messages', (req, res) => {
  const messages = db.prepare('SELECT id, user_id, text, created_at FROM messages WHERE room_id = ? ORDER BY created_at DESC LIMIT ?').all(req.params.id, parseInt(req.query.limit) || 50);
  res.json({ messages: messages.reverse() });
});

const PORT = 3000;
server.listen(PORT, () => console.log(`Chat API on :${PORT} (ws://localhost:${PORT}/ws)`));
module.exports = app;
