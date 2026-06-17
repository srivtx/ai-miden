// Observability Demo — Structured logging, metrics storage in SQLite, request tracing.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// Storage for observability data (in real app: Prometheus + ELK + Jaeger)
const db = new Database(':memory:');
db.exec(`CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, level TEXT, message TEXT, trace_id TEXT, data TEXT)`);
db.exec(`CREATE TABLE metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, name TEXT, value REAL, labels TEXT)`);
db.exec(`CREATE TABLE traces (id INTEGER PRIMARY KEY AUTOINCREMENT, trace_id TEXT, span_id TEXT, parent_span TEXT, name TEXT, start_time INTEGER, duration_ms INTEGER, status TEXT, attributes TEXT)`);

// === Structured logger (saves to SQLite) ===
function log(level, message, traceId, data) {
  db.prepare('INSERT INTO logs (timestamp, level, message, trace_id, data) VALUES (?, ?, ?, ?, ?)').run(new Date().toISOString(), level, message, traceId, JSON.stringify(data || {}));
  if (level === 'error' || level === 'warn') {
    console[level === 'warn' ? 'log' : 'error'](JSON.stringify({ level, message, traceId, ...data }));
  }
}

// === Middleware: trace every request ===
app.use((req, res, next) => {
  const traceId = req.headers['x-trace-id'] || crypto.randomBytes(8).toString('hex');
  const spanId = crypto.randomBytes(8).toString('hex');
  const start = process.hrtime.bigint();
  req.traceId = traceId;
  req.spanId = spanId;
  res.set('X-Trace-Id', traceId);
  res.set('X-Span-Id', spanId);
  log('info', `${req.method} ${req.path} started`, traceId, { method: req.method, path: req.path, ip: req.ip });
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e6;
    const status = res.statusCode;
    db.prepare('INSERT INTO traces (trace_id, span_id, parent_span, name, start_time, duration_ms, status, attributes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(traceId, spanId, req.headers['x-parent-span'] || null, `${req.method} ${req.path}`, Date.now(), duration, status, JSON.stringify({ method: req.method, path: req.path, status }));
    db.prepare('INSERT INTO metrics (timestamp, name, value, labels) VALUES (?, ?, ?, ?)').run(new Date().toISOString(), 'http_request_duration_ms', duration, JSON.stringify({ method: req.method, status }));
    db.prepare('INSERT INTO metrics (timestamp, name, value, labels) VALUES (?, ?, ?, ?)').run(new Date().toISOString(), 'http_request_count', 1, JSON.stringify({ method: req.method, status }));
    log(status >= 500 ? 'error' : 'info', `${req.method} ${req.path} ${status} ${duration.toFixed(1)}ms`, traceId, { status, duration });
  });
  next();
});

// === Routes ===
app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.get('/api/users', (req, res) => { log('info', 'fetched users', req.traceId, { count: 42 }); res.json({ users: [] }); });
app.get('/api/slow', async (req, res) => { await new Promise(r => setTimeout(r, 2000)); res.json({ data: 'slow response' }); });
app.get('/api/error', (req, res) => { log('error', 'simulated error', req.traceId, { code: 500 }); res.status(500).json({ error: 'fail' }); });

// === Observability endpoints (what your dashboards query) ===
// Logs query
app.get('/logs', (req, res) => {
  let query = 'SELECT * FROM logs WHERE 1=1';
  const params = [];
  if (req.query.level) { query += ' AND level = ?'; params.push(req.query.level); }
  if (req.query.trace) { query += ' AND trace_id = ?'; params.push(req.query.trace); }
  if (req.query.since) { query += ' AND timestamp > ?'; params.push(req.query.since); }
  query += ' ORDER BY id DESC LIMIT ?';
  params.push(parseInt(req.query.limit) || 50);
  res.json(db.prepare(query).all(...params).map(r => ({ ...r, data: JSON.parse(r.data) })));
});

// Metrics endpoint (Prometheus-compatible format)
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain; version=0.0.4');
  const lines = [];
  // Calculate RED metrics
  const total = db.prepare("SELECT COUNT(*) as c FROM metrics WHERE name = 'http_request_count'").get().c;
  const errors = db.prepare("SELECT COUNT(*) as c FROM metrics WHERE name = 'http_request_count' AND json_extract(labels, '$.status') >= 500").get().c;
  const durRows = db.prepare("SELECT value FROM metrics WHERE name = 'http_request_duration_ms' ORDER BY id DESC LIMIT 100").all();
  const durations = durRows.map(r => r.value).sort((a, b) => a - b);
  const p50 = durations[Math.floor(durations.length * 0.5)] || 0;
  const p99 = durations[Math.floor(durations.length * 0.99)] || 0;
  lines.push(`# HELP http_requests_total Total requests`);
  lines.push('# TYPE http_requests_total counter');
  lines.push(`http_requests_total ${total}`);
  lines.push(`# HELP http_errors_total Total errors`);
  lines.push('# TYPE http_errors_total counter');
  lines.push(`http_errors_total ${errors}`);
  lines.push(`# HELP http_request_duration_ms Request duration`);
  lines.push('# TYPE http_request_duration_ms gauge');
  lines.push(`http_request_duration_ms_p50 ${p50.toFixed(1)}`);
  lines.push(`http_request_duration_ms_p99 ${p99.toFixed(1)}`);
  res.send(lines.join('\n'));
});

// Trace search
app.get('/traces/:traceId', (req, res) => {
  const spans = db.prepare('SELECT * FROM traces WHERE trace_id = ?').all(req.params.traceId);
  spans.length ? res.json({ traceId: req.params.traceId, spans, count: spans.length }) : res.status(404).json({ error: 'Not found' });
});

app.listen(3000, () => console.log('Observability demo :3000 (GET /metrics, /logs, /traces/:id)'));
module.exports = app;
