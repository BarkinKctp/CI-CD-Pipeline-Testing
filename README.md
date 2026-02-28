# CI-CD-Pipeline-Testing

Simple test repository for practicing and validating CI/CD workflows.

## Table of Contents
- [What this repo is for](#what-this-repo-is-for)
- [Local quick run](#local-quick-run)
- [Azure getting started (quick)](#azure-getting-started-quick)
- [ARM template deployment (same environment + managed identity)](#arm-template-deployment-same-environment--managed-identity)
- [GitHub Actions deployment flow](#github-actions-deployment-flow)
- [Troubleshooting](#troubleshooting)
- [VS Code manual deploy](#vs-code-manual-deploy)

## What this repo is for
- Running GitHub Actions checks
- Verifying basic Python/Flask test flow
- Trying pipeline changes safely

## Local quick run
- Create venv: `python -m venv .venv`
- Activate venv: `\.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

## Azure getting started (quick)
Prerequisites:
- Install Azure CLI (`az`) locally.

Quick commands:
```bash
# Login
az login

# List subscriptions
az account list --output table

# Set the subscription you want to deploy to
az account set --subscription <your-subscription-id>
```

## ARM template deployment (same environment + managed identity)
Use `arm/webapp-managed-identity.template.json` to recreate the baseline Azure setup.

PowerShell (Windows):
- `$env:WEBAPP_NAME="my-webapp-name"`
- `$env:LOCATION="canadacentral"`
- `$env:GITHUB_ORGANIZATION_NAME="your-github-user-or-org"`
- `./arm/deploy-webapp-from-env.ps1`

Bash:
- `export WEBAPP_NAME=my-webapp-name`
- `export LOCATION=canadacentral`
- `export GITHUB_ORGANIZATION_NAME=your-github-user-or-org`
- `bash arm/deploy-webapp-from-env.sh`

PowerShell/Bash prompt cache behavior:
- Script reuses values in the current shell session by default.
- Force prompt without persisting new values: `./arm/deploy-webapp-from-env.ps1 -NoCache`
- Clear cached prompt values first: `./arm/deploy-webapp-from-env.ps1 -ClearCache`

- Force prompt and ignore shell-cached values: `bash arm/deploy-webapp-from-env.sh --no-cache`
- Clear cached prompt values first: `bash arm/deploy-webapp-from-env.sh --clear-cache`

Optional env vars:
- `RESOURCE_GROUP` (default: `rg-<WEBAPP_NAME>`)
- `APP_SERVICE_PLAN_NAME` (default: `<WEBAPP_NAME>-plan`)
- `MANAGED_IDENTITY_NAME` (default: `<WEBAPP_NAME>-oidc-mi`)

Prompt fallback behavior:
- Scripts prompt for `WEBAPP_NAME`, `LOCATION`, and `GITHUB_ORGANIZATION_NAME`.
- If you press Enter on prompts, scripts use defaults from `arm/webapp-managed-identity.parameters.json` (`webAppName`, `location`, `githubOrganizationName`).

**Warnings:**
- `WEBAPP_NAME` must be **globally unique** in Azure App Service.
- **Not all Azure Locations may support all resource types or SKUs used in the template.**(**Canada Central** is **recommended** for testing).
- Federated credential creation **can fail if organization/repository/branch values do not match your GitHub Actions OIDC subject.**
- Run `az account set --subscription <your-subscription-id>` before deployment; if the active subscription is wrong, managed identity role assignment can **fail or target the wrong scope.**



Deploy directly with parameters JSON (no prompt):
```bash
az deployment group create \
	--resource-group <your-rg> \
	--template-file arm/webapp-managed-identity.template.json \
	--parameters @arm/webapp-managed-identity.parameters.json
```

Creates:
- Linux App Service Plan (B1)
- Linux Python Web App (Python 3.14)
- System-assigned managed identity
- Startup command: empty by default during ARM provisioning (set later by deployment workflow or manual config)
- Tags including `repo=CI-CD-Pipeline-Testing`

## GitHub Actions deployment flow without ARM
Important:
- This workflow deploys to an existing Azure Web App; it does not create one.

Create Web App first:
- Option A (recommended): Azure Portal -> Web App -> enable automatic CI/CD during creation.
- Option B: VS Code Azure App Service extension -> Create New Web App.

If Web App already exists:
- Configure Deployment Center.
- Use Managed Identity or OIDC service principal for GitHub login. 
- Create a federated identity credential for Github Actions
- Ensure RBAC access on target subscription/resource group.

Create GitHub secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

Notes:
- `AZURE_CLIENT_ID` should match the identity/app registration used by your pipeline.
- `AZURE_TENANT_ID` must match that identity tenant.
- `AZURE_SUBSCRIPTION_ID` must be the target subscription.

Web App name resolution order in workflow:
1. Tag lookup: `repo=CI-CD-Pipeline-Testing`
2. `workflow_dispatch` input: `webapp_name`
3. Repository variable: `WEBAPP_NAME`

Trigger deployment:
- Automatic: push/PR to `main`
- Manual: run workflow from Actions and optionally pass `webapp_name`

## Troubleshooting
- No web app name resolved:
	- Add tag `repo=CI-CD-Pipeline-Testing`, or
	- Provide `webapp_name` in manual run, or
	- Set repo variable `WEBAPP_NAME`
- Azure login/OIDC failures:
	- Verify client/tenant/subscription IDs
	- Verify federated credential subject matches repo/branch/event
	- Verify RBAC assignment exists for identity

## VS Code manual deploy
- Install Azure App Service extension
- Sign in and locate your Web App
- Right-click -> **Deploy to Web App...**
- Choose this repository folder
- Set startup command in Web App config if needed:
	- `gunicorn --bind=0.0.0.0 --timeout 600 --chdir app main:app`

