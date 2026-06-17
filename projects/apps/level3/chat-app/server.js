// Chat App — WebSocket rooms + REST history + auth + online tracking.
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
app.use(express.json());
const server = http.createServer(app);
const io = new Server(server);
const SECRET = 'dev-secret';

// DB
const users = [];
const rooms = [{ id: 'general', name: 'General', createdBy: 'system' }];
const messages = []; // { roomId, userId, username, text, time }
const online = new Map(); // socketId -> { userId, username, roomId }

// === REST ===
app.post('/auth/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'username and password required' });
  if (users.find(u => u.username === username)) return res.status(409).json({ error: 'Username taken' });
  const user = { id: users.length + 1, username, password: await bcrypt.hash(password, 10) };
  users.push(user);
  res.status(201).json({ user: { id: user.id, username }, token: jwt.sign({ id: user.id, username }, SECRET, { expiresIn: '24h' }) });
});

app.post('/auth/login', async (req, res) => {
  const user = users.find(u => u.username === req.body.username);
  if (!user || !(await bcrypt.compare(req.body.password, user.password))) return res.status(401).json({ error: 'Invalid credentials' });
  res.json({ token: jwt.sign({ id: user.id, username: user.username }, SECRET, { expiresIn: '24h' }) });
});

app.get('/rooms', (req, res) => res.json(rooms));

app.get('/messages/:roomId', (req, res) => {
  const msgs = messages.filter(m => m.roomId === req.params.roomId).slice(-100);
  res.json(msgs);
});

// Create room
app.post('/rooms', (req, res) => {
  const { name } = req.body;
  try { jwt.verify((req.headers.authorization || '').split(' ')[1], SECRET); } catch { return res.status(401).json({ error: 'Auth required' }); }
  if (!name) return res.status(400).json({ error: 'name required' });
  const room = { id: name.toLowerCase().replace(/\s+/g, '-'), name, createdBy: 'user' };
  rooms.push(room);
  res.status(201).json(room);
});

// === WebSocket ===
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) return next(new Error('Auth required'));
  try { socket.user = jwt.verify(token, SECRET); next(); }
  catch { next(new Error('Invalid token')); }
});

io.on('connection', (socket) => {
  console.log(`${socket.user.username} connected`);

  socket.on('join', (roomId) => {
    // Leave previous room
    const prev = online.get(socket.id);
    if (prev) socket.leave(prev.roomId);

    socket.join(roomId);
    online.set(socket.id, { userId: socket.user.id, username: socket.user.username, roomId });
    socket.emit('message', { user: 'System', text: `Welcome to ${roomId}`, time: new Date().toISOString() });
    socket.to(roomId).emit('message', { user: 'System', text: `${socket.user.username} joined`, time: new Date().toISOString() });

    // Online list
    const roomUsers = [...io.sockets.adapter.rooms.get(roomId) || []].map(id => online.get(id)?.username).filter(Boolean);
    io.to(roomId).emit('online', roomUsers);
  });

  socket.on('message', (text) => {
    const user = online.get(socket.id);
    if (!user || !text.trim()) return;
    const msg = { user: user.username, text, time: new Date().toISOString() };
    messages.push({ roomId: user.roomId, userId: user.userId, username: user.username, text, time: msg.time });
    io.to(user.roomId).emit('message', msg);
  });

  socket.on('typing', () => {
    const user = online.get(socket.id);
    if (user) socket.to(user.roomId).emit('typing', user.username);
  });

  socket.on('disconnect', () => {
    const user = online.get(socket.id);
    if (user) {
      socket.to(user.roomId).emit('message', { user: 'System', text: `${user.username} left`, time: new Date().toISOString() });
      online.delete(socket.id);
      const roomUsers = [...io.sockets.adapter.rooms.get(user.roomId) || []].map(id => online.get(id)?.username).filter(Boolean);
      io.to(user.roomId).emit('online', roomUsers);
    }
  });
});

server.listen(3000, () => console.log('Chat :3000'));
module.exports = { app, server };
