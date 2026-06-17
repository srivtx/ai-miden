## Why it exists (THE PROBLEM)

You push code to main. Nothing happens. The CI server doesn't know. You SSH into the production server, run `git pull`, then `npm install`, then `pm2 restart`. Every. Single. Time. At 2 AM because the prod server is on fire. You make a typo. The deploy breaks. Customers are angry. You roll back by hand. You hate your life.

**CI/CD fixes this.** Push to main. Tests run automatically. If they pass, image is built, pushed to registry, deployed to production. Takes 3 minutes. No human in the loop. No 2 AM deploys. No typos. Same deploy every time.

**CI (Continuous Integration)** = on every commit, automatically: install deps, run tests, run linters, build the image. If any fails, the PR is blocked. You catch bugs in minutes, not weeks.

**CD (Continuous Delivery/Deployment)** = when CI passes, automatically deploy to staging (Delivery) or production (Deployment). With Delivery, a human clicks "deploy." With Deployment, it just happens.

## Definition (very simple)

**CI pipeline** = a config file (YAML) that says: "on every push/PR, run these steps." Lives in `.github/workflows/ci.yml` for GitHub Actions, `.gitlab-ci.yml` for GitLab, `Jenkinsfile` for Jenkins.

**Build matrix** = run the same job on multiple OS or Node versions. "Test on Node 18, 20, 22 on Ubuntu, Mac, Windows." Catches version-specific bugs.

**Artifact** = output of a CI job. The built image, the test report, the coverage report. Stored in a registry or as a build artifact.

**Environment** = a deployment target. Dev, staging, production. Different configs, different secrets, different approval levels.

**Rollback** = revert to the previous version. Your CI should make this one command. "Deploy the previous image."

## Real-life analogy

**CI/CD = the assembly line.** Each step is automated. If a step fails, the line stops. If everything works, the product rolls off the end, fully tested, ready to ship. No human needed except to maintain the line.

**Without CI/CD = bespoke manufacturing.** A craftsman makes each car by hand. Quality varies. Some are great, some have loose bolts. Each takes a week.

## Tiny numeric example

GitHub Actions workflow for our Express app:
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix: { node: [18, 20, 22] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node }} }
      - run: npm ci
      - run: npm test
      - run: npm run lint
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:${{ github.sha }} .
      - run: docker push myapp:${{ github.sha }}
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - run: kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
```

Three jobs: test (every push), build (on main), deploy (on main, after build). Each step is a line. Total: 30 lines. Replaces 30 minutes of manual deploys.

## Common confusion (5+ bullet points)

1. **"CI takes too long."** Optimize: cache `node_modules` between runs, run tests in parallel, only run changed tests. A Node project should be <2 min for full test. If longer, you're doing too much in CI (use separate jobs).

2. **"Tests are not needed, my code is simple."** Without tests, CI is just "build and deploy." When you break prod, you find out at 2 AM. With tests, you find out in 2 minutes. Even 5 minutes of writing a test saves hours of debugging.

3. **"Auto-deploy to prod is dangerous."** It is, if you don't have tests, monitoring, and rollback. With them, it's safer than manual deploys (no typos, no "I forgot to run migrations").

4. **"I don't need CD, my deploy is one command."** That command will fail at 3 AM when you're asleep. The command will fail in 6 months when someone who doesn't know the magic command has to deploy. Codify it.

5. **"My secrets are in the CI file."** No. Use your CI's secret store. GitHub: Settings → Secrets. GitLab: Settings → CI/CD → Variables. Never commit secrets. Never echo them in logs. Use `::add-mask::` in GitHub Actions to redact.

6. **"CI is only for tests."** CI is for: tests, linters, type check, security scan, build, deploy, database migrations, performance benchmarks, code coverage, dependency updates. Anything you do manually should be in CI.

## Key properties

| Property | CI | CD |
|---|---|---|
| Trigger | Every commit | After CI passes |
| Action | Build, test | Deploy |
| Failure | Block PR | Block deploy (or roll back) |
| Owner | Everyone | Whoever has merge access |

## Blue-green deployment pattern

```
[Load Balancer]
    /         \
[Blue v1]  [Green v2]
```

Deploy v2 to Green. Test it. If good, flip the load balancer. Zero downtime. If bad, switch back. The previous version (Blue) is still running.

## Database migrations in CI/CD

```yaml
deploy:
  steps:
    - run: npm run migrate          # run migrations
    - run: kubectl set image ...    # then deploy
```

Migrations BEFORE the new code deploys. Otherwise, the new code expects the new schema, but the old schema is still in prod. Crash. Always migrate forward, then deploy.

## Connection to our projects

For our 73 apps, you can add a `ci.yml` in 5 minutes:
```yaml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npm test
```

The projects in apps/level2 (microservices, audit-log) need the full pipeline: test → build → push image → deploy. Add `Dockerfile` + `ci.yml` + `docker-compose.yml`. Push to GitHub. Connect to a cloud (Render, Railway, Fly.io). Done.

For CortexCode, the same: CI runs tests, builds the FastAPI image, pushes to HuggingFace Spaces or AWS. Deploy = restart the running service with the new image.
