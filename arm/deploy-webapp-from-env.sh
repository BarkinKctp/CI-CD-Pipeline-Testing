#!/usr/bin/env bash
set -euo pipefail

if ! command -v az >/dev/null 2>&1; then
  echo "Azure CLI (az) is required." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARAMETERS_FILE="$SCRIPT_DIR/webapp-managed-identity.parameters.json"
TEMPLATE_FILE="$SCRIPT_DIR/webapp-managed-identity.template.json"
NO_CACHE=false
CLEAR_CACHE=false

for arg in "$@"; do
  case "$arg" in
    --no-cache)
      NO_CACHE=true
      ;;
    --clear-cache)
      CLEAR_CACHE=true
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: bash arm/deploy-webapp-from-env.sh [--no-cache] [--clear-cache]" >&2
      exit 1
      ;;
  esac
done

PYTHON_CMD="$(command -v python3 || command -v python || true)"

get_param_default() {
  local key="$1"

  if [[ ! -f "$PARAMETERS_FILE" || -z "$PYTHON_CMD" ]]; then
    echo ""
    return
  fi

  "$PYTHON_CMD" - "$PARAMETERS_FILE" "$key" <<'PY'
import json
import sys

file_path, key = sys.argv[1], sys.argv[2]
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

value = data.get("parameters", {}).get(key, {}).get("value", "")
print("" if value is None else value)
PY
}

prompt_if_empty() {
  local var_name="$1"
  local prompt="$2"
  local default_value="$3"
  local current_value="${!var_name:-}"

  if [[ "$NO_CACHE" == "true" || -z "$current_value" ]]; then
    local display_default="$default_value"
    if [[ -n "$current_value" ]]; then
      display_default="$current_value"
    fi
    read -r -p "$prompt [$display_default]: " entered
    printf -v "$var_name" '%s' "${entered:-$display_default}"
  fi
}

if [[ "$CLEAR_CACHE" == "true" ]]; then
  unset WEBAPP_NAME LOCATION GITHUB_ORGANIZATION_NAME
fi

DEFAULT_WEBAPP_NAME="$(get_param_default webAppName)"
DEFAULT_LOCATION="$(get_param_default location)"
DEFAULT_GITHUB_ORGANIZATION_NAME="$(get_param_default githubOrganizationName)"
DEFAULT_GITHUB_REPOSITORY="$(get_param_default githubRepository)"
DEFAULT_GITHUB_BRANCH="$(get_param_default githubBranch)"
DEFAULT_FEDERATED_CREDENTIAL_NAME="$(get_param_default federatedCredentialName)"

prompt_if_empty WEBAPP_NAME "Enter WEBAPP_NAME" "$DEFAULT_WEBAPP_NAME"
prompt_if_empty LOCATION "Enter LOCATION (e.g. canadacentral)" "$DEFAULT_LOCATION"
prompt_if_empty GITHUB_ORGANIZATION_NAME "Enter GITHUB_ORGANIZATION_NAME (e.g. your GitHub user/org)" "$DEFAULT_GITHUB_ORGANIZATION_NAME"


RESOURCE_GROUP="${RESOURCE_GROUP:-rg-${WEBAPP_NAME}}"
APP_SERVICE_PLAN_NAME="${APP_SERVICE_PLAN_NAME:-${WEBAPP_NAME}-plan}"
MANAGED_IDENTITY_NAME="${MANAGED_IDENTITY_NAME:-${WEBAPP_NAME}-oidc-mi}"
GITHUB_REPOSITORY="${DEFAULT_GITHUB_REPOSITORY:-CI-CD-Pipeline-Testing}"
GITHUB_BRANCH="${DEFAULT_GITHUB_BRANCH:-main}"
FEDERATED_CREDENTIAL_NAME="${DEFAULT_FEDERATED_CREDENTIAL_NAME:-github-main}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION" 1>/dev/null

DEPLOY_PARAMS=(
  appServicePlanName="$APP_SERVICE_PLAN_NAME"
  managedIdentityName="$MANAGED_IDENTITY_NAME"
  githubRepository="$GITHUB_REPOSITORY"
  githubBranch="$GITHUB_BRANCH"
  federatedCredentialName="$FEDERATED_CREDENTIAL_NAME"
)

if [[ -n "${WEBAPP_NAME:-}" ]]; then
  DEPLOY_PARAMS+=(webAppName="$WEBAPP_NAME")
fi

if [[ -n "${LOCATION:-}" ]]; then
  DEPLOY_PARAMS+=(location="$LOCATION")
fi

if [[ -n "${GITHUB_ORGANIZATION_NAME:-}" ]]; then
  DEPLOY_PARAMS+=(githubOrganizationName="$GITHUB_ORGANIZATION_NAME")
fi

echo "Warning: Web App name must be globally unique in Azure."
echo "Warning: Not all Azure Locations may support all resource types or SKUs used in the template.(Canada Central is recommended for testing)."
echo "Warning: Federated credential can fail if org/repo/branch do not match your GitHub workflow subject or if credential values differ unexpectedly."

az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$TEMPLATE_FILE" \
  --parameters "${DEPLOY_PARAMS[@]}" \
  --output none

echo "Deployment complete."
echo "Web App: ${WEBAPP_NAME:-<template-default>}"
echo "Location: ${LOCATION:-<template-default>}"
echo "Resource Group: $RESOURCE_GROUP"
echo "App Service Plan: $APP_SERVICE_PLAN_NAME"
echo "Managed Identity: $MANAGED_IDENTITY_NAME"
echo "GitHub Organization: ${GITHUB_ORGANIZATION_NAME:-<template-default>}"