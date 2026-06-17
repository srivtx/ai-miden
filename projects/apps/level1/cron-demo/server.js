// Cron Jobs Demo — Scheduled tasks with node-cron-like pattern, persisted in SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE tasks (id TEXT PRIMARY KEY, name TEXT, schedule TEXT, last_run INTEGER, last_status TEXT, last_error TEXT, run_count INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1)`);
db.exec(`CREATE TABLE runs (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT, started_at INTEGER, finished_at INTEGER, status TEXT, output TEXT)`);

// === Cron parser (5-field: minute hour day month weekday) ===
function parseField(field, min, max) {
  if (field === '*') return Array.from({ length: max - min + 1 }, (_, i) => i + min);
  if (field.includes(',')) return field.split(',').flatMap(f => parseField(f, min, max));
  if (field.includes('/')) {
    const [range, step] = field.split('/');
    const start = range === '*' ? min : parseInt(range);
    const result = [];
    for (let i = start; i <= max; i += parseInt(step)) result.push(i);
    return result;
  }
  if (field.includes('-')) {
    const [a, b] = field.split('-').map(Number);
    return Array.from({ length: b - a + 1 }, (_, i) => i + a);
  }
  return [parseInt(field)];
}

function shouldRun(schedule, now = new Date()) {
  const [m, h, d, mo, w] = schedule.split(' ');
  const minutes = parseField(m, 0, 59);
  const hours = parseField(h, 0, 23);
  const days = parseField(d, 1, 31);
  const months = parseField(mo, 1, 12);
  const weekdays = parseField(w, 0, 6);
  return minutes.includes(now.getMinutes()) && hours.includes(now.getHours()) && days.includes(now.getDate()) && months.includes(now.getMonth() + 1) && weekdays.includes(now.getDay());
}

// === Task registry ===
const taskHandlers = {
  cleanup_logs: async () => { /* would clean old logs */ return { deleted: 42 }; },
  send_digest: async () => { /* would send daily email */ return { sent: 15 }; },
  refresh_cache: async () => { /* would refresh Redis */ return { keysRefreshed: 200 }; },
  health_check: async () => { return { ok: true, ts: Date.now() }; },
};

async function runTask(id) {
  const task = db.prepare('SELECT * FROM tasks WHERE id = ?').get(id);
  if (!task) return;
  const handler = taskHandlers[task.name];
  if (!handler) return;
  const started = Date.now();
  const runId = db.prepare('INSERT INTO runs (task_id, started_at, status) VALUES (?, ?, ?)').run(id, started, 'running').lastInsertRowid;
  try {
    const result = await handler();
    db.prepare('UPDATE runs SET finished_at = ?, status = ?, output = ? WHERE id = ?').run(Date.now(), 'success', JSON.stringify(result), runId);
    db.prepare('UPDATE tasks SET last_run = ?, last_status = ?, run_count = run_count + 1 WHERE id = ?').run(started, 'success', id);
    console.log(`[cron] ${task.name} success in ${Date.now() - started}ms`);
  } catch (e) {
    db.prepare('UPDATE runs SET finished_at = ?, status = ?, output = ? WHERE id = ?').run(Date.now(), 'failed', e.message, runId);
    db.prepare('UPDATE tasks SET last_run = ?, last_status = ?, last_error = ?, run_count = run_count + 1 WHERE id = ?').run(started, 'failed', e.message, id);
    console.error(`[cron] ${task.name} failed: ${e.message}`);
  }
}

// === Scheduler loop (runs every minute) ===
let lastCheck = '';
setInterval(() => {
  const now = new Date();
  const key = `${now.getMinutes()}-${now.getHours()}-${now.getDate()}-${now.getMonth() + 1}-${now.getDay()}`;
  if (key === lastCheck) return;
  lastCheck = key;
  const tasks = db.prepare('SELECT * FROM tasks WHERE enabled = 1').all();
  for (const task of tasks) {
    if (shouldRun(task.schedule)) runTask(task.id);
  }
}, 5000); // every 5s for demo

// === Routes ===
app.get('/tasks', (req, res) => res.json({ tasks: db.prepare('SELECT * FROM tasks').all() }));
app.post('/tasks', (req, res) => {
  const { name, schedule } = req.body;
  if (!name || !schedule) return res.status(422).json({ error: 'missing_fields' });
  if (!taskHandlers[name]) return res.status(400).json({ error: 'unknown_task', available: Object.keys(taskHandlers) });
  try { parseField(schedule.split(' ')[0], 0, 59); }
  catch (e) { return res.status(400).json({ error: 'invalid_schedule', example: '* * * * *' }); }
  const id = 't_' + crypto.randomBytes(4).toString('hex');
  db.prepare('INSERT INTO tasks (id, name, schedule) VALUES (?, ?, ?)').run(id, name, schedule);
  res.status(201).json({ id, name, schedule });
});
app.post('/tasks/:id/run', (req, res) => { runTask(req.params.id); res.json({ triggered: true }); });
app.get('/runs', (req, res) => {
  const limit = parseInt(req.query.limit) || 20;
  res.json({ runs: db.prepare('SELECT * FROM runs ORDER BY id DESC LIMIT ?').all(limit) });
});

// Seed
db.prepare('INSERT INTO tasks (id, name, schedule) VALUES (?, ?, ?)').run('t1', 'health_check', '* * * * *');
db.prepare('INSERT INTO tasks (id, name, schedule) VALUES (?, ?, ?)').run('t2', 'cleanup_logs', '0 3 * * *');
db.prepare('INSERT INTO tasks (id, name, schedule) VALUES (?, ?, ?)').run('t3', 'send_digest', '0 9 * * 1');

app.listen(3000, () => console.log('Cron demo :3000 — GET /tasks, POST /tasks, POST /tasks/:id/run'));
module.exports = app;
