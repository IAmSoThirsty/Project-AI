# Project-AI CLI Documentation

Welcome to the Project-AI Command Line Interface (CLI) documentation. This guide covers everything you need to know about using the CLI effectively.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Command Groups](#command-groups)
- [Shell Completion](#shell-completion)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

The CLI is installed automatically when you install Project-AI:

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -m app.cli --version
```

You should see output like: `Project-AI CLI v1.0.0`

## Quick Start

### Basic Usage

Run the CLI with:

```bash
python -m app.cli [COMMAND] [OPTIONS]
```

### Get Help

To see all available commands:

```bash
python -m app.cli --help
```

To get help for a specific command:

```bash
python -m app.cli user --help
python -m app.cli ai --help
```

## Configuration

The CLI supports configuration files in TOML format. Configuration is loaded from the following locations (in priority order):

1. **Environment variables** (highest priority)
1. **Project config**: `.projectai.toml` (current directory)
1. **User config**: `~/.projectai.toml` (home directory)
1. **Default values** (lowest priority)

### Configuration File Format

Create a file named `~/.projectai.toml` or `.projectai.toml`:

```toml
[general]
log_level = "INFO"
data_dir = "data"
verbose = false

[ai]
model = "gpt-3.5-turbo"
temperature = 0.7
max_tokens = 256

[security]
enable_four_laws = true
enable_black_vault = true
enable_audit_log = true

[api]
timeout = 30
retry_attempts = 3
```

### Environment Variables

Override configuration with environment variables:

```bash
export PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
export PROJECTAI_AI_TEMPERATURE=0.9
```

Environment variable format: `PROJECTAI_SECTION_KEY=value`

## Command Groups

The CLI is organized into six main command groups:

### 1. User Commands

Manage user accounts and authentication.

```bash
python -m app.cli user --help
```

**Examples:**

```bash

# Example user command

python -m app.cli user example JohnDoe
```

### 2. Memory Commands

Work with the AI memory and knowledge base.

```bash
python -m app.cli memory --help
```

**Examples:**

```bash

# Example memory command

python -m app.cli memory example "important-fact"
```

### 3. Learning Commands

Manage AI learning requests and training data.

```bash
python -m app.cli learning --help
```

**Examples:**

```bash

# Example learning command

python -m app.cli learning example "machine-learning"
```

### 4. Plugin Commands

Manage and configure plugins.

```bash
python -m app.cli plugin --help
```

**Examples:**

```bash

# Example plugin command

python -m app.cli plugin example "my-plugin"
```

### 5. System Commands

System-level operations and configuration.

```bash
python -m app.cli system --help
```

**Examples:**

```bash

# Example system command

python -m app.cli system example "config-param"
```

### 6. AI Commands

Direct AI model interaction and configuration.

```bash
python -m app.cli ai --help
```

**Examples:**

```bash

# Example AI command

python -m app.cli ai example "gpt-4"
```

## Shell Completion

The CLI supports tab completion for bash, zsh, and fish shells.

### Installation

#### Bash

```bash
python -m app.cli --install-completion bash

# Or add to ~/.bashrc:

eval "$(_APP_CLI_COMPLETE=bash_source python -m app.cli)"
```

#### Zsh

```bash
python -m app.cli --install-completion zsh

# Or add to ~/.zshrc:

eval "$(_APP_CLI_COMPLETE=zsh_source python -m app.cli)"
```

#### Fish

```bash
python -m app.cli --install-completion fish

# Or add to ~/.config/fish/completions/app-cli.fish:

eval (env _APP_CLI_COMPLETE=fish_source python -m app.cli)
```

### Testing Completion

After installation, restart your shell and try:

```bash
python -m app.cli <TAB>
python -m app.cli user <TAB>
```

## Examples

### Common Workflows

#### 1. Check CLI Version

```bash
python -m app.cli --version
```

#### 2. Get Command Help

```bash

# Get general help

python -m app.cli --help

# Get help for specific command group

python -m app.cli user --help

# Get help for specific subcommand

python -m app.cli user example --help
```

#### 3. Using Configuration

```bash

# Create user config

cat > ~/.projectai.toml << EOF
[general]
log_level = "DEBUG"
verbose = true

[ai]
model = "gpt-4"
temperature = 0.8
EOF

# Config is automatically loaded

python -m app.cli ai example "gpt-4"
```

#### 4. Environment Overrides

```bash

# Override specific config values

PROJECTAI_AI_TEMPERATURE=0.9 python -m app.cli ai example "model"
```

## Troubleshooting

### CLI Not Found

If you get `ModuleNotFoundError`, ensure you're running from the project root:

```bash
cd /path/to/Project-AI
python -m app.cli --help
```

### Missing Dependencies

If you get import errors:

```bash
pip install -r requirements.txt
```

### Configuration Not Loading

Check file locations and permissions:

```bash

# Check if config exists

ls -la ~/.projectai.toml
ls -la .projectai.toml

# Verify TOML syntax

python -c "import tomllib; print(tomllib.load(open('.projectai.toml', 'rb')))"
```

### Shell Completion Not Working

1. Ensure completion is installed correctly
1. Restart your shell
1. Check shell-specific completion directories:
   - Bash: `~/.bash_completion.d/`
   - Zsh: `~/.zsh/completion/`
   - Fish: `~/.config/fish/completions/`

## Advanced Usage

### Scripting with the CLI

The CLI is designed to be script-friendly:

```bash

#!/bin/bash

# Example automation script

# Set error handling

set -e

# Configure via environment

export PROJECTAI_GENERAL_LOG_LEVEL=ERROR
export PROJECTAI_GENERAL_VERBOSE=false

# Run commands

python -m app.cli user example "script-user"
python -m app.cli memory example "script-memory"
```

### JSON Output (Future Feature)

Future versions may support JSON output for easier parsing:

```bash
python -m app.cli user example "name" --output json
```

### Batch Operations (Future Feature)

Future versions may support batch commands:

```bash
python -m app.cli batch --file commands.txt
```

## Related Documentation

- [CLI-CODEX.md](../../CLI-CODEX.md) - CLI development guidelines
- [commands.md](./commands.md) - Auto-generated command reference
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contributing to CLI development
- [README.md](../../README.md) - Main project documentation

## Getting Help

If you need help:

1. Check this documentation
1. Run `--help` on any command
1. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for development setup
1. Open an issue: [GitHub Issues](https://github.com/IAmSoThirsty/Project-AI/issues)
1. Join discussions: [GitHub Discussions](https://github.com/IAmSoThirsty/Project-AI/discussions)

______________________________________________________________________

**Note**: This documentation is for version 1.0.0. For the latest updates, see [CHANGELOG.md](../../CHANGELOG.md).
