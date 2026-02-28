# CI-CD-Pipeline-Testing

Simple test repository for practicing and validating CI/CD workflows.

## Table of Contents
- [Local quick run](#local-quick-run)
- [Azure getting started (quick)](#azure-getting-started-quick)
- [ARM template deployment (automated)](#arm-template-deployment-automated)
- [GitHub Actions deployment flow](#github-actions-deployment-flow)
- [VS Code manual deploy](#vs-code-manual-deploy)
- [GitHub secrets (required)](#github-secrets-required)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)


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

## ARM template deployment (automated)

PowerShell (Windows):
```powershell
$env:WEBAPP_NAME="your-webapp-name"
$env:LOCATION="canadacentral"
$env:GITHUB_ORGANIZATION_NAME="your-github-user-or-org"
$env:RESOURCE_GROUP="your-rg-name"
./arm/deploy-webapp-from-env.ps1
```

Bash:
```bash
export WEBAPP_NAME=your-webapp-name
export LOCATION=canadacentral
export GITHUB_ORGANIZATION_NAME=your-github-user-or-org
export RESOURCE_GROUP=your-rg-name
bash arm/deploy-webapp-from-env.sh
```

>Use ARM templates to recreate the baseline Azure setup.


PowerShell/Bash prompt cache behavior:
- Script reuses values in the current shell session by default.

- Force prompt without persisting new values: `./arm/deploy-webapp-from-env.ps1 -NoCache`
- Clear cached prompt values first: `./arm/deploy-webapp-from-env.ps1 -ClearCache`

- Force prompt and ignore shell-cached values: `bash arm/deploy-webapp-from-env.sh --no-cache`
- Clear cached prompt values first: `bash arm/deploy-webapp-from-env.sh --clear-cache`


**Warnings:**
- `WEBAPP_NAME` must be **globally unique** in Azure App Service.
- **Not all Azure Locations may support all resource types or SKUs used in the template.**(**Canada Central** is **recommended** for testing).
- Federated credential creation **can fail if organization/repository/branch values do not match your GitHub Actions OIDC subject.**
- Run `az account set --subscription <your-subscription-id>` before deployment; if the active subscription is wrong, managed identity role assignment can **fail or target the wrong scope.**

---

**Deploy directly with parameters JSON (no prompt):**
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
1. Tag lookup: `repo=CI-CD-Pipeline-Testing`
2. `workflow_dispatch` input: `webapp_name`
3. Repository variable: `WEBAPP_NAME`

**Trigger deployment:**
- Automatic: push/PR to `main`
- Manual: run workflow from Actions and optionally pass `webapp_name` and `resource_group`

## GitHub secrets (required)
Create GitHub secrets:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

>Important
- `AZURE_CLIENT_ID` should match the identity/app registration used by your pipeline.
- `AZURE_TENANT_ID` must match that identity tenant.
- `AZURE_SUBSCRIPTION_ID` must be the target subscription.

## Troubleshooting
- No web app name resolved:
	- Add tag `repo=CI-CD-Pipeline-Testing`, or
	- Provide `webapp_name` in manual run, or
	- Set repo variable `WEBAPP_NAME`

- Azure login/OIDC failures:
	- Verify client/tenant/subscription IDs
	- Verify federated credential subject matches repo/branch/event
	- Verify RBAC assignment exists for identity
	- If you see `AuthorizationFailed` on `Microsoft.Web/sites/read`, grant at least `Reader` on the target Web App or Resource Group to the deployment identity

## VS Code manual deploy
- Install Azure App Service extension
- Sign in and locate your Web App
- Right-click -> **Deploy to Web App...**
- Choose this repository folder
- Set startup command in Web App config if needed:
	- `gunicorn --bind=0.0.0.0 --timeout 600 --chdir app main:app`

## Notes
- Prefer running deployments manually (`workflow_dispatch`) when validating new Azure settings.
- You need to run `az account set --subscription <your-subscription-id>` only once per shell/session (run it again only if you switch account/subscription/session).
- ARM scripts and GitHub Actions use the currently selected subscription context; always verify with `az account show`.
- App Service names are globally unique in Azure, so choose distinct names for test environments.
- Keep naming consistent across Web App, Resource Group, and secrets to simplify troubleshooting.