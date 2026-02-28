# CI-CD-Pipeline-Testing

Simple test repository for practicing and validating CI/CD workflows.

## Table of Contents
- [Local quick run](#local-quick-run)
- [Azure getting started](#azure-getting-started)
- [GitHub secrets (required)](#github-secrets-required)
- [ARM template deployment (automated)](#arm-template-deployment-automated)
- [GitHub Actions deployment flow](#github-actions-deployment-flow)
- [VS Code manual deploy](#vs-code-manual-deploy)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)


## Local quick run
- Create venv: `python -m venv .venv`
- Activate venv: `\.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

## Azure getting started
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
## GitHub secrets (required)
Create GitHub secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

**Important:**
- `AZURE_CLIENT_ID` should be the **client ID of the created user-assigned managed identity** used by GitHub OIDC (from ARM output `userAssignedManagedIdentityClientId` or Azure Portal).
- `AZURE_TENANT_ID` must match that identity tenant.
- `AZURE_SUBSCRIPTION_ID` must be the target subscription.

## ARM template deployment (automated)

### General info
- The scripts prompt for `WEBAPP_NAME`, `LOCATION`, `GITHUB_ORGANIZATION_NAME`, and `RESOURCE_GROUP`.
- If you don’t specify prompt values, defaults are used from `azure/azuredeploy.parameters.json` (and `RESOURCE_GROUP` defaults from your script flow).
- Deployment creates/uses a Resource Group and provisions App Service + identity resources from `azure/azuredeploy.json`.
- Keep the active Azure subscription correct before running (`az account set --subscription <your-subscription-id>`).
- You can change default parameter values used by the scripts (for example `webAppName`, `location`, `githubOrganizationName`, SKU values, and tags) in `azure/azuredeploy.parameters.json`.

### Setup steps
Follow these steps on your local machine:

```bash
# Login to Azure and set subscription
az login
az account set --subscription <your-subscription-id>
```

```powershell
# PowerShell (Windows)
$env:WEBAPP_NAME="your-webapp-name"
$env:LOCATION="canadacentral"
$env:GITHUB_ORGANIZATION_NAME="your-github-user-or-org"
$env:RESOURCE_GROUP="your-rg-name"
./azure/deploy-wepapp-powershell.ps1
```

```bash
# Bash
export WEBAPP_NAME=your-webapp-name
export LOCATION=canadacentral
export GITHUB_ORGANIZATION_NAME=your-github-user-or-org
export RESOURCE_GROUP=your-rg-name
bash azure/deploy-webapp-bash.sh
```

```bash
# Optional: deploy directly with parameters file
az deployment group create \
	--resource-group <your-rg> \
	--template-file azure/azuredeploy.json \
	--parameters @azure/azuredeploy.parameters.json
```

### Prompt cache behavior
- Script reuses values in the current shell session by default.

- Force prompt without persisting new values: `./azure/deploy-wepapp-powershell.ps1 -NoCache`
- Clear cached prompt values first: `./azure/deploy-wepapp-powershell.ps1 -ClearCache`

- Force prompt and ignore shell-cached values: `bash azure/deploy-webapp-bash.sh --no-cache`
- Clear cached prompt values first: `bash azure/deploy-webapp-bash.sh --clear-cache`

### Resources created
- Linux App Service Plan (B1)
- Linux Python Web App (Python 3.14)
- System-assigned managed identity
- Startup command: empty by default during ARM provisioning (set later by deployment workflow or manual config)
- Tags including `repo=CI-CD-Pipeline-Testing`

**Warnings:**
- `WEBAPP_NAME` must be **globally unique** in Azure App Service.
- **Not all Azure Locations may support all resource types or SKUs used in the template.**(**Canada Central** is **recommended** for testing).
- Federated credential creation **can fail if organization/repository/branch values do not match your GitHub Actions OIDC subject.**
- Run `az account set --subscription <your-subscription-id>` before deployment; if the active subscription is wrong, managed identity role assignment can **fail or target the wrong scope.**

## GitHub Actions deployment flow without ARM
> This workflow deploys to an existing Azure Web App; it does not create one.

Create Web App first:
- Option A (recommended): Azure Portal -> Web App -> enable automatic CI/CD during creation.
- Option B: VS Code Azure App Service extension -> Create New Web App.

If Web App already exists:
- Configure Deployment Center.
- Use Managed Identity or OIDC service principal for GitHub login. 
- Create a federated identity credential for Github Actions
- Ensure RBAC access on target subscription/resource group.

---

**Web App name resolution order in workflow:**
1. `workflow_dispatch` input: `webapp_name`
2. Repository variable: `WEBAPP_NAME`
3. Tag lookup: `repo=CI-CD-Pipeline-Testing`

**Trigger deployment:**
- Automatic: push/PR to `main`
- Manual: run workflow from Actions (optionally pass `webapp_name` and `resource_group`)

## Troubleshooting
- No web app name resolved:
	- Provide `webapp_name` in manual run, or
	- Set repo variable `WEBAPP_NAME`, or
	- Add tag `repo=CI-CD-Pipeline-Testing`

- Azure login/OIDC failures:
	- Verify client/tenant/subscription IDs
	- Verify federated credential subject matches repo/branch/event
	- Verify RBAC assignment exists for identity
	- If you see `AuthorizationFailed` on `Microsoft.Web/sites/read`, grant at least `Reader` on the target Web App or Resource Group to the deployment identity
	- If you see `No matching federated identity record found`, your federated credential subject does not match the branch/ref used by the workflow run (for example `main` vs `pgbench/*`)

## VS Code manual deploy
- Install Azure App Service extension
- Sign in and locate your Web App
- Right-click -> **Deploy to Web App...**
- Choose this repository folder
- Set startup command in Web App config if needed:
	- `gunicorn --bind=0.0.0.0 --timeout 600 app.main:app`

## Notes
- Prefer running deployments manually (`workflow_dispatch`) when validating new Azure settings.
- You need to run `az account set --subscription <your-subscription-id>` only once per shell/session (run it again only if you switch account/subscription/session).
- ARM scripts and GitHub Actions use the currently selected subscription context; always verify with `az account show`.
- App Service names are globally unique in Azure, so choose distinct names for test environments.
- Keep naming consistent across Web App, Resource Group, and secrets to simplify troubleshooting.