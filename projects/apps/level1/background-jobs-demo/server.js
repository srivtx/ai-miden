// Background Jobs Demo — In-process job queue with status tracking in SQLite.
const express = require('express');
const Database = require('better-sqlite3');
const crypto = require('crypto');
const app = express();
app.use(express.json());

const db = new Database(':memory:');
db.exec(`CREATE TABLE jobs (id TEXT PRIMARY KEY, type TEXT, status TEXT, progress INTEGER DEFAULT 0, payload TEXT, result TEXT, error TEXT, created_at INTEGER, updated_at INTEGER)`);

// === Job runner (in-process, single-worker) ===
const jobQueue = [];
let processing = false;

function enqueue(type, payload) {
  const id = 'job_' + crypto.randomBytes(6).toString('hex');
  const now = Date.now();
  db.prepare('INSERT INTO jobs (id, type, status, payload, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)').run(id, type, JSON.stringify(payload), 'pending', now, now);
  jobQueue.push(id);
  processNext();
  return id;
}

async function processNext() {
  if (processing) return;
  const id = jobQueue.shift();
  if (!id) return;
  processing = true;
  const job = db.prepare('SELECT * FROM jobs WHERE id = ?').get(id);
  if (!job) { processing = false; return; }
  db.prepare('UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?').run('running', Date.now(), id);
  try {
    const result = await runJob(job.type, JSON.parse(job.payload), (progress) => {
      db.prepare('UPDATE jobs SET progress = ?, updated_at = ? WHERE id = ?').run(progress, Date.now(), id);
    });
    db.prepare('UPDATE jobs SET status = ?, result = ?, updated_at = ? WHERE id = ?').run('completed', JSON.stringify(result), Date.now(), id);
  } catch (e) {
    db.prepare('UPDATE jobs SET status = ?, error = ?, updated_at = ? WHERE id = ?').run('failed', e.message, Date.now(), id);
  }
  processing = false;
  if (jobQueue.length) setImmediate(processNext);
}

// === Job types ===
async function runJob(type, payload, onProgress) {
  switch (type) {
    case 'send_email': return await fakeEmailSend(payload, onProgress);
    case 'resize_image': return await fakeResize(payload, onProgress);
    case 'generate_report': return await fakeReport(payload, onProgress);
    default: throw new Error('Unknown job type: ' + type);
  }
}

async function fakeEmailSend({ to, subject }, onProgress) {
  for (let i = 1; i <= 5; i++) { await sleep(200); onProgress(i * 20); }
  return { sent: true, to, subject, messageId: 'msg_' + crypto.randomBytes(4).toString('hex') };
}

async function fakeResize({ url, width, height }, onProgress) {
  for (let i = 1; i <= 10; i++) { await sleep(150); onProgress(i * 10); }
  return { resized: true, url, width, height, outputUrl: url + '?w=' + width + '&h=' + height };
}

async function fakeReport({ userId, period }, onProgress) {
  for (let i = 1; i <= 20; i++) { await sleep(100); onProgress(i * 5); }
  return { report: 'ok', userId, period, rows: 1234 };
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// === Routes ===
app.post('/jobs', (req, res) => {
  const { type, payload } = req.body;
  if (!type) return res.status(422).json({ error: 'missing_type' });
  const id = enqueue(type, payload || {});
  res.status(202).json({ id, status: 'pending', statusUrl: '/jobs/' + id });
});

app.get('/jobs/:id', (req, res) => {
  const job = db.prepare('SELECT * FROM jobs WHERE id = ?').get(req.params.id);
  if (!job) return res.status(404).json({ error: 'not_found' });
  res.json({
    id: job.id, type: job.type, status: job.status, progress: job.progress,
    result: job.result ? JSON.parse(job.result) : null,
    error: job.error,
    createdAt: new Date(job.created_at).toISOString(),
    updatedAt: new Date(job.updated_at).toISOString(),
  });
});

app.get('/jobs', (req, res) => {
  const status = req.query.status;
  const jobs = status ? db.prepare('SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC LIMIT 50').all(status) : db.prepare('SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50').all();
  res.json({ count: jobs.length, jobs: jobs.map(j => ({ id: j.id, type: j.type, status: j.status, progress: j.progress })) });
});

app.listen(3000, () => console.log('Background jobs demo :3000'));
module.exports = app;
