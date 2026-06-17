# Background Jobs Demo — In-process job queue with progress tracking

Jobs that take time (send email, resize image, generate report) shouldn't block HTTP responses. The request returns 202 "Accepted" with a job ID. The job runs in the background. The client polls the job status.

## Endpoints
```
POST /jobs           { type, payload }    -> { id, statusUrl }
GET  /jobs/:id                            -> { id, type, status, progress, result }
GET  /jobs?status=...                     -> list jobs by status
```

## Job types
- `send_email` — simulate sending (1s, 5 progress updates)
- `resize_image` — simulate resizing (1.5s, 10 progress updates)
- `generate_report` — simulate report (2s, 20 progress updates)

## Try
```bash
# Enqueue
JOB=$(curl -X POST http://localhost:3000/jobs -H "Content-Type: application/json" \
  -d '{"type": "send_email", "payload": {"to": "alice@example.com", "subject": "Hi"}}' | jq -r .id)

# Poll status
curl http://localhost:3000/jobs/$JOB
# { id: "...", status: "pending|running|completed", progress: 0-100, result: {...} }
```

## What this teaches
1. **202 Accepted**: the request was queued, not completed
2. **Async pattern**: enqueue → return immediately → process in background
3. **Progress tracking**: 0-100% as the job runs
4. **Status state machine**: pending → running → completed/failed
5. **Job queue**: in-memory list, processed serially
6. **Polling pattern**: client polls status URL until completed
