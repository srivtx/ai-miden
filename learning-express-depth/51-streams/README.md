# 51 — Streams

**New concept:** streaming data in chunks instead of loading it all at once.

When you have a 1GB file, you don't want to load it all into memory before sending. Streams send it piece by piece. Same for uploads — you don't want to buffer the whole file before saving.

## Run it

```bash
npm install
node server.js
```

```bash
# Stream a file (large)
curl http://localhost:3000/stream/file -o /tmp/downloaded.txt
wc -l /tmp/downloaded.txt
# 100000 lines

# Stream NDJSON (one JSON per line)
curl http://localhost:3000/stream/ndjson
# Streams 100 records, one per line

# Stream a CSV
curl http://localhost:3000/stream/csv -o /tmp/export.csv
wc -l /tmp/export.csv
# 10001 lines

# Upload a stream
curl -X PUT --data-binary @/tmp/downloaded.txt http://localhost:3000/upload-stream
# { "received": 3500000 }
```

## How to think about it

A stream is like a fire hose. Water flows in, you don't have to fill a pool first. You can drink from the hose as water comes out. Same with data: it comes in chunks, you can process it as it arrives.

## How to build it (line by line)

```js
fs.createReadStream(BIG_FILE).pipe(res);
```

**Line 17.** Two lines that do a lot. `createReadStream` opens the file and creates a stream. `.pipe(res)` connects the file stream to the response stream. Data flows from file to network, in chunks.

**`pipe`** is a Node method that connects two streams. The source is a readable stream, the destination is a writable stream.

```js
res.write(JSON.stringify(...) + '\n');
```

**Line 22.** Write one line. The `+ '\n'` is what makes it NDJSON (newline-delimited).

**The client reads line by line.** Instead of waiting for the whole response, it can process each line as it arrives.

## What we learned

1. Streams send data in chunks, not all at once
2. `pipe` connects streams together
3. NDJSON is a streaming format: one JSON per line
4. CSV can be streamed too
5. For uploads, you can receive a stream with `req.on('data', ...)`
6. Real systems use streams for big files: video, logs, exports

## What's next

In **52-sse** we use Server-Sent Events for one-way real-time streams from server to client.
