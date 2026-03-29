<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# VS Code Extension for Thirsty-lang

This directory contains the VS Code extension for Thirsty-lang with syntax highlighting and code snippets.

## Installation

### Manual Installation

1. Copy this entire `vscode-extension` folder
2. Paste it into your VS Code extensions directory:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\thirsty-lang\`
   - **macOS**: `~/.vscode/extensions/thirsty-lang/`
   - **Linux**: `~/.vscode/extensions/thirsty-lang/`
3. Reload VS Code
4. Open any `.thirsty` file to see syntax highlighting!

### Alternative: Symlink (Advanced)

```bash

# From the Thirsty-lang directory

ln -s "$(pwd)/vscode-extension" ~/.vscode/extensions/thirsty-lang
```

## Features

- ✨ **Syntax Highlighting** for all Thirsty-lang keywords
- 🎨 **Code Snippets** for common patterns
- 📝 **Auto-completion** for keywords
- 🔧 **Auto-closing** for brackets, quotes, and parentheses
- 💬 **Comment toggling** support

## Supported File Extensions

- `.thirsty` - Base Thirsty-lang
- `.thirstyplus` - Thirsty+ edition
- `.thirstyplusplus` - Thirsty++ edition
- `.thirstofgods` - ThirstOfGods edition

## Available Snippets

Type these prefixes and press Tab:

- `drink` - Variable declaration
- `pour` - Output statement
- `//` - Comment
- `thirsty` - If statement (Thirsty+)
- `glass` - Function declaration (Thirsty++)
- `refill` - Loop (Thirsty++)
- `fountain` - Class declaration (ThirstOfGods)
- `cascade` - Async function (ThirstOfGods)

## Troubleshooting

If syntax highlighting doesn't work:

1. Make sure the extension is in the correct location
2. Reload VS Code (Ctrl/Cmd + Shift + P → "Reload Window")
3. Check that you're opening a `.thirsty` file

## Contributing

Want to improve the extension? Edit the files in this directory:

- `syntaxes/thirsty.tmLanguage.json` - Syntax grammar
- `snippets/thirsty.json` - Code snippets
- `language-configuration.json` - Language settings
- `package.json` - Extension metadata

Stay hydrated while coding! 💧
