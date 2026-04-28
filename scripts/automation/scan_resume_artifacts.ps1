$ErrorActionPreference = 'SilentlyContinue'
$targetFiles = @(
  'trainer_state.json','optimizer.pt','scheduler.pt','rng_state.pth','training_args.bin',
  'adapter_config.json','adapter_model.safetensors','adapter_model.bin',
  'pytorch_model.bin','pytorch_model.safetensors','config.json'
)
$excludeDirNames = @('Windows','Program Files','Program Files (x86)','$Recycle.Bin','node_modules','.git')
$overrideTokens = @('checkpoint-','trainer_state.json','adapter_model','optimizer.pt','scheduler.pt')
$drives = @('C:','D:','T:') | Where-Object { Test-Path ("$_\\") }
$found = New-Object System.Collections.Generic.List[object]

foreach ($drive in $drives) {
  $stack = New-Object 'System.Collections.Generic.Stack[string]'
  $stack.Push("${drive}\\")

  while ($stack.Count -gt 0) {
    $dir = $stack.Pop()
    $dirLower = $dir.ToLowerInvariant()
    $leaf = [System.IO.Path]::GetFileName($dir.TrimEnd('\\'))

    $isExcluded = $false
    if ($excludeDirNames -contains $leaf) { $isExcluded = $true }
    if ($dirLower -like '*\\appdata\\local\\programs*') { $isExcluded = $true }

    $hasOverride = $false
    foreach ($tok in $overrideTokens) {
      if ($dirLower.Contains($tok.ToLowerInvariant())) { $hasOverride = $true; break }
    }
    if ($isExcluded -and -not $hasOverride) { continue }

    if ($leaf -like 'checkpoint-*') {
      try {
        $dinfo = Get-Item -LiteralPath $dir
        $found.Add([pscustomobject]@{ Path=$dir; Name=$leaf; Type='checkpoint_dir'; LastWriteTime=$dinfo.LastWriteTime; Group=$dir }) | Out-Null
      } catch {}
    }

    try { $entries = [System.IO.Directory]::EnumerateFileSystemEntries($dir) } catch { continue }

    foreach ($entry in $entries) {
      if ([System.IO.Directory]::Exists($entry)) {
        $stack.Push($entry)
      }
      elseif ([System.IO.File]::Exists($entry)) {
        $name = [System.IO.Path]::GetFileName($entry)
        if ($targetFiles -contains $name) {
          try {
            $fi = Get-Item -LiteralPath $entry
            $parent = Split-Path -Parent $entry
            $found.Add([pscustomobject]@{ Path=$entry; Name=$name; Type='file'; LastWriteTime=$fi.LastWriteTime; Group=$parent }) | Out-Null
          } catch {}
        }
      }
    }
  }
}

$groups = $found | Group-Object Group | ForEach-Object {
  $gpath = $_.Name
  $items = $_.Group
  $names = $items.Name

  $hasTrainer = $names -contains 'trainer_state.json'
  $hasOptOrSched = ($names -contains 'optimizer.pt') -or ($names -contains 'scheduler.pt')
  $hasAdapterPair = ($names -contains 'adapter_config.json') -and ($names -contains 'adapter_model.safetensors')
  $gLeaf = Split-Path -Leaf $gpath
  $isCheckpointOrRun = ($gLeaf -like 'checkpoint-*') -or ($gLeaf.ToLowerInvariant().Contains('run'))

  $status = if (($hasTrainer -and $hasOptOrSched) -or ($hasAdapterPair -and $isCheckpointOrRun)) { 'RESUME_READY' } else { 'NOT_READY' }

  [pscustomobject]@{
    GroupPath = $gpath
    Status = $status
    Items = $items | Sort-Object Name, Path
  }
}

$readyCount = ($groups | Where-Object Status -eq 'RESUME_READY').Count
$notReadyCount = ($groups | Where-Object Status -eq 'NOT_READY').Count

$outFile = Join-Path $PWD 'resume_artifact_scan_results.txt'
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add('=== Grouped resumable-artifact scan results ===') | Out-Null
foreach ($g in ($groups | Sort-Object Status, GroupPath)) {
  $lines.Add('') | Out-Null
  $lines.Add(("[{0}] {1}" -f $g.Status, $g.GroupPath)) | Out-Null
  foreach ($it in $g.Items) {
    $lines.Add(("{0} | {1:yyyy-MM-dd HH:mm:ss} | {2}" -f $it.Name, $it.LastWriteTime, $it.Path)) | Out-Null
  }
}
$lines.Add('') | Out-Null
$lines.Add('=== Summary ===') | Out-Null
$lines.Add(("RESUME_READY count: {0}" -f $readyCount)) | Out-Null
$lines.Add(("NOT_READY count: {0}" -f $notReadyCount)) | Out-Null
Set-Content -Path $outFile -Value $lines -Encoding UTF8
Get-Content -Path $outFile
