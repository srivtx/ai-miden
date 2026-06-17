# 06 — Exports (Analytics)

Export events as CSV or JSON. Stream large exports.

**What's new:**
- `/export/events.json` — NDJSON stream (one JSON per line)
- `/export/events.csv` — CSV with proper escaping
- `Content-Disposition` header for download
- Streaming (we don't load all data into memory)

**Why streaming?** A million events is 200MB of JSON. Loading it all into memory, building a string, sending it = 200MB in memory. Streaming = constant memory regardless of size.

**Why NDJSON instead of a JSON array?** A JSON array needs the whole document to be parsed. NDJSON (one JSON per line) can be processed line by line. Same data, easier to handle large files.

**CSV escaping:** if a field contains `"`, we replace with `""` (CSV standard for escaping). Then wrap in quotes.

## Run
```bash
npm install && node server.js
```

```bash
# Track some events first
curl -X POST http://localhost:3000/track -H "Content-Type: application/json" -d '{"user_id": "u1", "event_name": "page_view"}'

# Export as CSV
curl http://localhost:3000/export/events.csv -o events.csv
cat events.csv
# id,user_id,event_name,ts,properties
# 1,u1,page_view,2024-12-15 14:00:00,"{}"

# Export as JSON
curl http://localhost:3000/export/events.json -o events.ndjson
cat events.ndjson
# {"id":1,"user_id":"u1","event_name":"page_view","ts":"2024-12-15 14:00:00","properties":{}}
```

## What this stage teaches
- CSV vs JSON export
- NDJSON (newline-delimited JSON)
- Streaming for large files
- Content-Disposition header
- CSV escaping

## Next
**07-alerts** — get notified when metrics cross thresholds. Anomaly detection.
