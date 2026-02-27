# CI-CD-Pipeline-Testing

Simple test repository for practicing and validating CI/CD workflows.

## What this repo is for
- Running GitHub Actions checks
- Verifying basic Python/Flask test flow
- Trying pipeline changes safely

## Local quick run
- Create venv: `python -m venv .venv`
- Activate venv: `.\.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

## Notes

- Deployment is handled via GitHub Actions
- Requires an Azure Web App (Basic tier or higher) for testing deployments

## Azure Web App deployment (GitHub Actions)

### 1) Create required GitHub secrets
In your GitHub repository, go to **Settings -> Secrets and variables -> Actions -> Secrets** and add:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

These are used by `azure/login@v2` with OIDC.

### 2) Configure how the workflow finds the Web App name
The deploy workflow resolves the app name in this order:
1. Azure Web App with tag `repo=CI-CD-Pipeline-Testing`
2. Manual `workflow_dispatch` input: `webapp_name`
3. Repository variable: `WEBAPP_NAME`

Recommended: set repository variable `WEBAPP_NAME` in **Settings -> Secrets and variables -> Actions -> Variables**.

### 3) (Optional) Tag the target Azure Web App
If you want automatic tag-based discovery, add this tag to your Web App:
- Key: `repo`
- Value: `CI-CD-Pipeline-Testing`

### 4) Trigger deployment
- Automatic deploy: push to `main` (or open/update PR to `main` for workflow checks).
- Manual deploy: run the workflow from **Actions -> Build and deploy Python app to Azure Web App - brk-flask-app-wapp** and optionally provide `webapp_name`.

### 5) Troubleshooting
- If deploy fails with "No web app name resolved":
	- Add the Azure tag `repo=CI-CD-Pipeline-Testing`, or
	- Provide `webapp_name` in manual run, or
	- Set repository variable `WEBAPP_NAME`.


