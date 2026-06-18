# The Decisions

> *"Every commit should be tested. Every merge to main should be deployed. Automate it."*

## Decision 1: GitHub Actions and not other CI/CD

**Alternatives**:
- **GitLab CI** — GitLab's built-in CI
- **CircleCI** — popular, hosted
- **Jenkins** — self-hosted, mature
- **Drone** — self-hosted, simple
- **Buildkite** — hybrid

**Why GitHub Actions: Built into GitHub. Free for public repos. Generous free tier for private repos. Massive marketplace of actions. The de-facto choice for GitHub repos.

**Trade-off**: Vendor lock-in to GitHub. We accept this.

## Decision 2: On every push and PR

**Alternative**: Only on merge to main.

**Why on push and PR: Catch bugs earlier. A bug caught on a PR is fixed before merge. A bug caught on push is fixed before the next push.

**Trade-off**: More CI runs = more cost. We accept this.

## Decision 3: Build the image in the deploy workflow

**Alternative**: Build the image in a separate workflow.

**Why in deploy: Simpler. One workflow for both. The image is built and pushed in one step.

**Trade-off**: Slower deploy (build time + push time). We accept this.

## Decision 4: Tag with git SHA

**Alternative**: Tag with `latest`, or a version number.

**Why SHA: Every commit has a unique SHA. We can always pull a specific version. No ambiguity.

**Trade-off**: Less human-readable. We accept this.

## Decision 5: Deploy via SSH

**Alternative**: Use a deployment service (ECS, Cloud Run, etc.).

**Why SSH: Simple. Works with any server. No extra infrastructure.

**Trade-off**: Manual SSH key management. We accept this.

## Decision 6: Secrets for sensitive data

**Alternative**: Bake secrets into the image.

**Why secrets: Security. Secrets are encrypted and only exposed to the workflow.

**Trade-off**: Must configure secrets in GitHub. We accept this.

## Decision 7: Single environment (production)

**Alternative**: Multiple environments (dev, staging, prod).

**Why single: Simpler. For learning, one environment is enough.

**Trade-off**: No staging environment to test in. We accept this.

## Decision 8: No auto-rollback

**Alternative**: Auto-rollback if the deploy fails (e.g., health check fails).

**Why no: Out of scope. We can manually roll back by deploying a previous SHA.

**Trade-off**: A failed deploy stays in production. We accept this.

## Decision 9: No canary

**Alternative**: Deploy to 1% of users first, then 100%.

**Why no: Out of scope. Canary is for high-scale apps.

**Trade-off**: A bug reaches 100% of users. We accept this.

## Decision 10: No approval workflow

**Alternative**: Require approval from a reviewer before deploy.

**Why no: Out of scope. We trust the CI tests.

**Trade-off**: A bad deploy can happen without human review. We accept this.

---

## What We Did Not Decide

- **Multi-environment** (dev, staging, prod) — out of scope
- **Auto-rollback** — out of scope
- **Canary deployment** — out of scope
- **Approval workflow** — out of scope
- **Blue/green deployment** — out of scope
- **Deployment service (ECS, Cloud Run, etc.)** — out of scope
- **Changelog generation** — out of scope
- **Release notes** — out of scope
- **Notifications (Slack, email)** — out of scope
- **Secrets management (Vault, AWS Secrets Manager)** — out of scope

Each is a future decision.

---

## The Meta-Decision: The App Is Continuously Deployed

For 37 projects, the app ran on our machine. Deploy was a manual process. Different environments had different configurations.

Now the app is continuously deployed. Every commit is tested. Every merge to main is built and deployed. The pipeline is automatic.

This is the foundation of *automation*. From here, every project that needs CI/CD can use GitHub Actions. The patterns (workflows, secrets, jobs) are universal.

The next 2 projects will assume CI/CD exists. The path diverges:

- **Observability** (project 39): metrics
- **Microservice** (project 40): split

The app is continuously deployed. The path continues.
