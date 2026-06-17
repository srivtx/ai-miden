# Graceful Shutdown Demo — Handle SIGTERM, drain in-flight requests

When Kubernetes/ECS/systemd wants to stop your service, they send SIGTERM. You should:
1. Stop accepting new requests (return 503)
2. Wait for in-flight requests to complete (up to N seconds)
3. Close the server, exit cleanly

## Endpoints
```
GET  /health            # shows inflight count
GET  /slow              # takes 3 seconds (useful for testing)
POST /work              # quick request
GET  /admin/status      # current state
```

## Try
```bash
# Terminal 1: start the server
node server.js

# Terminal 2: make a slow request, then SIGTERM
curl http://localhost:3000/slow &
PID=$!
sleep 0.5
kill -TERM <server-pid>    # sends SIGTERM
# Server logs: "[shutdown] SIGTERM received. 1 requests in flight."
# Slow request still completes successfully
# New requests get 503 shutting_down
```

## What this teaches
1. **SIGTERM handling**: the standard "please stop" signal
2. **Drain pattern**: stop accepting new, finish in-flight
3. **503 during shutdown**: tell clients to retry elsewhere
4. **`Connection: close` header**: tell the client/server to drop the connection
5. **Max wait timeout**: don't wait forever (10s in this demo)
6. **vs SIGKILL**: SIGKILL is immediate, no cleanup
