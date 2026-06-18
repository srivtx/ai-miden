# The Problem

> *"It works on my machine." — every developer, ever.*

## Why "It Works on My Machine" Is a Problem

In projects 01-36, our server runs on our development machine. We have:

- Node 20.x
- npm 10.x
- A specific OS (macOS, Linux, Windows)
- Specific system libraries (OpenSSL version, etc.)

Deploy to a different machine (a CI server, a staging server, production) and:

- The Node version might differ
- The npm version might differ
- The OS might differ
- A system library might be missing or the wrong version

The result: the app doesn't work in production. We debug for hours. "It worked on my machine."

## What Pain Is This Solving?

**Docker** solves this. We package the app and ALL its dependencies into a **container** — a standardized unit. The container includes:

- A minimal OS (Alpine Linux, ~5MB)
- Node.js (specific version)
- npm packages
- The application code
- Configuration

The container runs the same on:

- Our laptop (macOS)
- A CI server (Linux)
- A staging server (Linux)
- Production (Linux)

No more "it works on my machine." The container is the same everywhere.

## The Deeper Problem: Isolation

A container is **isolated** from the host system. It has its own:

- File system
- Network
- Processes
- Environment variables

This means:

- Two containers can use different Node versions without conflict
- A container can't accidentally affect the host
- We can run multiple instances of the same app on the same host
- We can ship the container to any Docker host (laptop, server, cloud)

Containers are like lightweight virtual machines, but they share the host kernel. They're faster to start, use less memory, and are easier to manage than full VMs.

## What This Project Will Solve

This project will:

1. Add a `Dockerfile` (build instructions)
2. Add a `docker-compose.yml` (multi-container orchestration)
3. Build the image
4. Run the container

By the end, the app is reproducible. Anyone with Docker can run it. Deploy is a single command.

## What This Project Will *Not* Solve

- **Orchestration at scale** — for hundreds of containers, use Kubernetes. We use Docker Compose for local dev.
- **CI/CD** — we don't set up GitHub Actions. Project 38.
- **Monitoring** — we don't add metrics. Project 39.
- **Microservices** — we don't split the app. Project 40.
- **Multi-region** — we don't deploy to multiple regions. Out of scope.

## The Question This Project Answers

> *"How do I deploy my app reproducibly?"*

If you can answer: "use Docker, package the app and dependencies into a container, run with `docker compose up`," you are ready for project 38.
