# The Thought

> *"A container is a lightweight, isolated, reproducible unit. The Dockerfile is the recipe."*

## Image vs. Container

Two important concepts:

- **Image**: a snapshot of the filesystem and config. Like a class. Read-only.
- **Container**: a running instance of an image. Like an object. Writable.

You build an image from a `Dockerfile`. You run a container from an image.

```
Dockerfile → docker build → Image → docker run → Container
```

You can have multiple containers from the same image (like multiple objects from a class).

## The Dockerfile

A `Dockerfile` is a recipe for building an image. Each line is an instruction:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

- `FROM node:20-alpine`: the base image. Alpine is a minimal Linux (~5MB). Node 20 is the version.
- `WORKDIR /app`: set the working directory inside the container.
- `COPY package*.json ./`: copy `package.json` and `package-lock.json` first (for layer caching).
- `RUN npm ci`: install dependencies.
- `COPY . .`: copy the rest of the app.
- `EXPOSE 3000`: document that the app listens on port 3000.
- `CMD ["node", "server.js"]`: the command to run when the container starts.

## Multi-Stage Builds

A multi-stage build uses multiple `FROM` instructions. The first stage builds the app. The second stage copies only the built artifacts.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app . .
```

The final image only has the production dependencies (`node_modules`) and the app code. The dev dependencies are excluded. The image is smaller.

## Layer Caching

Docker caches each layer. If a layer hasn't changed, Docker reuses the cache. This makes builds fast.

We copy `package.json` first and run `npm ci` before copying the rest. If only the app code changes, Docker reuses the `npm ci` layer. We don't reinstall dependencies on every code change.

## docker-compose

`docker-compose.yml` orchestrates multiple containers. For our app, we have two:

- `app`: the Node.js server
- `redis`: the Redis server (for cache, queue, presence, rate limiting)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - REDIS_HOST=redis
      - NODE_ENV=production
    depends_on:
      - redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

- `app` is built from the local `Dockerfile`
- `app` exposes port 3000 to the host
- `app` uses `redis` as the Redis host (Docker DNS)
- `redis` is the official Redis image

`docker compose up` starts both services. `docker compose down` stops them.

## Common Confusions (read these)

**Confusion 1: "Why not just use a VM?"**
VMs are heavier. They include a full OS kernel. Containers share the host kernel. Containers start in milliseconds; VMs take seconds. Containers use less memory.

**Confusion 2: "Why Alpine?"**
Alpine is a minimal Linux distribution. The base image is ~5MB. The full Node image is ~900MB. For production, smaller is better.

**Confusion 3: "Why multi-stage?"**
The dev dependencies (TypeScript, test runners, etc.) are not needed in production. Multi-stage builds produce a smaller final image.

**Confusion 4: "Where does the database file go?"**
In a container, the file system is ephemeral. Restart the container, the file is gone. We use a volume (named volume or bind mount) to persist the database file outside the container.

**Confusion 5: "What about environment variables?"**
We pass them via `environment` in `docker-compose.yml`. For production, use a secrets manager (e.g., Docker secrets, AWS Secrets Manager).

**Confusion 6: "What about secrets?"**
Don't put secrets in the Dockerfile. Use environment variables or a secrets manager. We use environment variables.

**Confusion 7: "Why expose port 3000?"**
The app listens on 3000 inside the container. We map it to 3000 on the host. Users access the app at `http://localhost:3000`.

**Confusion 8: "What about `EXPOSE` vs `ports`?"**
`EXPOSE` is documentation (the container listens on this port). `ports` actually maps the port to the host. We need both.

## What We Are About to Build

A `Dockerfile` and `docker-compose.yml`. The app runs in a container. Redis runs in a container. They communicate via Docker's internal network.

In [BUILD.md](./BUILD.md) we will go line by line.
