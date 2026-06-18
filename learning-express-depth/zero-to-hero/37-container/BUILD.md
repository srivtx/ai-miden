# The Build

> *"A container is a lightweight, isolated, reproducible unit."*

We are going to add Docker. The change from project 36: add a `Dockerfile` and a `docker-compose.yml`.

## Setup

```bash
# Install Docker
# macOS: https://docs.docker.com/docker-for-mac/install/
# Linux: https://docs.docker.com/engine/install/
# Windows: https://docs.docker.com/docker-for-windows/install/

# Verify Docker is installed
docker --version
docker compose version
```

## The Code

### `.dockerignore`

```
node_modules
npm-debug.log
.env
.git
.gitignore
tests
coverage
.vscode
.idea
```

We exclude these from the build context. Smaller context = faster builds.

### `Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Run as non-root user
USER node

EXPOSE 3000

CMD ["node", "server.js"]
```

### `docker-compose.yml`

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
      - LOG_LEVEL=info
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USER=${SMTP_USER}
      - SMTP_PASS=${SMTP_PASS}
    depends_on:
      - redis
    volumes:
      - app-data:/app/data
      - app-uploads:/app/uploads
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  app-data:
  app-uploads:
  redis-data:
```

## Run It

```bash
# Build and start
docker compose up --build

# In another terminal, verify
curl http://localhost:3000/
# {"message":"Welcome to the API."}

# Stop
docker compose down
```

The pain of "it works on my machine" is solved. The app runs the same in any environment.

---

## Experiments

### Experiment 1: Multi-stage for smaller image

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app . .
CMD ["node", "server.js"]
```

Use `npm ci --production` to skip dev dependencies. The final image is smaller.

### Experiment 2: Health check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1
```

Docker checks if the container is healthy. If not, it can restart.

### Experiment 3: Run in production

```bash
# Build the image
docker build -t myapp:latest .

# Run with environment variables
docker run -d \
  --name myapp \
  -p 3000:3000 \
  -e REDIS_HOST=redis.example.com \
  -e STRIPE_SECRET_KEY=sk_live_... \
  myapp:latest
```

### Experiment 4: Push to a registry

```bash
# Tag the image
docker tag myapp:latest registry.example.com/myapp:v1.0.0

# Push
docker push registry.example.com/myapp:v1.0.0

# Pull and run on another machine
docker pull registry.example.com/myapp:v1.0.0
docker run -d -p 3000:3000 registry.example.com/myapp:v1.0.0
```

### Experiment 5: Use a smaller base image

```dockerfile
FROM gcr.io/distroless/nodejs20-debian12
```

Distroless images are even smaller than Alpine. They have no shell, no package manager. Just the app and its dependencies.

---

## Summary

You now have Docker. The app is reproducible. Anyone with Docker can run it. Deploy is `docker compose up`.

This is the foundation of *containerization*. From here, every project that needs reproducible deployments can use Docker. The patterns (Dockerfile, docker-compose, multi-stage builds) are universal.

In project 38, we will add **CI/CD**. We will set up GitHub Actions to run tests automatically on every commit and deploy on merge to main.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
