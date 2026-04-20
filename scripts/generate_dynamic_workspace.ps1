param(
    [string]$BaseWorkspacePath = (Join-Path $PSScriptRoot "..\Project-AI.code-workspace"),
    [string]$OutputWorkspacePath = (Join-Path $PSScriptRoot "..\Project-AI.dynamic.code-workspace"),
    [string]$RegistryPath = (Join-Path $PSScriptRoot "..\config\component-registry.json"),
    [switch]$IncludeMissingFolders,
    [switch]$IncludeLegacyCandidatePaths,
    [switch]$EnforceLocalOperational
)

$resolvedBasePath = (Resolve-Path $BaseWorkspacePath).Path
$workspaceRoot = Split-Path -Parent $resolvedBasePath

if (-not (Test-Path $RegistryPath)) {
    throw "Component registry not found: $RegistryPath"
}

$registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json
$profilesToInclude = @("canonical-native")
if ($IncludeLegacyCandidatePaths) {
    $profilesToInclude += "legacy-distributed"
}

$componentItems = @()
foreach ($profileName in $profilesToInclude) {
    $profile = $registry.profiles.$profileName
    if (-not $profile) {
        continue
    }

    foreach ($path in $profile.paths) {
        $componentItems += [PSCustomObject]@{
            profile = $profileName
            path = $path
            classification = $profile.classification
            lifecycle = $profile.lifecycle
            readiness = $profile.readiness
            locality = $profile.locality
            purpose = $profile.purpose
        }
    }
}

$componentItems = $componentItems | Group-Object -Property path | ForEach-Object { $_.Group[0] }

$folders = @(
    @{ path = "." }
)
$includedLocal = @()
$includedReferenceOnly = @()
$deferred = @()

$purposeLabelByPath = @{}
foreach ($item in $componentItems) {
    $relativePath = $item.path
    $absolutePath = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot $relativePath))
    $isPresent = Test-Path $absolutePath
    $purposeState = "$($item.classification)-$($item.lifecycle)-$($item.readiness)"

    if ($isPresent -or $IncludeMissingFolders) {
        $folders += @{ path = $relativePath }
        if ($isPresent) {
            $includedLocal += "$relativePath [$purposeState | local-present]"
            $purposeLabelByPath[$relativePath] = "$purposeState | local-present"
        }
        else {
            $includedReferenceOnly += "$relativePath [$purposeState | reference-only]"
            $purposeLabelByPath[$relativePath] = "$purposeState | reference-only"
        }
    }
    else {
        $deferred += "$relativePath [$purposeState | deferred-localization]"
    }
}

$baseWorkspace = Get-Content $resolvedBasePath -Raw | ConvertFrom-Json
$outputWorkspace = [ordered]@{
    folders = $folders
    settings = $baseWorkspace.settings
}

$outputWorkspace | ConvertTo-Json -Depth 100 | Set-Content -Path $OutputWorkspacePath -Encoding UTF8

Write-Output "Generated: $OutputWorkspacePath"
Write-Output "IncludeMissingFolders: $($IncludeMissingFolders.IsPresent)"
Write-Output "IncludeLegacyCandidatePaths: $($IncludeLegacyCandidatePaths.IsPresent)"
Write-Output "EnforceLocalOperational: $($EnforceLocalOperational.IsPresent)"
Write-Output "Candidate folders considered: $($componentItems.Count)"
Write-Output "Included optional folders (local-present): $($includedLocal.Count)"
Write-Output "Included optional folders (reference-only): $($includedReferenceOnly.Count)"
Write-Output "Deferred optional folders: $($deferred.Count)"
if ($includedLocal.Count -gt 0) {
    Write-Output "Included local-present list:"
    $includedLocal | ForEach-Object { Write-Output " - $_" }
}
if ($includedReferenceOnly.Count -gt 0) {
    Write-Output "Included reference-only list:"
    $includedReferenceOnly | ForEach-Object { Write-Output " - $_" }
}
if ($deferred.Count -gt 0) {
    Write-Output "Deferred localization list:"
    $deferred | ForEach-Object { Write-Output " - $_" }
}

if ($EnforceLocalOperational) {
    $gateFailures = @($includedReferenceOnly) + @($deferred)
    if ($gateFailures.Count -gt 0) {
        Write-Error "Enforcement gate failed: $($gateFailures.Count) component(s) are not local-present."
        $gateFailures | ForEach-Object { Write-Error " - $_" }
        exit 2
    }
    Write-Output "Enforcement gate passed: all selected components are local-present."
}
