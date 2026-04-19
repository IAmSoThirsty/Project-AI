# resolve_renames.ps1 - Master-Tier Native Rename Cleanup
# 2026-03-15 07:55 | Productivity: Active

$substrateRoot = "c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos"

Write-Host "--- SOVEREIGN STACK: Rename Resolution Utility ---" -ForegroundColor Cyan

$legacyFolders = Get-ChildItem -Path $substrateRoot -Directory | Where-Object { $_.Name -like "thirsty-lang-*" }

if ($null -eq $legacyFolders) {
    Write-Host "No legacy thirsty-lang-* folders found." -ForegroundColor Yellow
    exit 0
}

foreach ($legacy in $legacyFolders) {
    $rawName = $legacy.Name -replace "thirsty-lang-", "" -replace "-", " "
    $newName = "Thirstys " + ((Get-Culture).TextInfo.ToTitleCase($rawName))
    $dest = Join-Path $substrateRoot $newName
    
    Write-Host "Analyzing: $($legacy.Name) -> $newName" -ForegroundColor Cyan
    
    if (Test-Path $dest) {
        Write-Host "  Destination exists. Checking for nesting..." -ForegroundColor Yellow
        $nestedLegacy = Join-Path $dest $legacy.Name
        if (Test-Path $nestedLegacy) {
            Write-Host "  Found nested legacy folder. Moving contents up..."
            Get-ChildItem -Path $nestedLegacy | Move-Item -Destination $dest -Force -ErrorAction SilentlyContinue
            Remove-Item -Path $nestedLegacy -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "  Merging loose files from root legacy folder..."
        Get-ChildItem -Path $legacy.FullName | ForEach-Object {
            $itemDest = Join-Path $dest $_.Name
            if (-not (Test-Path $itemDest)) {
                Move-Item -Path $_.FullName -Destination $dest -Force -ErrorAction SilentlyContinue
            }
        }
        
        Write-Host "  Cleanup: Removing legacy folder $($legacy.Name)"
        Remove-Item -Path $legacy.FullName -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "  Moving legacy to NEW destination..."
        Move-Item -Path $legacy.FullName -Destination $dest -Force
    }
}
Write-Host "Rename resolution complete." -ForegroundColor Green
