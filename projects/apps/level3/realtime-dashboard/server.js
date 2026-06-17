// Real-time Dashboard — SSE events, live stats, Redis pub/sub, alert thresholds.
const express = require('express');
const app = express();

// Simulated metrics (in production: from Prometheus, DB queries, etc.)
const metrics = {
  requests: { total: 0, perSecond: 0, lastReset: Date.now() },
  users: { active: 0, total: 0 },
  errors: { lastHour: 0, rate: 0 },
  latency: { p50: 0, p95: 0, p99: 0 },
  cpu: { percent: 0 },
  memory: { usedMB: 0, totalMB: 0 },
  alerts: [],
};

// Simulate metrics changing
function updateMetrics() {
  metrics.requests.total += Math.floor(Math.random() * 10);
  metrics.requests.perSecond = Math.floor(Math.random() * 50);
  metrics.users.active = Math.floor(Math.random() * 200);
  metrics.users.total = 1500 + Math.floor(Math.random() * 100);
  metrics.errors.lastHour = Math.floor(Math.random() * 20);
  metrics.errors.rate = (metrics.errors.lastHour / 100).toFixed(1);
  metrics.latency.p50 = Math.round((20 + Math.random() * 50) * 10) / 10;
  metrics.latency.p95 = Math.round((100 + Math.random() * 200) * 10) / 10;
  metrics.latency.p99 = Math.round((300 + Math.random() * 500) * 10) / 10;
  metrics.cpu.percent = Math.round((20 + Math.random() * 60) * 10) / 10;
  const used = process.memoryUsage();
  metrics.memory.usedMB = Math.round(used.heapUsed / 1024 / 1024);

  // Alerts
  if (metrics.latency.p99 > 500) metrics.alerts.push({ level: 'warn', message: `High p99 latency: ${metrics.latency.p99}ms`, time: new Date().toISOString() });
  if (metrics.errors.lastHour > 15) metrics.alerts.push({ level: 'critical', message: `Error rate spike: ${metrics.errors.lastHour}/hr`, time: new Date().toISOString() });
  if (metrics.alerts.length > 20) metrics.alerts = metrics.alerts.slice(-20);
}
setInterval(updateMetrics, 2000);

// Track active SSE connections
let sseClients = [];

// HTML dashboard
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html><head><title>Dashboard</title>
<style>body{font-family:monospace;background:#111;color:#0f0;padding:20px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}
.card{background:#1a1a1a;padding:15px;border-radius:8px;border:1px solid #333}
.card h3{margin:0 0 10px;color:#0af;font-size:14px}
.card .val{font-size:28px;font-weight:bold}
.alerts{grid-column:1/-1;max-height:200px;overflow-y:auto}
.alert{padding:5px;margin:3px 0;border-radius:4px}
.alert.warn{background:#332;color:#fa0}.alert.critical{background:#322;color:#f44}
</style></head><body><h2>Real-time Dashboard</h2><div class=grid id=grid></div>
<script>
const evt = new EventSource('/events');
evt.onmessage = (e) => {
  const m = JSON.parse(e.data);
  document.getElementById('grid').innerHTML = [
    ['Requests', \`<div class=val>\${m.requests.perSecond}</div>req/s<br>\${m.requests.total} total\`],
    ['Users', \`<div class=val>\${m.users.active}</div>active<br>\${m.users.total} total\`],
    ['Errors', \`<div class=val>\${m.errors.lastHour}</div>last hour<br>\${m.errors.rate}% rate\`],
    ['CPU', \`<div class=val>\${m.cpu.percent}%</div>\`],
    ['Memory', \`<div class=val>\${m.memory.usedMB}</div>MB\`],
    ['Latency p50', \`<div class=val>\${m.latency.p50}</div>ms\`],
    ['Latency p95', \`<div class=val style=color:orange>\${m.latency.p95}</div>ms\`],
    ['Latency p99', \`<div class=val style=color:red>\${m.latency.p99}</div>ms\`],
  ].map(([title, body]) => \`<div class=card><h3>\${title}</h3>\${body}</div>\`).join('');
  if (m.alerts?.length) {
    document.getElementById('grid').innerHTML += '<div class="card alerts"><h3>Alerts</h3>' + m.alerts.map(a => \`<div class="alert \${a.level}">[\${new Date(a.time).toLocaleTimeString()}] \${a.message}</div>\`).join('') + '</div>';
  }
};
</script></body></html>`);
});

// SSE endpoint
app.get('/events', (req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  const clientId = Date.now();
  sseClients.push({ id: clientId, res });

  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify(metrics)}\n\n`);
  }, 2000);

  req.on('close', () => {
    clearInterval(interval);
    sseClients = sseClients.filter(c => c.id !== clientId);
  });
});

// API endpoints
app.get('/api/metrics', (req, res) => res.json(metrics));
app.get('/api/mock-alert', (req, res) => {
  metrics.alerts.push({ level: 'critical', message: `Manual alert: ${req.query.msg || 'Test alert'}`, time: new Date().toISOString() });
  res.json({ triggered: true });
});

app.listen(3000, () => console.log('Dashboard: http://localhost:3000'));
module.exports = app;
