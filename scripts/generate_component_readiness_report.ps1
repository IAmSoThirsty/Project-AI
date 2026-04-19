param(
    [string]$RegistryPath = (Join-Path $PSScriptRoot "..\config\component-registry.json"),
    [string]$OutputPath = (Join-Path $PSScriptRoot "..\docs\reports\COMPONENT_PRODUCTION_READINESS_REPORT.md")
)

if (-not (Test-Path $RegistryPath)) {
    throw "Component registry not found: $RegistryPath"
}

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$registry = Get-Content $RegistryPath -Raw | ConvertFrom-Json

$rows = @()
$profileNames = @($registry.profiles.PSObject.Properties.Name)
foreach ($profileName in $profileNames) {
    $profile = $registry.profiles.$profileName
    foreach ($path in $profile.paths) {
        $absolutePath = [System.IO.Path]::GetFullPath((Join-Path $workspaceRoot $path))
        $exists = Test-Path $absolutePath
        $gitDir = Join-Path $absolutePath ".git"
        $gitState = if ($exists -and (Test-Path $gitDir)) { "git-present" } elseif ($exists) { "path-present" } else { "reference-only" }
        $operationalState = if ($exists) { "operationally-addressable" } else { "distributed-reference" }
        $logicalState = "purpose-asserted"

        $rows += [PSCustomObject]@{
            Profile = $profileName
            Path = $path
            Classification = $profile.classification
            Lifecycle = $profile.lifecycle
            Readiness = $profile.readiness
            Locality = $profile.locality
            OperationalState = $operationalState
            LogicalState = $logicalState
            GitState = $gitState
            Purpose = $profile.purpose
        }
    }
}

$generatedAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$lines = @()
$lines += "# Component Production Readiness Report"
$lines += ""
$lines += "Generated: $generatedAt"
$lines += ""
$lines += "## Summary"
$lines += ""
$lines += "- Total components tracked: $($rows.Count)"
$lines += "- Local operationally-addressable: $((@($rows | Where-Object { $_.OperationalState -eq 'operationally-addressable' })).Count)"
$lines += "- Distributed references: $((@($rows | Where-Object { $_.OperationalState -eq 'distributed-reference' })).Count)"
$lines += "- Production-ready declarations: $((@($rows | Where-Object { $_.Readiness -eq 'production-ready' })).Count)"
$lines += ""
$lines += "## Components"
$lines += ""
$lines += "| Profile | Path | Purpose State | Operational State | Git State | Purpose |"
$lines += "|---|---|---|---|---|---|"

foreach ($row in $rows) {
    $purposeState = "$($row.Classification)-$($row.Lifecycle)-$($row.Readiness)"
    $lines += "| $($row.Profile) | $($row.Path) | $purposeState | $($row.OperationalState) | $($row.GitState) | $($row.Purpose) |"
}

$dir = Split-Path -Parent $OutputPath
if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Set-Content -Path $OutputPath -Value $lines -Encoding UTF8
Write-Output "Generated readiness report: $OutputPath"
