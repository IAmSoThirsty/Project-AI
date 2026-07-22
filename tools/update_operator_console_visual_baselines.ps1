[CmdletBinding()]
param(
    [switch]$SkipWindows
)

$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$snapshotDirectory = Join-Path $repoRoot "apps\web\operator-console\tests\visual\__screenshots__"
$linuxImage = "mcr.microsoft.com/playwright@sha256:5b8f294aff9041b7191c34a4bab3ac270157a28774d4b0660e9743297b697e48"
$containerName = "project-ai-visual-baselines-$PID"

Push-Location $repoRoot
try {
    if (-not $SkipWindows) {
        & pnpm --filter @project-ai/operator-console test:visual:update
        if ($LASTEXITCODE -ne 0) { throw "Windows visual baseline generation failed." }
    }

    $desktopStatus = (& docker desktop status | Out-String)
    if ($LASTEXITCODE -ne 0 -or $desktopStatus -notmatch "Status\s+running") {
        throw "Docker Desktop must be running to generate the Linux visual baselines."
    }

    & docker pull $linuxImage
    if ($LASTEXITCODE -ne 0) { throw "Unable to resolve the pinned Playwright Linux image." }

    $linuxCommand = @"
tar -C /source --exclude='*/node_modules' --exclude='*/dist' --exclude='apps/web/operator-console/tests/visual/__screenshots__' -cf - package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.web.json eslint.config.js apps/web/operator-console apps/web/shared | tar -xf - && corepack enable && corepack prepare pnpm@10.30.0 --activate && pnpm install --frozen-lockfile && pnpm --filter @project-ai/operator-console test:visual:update
"@

    & docker run --rm --name $containerName `
        --mount "type=bind,source=$repoRoot,target=/source,readonly" `
        --mount "type=bind,source=$snapshotDirectory,target=/work/apps/web/operator-console/tests/visual/__screenshots__" `
        --workdir /work `
        $linuxImage bash -lc $linuxCommand
    if ($LASTEXITCODE -ne 0) { throw "Linux visual baseline generation failed." }
}
finally {
    $existing = & docker ps -a --filter "name=^/$containerName$" --format "{{.ID}}" 2>$null
    if ($existing) { & docker rm --force $containerName | Out-Null }
    Pop-Location
}
