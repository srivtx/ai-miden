// 09_background_jobs.js — Queue-based job processing. Learn: Bull, Redis, retry, progress.

const express = require('express');
const Queue = require('bull');
const app = express();
app.use(express.json());

// ---- Job queues ----
const emailQueue = new Queue('email', 'redis://localhost:6379');
const reportQueue = new Queue('report', 'redis://localhost:6379');

// ---- Process email jobs ----
emailQueue.process(async (job) => {
  const { to, subject, body } = job.data;
  console.log(`[EMAIL] Sending to ${to}: ${subject}`);

  // Report progress (can be queried by client)
  for (let i = 0; i <= 100; i += 20) {
    await new Promise(r => setTimeout(r, 500)); // simulate sending
    job.progress(i);
  }

  return { sent: true, messageId: `msg_${Date.now()}` };
});

// ---- Process report generation (heavy, with retry) ----
reportQueue.process(async (job) => {
  const { userId, format } = job.data;
  console.log(`[REPORT] Generating ${format} report for user ${userId}`);

  // Simulate occasional failure
  if (Math.random() < 0.2) throw new Error('Generation failed (simulated)');

  await new Promise(r => setTimeout(r, 3000)); // heavy work
  return { url: `https://reports.example.com/${userId}_${Date.now()}.${format}` };
});

// ---- API: enqueue an email ----
app.post('/send-email', async (req, res) => {
  const { to, subject, body } = req.body;
  const job = await emailQueue.add({ to, subject, body });
  res.json({ message: 'Email queued', jobId: job.id });
});

// ---- API: enqueue a report ----
app.post('/reports', async (req, res) => {
  const job = await reportQueue.add(
    { userId: req.body.userId, format: req.body.format || 'pdf' },
    { attempts: 3, backoff: { type: 'exponential', delay: 2000 } } // retry 3x
  );
  res.json({ message: 'Report queued', jobId: job.id });
});

// ---- API: check job status ----
app.get('/jobs/:id', async (req, res) => {
  const queues = [emailQueue, reportQueue];
  for (const q of queues) {
    const job = await q.getJob(req.params.id);
    if (!job) continue;
    const state = await job.getState();
    const progress = job._progress;
    const result = job.returnvalue;
    res.json({ id: job.id, state, progress, result });
    return;
  }
  res.status(404).json({ error: 'Job not found' });
});

// ---- Dashboard (Bull Dashboard UI at /admin/queues) ----
const { createBullBoard } = require('@bull-board/api');
const { BullAdapter } = require('@bull-board/api/bullAdapter');
const { ExpressAdapter } = require('@bull-board/express');
const serverAdapter = new ExpressAdapter();
createBullBoard({ queues: [new BullAdapter(emailQueue), new BullAdapter(reportQueue)], serverAdapter });
serverAdapter.setBasePath('/admin/queues');
app.use('/admin/queues', serverAdapter.getRouter());

app.listen(3000, () => console.log('Job queue on :3000 | Dashboard: http://localhost:3000/admin/queues'));
/*
Test:
  curl -X POST localhost:3000/send-email -H "Content-Type: application/json" \
    -d '{"to":"user@test.com","subject":"Hello","body":"Test email"}'
  curl -X POST localhost:3000/reports -H "Content-Type: application/json" -d '{"userId":42}'
  curl localhost:3000/jobs/1   # check status
*/
