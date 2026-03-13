# GitHub App Authentication Example

This document briefly explains what a GitHub App is, why it is useful for automation, and how it is used in this repository.

In this project, the GitHub App is used by GitHub Actions workflows to generate short-lived tokens for secure repo operations such as checkout, authenticated clone tests, and pushing CI results to a target repository.

## What is a GitHub App?

A GitHub App is an integration that can authenticate with GitHub using **short-lived installation tokens** instead of long-lived credentials.

In CI/CD workflows, a GitHub App can generate a token during the workflow run and use it to:

- access repositories
- call the GitHub API
- clone or push code
- automate cross-repository tasks

The token is generated dynamically and expires automatically.

## Why GitHub Apps are useful

GitHub Apps are commonly used for CI/CD automation because they provide:

- **Short-lived tokens** instead of long-lived credentials
- **Fine-grained permissions** for repositories
- **Repository-level installation control**
- **Better security and auditability**

This avoids relying on a developer's personal account or storing sensitive credentials.

## GitHub App vs Personal Access Token (PAT)

| Feature        | GitHub App                   | PAT                                |
| -------------- | ---------------------------- | ---------------------------------- |
| Identity       | App installation             | User account                       |
| Token lifetime | Short-lived                  | Usually long-lived                 |
| Permissions    | Fine-grained app permissions | Token scopes                       |
| Security       | Recommended for automation   | Better suited for personal scripts |

For CI/CD pipelines, GitHub Apps are generally the preferred approach.

## How it works in a workflow

A workflow generates an installation token using the GitHub App's ID and private key:

```yaml
- name: Create GitHub App token
  id: app
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ vars.GH_APPLICATION_ID }}
    private-key: ${{ secrets.GH_APP_KEY }}
    owner: ${{ github.repository_owner }}
```

## What the generated token can be used for

The generated token can be used for GitHub operations such as:

- checking out repositories
- accessing the GitHub API
- cloning or pushing to other repositories

## GITHUB_TOKEN vs GitHub App token

These are different tokens and are managed differently:

- `GITHUB_TOKEN` is automatically created by GitHub Actions for each workflow run.
- GitHub App token (for example `steps.app.outputs.token`) is created by `actions/create-github-app-token`.

Important behavior:

- The workflow `permissions:` block controls the auto-generated `GITHUB_TOKEN`.
- GitHub App permissions are configured in the GitHub App settings (for example Contents read/write).
- If you set `env: GITHUB_TOKEN: ${{ steps.app.outputs.token }}`, you override the default token value for that step.

Recommended pattern:

- Keep default `GITHUB_TOKEN` unchanged.
- Pass the GitHub App token with a separate name such as `GH_TOKEN` or `GITHUB_APP_TOKEN`.
- Use the App token explicitly only in steps that require app-level or cross-repository access.

This avoids token collisions and prevents breaking actions that expect the default Actions token behavior.

## Example use in this repository

In this repository, the GitHub App token is used to:

- authenticate workflow steps
- access repositories using GitHub CLI and Git
- push test result files to another repository

GitHub Apps can support **secure cross-repository automation** without relying on personal tokens.

## Dockerfiles in this repo

- `docker/local-image/Dockerfile` builds a local Python test image (installs app dependencies and copies `app/`).
  It is used by `.github/workflows/test-flask.yml` via `python -m app.build_packages`.

- `docker/dockerhub-image/Dockerfile` builds the published DockerHub test image (uses an `entrypoint.sh` clone flow inside the container).
  It is built and pushed by `.github/workflows/publish-docker-image.yml`, then pulled and tested by `.github/workflows/test-ghapp-docker.yml`.

- In both flows, the GitHub App token is passed as `GH_TOKEN` so the container can perform authenticated Git operations against `TARGET_REPO`.

## Setup overview

To use a GitHub App in a workflow:

1. Create a **GitHub App** in _Developer Settings_
2. Generate a **private key**
3. Install the app on the required repositories
4. Store the following values in GitHub Actions:
   - `GH_APPLICATION_ID` (repository variable)
   - `GH_APP_KEY` (repository secret)

The workflow can then generate **installation tokens dynamically**.

## Docker setup

After completing **Setup overview** above, add the Docker-specific configuration below.

### Required GitHub secrets and variables

- Repository secret: `DOCKERHUB_USERNAME`
- Repository secret: `DOCKERHUB_TOKEN`

### Workflow order

1. Run `.github/workflows/publish-docker-image.yml` to publish `<DOCKERHUB_USERNAME>/ghapp-test:latest`.
2. Run `.github/workflows/test-ghapp-docker.yml` to pull and validate the published DockerHub image.
3. Run `.github/workflows/test-flask.yml` for app tests plus local image build validation.

## Notes

- A GitHub App only has access to repositories where it is **installed**.  
  If your workflow needs to read or push to another repository, the app must be installed on **both the source and target repositories**.

- The permissions configured when creating the GitHub App determine what the workflow can do.  
  For example, pushing files to another repository requires **Contents: Read and write** permission.

- This permission model makes GitHub Apps safer for automation because access can be limited to only the repositories and actions required.

- If the app is not installed on a repository or lacks the required permissions, operations such as cloning, committing, or pushing will fail even if the token generation step succeeds.

- They are especially useful when automation must access multiple repositories without tying that access to an individual developer account.

## References

- https://docs.github.com/en/apps
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication
