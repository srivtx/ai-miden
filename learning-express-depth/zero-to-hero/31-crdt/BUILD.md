# The Build

> *"A CRDT is a data structure that merges without conflicts. Yjs is a popular CRDT library. The server is just a relay."*

We are going to add Yjs for co-editing. The change from project 30: add `y-websocket` and `yjs`, set up a Yjs WebSocket server.

## Setup

```bash
npm install y-websocket yjs
```

## The Code

### The Yjs WebSocket Server

```js
const { WebSocketServer } = require('ws');
const { setupWSConnection } = require('y-websocket/bin/utils');

const yWss = new WebSocketServer({ noServer: true });

yWss.on('connection', setupWSConnection);

server.on('upgrade', (req, socket, head) => {
  yWss.handleUpgrade(req, socket, head, (ws) => {
    yWss.emit('connection', ws, req);
  });
});
```

The Yjs WebSocket server is attached to the same HTTP server, but it's a separate `WebSocketServer` (with `noServer: true`). The `upgrade` event on the HTTP server is handled by the Yjs server.

`setupWSConnection` is a function from `y-websocket` that handles the Yjs protocol. The server is a *relay*: it forwards Yjs updates between clients.

### The Combined HTTP and Yjs Servers

```js
const server = app.listen(3000, () => logger.info('Server listening on http://localhost:3000'));

// Chat WebSocket (project 28)
const wss = new WebSocketServer({ server });
wss.on('connection', (ws, req) => {
  // ... chat logic from project 30
});

// Yjs WebSocket (this project)
const yWss = new WebSocketServer({ noServer: true });
yWss.on('connection', setupWSConnection);
server.on('upgrade', (req, socket, head) => {
  // Yjs handles `/<doc-name>` paths
  yWss.handleUpgrade(req, socket, head, (ws) => {
    yWss.emit('connection', ws, req);
  });
});
```

We have two WebSocket servers on the same HTTP server:

- The chat WebSocket handles any path (or `/` for the chat)
- The Yjs WebSocket handles `/<doc-name>` paths (e.g., `/my-document`)

In practice, you'd separate them by path. The Yjs client connects to `ws://localhost:3000/my-document`. The chat client connects to `ws://localhost:3000`. The `upgrade` handler routes based on the URL.

### The Yjs Client

```javascript
// client.js
const Y = require('yjs');
const { WebsocketProvider } = require('y-websocket');

const ydoc = new Y.Doc();
const provider = new WebsocketProvider('ws://localhost:3000', 'my-document', ydoc);

const ytext = ydoc.getText('content');

// Insert text
ytext.insert(0, 'Hello, world!');

// Listen for changes from other clients
ytext.observe(() => {
  console.log('text:', ytext.toString());
});
```

The client creates a Yjs document, connects to the server with a document name, and gets a shared text. The Yjs library handles the local edit, the sync with the server, and the merge of other clients' edits.

## Run It

```bash
# Terminal 1: start the server
node server.js

# Terminal 2: client A
node client.js
# (waits for input or just prints the current state)

# Terminal 3: client B
node client.js
# (sees the same document)
```

Type in one terminal, see the change in the other. Both clients stay in sync. If you type in both, the changes are merged automatically.

The pain of "two users editing the same document" is solved. Yjs handles the merging.

---

## Experiments

### Experiment 1: Two browsers

Open two browser tabs. In each, use the Yjs client (via a script tag). Both connect to the same document. Type in one. See the change in the other.

### Experiment 2: Disconnect and reconnect

Connect a client. Type. Disconnect. Reconnect. The state is preserved (it's in memory on the server, and the client syncs from the server on reconnect).

### Experiment 3: Persistence with y-leveldb

```bash
npm install y-leveldb level
```

```js
const { LeveldbPersistence } = require('y-leveldb');
const persistence = new LeveldbPersistence('./yjs-data');

const ydoc = await persistence.getYDoc('my-document');
// Now the document is persisted to disk
```

### Experiment 4: Rich text with Quill

Yjs integrates with Quill:

```bash
npm install y-quill quill
```

```js
import Quill from 'quill';
import { QuillBinding } from 'y-quill';

const quill = new Quill('#editor');
const ytext = ydoc.getText('content');
new QuillBinding(ytext, quill);
```

Now you have a rich text editor with co-editing.

### Experiment 5: Awareness (cursors, selections)

Yjs has *awareness* — a way to share non-document state (cursors, selections, user names). The client sends its awareness; the server broadcasts it.

```js
provider.awareness.setLocalStateField('user', { name: 'Alice', color: '#ff0000' });

provider.awareness.on('change', () => {
  const states = provider.awareness.getStates();
  for (const [clientId, state] of states) {
    console.log(`${state.user.name} is at`, state.cursor);
  }
});
```

Show other users' cursors in your editor.

---

## Summary

You now have co-editing. Two users can edit the same document in real time. Yjs handles the merging. The server is a relay.

This is the foundation of *collaborative editing*. From here, every project that needs real-time co-editing can use Yjs. The patterns (Y.Doc, y-websocket, awareness) are universal.

In project 32, we will add **WebRTC** for voice and video. Users can join a "huddle" and talk. The final artifact (Cove) needs this.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
