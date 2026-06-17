# Bulk Operations Demo — Insert/update/delete many rows in one request

Most APIs do one thing per request. For data migrations, imports, and admin tools, you need bulk operations. The trick: process asynchronously, return a job ID, let the client poll for progress.

## Endpoints
```
POST /bulk/insert      { items: [{id, name, value}, ...] }
POST /bulk/update      { updates: [{id, value}, ...] }
POST /bulk/delete      { ids: ["it_1", "it_2", ...] }
GET  /bulk/jobs/:id                   # progress: { processed, total, errors }
GET  /items                            # see what was inserted
GET  /items/count                      # total count
```

## Try
```bash
# Bulk insert 1000 items
curl -X POST http://localhost:3000/bulk/insert \
  -H "Content-Type: application/json" \
  -d '{"items": [{"name": "Item 1", "value": 10}, {"name": "Item 2", "value": 20}, ...]}'
# 202 { jobId: "bj_...", statusUrl: "/bulk/jobs/bj_..." }

# Poll for status
curl http://localhost:3000/bulk/jobs/bj_...
# { status: "running", total: 1000, processed: 500, errors: 0 }

# When done
# { status: "completed", total: 1000, processed: 1000, errors: 0, finished_at: ... }
```

## What this teaches
1. **Async pattern**: client gets 202 + job ID, polls for status
2. **Progress tracking**: processed/total/percentage
3. **Partial success**: some items may fail, others succeed
4. **Error reporting**: which items failed and why
5. **Per-row validation**: validate each item, skip the bad ones
6. **vs sync**: bulk of 10K items would time out as a single request
