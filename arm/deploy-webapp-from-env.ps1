param(
    [switch]$NoCache,
    [switch]$ClearCache
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$parametersFile = Join-Path $scriptDir 'webapp-managed-identity.parameters.json'
$templateFile = Join-Path $scriptDir 'webapp-managed-identity.template.json'
$defaults = $null

if (Test-Path $parametersFile) {
    $defaults = Get-Content $parametersFile -Raw | ConvertFrom-Json
}

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw 'Azure CLI (az) is required.'
}

function Get-DefaultParamValue([string]$name) {
    if (-not $defaults) { return '' }
    $paramObj = $defaults.parameters.$name
    if ($null -eq $paramObj) { return '' }
    $value = $paramObj.value
    if ($null -eq $value) { return '' }
    return [string]$value
}

function Resolve-Value([string]$envName, [string]$prompt, [string]$defaultValue) {
    $current = [Environment]::GetEnvironmentVariable($envName)
    if ($NoCache -or [string]::IsNullOrWhiteSpace($current)) {
        $displayDefault = if ([string]::IsNullOrWhiteSpace($current)) { $defaultValue } else { $current }
        $entered = Read-Host "$prompt [$displayDefault]"
        $current = if ([string]::IsNullOrWhiteSpace($entered)) { $displayDefault } else { $entered }
        if (-not $NoCache) {
            [Environment]::SetEnvironmentVariable($envName, $current, 'Process')
        }
    }
    return $current
}

if ($ClearCache) {
    [Environment]::SetEnvironmentVariable('WEBAPP_NAME', $null, 'Process')
    [Environment]::SetEnvironmentVariable('LOCATION', $null, 'Process')
    [Environment]::SetEnvironmentVariable('GITHUB_ORGANIZATION_NAME', $null, 'Process')
}

$webAppNameDefault = Get-DefaultParamValue 'webAppName'
$locationDefault = Get-DefaultParamValue 'location'
$ghOrgDefault = Get-DefaultParamValue 'githubOrganizationName'
$ghRepoDefault = Get-DefaultParamValue 'githubRepository'
$ghBranchDefault = Get-DefaultParamValue 'githubBranch'
$fcNameDefault = Get-DefaultParamValue 'federatedCredentialName'

$webAppName = Resolve-Value 'WEBAPP_NAME' 'Enter WEBAPP_NAME' $webAppNameDefault
$location = Resolve-Value 'LOCATION' 'Enter LOCATION (e.g. canadacentral)' $locationDefault
$githubOrganizationName = Resolve-Value 'GITHUB_ORGANIZATION_NAME' 'Enter GITHUB_ORGANIZATION_NAME (e.g. your GitHub user/org)' $ghOrgDefault

$resourceGroup = [Environment]::GetEnvironmentVariable('RESOURCE_GROUP')
if ([string]::IsNullOrWhiteSpace($resourceGroup)) { $resourceGroup = "rg-$webAppName" }

$appServicePlanName = [Environment]::GetEnvironmentVariable('APP_SERVICE_PLAN_NAME')
if ([string]::IsNullOrWhiteSpace($appServicePlanName)) { $appServicePlanName = "$webAppName-plan" }

$managedIdentityName = [Environment]::GetEnvironmentVariable('MANAGED_IDENTITY_NAME')
if ([string]::IsNullOrWhiteSpace($managedIdentityName)) { $managedIdentityName = "$webAppName-oidc-mi" }

$githubRepository = if ([string]::IsNullOrWhiteSpace($ghRepoDefault)) { 'CI-CD-Pipeline-Testing' } else { $ghRepoDefault }
$githubBranch = if ([string]::IsNullOrWhiteSpace($ghBranchDefault)) { 'main' } else { $ghBranchDefault }
$federatedCredentialName = if ([string]::IsNullOrWhiteSpace($fcNameDefault)) { 'github-main' } else { $fcNameDefault }

az group create --name $resourceGroup --location $location | Out-Null

$deploymentParams = @(
    "appServicePlanName=$appServicePlanName",
    "managedIdentityName=$managedIdentityName",
    "githubRepository=$githubRepository",
    "githubBranch=$githubBranch",
    "federatedCredentialName=$federatedCredentialName"
)

if (-not [string]::IsNullOrWhiteSpace($webAppName)) {
    $deploymentParams += "webAppName=$webAppName"
}

if (-not [string]::IsNullOrWhiteSpace($location)) {
    $deploymentParams += "location=$location"
}

if (-not [string]::IsNullOrWhiteSpace($githubOrganizationName)) {
    $deploymentParams += "githubOrganizationName=$githubOrganizationName"
}

Write-Warning 'Web App name must be globally unique in Azure.'
Write-Warning 'Not all Azure Locations may support all resource types or SKUs used in the template.(Canada Central is recommended for testing).'
Write-Warning 'Federated credential can fail if org/repo/branch do not match your GitHub workflow subject or if credential values differ unexpectedly.'
Write-Warning 'Ensure Azure CLI is set to the intended subscription (az account set --subscription <id>) before deployment; otherwise managed identity role assignment may fail or apply in the wrong subscription.'

az deployment group create `
    --resource-group $resourceGroup `
    --template-file $templateFile `
    --parameters $deploymentParams `
    --output none

Write-Host "Deployment complete."
Write-Host "Web App: $(if ([string]::IsNullOrWhiteSpace($webAppName)) { '<template-default>' } else { $webAppName })"
Write-Host "Location: $(if ([string]::IsNullOrWhiteSpace($location)) { '<template-default>' } else { $location })"
Write-Host "Resource Group: $resourceGroup"
Write-Host "App Service Plan: $appServicePlanName"
Write-Host "Managed Identity: $managedIdentityName"
Write-Host "GitHub Organization: $(if ([string]::IsNullOrWhiteSpace($githubOrganizationName)) { '<template-default>' } else { $githubOrganizationName })"