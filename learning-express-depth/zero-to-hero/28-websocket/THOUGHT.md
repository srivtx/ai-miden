# The Thought

> *"The HTTP connection upgrades. The protocol switches. The conversation begins."*

## What WebSocket Is

WebSocket is a protocol that runs over TCP. It's an *upgrade* from HTTP. The connection starts as HTTP, then upgrades to WebSocket via a special handshake. After the upgrade, both sides can send messages at any time.

The protocol is:

- **Bidirectional**: both client and server can send messages
- **Persistent**: the connection stays open
- **Low-latency**: no HTTP overhead per message
- **Framed**: messages are discrete (not streamed)

WebSocket is the standard for real-time communication on the web. Browsers have built-in `WebSocket`. Node has `ws`. Almost every real-time app uses it.

## The Handshake

The connection starts as HTTP. The client sends a request with special headers:

```
GET /chat HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

The server responds with:

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After this `101 Switching Protocols` response, the connection is no longer HTTP. It's WebSocket. The client and server exchange *frames* (messages).

## Frames

WebSocket messages are called *frames*. There are two types:

- **Text frames**: UTF-8 text (typically JSON)
- **Binary frames**: arbitrary bytes

We use text frames with JSON. Each message is a JSON object: `{ type: 'chat', user: 'alice', text: 'Hello' }`.

## The `ws` Library

`ws` is the de-facto WebSocket library for Node. The basic usage:

```js
const { WebSocketServer } = require('ws');

const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  // A client connected
  ws.on('message', (data) => {
    // The client sent a message
    // data is a Buffer
    const message = JSON.parse(data.toString());
    // ...
  });

  ws.on('close', () => {
    // The client disconnected
  });

  ws.send('Hello!'); // Send a message to this client
});
```

`WebSocketServer` is attached to the HTTP server. The `connection` event fires for each new client. The `message` event fires for each message. The `close` event fires when the connection is closed.

## Broadcasting

To send a message to all connected clients:

```js
wss.clients.forEach((client) => {
  if (client.readyState === WebSocket.OPEN) {
    client.send(JSON.stringify({ type: 'chat', text: 'Hello!' }));
  }
});
```

`wss.clients` is a `Set` of all connected clients. We iterate and send. We check `readyState === OPEN` to skip clients that are closing or closed.

## The Chat Example

```js
wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    if (message.type === 'chat') {
      // Broadcast to all clients (including the sender)
      wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify({
            type: 'chat',
            user: message.user,
            text: message.text,
            timestamp: Date.now(),
          }));
        }
      });
    }
  });

  // Send a welcome message to the new client
  ws.send(JSON.stringify({ type: 'welcome', message: 'Connected to the chat' }));
});
```

The flow:

1. Client connects
2. Server sends a welcome message
3. Client sends a chat message
4. Server broadcasts to all clients (including the sender)
5. All clients receive the message

## Common Confusions (read these)

**Confusion 1: "Why not just use HTTP with long polling?"**
Long polling works but uses a connection per request. WebSocket uses one persistent connection. For high-frequency updates, WebSocket is more efficient.

**Confusion 2: "Why not Socket.IO?"**
Socket.IO is a higher-level library on top of WebSocket. It adds features (rooms, namespaces, fallback to long polling). For simple use cases, `ws` is enough. We use `ws` to learn the protocol.

**Confusion 3: "What about authentication?"**
Anyone can connect. For auth, you'd verify a token in the handshake (e.g., as a query parameter or in a message after connection). We add auth in a future project.

**Confusion 4: "What about scaling?"**
`wss.clients` is local to the process. For multi-process / multi-server, use Redis pub/sub to broadcast across processes. We add this in project 30.

**Confusion 5: "What if the connection drops?"**
The client doesn't know until it tries to send. The client should ping periodically (WebSocket has built-in ping/pong frames). We don't add this here.

**Confusion 6: "What about the order of messages?"**
WebSocket guarantees in-order delivery. Messages are received in the order they were sent.

**Confusion 7: "What about binary?"**
WebSocket supports binary frames. We use text/JSON. For binary, you'd send Buffers instead of strings.

**Confusion 8: "What about CORS?"**
WebSocket doesn't have CORS (it's not HTTP). The server accepts any connection. For auth, you'd verify a token. We accept this for the demo.

## What We Are About to Build

A ~500-line Express app that:

1. Has a WebSocket server attached to the HTTP server
2. Accepts connections on `/ws`
3. Handles chat messages
4. Broadcasts to all clients
5. Sends a welcome message on connection

The handlers are unchanged. The new piece is the WebSocket server.

In [BUILD.md](./BUILD.md) we will go line by line.
