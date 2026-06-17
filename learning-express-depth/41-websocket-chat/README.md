# 41 — WebSocket Chat

**New concept:** real-time bidirectional communication.

HTTP is one-and-done: client sends request, server sends response, connection closes. WebSocket is different: the connection stays open, and both sides can send messages at any time.

## Run it

```bash
npm install
node server.js
```

Then in another terminal, install a WebSocket client:
```bash
npm install -g wscat
wscat -c ws://localhost:3000
```

Type a message and press Enter. Open another terminal and run `wscat` again. Now you have two people chatting.

## How to think about it

HTTP is like sending letters. WebSocket is like a phone call. Once the call is connected, both people can talk whenever they want, without hanging up and redialing.

## How to build it (line by line)

```js
const http = require('http');
const { WebSocketServer } = require('ws');
```

**Lines 4-5.** Load Node's built-in `http` and the `ws` library. We installed `ws` with `npm install`.

```js
const wss = new WebSocketServer({ server });
```

**Line 9.** Create a WebSocket server. It uses the same HTTP server but upgrades the connection to WebSocket when the client asks.

```js
wss.on('connection', (ws) => {
  clients.add(ws);
  ws.on('message', (raw) => {
    const msg = JSON.parse(raw.toString());
    for (const client of clients) {
      if (client.readyState === 1) {
        client.send(JSON.stringify({ ...msg, ts: Date.now() }));
      }
    }
  });
  ws.on('close', () => clients.delete(ws));
});
```

**Lines 11-25.** When a new client connects:
1. Add them to the set of clients
2. Listen for messages from them
3. When a message comes in, parse it and broadcast to all clients
4. When they disconnect, remove them

**`raw.toString()`** — the message is binary, we convert to string first.

**`JSON.parse`** — the string is JSON, we parse it to an object.

**`client.readyState === 1`** — 1 means the connection is open. We only send to open connections.

## What we learned

1. WebSocket = real-time bidirectional
2. `ws` is a popular WebSocket library
3. `client.send(...)` sends to one client
4. To broadcast, loop over all clients
5. The shape is different from HTTP — events, not routes

## What's next

In **42-file-upload** we learn how to receive files from clients (multipart/form-data).
