// 13_websocket_chat.js — Socket.io: rooms, events, typing, online list, emoji reactions.
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const app = express();
const server = http.createServer(app);
const io = new Server(server);

const online = new Map();

io.on('connection', (socket) => {
  socket.on('join', ({ username, room }) => {
    socket.join(room);
    online.set(socket.id, { username, room });
    socket.emit('message', { user: 'System', text: `Welcome ${username}` });
    socket.to(room).emit('message', { user: 'System', text: `${username} joined` });
    const roomUsers = [...io.sockets.adapter.rooms.get(room) || []].map(id => online.get(id)?.username);
    io.to(room).emit('online', roomUsers);
  });

  socket.on('message', (text) => {
    const u = online.get(socket.id);
    if (u) io.to(u.room).emit('message', { user: u.username, text, time: new Date().toISOString() });
  });

  socket.on('typing', () => {
    const u = online.get(socket.id);
    if (u) socket.to(u.room).emit('typing', u.username);
  });

  socket.on('disconnect', () => {
    const u = online.get(socket.id);
    if (u) {
      socket.to(u.room).emit('message', { user: 'System', text: `${u.username} left` });
      online.delete(socket.id);
      const roomUsers = [...io.sockets.adapter.rooms.get(u.room) || []].map(id => online.get(id)?.username);
      io.to(u.room).emit('online', roomUsers);
    }
  });
});

server.listen(3000, () => console.log('Chat :3000'));
