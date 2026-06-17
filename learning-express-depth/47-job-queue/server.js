// 47 — Job Queue
// NEW CONCEPT: async work.
// Some tasks take time (send email, resize image, generate report).
// The client doesn't want to wait. So we return immediately with a job ID,
// then do the work in the background.
const express = require('express');
const app = express();
app.use(express.json());

// Job store
const jobs = new Map();
let nextId = 1;

// Job types and their handlers
const handlers = {
  'send-email': async (payload) => {
    // Simulate work
    await new Promise(r => setTimeout(r, 1000));
    return { sent: true, to: payload.to, messageId: 'msg_' + Date.now() };
  },
  'resize-image': async (payload) => {
    await new Promise(r => setTimeout(r, 2000));
    return { resized: true, url: payload.url, width: payload.width };
  },
  'generate-report': async (payload) => {
    await new Promise(r => setTimeout(r, 3000));
    return { report: 'ready', rows: 1000 };
  },
};

// Process the queue one job at a time
let processing = false;
async function processQueue() {
  if (processing) return;
  const job = Array.from(jobs.values()).find(j => j.status === 'pending');
  if (!job) return;

  processing = true;
  job.status = 'running';
  job.startedAt = new Date().toISOString();

  try {
    const handler = handlers[job.type];
    if (!handler) throw new Error('Unknown job type: ' + job.type);
    job.result = await handler(job.payload);
    job.status = 'completed';
  } catch (e) {
    job.status = 'failed';
    job.error = e.message;
  } finally {
    job.completedAt = new Date().toISOString();
    processing = false;
    setImmediate(processQueue);  // Process next
  }
}

// Submit a job
app.post('/jobs', (req, res) => {
  const { type, payload } = req.body;
  if (!type || !handlers[type]) return res.status(422).json({ error: 'unknown job type' });

  const id = 'job_' + nextId++;
  const job = { id, type, payload, status: 'pending', createdAt: new Date().toISOString() };
  jobs.set(id, job);
  setImmediate(processQueue);

  res.status(202).json({ id, status: 'pending', statusUrl: `/jobs/${id}` });
});

// Check job status
app.get('/jobs/:id', (req, res) => {
  const job = jobs.get(req.params.id);
  if (!job) return res.status(404).json({ error: 'Not found' });
  res.json(job);
});

// List all jobs
app.get('/jobs', (req, res) => {
  res.json({ count: jobs.size, jobs: Array.from(jobs.values()) });
});

app.listen(3000, () => console.log('Job queue on http://localhost:3000'));
