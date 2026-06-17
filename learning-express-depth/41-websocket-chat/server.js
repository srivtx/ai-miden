// 41 — WebSocket Chat
// NEW CONCEPT: real-time bidirectional communication.
// HTTP is request-response. WebSocket is "stay connected, send messages both ways."
const http = require('http');
const { WebSocketServer } = require('ws');

const server = http.createServer();
const wss = new WebSocketServer({ server });

// Track connected clients
const clients = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  console.log(`New connection. Total: ${clients.size}`);

  // When this client sends a message
  ws.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());
    console.log('Got:', msg);

    // Broadcast to all clients (including the sender)
    for (const client of clients) {
      if (client.readyState === 1) {  // 1 = OPEN
        client.send(JSON.stringify({ ...msg, ts: Date.now() }));
      }
    }
  });

  // When this client disconnects
  ws.on('close', () => {
    clients.delete(ws);
    console.log(`Connection closed. Total: ${clients.size}`);
  });
});

server.listen(3000, () => console.log('WebSocket chat on ws://localhost:3000'));
