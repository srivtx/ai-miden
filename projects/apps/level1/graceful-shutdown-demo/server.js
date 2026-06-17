// Graceful Shutdown Demo — SIGTERM handling, in-flight request draining, cleanup.
const express = require('express');
const app = express();
app.use(express.json());

let shuttingDown = false;
let inflight = 0;
const maxWaitMs = 10000;
let server = null;

app.use((req, res, next) => {
  if (shuttingDown) {
    res.set('Connection', 'close');
    return res.status(503).json({ error: 'shutting_down', retryAfter: 5 });
  }
  inflight++;
  res.on('finish', () => { inflight--; if (shuttingDown && inflight === 0) finishShutdown(); });
  res.on('close', () => { inflight--; if (shuttingDown && inflight === 0) finishShutdown(); });
  next();
});

app.get('/health', (req, res) => res.json({ status: 'ok', inflight, shuttingDown }));
app.get('/slow', async (req, res) => { await new Promise(r => setTimeout(r, 3000)); res.json({ done: true }); });
app.post('/work', (req, res) => { setTimeout(() => res.json({ ok: true }), 100); });

app.get('/admin/status', (req, res) => res.json({ shuttingDown, inflight, uptime: process.uptime() }));

function startShutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log(`[shutdown] ${signal} received. ${inflight} requests in flight.`);
  if (server) server.close(() => finishShutdown());
  setTimeout(() => {
    if (inflight > 0) console.log(`[shutdown] Force exit. ${inflight} requests still in flight.`);
    else console.log('[shutdown] Clean exit.');
    process.exit(0);
  }, maxWaitMs).unref();
}

function finishShutdown() {
  console.log('[shutdown] All connections closed. Exiting.');
  process.exit(0);
}

process.on('SIGTERM', () => startShutdown('SIGTERM'));
process.on('SIGINT', () => startShutdown('SIGINT'));

const PORT = 3000;
server = app.listen(PORT, () => console.log(`Graceful shutdown demo on :${PORT} (send SIGTERM to test)`));
module.exports = app;
