# update_workspace.ps1 - Master-Tier Workspace Alignment Logic
# 2026-03-15 07:58 | Productivity: Active

$substrateRoot = "c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos"
$workspaceFile = Join-Path $substrateRoot "Project-AI\Project-AI.code-workspace"

Write-Host "--- SOVEREIGN STACK: Workspace Sync Utility ---" -ForegroundColor Cyan

$folders = Get-ChildItem -Path $substrateRoot -Directory | Where-Object { 
    $_.Name -notlike ".*" -and $_.Name -ne ".mypy_cache"
}

$folderEntries = @()
$folderEntries += @{ name = "Project-AI"; path = "." }

foreach ($folder in $folders) {
    if ($folder.Name -eq "Project-AI") { continue }
    $folderEntries += @{ name = $folder.Name; path = "..\$($folder.Name)" }
}

$workspaceData = @{
    folders = $folderEntries
    settings = @{
        "chat.checkpoints.showFileChanges" = $true
        "chat.edits2.enabled" = $true
        "chat.mcp.assisted.nuget.enabled" = $true
        "chat.mcp.discovery.enabled" = @{
            "claude-desktop" = $true
            "windsurf" = $true
            "cursor-global" = $true
            "cursor-workspace" = $true
        }
        "chat.mcp.gallery.enabled" = $true
        "chat.tools.terminal.autoReplyToPrompts" = $true
        "inlineChat.enableV2" = $true
        "inlineChat.notebookAgent" = $true
        "terminal.integrated.suggest.enabled" = $true
    }
}

$workspaceData | ConvertTo-Json -Depth 10 | Set-Content -Path $workspaceFile
Write-Host "Success: Workspace sync complete: $($folders.Count) members aligned." -ForegroundColor Green
