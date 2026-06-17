## Why it exists (THE PROBLEM)

You deploy to production. Something breaks. You ssh in, `tail -f /var/log/app.log`, and watch... nothing. Because the bug only happens for 1% of users and the log level is `info`, so the bug is buried in 100,000 lines of normal traffic. Or the log is just `console.log("error: " + err.message)` and you have no idea what request, what user, what state.

**Logging is the eyes of production.** Without good logging, you're flying blind. With it, you can answer: "what happened when this user got this error?" in seconds.

The five problems bad logging creates:
1. **No context**: `console.log("user not found")` — which user? which request? which tenant?
2. **Wrong level**: all logs at `info` level = noise. Important events lost.
3. **No structure**: text logs are hard to search, graph, alert on.
4. **No request ID**: can't correlate logs from the same request.
5. **No correlation**: API call to service A, service A calls service B, but their logs are separate.

## Definition (very simple)

**Log level** = severity. Standard: `trace`, `debug`, `info`, `warn`, `error`, `fatal`. Lower = more verbose. In production: `info` or `warn`. In dev: `debug` or `trace`.

**Structured log** = a log entry with typed fields, not a string. JSON is the standard. `{ timestamp, level, message, requestId, userId, ...fields }`. Searchable. Graphable. Alertable.

**Context** = the data that makes the log entry useful. `requestId`, `userId`, `sessionId`, `traceId`, `tenantId`. Pass through the request, attach to every log line.

**Log shipping** = sending logs from the app to a central store. The app writes to stdout (Docker captures) or a file. A sidecar (Filebeat, Fluentd) ships to Elasticsearch, Loki, Datadog.

**Log rotation** = splitting a single log file into many. Daily files: `app.log.2024-01-15`. Old files are compressed, then deleted after N days.

**Sampling** = logging only some events. At high QPS, logging every event is too expensive. Sample 1% of `info` events, but log 100% of `error` events.

## Real-life analogy

**Bad logging = a security camera with a foggy lens.** It's "recording" but you can't see anything. When something happens, you can't tell who, what, when.

**Good logging = a security camera with timestamps, motion detection, and labels.** "Person entered at 14:32:05. Motion detected at 14:35:20. Door opened at 14:35:21." You can search by time, by person, by event. Reconstruct what happened.

**Structured logging = the camera's event log.** Each line is `{"time": "...", "event": "motion", "subject": "person", "location": "lobby"}`. You can filter `event:motion AND location:lobby`. You can't filter `console.log` text easily.

## Tiny numeric example

Bad log:
```
2024-01-15 10:30:00 INFO user signed in
2024-01-15 10:30:01 ERROR payment failed
```

Good log:
```json
{"timestamp":"2024-01-15T10:30:00.123Z","level":"info","msg":"user signed in","requestId":"req_abc","userId":42,"email":"alice@example.com","ip":"1.2.3.4","durationMs":87}
{"timestamp":"2024-01-15T10:30:01.456Z","level":"error","msg":"payment failed","requestId":"req_def","userId":42,"orderId":"ord_99","error":{"code":"card_declined","declineCode":"insufficient_funds"},"durationMs":1230}
```

With the second, you can:
- Search: `level:error AND userId:42` → all errors for user 42
- Graph: `error.code` over time → which error is rising
- Alert: `count(level:error) > 100/minute` → page the on-call
- Correlate: `requestId:req_abc` → all logs for that request

## Common confusion (5+ bullet points)

1. **"I have `console.log` everywhere. It's fine."** No. `console.log` writes to stdout. In production, stdout is captured by Docker, but you can't search it without a log shipper. And `console.log("err:", err)` is unstructured. Switch to a logging library (Winston, Pino, Bunyan) and structured JSON.

2. **"Log everything at debug in production."** Disk fills up. Performance degrades. Pick: `error` for failures, `warn` for unusual-but-recoverable, `info` for state changes (signed in, signed out, created, deleted), `debug` for dev only. Don't use `debug` in prod.

3. **"PII in logs is fine."** NO. Email, IP, name, address — if you log it, you store it. If you store it, you need to comply with GDPR, CCPA, etc. Mask PII: `email: "a***@e****.com"` or hash it. Some companies log only the user ID, not the email.

4. **"I'll use `req.log.info()` everywhere."** Some frameworks have this (Pino, Bunyan). It's nice. The point: every log line in a request handler has `requestId`, `userId`, `path`. The logger adds these automatically.

5. **"Async logging is too complex."** It's the default. Pino, Bunyan, Winston all write to a buffer, flush async. The OS handles the disk. You don't wait for the disk. The trade-off: a crash might lose the last few logs. Acceptable.

6. **"I'll log to a file and tail it."** That works for one server. For 10 servers, you have 10 log files. Use log shipping: app writes to stdout, Docker captures, sidecar ships to central store.

7. **"I need to log every event for compliance."** No. Log what compliance requires (auth events, data changes, access). Don't log chat messages, support tickets, etc. for compliance reasons. Talk to your legal team.

## Key properties

| Property | Text log | Structured log |
|---|---|---|
| Searchable | grep | query language (KQL, Lucene) |
| Graphable | awk/sed | direct (timestamp + value) |
| Alertable | no | yes (count over time) |
| Storage | text | JSON lines (still text) |
| Cost to ship | low | low |
| Human readable | yes | yes (formatted) |

## Log levels in practice

| Level | When to use | Example |
|---|---|---|
| `error` | Failed operation that affects a user | DB query failed, payment declined |
| `warn` | Unusual but recoverable | Retry succeeded, deprecated API used |
| `info` | State changes, business events | User signed up, order created |
| `debug` | Diagnostic info (dev only) | Function entry/exit, variable values |
| `trace` | Very verbose (rare) | Every loop iteration, every request byte |

## Request-scoped logging (the killer pattern)

```js
// Middleware
app.use((req, res, next) => {
  req.log = logger.child({ requestId: req.requestId, userId: req.user?.id, path: req.path });
  next();
});

// In handler
app.get('/users/:id', (req, res) => {
  req.log.info({ userId: req.params.id }, 'fetching user');
  // logger auto-includes requestId, userId, path
});
```

Every log line in the request is correlated. Search by `requestId` → all logs for that request.

## Connection to our projects

For our 73 apps, add a logger:
```js
const pino = require('pino');
const logger = pino({ level: process.env.LOG_LEVEL || 'info' });
```
Use `logger.info({ userId, requestId }, 'message')` everywhere. The observability service we built stores these in SQLite. In production, ship to Loki or Datadog.

For CortexCode and logogen: log every request, every generation, every error. The user reports "I got a bad result" — search by `requestId`, see the full request, the model output, the latency. Fix the issue.
