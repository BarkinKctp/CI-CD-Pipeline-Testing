# GitHub App Authentication Example

This document briefly explains what a GitHub App is, why it is useful for automation, and how it is used in this repository.

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

| Feature | GitHub App | PAT |
|--------|------------|-----|
| Identity | App installation | User account |
| Token lifetime | Short-lived | Usually long-lived |
| Permissions | Fine-grained app permissions | Token scopes |
| Security | Recommended for automation | Better suited for personal scripts |

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

## Example use in this repository

In this repository, the GitHub App token is used to:

- authenticate workflow steps
- access repositories using GitHub CLI and Git
- push test result files to another repository

GitHub Apps can support **secure cross-repository automation** without relying on personal tokens.

## Setup overview

To use a GitHub App in a workflow:

1. Create a **GitHub App** in *Developer Settings*  
2. Generate a **private key**  
3. Install the app on the required repositories  
4. Store the following values in GitHub Actions:
   - `GH_APPLICATION_ID` (repository variable)  
   - `GH_APP_KEY` (repository secret)  

The workflow can then generate **installation tokens dynamically**.

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
