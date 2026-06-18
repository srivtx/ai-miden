# The Build

> *"Every commit should be tested. Every merge to main should be deployed. Automate it."*

We are going to add CI/CD. The change from project 37: add `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`.

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
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build
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
          cache: 'npm'

      - run: npm ci
      - run: npm test

      - name: Log in to container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY }}
          username: ${{ secrets.REGISTRY_USER }}
          password: ${{ secrets.REGISTRY_PASS }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.REGISTRY }}/myapp:${{ github.sha }}
            ${{ secrets.REGISTRY }}/myapp:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            docker pull ${{ secrets.REGISTRY }}/myapp:${{ github.sha }}
            docker compose up -d
```

## Run It

```bash
# Push the workflows
git add .github/workflows/
git commit -m "Add CI/CD"
git push

# GitHub Actions runs the CI workflow on push
# View at: https://github.com/your-org/your-repo/actions
```

The pain of "I forgot to run the tests" is solved. Every push runs the tests. Every merge to main deploys.

---

## Experiments

### Experiment 1: Add a status badge to README

```markdown
![CI](https://github.com/your-org/your-repo/actions/workflows/ci.yml/badge.svg)
```

Shows the status of the latest CI run in the README.

### Experiment 2: Run on multiple Node versions

```yaml
strategy:
  matrix:
    node: ['18', '20', '22']
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node }}
```

Test on multiple Node versions in parallel.

### Experiment 3: Deploy to multiple environments

```yaml
jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/main'
    environment: staging
    # ...
  deploy-prod:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    environment: production
    # ...
```

Deploy to staging first, then production. The production deploy requires staging to succeed.

### Experiment 4: Use a deployment service

Instead of SSH, use a deployment service:

- AWS ECS: deploy to ECS
- Google Cloud Run: deploy to Cloud Run
- Heroku: deploy to Heroku
- Vercel: deploy to Vercel

Each has its own GitHub Action.

### Experiment 5: Add a changelog

After deploy, generate a changelog from the git log:

```yaml
- name: Generate changelog
  run: |
    git log --oneline ${{ github.event.before }}..${{ github.sha }} > CHANGELOG.md
- name: Commit changelog
  run: |
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git add CHANGELOG.md
    git commit -m "Update changelog"
    git push
```

---

## Summary

You now have CI/CD. Every commit is tested. Every merge to main is deployed. The pipeline is in `.github/workflows/`.

This is the foundation of *automation*. From here, every project that needs CI/CD can use GitHub Actions. The patterns (workflows, secrets, jobs) are universal.

In project 39, we will add **observability**. We will add metrics, dashboards, and alerts. We can see what's happening in production.

Move to [CONNECT.md](./CONNECT.md) to see what pain this project leaves.
