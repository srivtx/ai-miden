# Streams Demo — File streams, NDJSON, CSV, SSE, upload streams

Streams let you handle data that's too big to fit in memory. Instead of loading everything at once, you process chunks as they arrive.

## Endpoints
```
GET  /stream/file        # stream a 10MB file
GET  /stream/ndjson      # stream 100 JSON objects (one per line)
GET  /stream/csv         # stream a 10K-row CSV
GET  /stream/sse         # server-sent events (20 ticks)
PUT  /stream/upload      # receive a stream, count bytes
GET  /admin/file-info    # file size info
```

## What this teaches
1. **`fs.createReadStream`**: read a file in chunks
2. **`.pipe(res)`**: send the stream to the response
3. **Backpressure**: `res.write()` returns false when the buffer is full; wait for `drain`
4. **NDJSON**: newline-delimited JSON, one record per line
5. **CSV streaming**: write a large file without keeping it in memory
6. **Server-Sent Events (SSE)**: one-way streaming from server to client
7. **Request streams**: `req.on('data', ...)` to read uploaded data
