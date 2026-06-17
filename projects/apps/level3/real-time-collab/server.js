// Real-time Collaboration — Multi-user document editing (Figma-style).
// Server holds the document, broadcasts operations via WebSocket, handles conflict resolution.
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const docs = new Map(); // docId -> { content, version, clients }
const clients = new Map(); // socketId -> { docId, userId, name, color }

const COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'];

// HTTP API
app.get('/docs/:id', (req, res) => {
  let doc = docs.get(req.params.id);
  if (!doc) { doc = { content: `# New Document ${req.params.id}\n\nStart typing...`, version: 0, clients: 0 }; docs.set(req.params.id, doc); }
  res.json({ id: req.params.id, content: doc.content, version: doc.version, activeUsers: doc.clients });
});

// WebSocket
io.on('connection', (socket) => {
  const color = COLORS[Math.floor(Math.random() * COLORS.length)];

  socket.on('join-doc', ({ docId, userId, name }) => {
    if (!docs.has(docId)) docs.set(docId, { content: '', version: 0, clients: 0 });
    const doc = docs.get(docId);
    doc.clients++;
    clients.set(socket.id, { docId, userId, name: name || 'Anonymous', color });
    socket.join(docId);
    // Send current state
    socket.emit('doc-state', { content: doc.content, version: doc.version });
    // Notify others
    socket.to(docId).emit('user-joined', { userId, name: name || 'Anonymous', color, activeUsers: doc.clients });
  });

  // Cursor position
  socket.on('cursor', (pos) => {
    const c = clients.get(socket.id);
    if (c) socket.to(c.docId).emit('cursor', { userId: c.userId, name: c.name, color: c.color, position: pos });
  });

  // Text operation (character insert/delete)
  socket.on('op', ({ position, type, char }) => {
    const c = clients.get(socket.id);
    if (!c) return;
    const doc = docs.get(c.docId);
    if (!doc) return;
    // Simple last-write-wins (for OT/CRDT, use Yjs)
    if (type === 'insert') doc.content = doc.content.slice(0, position) + char + doc.content.slice(position);
    else if (type === 'delete' && position < doc.content.length) doc.content = doc.content.slice(0, position) + doc.content.slice(position + 1);
    doc.version++;
    // Broadcast to others
    socket.to(c.docId).emit('op', { userId: c.userId, position, type, char, version: doc.version });
  });

  // Full doc replace
  socket.on('replace-doc', ({ content }) => {
    const c = clients.get(socket.id);
    if (!c) return;
    const doc = docs.get(c.docId);
    if (!doc) return;
    doc.content = content;
    doc.version++;
    socket.to(c.docId).emit('doc-update', { content, version: doc.version, by: c.name });
  });

  socket.on('disconnect', () => {
    const c = clients.get(socket.id);
    if (c) {
      const doc = docs.get(c.docId);
      if (doc) { doc.clients--; socket.to(c.docId).emit('user-left', { userId: c.userId, activeUsers: doc.clients }); }
      clients.delete(socket.id);
    }
  });
});

app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html><head><title>Real-time Doc</title>
<style>body{font-family:sans-serif;padding:20px}
#editor{width:100%;height:400px;font:14px monospace}
#users{position:fixed;top:10px;right:10px}
.user{display:inline-block;padding:4px 8px;border-radius:4px;color:white;margin:2px}
</style></head><body>
<h2>Real-time Document <span id=docId></span></h2>
<div id=users></div>
<textarea id=editor placeholder="Loading..."></textarea>
<div id=version>Version: 0</div>
<script src="/socket.io/socket.io.js"></script>
<script>
const docId = location.hash.slice(1) || 'demo';
document.getElementById('docId').textContent = '#' + docId;
const editor = document.getElementById('editor');
const usersDiv = document.getElementById('users');
const myName = 'User' + Math.random().toString(36).slice(2, 5);
const myColor = '#' + Math.floor(Math.random() * 16777215).toString(16);

const socket = io();
let version = 0;

fetch('/docs/' + docId).then(r => r.json()).then(doc => { editor.value = doc.content; version = doc.version; document.getElementById('version').textContent = 'Version: ' + version; });

socket.on('connect', () => socket.emit('join-doc', { docId, userId: myName, name: myName }));
socket.on('doc-state', ({ content, version: v }) => { editor.value = content; version = v; document.getElementById('version').textContent = 'Version: ' + version; });
socket.on('op', ({ userId, position, type, char, version: v }) => {
  if (type === 'insert') editor.value = editor.value.slice(0, position) + char + editor.value.slice(position);
  else if (type === 'delete') editor.value = editor.value.slice(0, position) + editor.value.slice(position + 1);
  version = v; document.getElementById('version').textContent = 'Version: ' + version;
});
socket.on('doc-update', ({ content, version: v }) => { editor.value = content; version = v; document.getElementById('version').textContent = 'Version: ' + version; });
socket.on('user-joined', ({ name, color, activeUsers }) => updateUsers(name, color, activeUsers, true));
socket.on('user-left', ({ activeUsers }) => { /* re-render */ });

editor.addEventListener('input', (e) => {
  const newVal = editor.value;
  // Naive: send whole diff (in real app: use operational transform)
  socket.emit('replace-doc', { content: newVal });
});

function updateUsers(name, color, count, joined) {
  const tag = document.createElement('span');
  tag.className = 'user';
  tag.style.background = color;
  tag.textContent = (joined ? '+ ' : '') + name;
  usersDiv.appendChild(tag);
}
</script></body></html>`);
});

server.listen(3000, () => console.log('Real-time Collab :3000 (open /#demo in two tabs)'));
module.exports = { app, server };
