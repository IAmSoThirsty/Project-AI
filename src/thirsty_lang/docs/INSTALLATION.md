# Installation and Setup Guide

## Prerequisites

Before installing Thirsty-lang, ensure you have:

- **Node.js** version 14.0.0 or higher
- **npm** (comes with Node.js) or **yarn**
- A terminal/command prompt
- A code editor (VS Code recommended)

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
git clone https://github.com/IAmSoThirsty/Thirsty-lang.git

# Navigate to the directory
cd Thirsty-lang

# Install dependencies (if any in future)
npm install

# Verify installation
npm test
```

### Method 2: Direct Download

1. Download the repository as a ZIP file from GitHub
1. Extract to your desired location
1. Open terminal in the extracted folder
1. Run `npm install`
1. Run `npm test` to verify

## Installing the CLI Globally (Optional)

To use the `thirsty` command from anywhere:

```bash
# In the Thirsty-lang directory
npm link

# Now you can use 'thirsty' from anywhere
thirsty run myprogram.thirsty
thirsty repl
thirsty train
```

## Verification

After installation, verify everything works:

```bash
# Run tests
npm test

# Run an example
npm start examples/hello.thirsty

# Start the REPL
npm run repl
# (press Ctrl+C twice to exit)

# Start training
npm run train
# (select option 6 to exit)
```

## Setting Up Your First Project

```bash
# Create a new Thirsty-lang project
node src/thirsty-cli.js init my-first-project

# Navigate to your project
cd my-first-project

# Run the program
thirsty run src/main.thirsty
```

## Installing the VS Code Extension

1. Open VS Code
1. Copy `.vscode/extensions/thirsty-lang` to your VS Code extensions folder:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`
   - **macOS**: `~/.vscode/extensions/`
   - **Linux**: `~/.vscode/extensions/`
1. Reload VS Code
1. Open any `.thirsty` file to see syntax highlighting!

## Troubleshooting

### "Command not found: thirsty"

If the `thirsty` command isn't found after `npm link`:

```bash
# Try running with full path
node /path/to/Thirsty-lang/src/thirsty-cli.js

# Or use npm scripts
npm start
npm run repl
npm run train
```

### Node.js version issues

Check your Node.js version:

```bash
node --version
```

If it's below 14.0.0, upgrade Node.js from [nodejs.org](https://nodejs.org)

### Tests failing

Make sure you're in the Thirsty-lang directory:

```bash
cd /path/to/Thirsty-lang
npm test
```

### Permission errors on Linux/macOS

You may need to make scripts executable:

```bash
chmod +x src/*.js
```

## Next Steps

After installation:

1. 🎓 **Start learning**: Run `npm run train` for interactive lessons
1. 🔍 **Explore examples**: Check out the `examples/` directory
1. 📚 **Read docs**: Browse the `docs/` directory
1. 🎮 **Try the playground**: Open `playground/index.html` in a browser
1. 💻 **Start coding**: Create your first Thirsty-lang program!

## Getting Help

- 📖 Read the [FAQ](FAQ.md)
- 📚 Check the [Quick Reference](QUICK_REFERENCE.md)
- 🐛 Report issues on [GitHub](https://github.com/IAmSoThirsty/Thirsty-lang/issues)

## Uninstallation

To remove Thirsty-lang:

```bash
# If you used npm link
npm unlink

# Remove the directory
rm -rf /path/to/Thirsty-lang
```

Stay hydrated! 💧
