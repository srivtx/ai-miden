# Docker Demo — Multi-stage Dockerfile + docker-compose

A minimal Express app, packaged in a 50MB image, with a compose file for local dev.

## Files
- `server.js` — minimal app
- `package.json` — deps (just express)
- `Dockerfile` — multi-stage, alpine, non-root, healthcheck
- `docker-compose.yml` — full local setup
- `.dockerignore` — exclude dev cruft

## Run
```
docker-compose up --build
# Visit http://localhost:3000
```

## Build manually
```
docker build -t docker-demo:1.0 .
docker run -p 3000:3000 docker-demo:1.0
```

## What this teaches
1. **Multi-stage builds**: smaller final image, only production deps
2. **Layer caching**: `COPY package*.json` first, then `npm ci`, then code (so code changes don't bust npm cache)
3. **`.dockerignore`**: prevent node_modules from being COPYed in
4. **Non-root user**: `USER node` so the process doesn't run as root
5. **Healthcheck**: `HEALTHCHECK` tells Docker when the container is healthy
6. **Compose**: one command runs everything, with volumes for persistence
