// 23_graceful_shutdown.js — Drain connections, close DB, flush logs on SIGTERM/SIGINT.
const express = require('express');
const http = require('http');
const app = express();

// Simulated connections
let activeConnections = 0;
const server = http.createServer(app);

// Track connections
server.on('connection', (socket) => {
  activeConnections++;
  socket.on('close', () => activeConnections--);
});

app.get('/', (req, res) => {
  // Simulate long-running request
  setTimeout(() => res.json({ msg: 'Done' }), 2000);
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.get('/connections', (req, res) => res.json({ active: activeConnections }));

// ---- Graceful shutdown ----
async function shutdown(signal) {
  console.log(`\n${signal} received. Shutting down gracefully...`);

  // 1. Stop accepting new requests
  server.close(() => console.log('Server closed'));

  // 2. Wait for active requests to finish (max 10s)
  let waited = 0;
  while (activeConnections > 0 && waited < 10000) {
    console.log(`  Waiting for ${activeConnections} connections...`);
    await new Promise(r => setTimeout(r, 1000));
    waited += 1000;
  }
  if (activeConnections > 0) console.log(`  Force closing ${activeConnections} connections`);

  // 3. Close database connections
  // await db.close();  console.log('Database closed');

  // 4. Close Redis
  // await redis.quit();  console.log('Redis closed');

  // 5. Exit
  console.log('Shutdown complete');
  process.exit(0);
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

server.listen(3000, () => {
  console.log(`Server :3000 (PID: ${process.pid})`);
  console.log('  Test: curl localhost:3000/ &  (start a long request)');
  console.log('  Then: kill -SIGTERM', process.pid);
  console.log('  The server waits for active requests before shutting down');
});
