# CI/CD Demo — GitHub Actions workflow

This is a working `.github/workflows/ci-cd.yml` you can copy into any project. Three jobs: test, build-image, deploy.

## Jobs
1. **test**: runs on Node 18, 20, 22. Install, lint, test, build. Fails the PR if any step fails.
2. **build-image**: runs only on push to main, after tests pass. Builds a Docker image, pushes to a registry.
3. **deploy**: runs only on push to main, after image builds. Deploys to production. (Replace the comment with your actual deploy command.)

## What this teaches
1. **Matrix testing**: same tests on multiple Node versions. Catches version-specific bugs.
2. **Job dependencies**: `needs: test` means build only runs if test passes. `needs: build-image` means deploy only runs after image is built.
3. **Conditional execution**: `if: github.ref == 'refs/heads/main'` so PRs from forks don't push images.
4. **Environments**: `environment: production` gates the deploy with required reviewers (configure in GitHub repo settings).
5. **Secrets**: `secrets.REGISTRY_USER` and `secrets.REGISTRY_TOKEN` are stored in repo settings, never in the workflow.
6. **Caching**: `cache: 'npm'` and `cache-from: type=gha` speed up builds.

## How to use
1. Copy this file to `.github/workflows/ci-cd.yml` in your project
2. Configure secrets in repo settings (REGISTRY_USER, REGISTRY_TOKEN)
3. Push to main. Watch the Actions tab.
4. Replace the deploy step with your actual deploy command.
