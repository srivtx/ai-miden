# 47 — Job Queue

**New concept:** async work. Some tasks take time. The client doesn't want to wait. So we return immediately with a job ID, and do the work in the background.

## Run it

```bash
npm install
node server.js
```

```bash
# Submit a job
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type": "send-email", "payload": {"to": "alice@example.com"}}'
# 202 { "id": "job_1", "status": "pending", "statusUrl": "/jobs/job_1" }

# Check status (right away, it's pending or running)
curl http://localhost:3000/jobs/job_1
# { "id": "job_1", "status": "running", ... }

# Wait a second, then check again
sleep 2
curl http://localhost:3000/jobs/job_1
# { "status": "completed", "result": { "sent": true, ... } }

# Submit a slower job
curl -X POST http://localhost:3000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type": "generate-report", "payload": {}}'
# This takes 3 seconds
```

## How to think about it

When you upload a video to YouTube, you don't wait while it processes. You get back a "processing" status, then YouTube emails you when it's done. That's a job queue.

The client doesn't wait. The server does the work later. The client polls (or gets a webhook) to find out when it's done.

## How to build it (line by line)

```js
const handlers = {
  'send-email': async (payload) => { ... },
  'resize-image': async (payload) => { ... },
  'generate-report': async (payload) => { ... },
};
```

**Lines 14-26.** A map of job types to handler functions. Each one is async and returns a result.

```js
app.post('/jobs', (req, res) => {
  const id = 'job_' + nextId++;
  const job = { id, type, payload, status: 'pending' };
  jobs.set(id, job);
  setImmediate(processQueue);
  res.status(202).json({ id, status: 'pending' });
});
```

**Lines 51-58.** Submit a job. Return 202 (Accepted) with a job ID. Trigger the queue to start processing.

**`202 Accepted`** — the right status code for "we got your request, we're working on it."

```js
app.get('/jobs/:id', (req, res) => {
  const job = jobs.get(req.params.id);
  res.json(job);
});
```

**Lines 61-65.** Check job status. Returns the current state.

## What we learned

1. Job queues: submit now, do later
2. Status 202 means "accepted, working on it"
3. The job has a state machine: pending → running → completed/failed
4. Real systems: Bull, BullMQ, Celery, Sidekiq

## What's next

In **48-caching** we add a cache so we don't have to recompute or re-fetch the same data.
