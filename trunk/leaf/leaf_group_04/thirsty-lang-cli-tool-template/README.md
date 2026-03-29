<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang CLI Tool Template 💧

Build command-line applications with Thirsty-lang.

## Features

- Argument parsing
- Subcommands
- Configuration files
- Progress bars
- Interactive prompts with sip

## Example

```thirsty
glass main() {
  drink args = parseArgs()
  
  thirsty args.command == "process"
    processFiles(args.files)
  hydrated thirsty args.command == "help"
    showHelp()
}
```

## Commands

- `mytool process <files>` - Process files
- `mytool config` - Show configuration
- `mytool help` - Show help

## License

MIT
