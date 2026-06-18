# Project 38: The Pipeline

> *"Every commit should be tested. Every merge to main should be deployed. Automate it."*

In projects 36-37, we have tests and Docker. But we still run them manually. We want **CI/CD** (Continuous Integration / Continuous Deployment):

- **CI**: on every push, run the tests automatically. If they fail, the PR can't merge.
- **CD**: on every merge to main, build the Docker image, push it, deploy to production.

We use **GitHub Actions** — the standard for GitHub repos. We add a `.github/workflows/ci.yml` that runs the tests on every push. We add `.github/workflows/deploy.yml` that builds and pushes the image on every merge to main.

By the end, every change is tested automatically. Every merge to main is deployed automatically. We catch bugs before they reach production. We deploy with confidence.

---

## Table of Contents

1. [The Problem](./PROBLEM.md) — Why is manual testing not enough? What is CI/CD?
2. [The Thought](./THOUGHT.md) — How do GitHub Actions work? What is a workflow?
3. [The Build](./BUILD.md) — Line-by-line construction of the CI/CD pipeline
4. [The Decisions](./DECISIONS.md) — Why GitHub Actions? Why on every push?
5. [The Connect](./CONNECT.md) — What pain does this project leave us with?

---

## The One-Paragraph Summary

CI/CD automates testing and deployment. We use GitHub Actions. On every push, we run the tests. If they fail, the PR can't merge. On every merge to main, we build the Docker image, push it, and deploy. The pipeline is in `.github/workflows/`.

---

## The Code

### `.github/workflows/ci.yml`

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

### `.github/workflows/deploy.yml`

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
      - uses: actions/setup-buildx-action@v3
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

The pain of "I forgot to run the tests" is solved. Every push runs the tests. Every merge to main deploys.

---

## What You Will Have Learned

- What CI/CD is (Continuous Integration / Continuous Deployment)
- How to use GitHub Actions
- How to write a workflow file (`.github/workflows/`)
- How to run tests on every push
- How to build and push Docker images
- How to deploy to a server via SSH

These are the foundations of *automation*. From here, every project that needs CI/CD can use GitHub Actions.
