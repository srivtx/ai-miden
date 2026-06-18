# The Thought

> *"Every commit should be tested. Every merge to main should be deployed. Automate it."*

## What CI/CD Is

**CI (Continuous Integration)**: on every code change, automatically run the tests. If the tests fail, the change can't be merged.

**CD (Continuous Deployment)**: on every merge to main, automatically build the artifact (Docker image) and deploy it to production.

The two together: every change is tested and deployed automatically. No human intervention.

## GitHub Actions

GitHub Actions is a CI/CD service built into GitHub. We write *workflows* (YAML files) in `.github/workflows/`. Each workflow defines a set of *jobs* (things to do) and *steps* (individual commands).

A workflow runs on:
- `push` to a branch
- `pull_request` to a branch
- A schedule (e.g., nightly)
- A manual trigger (`workflow_dispatch`)

The workflow runs on a GitHub-hosted runner (e.g., `ubuntu-latest`). The runner has Node, Python, Docker, etc. pre-installed.

## The CI Workflow

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
```

This workflow:
- Runs on push to main and on PRs to main
- Checks out the code
- Sets up Node 20
- Installs dependencies with `npm ci`
- Runs the tests with `npm test`

If the tests fail, the workflow fails, the PR can't merge.

## The CD Workflow

`.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - uses: docker/login-action@v3
        with:
          registry: registry.example.com
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASS }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: registry.example.com/myapp:${{ github.sha }}
      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull registry.example.com/myapp:${{ github.sha }}
            docker compose up -d
```

This workflow:
- Runs on push to main
- Checks out, installs, tests (same as CI)
- Logs into the container registry
- Builds and pushes the Docker image (tagged with the git SHA)
- SSHes into the server and runs `docker compose up -d`

The image is tagged with the git SHA. We can always pull a specific version.

## Secrets

We use GitHub Secrets to store sensitive data:

- `REGISTRY_USER`, `REGISTRY_PASS`: container registry credentials
- `SERVER_HOST`, `SERVER_USER`, `SSH_KEY`: SSH credentials to the server

Secrets are encrypted and only exposed to the workflow. They're not visible in logs.

To add a secret: GitHub repo → Settings → Secrets → New repository secret.

## Common Confusions (read these)

**Confusion 1: "Why on every push?"**
The earlier we catch a bug, the cheaper it is to fix. A bug caught in CI is fixed in minutes. A bug caught in production is fixed in hours (or days).

**Confusion 2: "Why on PRs too?"**
A PR might pass tests on the branch but fail on main (e.g., merge conflict). Running on PRs catches this.

**Confusion 3: "What if the tests are slow?"**
Use parallel jobs. Split tests into multiple jobs that run in parallel. Or use a matrix.

**Confusion 4: "What about caching?"**
GitHub Actions caches `node_modules` by default (with `npm ci`). This makes builds faster.

**Confusion 5: "What about secrets in logs?"**
GitHub Actions automatically masks secrets in logs. Don't print them.

**Confusion 6: "What about multi-environment?"**
You can have separate workflows for dev, staging, prod. They deploy to different environments. We have one environment.

**Confusion 7: "What about canary?"**
GitHub Actions supports canary via deployment jobs with conditions. Out of scope for this project.

**Confusion 8: "What about rollback?"**
We can roll back by deploying a previous SHA. Out of scope for this project.

## What We Are About to Build

Two workflow files (`.github/workflows/ci.yml` and `.github/workflows/deploy.yml`). The CI runs on every push. The CD runs on every merge to main.

The HTTP handlers are unchanged. The new piece is the CI/CD pipeline.

In [BUILD.md](./BUILD.md) we will go line by line.
