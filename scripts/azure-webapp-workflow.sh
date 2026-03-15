#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

mode="${1:-}"

if [[ -z "${mode}" ]]; then
  echo "Usage: $0 <mode>" >&2
  exit 64
fi

resolve_app_name() {
  local input_app_name="${INPUT_APP_NAME:-}"
  local input_tag_key="${INPUT_TAG_KEY:-repo}"
  local input_tag_value="${INPUT_TAG_VALUE:-}"
  local repo_app_name="${REPO_APP_NAME:-}"
  local default_tag_value="${DEFAULT_TAG_VALUE:-${GITHUB_REPOSITORY#*/}}"
  local effective_tag_value
  local resolved_app_name

  if [[ -n "${input_tag_value}" ]]; then
    effective_tag_value="${input_tag_value}"
  else
    effective_tag_value="${default_tag_value}"
  fi

  if [[ -n "${input_app_name}" ]]; then
    resolved_app_name="${input_app_name}"
    echo "Using workflow_dispatch input webapp_name: ${resolved_app_name}"
  elif [[ -n "${repo_app_name}" ]]; then
    resolved_app_name="${repo_app_name}"
    echo "Using repository variable WEBAPP_NAME: ${resolved_app_name}"
  else
    local query="[?tags.${input_tag_key}=='${effective_tag_value}'].name | [0]"
    resolved_app_name="$(az webapp list --query "${query}" -o tsv)"
    if [[ -n "${resolved_app_name}" ]]; then
      echo "Using web app found by tag ${input_tag_key}=${effective_tag_value}: ${resolved_app_name}"
    fi
  fi

  if [[ -z "${resolved_app_name}" ]]; then
    echo "No web app name resolved. Provide workflow_dispatch input webapp_name, set repository variable WEBAPP_NAME, or tag a web app with ${input_tag_key}=${effective_tag_value}." >&2
    exit 1
  fi

  echo "app_name=${resolved_app_name}" >> "${GITHUB_OUTPUT}"
}

preflight_validate() {
  local app_name="${APP_NAME:?APP_NAME is required}"
  local input_resource_group="${INPUT_RESOURCE_GROUP:-}"
  local required_resource_group
  local active_subscription_id
  local webapp_show_output=""
  local webapp_show_exit=0

  active_subscription_id="$(az account show --query id -o tsv)"

  echo "Azure subscription in workflow context: ${active_subscription_id}"
  echo "Input resource group: ${input_resource_group}"

  if [[ -z "${input_resource_group}" ]]; then
    required_resource_group="${app_name}-rg"
    echo "No resource_group input provided. Defaulting to: ${required_resource_group}"
  else
    required_resource_group="${input_resource_group}"
    echo "Using provided resource_group: ${required_resource_group}"
  fi

  webapp_show_output="$(az webapp show --name "${app_name}" --resource-group "${required_resource_group}" --query name -o tsv 2>&1)" || webapp_show_exit=$?

  if [[ "${webapp_show_exit}" -ne 0 ]]; then
    if echo "${webapp_show_output}" | grep -Eiq "AuthorizationFailed|does not have authorization"; then
      echo "::error::Azure identity does not have permission to read web app '${app_name}' in resource group '${required_resource_group}'."
      echo "::error::Grant at least Reader on the target resource group (or Web App), then rerun."
      echo "::error::Identity object id is shown in the Azure CLI error above."
      exit 1
    fi

    echo "::error::Web app '${app_name}' was not found in resource group '${required_resource_group}' under subscription '${active_subscription_id}'."
    echo "::error::If your ARM deployment used a different RG name, provide workflow_dispatch input resource_group explicitly."
    echo "::error::Also verify AZURE_SUBSCRIPTION_ID, AZURE_TENANT_ID, and AZURE_CLIENT_ID."
    exit 1
  fi

  echo "Resolved resource group: ${required_resource_group}"
  echo "resource_group=${required_resource_group}" >> "${GITHUB_OUTPUT}"
}

debug_payload() {
  local deploy_pkg_dir="${DEPLOY_PKG_DIR:-deploy_pkg}"

  echo "PWD=$(pwd)"
  ls -la "${deploy_pkg_dir}"
  echo "---- app dir ----"
  ls -la "${deploy_pkg_dir}/app" || echo "NO app/ folder"
  echo "---- find main.py ----"
  find "${deploy_pkg_dir}" -maxdepth 3 -name "main.py" -print
}

package_deploy() {
  local deploy_pkg_dir="${DEPLOY_PKG_DIR:-deploy_pkg}"
  local deploy_zip="${DEPLOY_ZIP:-deploy.zip}"

  if [[ -d "./${deploy_pkg_dir}/app" && -f "./${deploy_pkg_dir}/requirements.txt" ]]; then
    echo "Deploy package verified: app/ directory and requirements.txt found."
  else
    echo "::error::Deploy package is missing required files. Ensure app/ directory and requirements.txt are included in the artifact."
    exit 1
  fi

  ls -la "./${deploy_pkg_dir}"

  (
    cd "${deploy_pkg_dir}"
    zip -r "../${deploy_zip}" .
  )

  echo "Zip created:"
  ls -lh "${deploy_zip}"
  echo "Zip contents (top):"
  unzip -l "${deploy_zip}" | head -n 60
}

restart_before_retry() {
  local app_name="${APP_NAME:?APP_NAME is required}"
  local resource_group="${RESOURCE_GROUP:?RESOURCE_GROUP is required}"
  local wait_seconds="${WAIT_SECONDS:-20}"

  echo "Attempt 1 failed. Restarting ${app_name} before retry..."
  az webapp restart --name "${app_name}" --resource-group "${resource_group}" || true
  echo "Waiting ${wait_seconds}s before retry..."
  sleep "${wait_seconds}"
}

configure_startup() {
  local app_name="${APP_NAME:?APP_NAME is required}"
  local resource_group="${RESOURCE_GROUP:?RESOURCE_GROUP is required}"
  local startup_file="${STARTUP_FILE:-gunicorn --bind=0.0.0.0 --timeout 600 app.main:app}"

  az webapp config set \
    --name "${app_name}" \
    --resource-group "${resource_group}" \
    --startup-file "${startup_file}"

  az webapp restart --name "${app_name}" --resource-group "${resource_group}"
}

case "${mode}" in
  resolve_app_name)
    resolve_app_name
    ;;
  preflight_validate)
    preflight_validate
    ;;
  debug_payload)
    debug_payload
    ;;
  package_deploy)
    package_deploy
    ;;
  restart_before_retry)
    restart_before_retry
    ;;
  configure_startup)
    configure_startup
    ;;
  *)
    echo "Unknown mode: ${mode}" >&2
    exit 64
    ;;
esac
