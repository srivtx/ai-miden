# The Thought

> *"A CRDT is a data structure that merges without conflicts. Yjs is a popular CRDT library. The server is just a relay."*

## What a CRDT Is

A *Conflict-free Replicated Data Type* is a data structure that can be edited by multiple users simultaneously and merged without conflicts. The mathematical properties:

- **Commutativity**: A then B gives the same result as B then A
- **Idempotence**: Applying the same operation twice has the same effect as applying it once
- **Associativity**: A then (B then C) gives the same result as (A then B) then C

These properties guarantee that all replicas converge to the same state, regardless of the order operations are applied.

## How Yjs Works

Yjs is a CRDT library. The most common type is `Y.Text` — a shared text.

```js
const ydoc = new Y.Doc();
const ytext = ydoc.getText('content');
ytext.insert(0, 'Hello');
ytext.insert(5, ' World');
// ytext.toString() === 'Hello World'
```

Each operation has a unique ID: `(clientId, clock)`. The client ID is assigned at startup. The clock is a counter that increments with each operation.

```
insert(0, 'Hello')  -> operation (1, 0)
insert(5, ' World') -> operation (1, 1)
```

When two users edit the same document:

```
User A: insert(0, 'Hello')  -> (1, 0)
User B: insert(0, 'World')  -> (2, 0)
```

Yjs merges these operations. The result is deterministic (same on all replicas):

```
"HelloWorld" or "WorldHello" (deterministic, based on the IDs)
```

The order is determined by the IDs, not the wall clock. So even if User B's operation arrives first, the merge result is the same.

## y-websocket: The Server

`y-websocket` is a WebSocket relay for Yjs. The server is *dumb*: it just forwards Yjs updates between clients. The CRDT handles the merging.

```js
const { setupWSConnection } = require('y-websocket/bin/utils');

wss.on('connection', setupWSConnection);
```

That's it. The server is a relay. When a client sends a Yjs update, the server broadcasts it to all other clients connected to the same document.

## The Client

```javascript
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

const ydoc = new Y.Doc();
const provider = new WebsocketProvider('ws://localhost:3000', 'my-document', ydoc);

const ytext = ydoc.getText('content');
ytext.insert(0, 'Hello world!');

// Listen for changes from other clients
ytext.observe((event) => {
  console.log('text changed:', ytext.toString());
});
```

The client creates a Yjs document, connects to the server, and gets a shared text. When the user types, the change is sent to the server. The server broadcasts to other clients. Yjs handles the merging.

## Persistence

Yjs has a `Y.Doc` API for saving and loading:

```js
const state = Y.encodeStateAsUpdate(ydoc); // Uint8Array
// Save to file, database, etc.

const ydoc2 = new Y.Doc();
Y.applyUpdate(ydoc2, state);
```

For persistence, use `y-leveldb` (LevelDB), `y-redis` (Redis), or a custom save/load to your database.

We don't add persistence in this project. The state is in memory. Restart the server, the document is gone.

## Common Confusions (read these)

**Confusion 1: "Why not just use a database with locking?"**
Locks would make the user wait. CRDTs allow local edits (instant) and eventual consistency (fast sync). No locks.

**Confusion 2: "Why not just merge on the server?"**
Server-side merging is complex (OT). CRDTs are simpler. The client knows how to merge. The server is a relay.

**Confusion 3: "What about binary data (images)?"**
Yjs supports binary data via `Y.ArrayBuffer`. We don't use it here.

**Confusion 4: "What about rich text (bold, italic)?"**
Yjs has `Y.XmlFragment` for rich text. Quill and ProseMirror integrate with Yjs.

**Confusion 5: "What if the server is down?"**
Yjs supports offline editing. The client keeps the local state. When the server comes back, the client syncs.

**Confusion 6: "What about authentication?"**
Anyone with the doc name can connect. For auth, you'd verify a token in the WebSocket handshake. We add this in a future project.

**Confusion 7: "What about permissions?"**
Anyone can edit. For permissions, you'd check before allowing edits. We add this in project 33 (RBAC).

**Confusion 8: "What if two users delete the same character?"**
Yjs handles this. The deletion is an operation with an ID. Both deletions are applied. The character is deleted (only once, due to idempotence).

## What We Are About to Build

A ~600-line Express app that:

1. Has a Yjs WebSocket server at `ws://localhost:3000`
2. The server relays Yjs updates between clients
3. Clients can connect and edit the same document
4. Yjs handles the merging (commutative operations)

The HTTP handlers are unchanged. The new piece is the Yjs WebSocket endpoint.

In [BUILD.md](./BUILD.md) we will go line by line.
