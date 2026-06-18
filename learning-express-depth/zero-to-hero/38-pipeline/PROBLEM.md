# The Problem

> *"I forgot to run the tests." — every developer, ever.*

## Why Manual Testing Is Not Enough

In project 36, we have tests. In project 37, we have Docker. But we still run them manually:

1. Pull the latest code
2. Install dependencies
3. Run the tests
4. If they pass, build the Docker image
5. Push the image
6. Deploy to the server

This is manual. It's slow. It's error-prone. We forget steps. We deploy without running tests. Bugs reach production.

## What Pain Is This Solving?

**CI/CD** automates this:

- **CI (Continuous Integration)**: on every push, run the tests automatically. If they fail, the PR can't merge.
- **CD (Continuous Deployment)**: on every merge to main, build the Docker image, push it, and deploy. No human intervention.

The result:

- Every change is tested
- Bugs are caught before merge
- Deploy is automatic
- Time to deploy is minutes, not hours
- We deploy with confidence

## The Deeper Problem: The Deployment Bottleneck

In a team, "deploy to production" is a ceremony:

- Wait for a code freeze
- Run the tests manually
- Build the Docker image
- Get sign-off from 3 people
- Deploy during a maintenance window
- Hope nothing breaks

This is slow, error-prone, and stressful. With CI/CD:

- Push to main
- Tests run automatically
- Image builds automatically
- Deploys automatically
- Roll back automatically if it fails

We deploy 10 times a day instead of once a week. The risk per deploy is lower (smaller changes). The total risk is the same or lower.

## What This Project Will Solve

This project will:

1. Add a GitHub Actions workflow for CI (run tests on every push)
2. Add a GitHub Actions workflow for CD (build and deploy on every merge to main)
3. Set up secrets for the registry and server
4. Document the deployment process

By the end, every change is tested and deployed automatically.

## What This Project Will *Not* Solve

- **Multi-environment deployment** (dev, staging, prod) — we deploy to one environment.
- **Canary deployment** — we deploy to all users at once.
- **Auto-rollback** — out of scope.
- **Approval workflows** — we deploy on every merge, no approval.
- **Multi-region** — we deploy to one region.

## The Question This Project Answers

> *"How do I run tests and deploy automatically?"*

If you can answer: "use GitHub Actions, run tests on every push, build and deploy on every merge to main," you are ready for project 39.
