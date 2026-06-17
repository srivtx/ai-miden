// 14_background_jobs.js — Bull queues: enqueue, process, retry, progress, delay, priority.
const express = require('express');
const Queue = require('bull');
const app = express();
app.use(express.json());

const emailQueue = new Queue('email');
const reportQueue = new Queue('report');

emailQueue.process(async (job) => {
  for (let i = 0; i <= 100; i += 25) {
    await new Promise(r => setTimeout(r, 300));
    job.progress(i);
  }
  return { sent: true, msgId: Date.now() };
});

reportQueue.process(async (job) => {
  if (Math.random() < 0.25) throw new Error('Failed');
  await new Promise(r => setTimeout(r, 2000));
  return { url: `https://reports/rep_${Date.now()}.pdf` };
});

// Enqueue with options
app.post('/email', async (req, res) => {
  const job = await emailQueue.add(req.body, { priority: 1, attempts: 3 });
  res.json({ jobId: job.id, status: 'queued' });
});

app.post('/report', async (req, res) => {
  const job = await reportQueue.add(req.body, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 },
    delay: req.body.sendAt ? new Date(req.body.sendAt).getTime() - Date.now() : 0,
  });
  res.json({ jobId: job.id });
});

app.get('/jobs/:id', async (req, res) => {
  const job = await emailQueue.getJob(req.params.id) || await reportQueue.getJob(req.params.id);
  if (!job) return res.status(404).json({ error: 'Not found' });
  const state = await job.getState();
  const progress = job._progress;
  const result = job.returnvalue;
  const failed = job.failedReason;
  res.json({ id: job.id, state, progress, result, failed });
});

app.listen(3000, () => console.log('Jobs :3000'));
