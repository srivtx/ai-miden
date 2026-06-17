## Why it exists (THE PROBLEM)

"Works on my machine." The senior dev says it. The new hire tries to run it. Doesn't work. Different Node version. Different Python version. SQLite on Mac vs Linux. The list of "almost right" ways to set up a dev environment is infinite. Every new dev spends 3 days debugging setup instead of writing code.

**Docker solves this.** A `Dockerfile` is a recipe: "install Node 18, copy this code, run this command." Anyone with Docker runs the same thing. Mac, Windows, Linux, cloud. The image is the same byte-for-byte. "Works on my machine" becomes "works in the image." CI runs the same image as production. No more "but it worked in staging."

The second problem: "we need to deploy to a different server." Without Docker, you SSH in, install Node, copy files, run npm install, configure nginx, hope you didn't miss anything. With Docker: `docker run myimage`. That's it.

## Definition (very simple)

**Image** = a snapshot. A read-only template that includes the OS, libraries, code, and config. Like a class in OOP: blueprint for containers.

**Container** = a running instance of an image. Like an object: an instance of the class. You can run 10 containers from the same image. Each has its own filesystem (in a layer), network, processes.

**Dockerfile** = a recipe. Lines like `FROM node:18`, `COPY . /app`, `CMD ["node", "server.js"]`. Build it once, run anywhere.

**docker-compose** = a multi-container recipe. Run your app, your database, your cache, all with one command.

**Registry** = a place to store images. Docker Hub is the public one. AWS ECR, GCP Artifact Registry are private ones.

**Volume** = persistent storage outside the container. If you delete the container, the data survives.

## Real-life analogy

**Image = a class in OOP.** `class MyApp` is a blueprint. You don't "run" a class. You instantiate it.

**Container = an instance.** `myapp = new MyApp()`. You can have `myapp1`, `myapp2`, `myapp3` running at the same time. They share the same code (the image) but have different state (in-memory data, file system, network).

**Dockerfile = a recipe for the class.** What does it extend? What does it import? What constructor does it have?

**docker-compose = a system diagram.** "These classes talk to each other: myapp depends on postgres and redis. Run them all together with the right network and volumes."

## Tiny numeric example

A `Dockerfile` for our Express app:
```dockerfile
FROM node:18-alpine                    # Start from Node 18, alpine Linux (small)
WORKDIR /app                           # Set working directory
COPY package*.json ./                  # Copy package files first (for layer caching)
RUN npm ci --production                 # Install dependencies
COPY . .                               # Copy the rest of the code
EXPOSE 3000                            # Document that this app listens on 3000
USER node                              # Run as non-root user (security)
CMD ["node", "server.js"]              # The default command when the container starts
```

Build: `docker build -t myapp:1.0 .` — produces image `myapp:1.0`.
Run: `docker run -p 3000:3000 myapp:1.0` — port 3000 on host maps to 3000 in container.

A `docker-compose.yml` to run with SQLite:
```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["3000:3000"]
    environment:
      - NODE_ENV=production
    volumes:
      - ./data:/app/data  # persist SQLite file
```

Run: `docker-compose up`. Stops with `docker-compose down`. The SQLite file in `./data/` survives restarts.

## Common confusion (5+ bullet points)

1. **"Docker is a VM."** NO. A VM has its own kernel, BIOS, drivers. A Docker container shares the host kernel. A container is just a process tree with restricted filesystem and network. Containers start in 0.1s, VMs take 30s. Containers are smaller (100MB vs 10GB for a basic VM).

2. **"I need to use a different language for production."** No. The same `node`, the same `python`, the same code. Docker just packages it. Some people use alpine (small) vs debian (more compatible). Pick alpine if you have no native deps with glibc.

3. **"Containers are stateless."** The container is. The volume isn't. If you write a SQLite file to a volume, it persists. If you write it inside the container, it dies when the container dies. Always use volumes for state.

4. **"I can use any base image."** Yes, but be careful. `node:18` is 1GB. `node:18-alpine` is 180MB. `node:18-slim` is 250MB. Smaller is better for production but more chances of missing system libs.

5. **"Docker is enough for production."** Almost. You also need: orchestration (Kubernetes, ECS, Nomad), a registry (Docker Hub, ECR), persistent storage, secrets management, monitoring. Docker is the packaging layer. The rest is your platform.

6. **"My image is 2GB. Why is it slow to build?"** Probably no `.dockerignore` and you're COPYing node_modules, .git, .env. Add `.dockerignore` and use multi-stage builds to shrink the final image.

## Key properties

| Property | Container | VM |
|---|---|---|
| Boot time | 0.1s | 30s |
| Size | 100MB | 10GB |
| Kernel | Shared with host | Own kernel |
| Isolation | Process + filesystem | Full |
| Use | Microservices, dev env | Different OS, strong isolation |

## Multi-stage build example (real-world pattern)

```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage (only the build output)
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

Result: 1GB build image becomes 200MB final image. Only production deps in the final image.

## Connection to our projects

For our 73 apps, you can add a `Dockerfile` to each in 5 minutes. Same pattern. Run with `docker-compose up`. Ship to a registry. Deploy to any cloud.

For CortexCode and logogen, the same: package the FastAPI server in a Docker image, ship it to HuggingFace Spaces, AWS, GCP, or just run on your laptop.
