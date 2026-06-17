// 06_websocket_chat.js — Real-time chat with Socket.io. Learn: rooms, events, broadcast.

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public')); // serves the chat HTML

// ---- Track connected users ----
const onlineUsers = new Map(); // socketId -> { username, room }

io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // JOIN ROOM: user picks a username and joins a room
  socket.on('join', ({ username, room }) => {
    socket.join(room);
    onlineUsers.set(socket.id, { username, room });

    // Tell the user who joined
    socket.emit('message', { user: 'System', text: `Welcome ${username}. Room: ${room}` });

    // Tell everyone ELSE in the room
    socket.to(room).emit('message', { user: 'System', text: `${username} joined` });

    // Send updated user list
    const roomUsers = [...io.sockets.adapter.rooms.get(room) || []].map(id => {
      return onlineUsers.get(id)?.username || id;
    });
    io.to(room).emit('roomUsers', roomUsers);
  });

  // CHAT MESSAGE: broadcast to everyone in the room
  socket.on('chatMessage', (text) => {
    const user = onlineUsers.get(socket.id);
    if (!user) return;
    io.to(user.room).emit('message', { user: user.username, text, time: new Date().toISOString() });
  });

  // TYPING INDICATOR
  socket.on('typing', () => {
    const user = onlineUsers.get(socket.id);
    if (user) socket.to(user.room).emit('typing', user.username);
  });

  // DISCONNECT
  socket.on('disconnect', () => {
    const user = onlineUsers.get(socket.id);
    if (user) {
      io.to(user.room).emit('message', { user: 'System', text: `${user.username} left` });
      onlineUsers.delete(socket.id);
    }
    console.log(`User disconnected: ${socket.id}`);
  });
});

server.listen(3000, () => console.log('Chat server on http://localhost:3000'));
