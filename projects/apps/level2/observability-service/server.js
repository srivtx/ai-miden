// Observability Service — Metrics (Prometheus), Traces (OpenTelemetry-style), Logs correlation.
const express = require('express');
const crypto = require('crypto');
const app = express();
app.use(express.json());

// In-memory time-series storage
const metrics = {
  http_requests: {},  // { method, path, status } -> { count, sumDuration, p50, p99 }
  http_durations: [], // raw recent durations for percentile calculation
  errors: [],
  traces: [], // distributed trace records
};

function recordMetric(method, path, status, duration) {
  const key = `${method}:${path}:${status}`;
  const m = metrics.http_requests[key] || { count: 0, sumDuration: 0, durations: [] };
  m.count++;
  m.sumDuration += duration;
  m.durations.push(duration);
  if (m.durations.length > 1000) m.durations.shift();
  metrics.http_requests[key] = m;
  metrics.http_durations.push({ duration, timestamp: Date.now() });
  if (metrics.http_durations.length > 5000) metrics.http_durations.shift();
  if (status >= 500) metrics.errors.push({ method, path, status, timestamp: new Date().toISOString() });
}

// Middleware: trace + metric per request
app.use((req, res, next) => {
  const traceId = req.headers['x-trace-id'] || crypto.randomBytes(8).toString('hex');
  const spanId = crypto.randomBytes(8).toString('hex');
  req.traceId = traceId;
  req.spanId = spanId;
  res.set('X-Trace-Id', traceId);
  res.set('X-Span-Id', spanId);
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    recordMetric(req.method, req.path, res.statusCode, duration);
    metrics.traces.push({ traceId, spanId, parentSpan: req.headers['x-parent-span'], method: req.method, path: req.path, status: res.statusCode, duration, timestamp: new Date().toISOString() });
    if (metrics.traces.length > 10000) metrics.traces.shift();
  });
  next();
});

// Routes
app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.get('/items', (req, res) => res.json([1, 2, 3]));

app.get('/error', (req, res) => res.status(500).json({ error: 'Simulated error' }));

// ===== OBSERVABILITY ENDPOINTS =====

// Prometheus-compatible metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain; version=0.0.4');
  const lines = [];
  lines.push('# HELP http_requests_total Total HTTP requests');
  lines.push('# TYPE http_requests_total counter');
  for (const [key, m] of Object.entries(metrics.http_requests)) {
    lines.push(`http_requests_total{method="${key.split(':')[0]}",path="${key.split(':')[1]}",status="${key.split(':')[2]}"} ${m.count}`);
  }
  lines.push('# HELP http_request_duration_ms Request duration in ms');
  lines.push('# TYPE http_request_duration_ms histogram');
  // Simplified: just total/avg/p99
  for (const [key, m] of Object.entries(metrics.http_requests)) {
    if (m.durations.length) {
      const sorted = [...m.durations].sort((a, b) => a - b);
      const p50 = sorted[Math.floor(sorted.length * 0.5)];
      const p99 = sorted[Math.floor(sorted.length * 0.99)];
      const avg = m.sumDuration / m.count;
      lines.push(`http_request_duration_ms{method="${key.split(':')[0]}",path="${key.split(':')[1]}"} avg=${avg.toFixed(1)},p50=${p50},p99=${p99}`);
    }
  }
  res.send(lines.join('\n'));
});

// Trace search by trace ID
app.get('/traces/:traceId', (req, res) => {
  const spans = metrics.traces.filter(t => t.traceId === req.params.traceId);
  spans.length ? res.json({ traceId: req.params.traceId, spans, count: spans.length }) : res.status(404).json({ error: 'Not found' });
});

// Error log
app.get('/errors', (req, res) => {
  const last = metrics.errors.slice(-50);
  res.json({ total: metrics.errors.length, recent: last });
});

// Aggregate stats
app.get('/stats', (req, res) => {
  const total = Object.values(metrics.http_requests).reduce((s, m) => s + m.count, 0);
  const errors = metrics.errors.length;
  const totalDur = Object.values(metrics.http_requests).reduce((s, m) => s + m.sumDuration, 0);
  const avgDur = total ? (totalDur / total).toFixed(1) : 0;
  const allDur = metrics.http_durations.map(d => d.duration).sort((a, b) => a - b);
  const p99 = allDur.length ? allDur[Math.floor(allDur.length * 0.99)] : 0;
  res.json({ totalRequests: total, errorRate: total ? (errors / total * 100).toFixed(2) + '%' : '0%', avgDuration: avgDur + 'ms', p99: p99 + 'ms' });
});

app.listen(3000, () => console.log('Observability :3000'));
module.exports = app;
