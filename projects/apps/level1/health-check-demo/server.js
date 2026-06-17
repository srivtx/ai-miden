// Health Check Demo — Liveness, readiness, dependency checks, response time, status page.
const express = require('express');
const Database = require('better-sqlite3');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE checks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, latency_ms INTEGER, error TEXT, ts INTEGER)`);

// === Individual checks ===
async function checkDb() {
  const start = process.hrtime.bigint();
  try { db.prepare('SELECT 1').get(); return { status: 'pass', latencyMs: Number(process.hrtime.bigint() - start) / 1e6 }; }
  catch (e) { return { status: 'fail', error: e.message }; }
}

async function checkMemory() {
  const used = process.memoryUsage();
  const heapUsedMB = used.heapUsed / 1024 / 1024;
  const status = heapUsedMB < 200 ? 'pass' : 'warn';
  return { status, heapUsedMB: Math.round(heapUsedMB) };
}

async function checkDisk() {
  const fs = require('fs');
  try {
    fs.writeFileSync('/tmp/_healthcheck_test', 'x');
    fs.unlinkSync('/tmp/_healthcheck_test');
    return { status: 'pass' };
  } catch (e) { return { status: 'fail', error: e.message }; }
}

async function checkEventLoop() {
  return new Promise((resolve) => {
    const start = Date.now();
    setImmediate(() => resolve({ status: 'pass', lagMs: Date.now() - start }));
  });
}

async function checkFakeExternal() {
  // Simulates a dependency. Toggle with ?external=fail
  const start = process.hrtime.bigint();
  await new Promise(r => setTimeout(r, 50));
  const shouldFail = process.env.HEALTH_EXTERNAL_FAIL === '1';
  const ms = Number(process.hrtime.bigint() - start) / 1e6;
  if (shouldFail) return { status: 'fail', error: 'simulated outage', latencyMs: ms };
  return { status: 'pass', latencyMs: ms };
}

// === Run all checks ===
async function runAllChecks() {
  const checks = [
    { name: 'database', check: checkDb, required: true },
    { name: 'memory', check: checkMemory, required: false },
    { name: 'disk', check: checkDisk, required: true },
    { name: 'event_loop', check: checkEventLoop, required: true },
    { name: 'external_api', check: checkFakeExternal, required: false },
  ];
  const results = [];
  for (const { name, check, required } of checks) {
    const start = process.hrtime.bigint();
    try {
      const result = await check();
      const latencyMs = result.latencyMs ?? (Number(process.hrtime.bigint() - start) / 1e6);
      results.push({ name, required, ...result, latencyMs: Math.round(latencyMs * 100) / 100 });
    } catch (e) {
      results.push({ name, required, status: 'fail', error: e.message });
    }
  }
  const hasRequiredFailure = results.some(r => r.required && r.status === 'fail');
  const anyFailure = results.some(r => r.status === 'fail');
  return {
    status: hasRequiredFailure ? 'unhealthy' : anyFailure ? 'degraded' : 'healthy',
    checks: results,
    timestamp: new Date().toISOString(),
  };
}

// === Routes ===
app.get('/health', async (req, res) => {
  const result = await runAllChecks();
  const code = result.status === 'unhealthy' ? 503 : 200;
  res.status(code).json(result);
});

app.get('/health/live', (req, res) => res.json({ status: 'alive', ts: Date.now() }));

app.get('/health/ready', async (req, res) => {
  const dbCheck = await checkDb();
  dbCheck.status === 'pass' ? res.json({ status: 'ready' }) : res.status(503).json({ status: 'not_ready', reason: dbCheck.error });
});

app.get('/health/:name', async (req, res) => {
  const checks = { db: checkDb, memory: checkMemory, disk: checkDisk, external: checkFakeExternal };
  const check = checks[req.params.name];
  if (!check) return res.status(404).json({ error: 'unknown_check', available: Object.keys(checks) });
  const result = await check();
  res.json({ name: req.params.name, ...result });
});

app.get('/admin/history', (req, res) => {
  const limit = parseInt(req.query.limit) || 20;
  res.json({ checks: db.prepare('SELECT * FROM checks ORDER BY id DESC LIMIT ?').all(limit) });
});

app.listen(3000, () => console.log('Health check demo :3000 — GET /health, /health/live, /health/ready'));
module.exports = app;
