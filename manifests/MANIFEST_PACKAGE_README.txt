# Manifest Package

GeneratedUtc,2026-04-04T03:59:04.3305476Z
TotalFiles,88719
TotalBytes,2734891081
TotalLOC,19308393
TotalNonEmptyLOC,17072799
TextFiles,79142
BinaryFiles,9577

Files:
- manifest.master.csv (enriched per-file schema including LOC and text/binary classification)
- summary.by-top-level.csv (folder-level counts, size, LOC, non-empty LOC)
- summary.by-extension.csv (extension-level counts, size, LOC, non-empty LOC)
- summary.largest-200.csv (largest files)
- summary.highest-loc-500.csv (highest LOC files)
- summary.text-vs-binary.csv (global text/binary and LOC totals)
- by-top-level/*.csv (split manifests by top-level folder)

Columns in manifest.master.csv:
- RelativePath, TopLevelFolder, Directory, FileName, Extension, SizeBytes, SizeKiB, LastWriteTimeUtc, FileAgeDays, IsText, IsBinary, LineCount, NonEmptyLineCount, CharCount, AvgLineLength, MaxLineLength
