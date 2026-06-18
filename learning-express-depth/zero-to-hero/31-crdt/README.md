# Project 31: The CRDT

> *"Two users. Same document. No conflicts. No server merging. Magic."*

In projects 28-30, we have real-time communication. But co-editing is hard. If User A types "Hello" and User B types "World" simultaneously, what happens?

The naive approach: last-write-wins. Whoever saves last wins. The other's changes are lost. Bad.

The smart approach: **CRDT** (Conflict-free Replicated Data Type). A CRDT is a data structure that can be edited by multiple users simultaneously and merged without conflicts. Every change has a unique ID. Changes are commutative and idempotent.

We use **Yjs** — the most popular CRDT library. It's specifically designed for collaborative text editing. It works with rich text, plain text, JSON, and more.

The flow:
1. User A and User B both open the same document
2. They edit simultaneously
3. Yjs merges the changes automatically
4. The server syncs the merged state to both clients
5. Both clients see the same final state

By the end, two users can edit the same document in real time without conflicts. This is the foundation of Notion-style co-editing.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is co-editing hard? What is a CRDT?
2. [The Thought](./THOUGHT.md) — How do CRDTs work? What is Yjs?
3. [The Build](./BUILD.md) — Line-by-line construction of the co-editing endpoint
4. [The Decisions](./DECISIONS.md) — Why Yjs? Why not Operational Transform?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

A CRDT is a data structure that can be edited concurrently and merged without conflicts. Yjs is a popular CRDT library for collaborative editing. We use `y-websocket` for the server (broadcasts Yjs updates via WebSocket) and `yjs` + `y-websocket` for the client. The server is a *relay*: it forwards Yjs updates between clients. The CRDT handles the merging.

---

## The Code

```bash
npm install y-websocket yjs
```

```js
const { WebSocketServer } = require('ws');
const { setupWSConnection } = require('y-websocket/bin/utils');

const wss = new WebSocketServer({ noServer: true });

wss.on('connection', setupWSConnection);

server.on('upgrade', (req, socket, head) => {
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit('connection', ws, req);
  });
});
```

Test it with the Yjs client:

```javascript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const ydoc = new Y.Doc();
const provider = new WebsocketProvider('ws://localhost:3000', 'my-document', ydoc);

const ytext = ydoc.getText('content');
ytext.insert(0, 'Hello world!');
```

The pain of "two users editing the same document" is solved. Yjs handles the merging. The server is a relay.

---

## What You Will Have Learned

- What a CRDT is (a data structure that merges without conflicts)
- How Yjs works (operations with unique IDs, commutative merging)
- How to use `y-websocket` for the server (relay)
- How to use Yjs in the client
- The difference between CRDTs and Operational Transform

These are the foundations of *collaborative editing*. From here, every project that needs real-time co-editing can use Yjs.
