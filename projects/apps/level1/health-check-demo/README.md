# Health Check Demo — Liveness, readiness, dependency checks

Three kinds of health checks:
- **Liveness**: am I alive? (used to decide whether to restart the container)
- **Readiness**: am I ready to serve traffic? (used to decide whether to route to me)
- **Deep health**: are my dependencies healthy? (DB, memory, disk, external APIs)

## Endpoints
```
GET /health               # all checks, 503 if any required fails
GET /health/live          # always 200 (process is running)
GET /health/ready         # 200 if DB is up, 503 otherwise
GET /health/db            # individual check
GET /health/memory        # heap usage
GET /health/disk          # can write to /tmp
GET /health/external      # fake dependency
GET /admin/history        # past check results
```

## Try
```bash
# Full health
curl http://localhost:3000/health
# { status: "healthy", checks: [...], timestamp: "..." }

# Liveness
curl http://localhost:3000/health/live
# { status: "alive" }

# Make external check fail
HEALTH_EXTERNAL_FAIL=1 node server.js
curl http://localhost:3000/health
# { status: "degraded", checks: [{ name: "external_api", status: "fail", error: "simulated outage" }] }
```

## What this teaches
1. **Liveness vs readiness**: different questions, different endpoints
2. **Multiple checks**: DB, memory, disk, event loop, external APIs
3. **Required vs optional**: DB required (no DB = dead), external optional (degraded = OK)
4. **Status levels**: healthy, degraded, unhealthy
5. **HTTP status codes**: 200 for healthy/degraded, 503 for unhealthy
6. **Latency tracking**: how long each check took
7. **History**: log every check for debugging
