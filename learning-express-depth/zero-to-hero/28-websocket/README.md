# Project 28: The WebSocket

> *"HTTP is a question. WebSocket is a conversation."*

In projects 01-27, every request is a *question* (client asks, server answers) and a *response* (server answers, client receives). After the response, the connection is over. The server can't push more.

WebSocket is a different protocol. The connection is *bidirectional* and *persistent*. Both the client and the server can send messages at any time. The server can push updates without the client asking.

We use `ws` — the de-facto WebSocket library for Node. We add a WebSocket endpoint to our server. The client connects, sends messages, receives messages. The server can broadcast to all connected clients.

The flow:
1. Client opens a WebSocket connection
2. Server accepts the connection
3. Client and server exchange messages
4. Either side can close the connection

By the end, the server can push real-time updates. The final artifact (a collaborative workspace) needs this.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is HTTP not enough? What is WebSocket?
2. [The Thought](./THOUGHT.md) — How does WebSocket work? What is the handshake? What is a frame?
3. [The Build](./BUILD.md) — Line-by-line construction of the WebSocket
4. [The Decisions](./DECISIONS.md) — Why ws? Why not Socket.IO? Why a separate port?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

WebSocket is a protocol that upgrades an HTTP connection to a bidirectional, persistent connection. The handshake is HTTP (the client sends an `Upgrade: websocket` request); after the upgrade, the protocol switches to WebSocket. Both sides can send messages at any time. We use `ws` to create a WebSocket server. Clients connect to `ws://localhost:3000/ws`. The server can broadcast messages to all clients or send to specific clients.

---

## The Code

```bash
npm install ws
```

```js
const { WebSocketServer } = require('ws');

const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  logger.info('Client connected');

  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    logger.info({ type: message.type }, 'Received message');

    if (message.type === 'chat') {
      // Broadcast to all clients
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({ type: 'chat', user: message.user, text: message.text }));
        }
      });
    }
  });

  ws.on('close', () => {
    logger.info('Client disconnected');
  });

  ws.send(JSON.stringify({ type: 'welcome', message: 'Connected to the chat' }));
});
```

Test it:

```javascript
// In a browser or Node client
const ws = new WebSocket('ws://localhost:3000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'chat', user: 'alice', text: 'Hello!' }));
};

ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

The pain of "the server can't push to the client" is solved. The server broadcasts. The clients receive.

---

## What You Will Have Learned

- What WebSocket is (a bidirectional, persistent protocol)
- The HTTP-to-WebSocket upgrade handshake
- How to use `ws` to create a WebSocket server
- How to handle messages and disconnections
- How to broadcast to all clients
- The differences between HTTP and WebSocket

These are the foundations of *real-time communication*. From here, every project that needs bidirectional communication can use WebSocket.
