# The Decisions

> *"It works on my machine." — every developer, ever.*

## Decision 1: Docker and not VMs

**Alternative**: Virtual machines (VirtualBox, VMware).

**Why Docker: Lighter. Faster to start. Less memory. The industry standard for containerization.

**Trade-off**: Containers share the host kernel. For full isolation, use VMs. For most apps, containers are enough.

## Decision 2: Alpine and not Ubuntu

**Alternative**: Ubuntu base image.

**Why Alpine: Minimal. ~5MB. Faster pulls. Smaller attack surface.

**Trade-off**: Some packages don't have Alpine builds. musl libc (Alpine) instead of glibc (Ubuntu) can cause issues with some Node modules. We use Alpine.

## Decision 3: Multi-stage and not single-stage

**Alternative**: Single-stage Dockerfile.

**Why multi-stage: Smaller final image. Dev dependencies (test runners, linters) are excluded.

**Trade-off**: Slightly more complex Dockerfile. We accept this.

## Decision 4: Node 20 and not LTS

**Alternative**: Node 18 (older LTS).

**Why Node 20: Current LTS. Newer features. Better performance.

**Trade-off**: Some older packages don't support Node 20. We accept this.

## Decision 5: docker compose and not Kubernetes

**Alternative**: Kubernetes (k8s).

**Why docker compose: Simpler. For local dev and small deployments. No extra infrastructure.

**Trade-off**: For hundreds of containers, use Kubernetes. For our scale, compose is enough.

## Decision 6: Volume for SQLite file

**Alternative**: Use a managed database (Postgres, etc.) in a separate container.

**Why volume: For dev, SQLite is fine. A volume persists the file outside the container. Restart the container, the data is still there.

**Trade-off**: For production, use Postgres. SQLite doesn't scale to multiple writers.

## Decision 7: Non-root user

We run as the `node` user, not `root`. This is a security best practice.

**Alternative**: Run as `root`.

**Why not root: If the container is compromised, the attacker has root inside the container. With a non-root user, the attacker is limited.

**Trade-off**: Some operations require root (e.g., binding to port 80). For port 3000+, non-root is fine.

## Decision 8: Restart policy `unless-stopped`

We use `restart: unless-stopped`. The container restarts automatically if it crashes.

**Alternative**: `always`, `on-failure`, `no`.

**Why `unless-stopped`: Restarts on crash but not when manually stopped. Good for production.

**Trade-off**: Different policies for different use cases. We use `unless-stopped`.

## Decision 9: Environment variables for config

We pass config via environment variables in `docker-compose.yml`.

**Alternative**: Bake into the image, use a config file, use a secrets manager.

**Why env vars: Standard. Easy to change. Works in dev and prod.

**Trade-off**: Secrets in env vars are visible in `docker inspect`. For production, use a secrets manager.

## Decision 10: No Kubernetes manifests

**Alternative**: Kubernetes manifests (yaml files for k8s).

**Why no: Out of scope. K8s is a different deployment model. We use Docker Compose.

**Trade-off**: For production at scale, you'd use K8s.

---

## What We Did Not Decide

- **Kubernetes** — out of scope
- **Helm charts** — out of scope
- **Multi-region deployment** — out of scope
- **Blue/green deployment** — out of scope
- **Canary deployment** — out of scope
- **Auto-scaling** — out of scope
- **Service mesh (Istio, Linkerd)** — out of scope
- **Secrets management (Vault, AWS Secrets Manager)** — out of scope
- **Image scanning (Trivy, Snyk)** — out of scope
- **Distroless images** — out of scope

Each is a future decision.

---

## The Meta-Decision: The App Is Reproducible

For 36 projects, the app ran on our development machine. Deploy was a manual process. Different machines had different environments.

Now the app is reproducible. Docker packages the app and all its dependencies into a container. The container runs the same on any machine. Deploy is `docker compose up`.

This is the foundation of *containerization*. From here, every project that needs reproducible deployments can use Docker. The patterns (Dockerfile, docker-compose, multi-stage builds) are universal.

The next 3 projects will assume Docker exists. The path diverges:

- **Pipeline** (project 38): CI/CD
- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The app is reproducible. The path continues.
