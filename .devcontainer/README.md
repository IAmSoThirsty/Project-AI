# DevContainer Configuration

This directory contains the GitHub Codespaces and VS Code Dev Containers configuration for Project-AI.

## What's Included

- **Python 3.12**: Matches the project's Python version requirement
- **Node.js 18**: For frontend tooling and package management
- **VS Code Extensions**: Pre-configured extensions for Python development, including:
  - Python language support with Pylance
  - Ruff linter
  - Black formatter
  - Jupyter notebooks
  - GitHub Copilot

## Files

- `devcontainer.json`: Main configuration file for the development container
- `postCreateCommand.sh`: Script that runs after the container is created to set up the environment

## Usage

### GitHub Codespaces

1. Navigate to the repository on GitHub
1. Click the "Code" button
1. Select "Create codespace on main"
1. Wait for the environment to build (first time takes ~5 minutes)

### VS Code Dev Containers

1. Install the "Dev Containers" extension in VS Code
1. Open the project folder
1. Press F1 and select "Dev Containers: Reopen in Container"
1. Wait for the environment to build

## Post-Setup

After the container is created:

1. Copy `.env.example` to `.env` (done automatically)
1. Add your API keys to `.env`:

   ```bash
   OPENAI_API_KEY=sk-...
   HUGGINGFACE_API_KEY=hf_...
   FERNET_KEY=<generated_key>
   ```

1. Generate a Fernet key if needed:

   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

## Running the Application

```bash

# Desktop application (PyQt6)

python -m src.app.main

# Run tests

pytest -v

# Lint code

ruff check .
```

## Ports

The devcontainer forwards these ports:

- **5000**: Flask backend (if running web version)
- **8000**: Web frontend (if running web version)

## Customization

You can customize the devcontainer by modifying `devcontainer.json`:

- Add more VS Code extensions
- Install additional system packages
- Change Python or Node.js versions
- Modify environment variables

## Troubleshooting

### Container Build Fails

If the container fails to build:

1. Check your internet connection
1. Try rebuilding: F1 → "Dev Containers: Rebuild Container"
1. Check the build logs for specific errors

### Missing Dependencies

If dependencies are missing after container creation:

```bash
pip install -r requirements.txt
npm install
```

### Permission Issues

If you encounter permission issues with files:

```bash
sudo chown -R vscode:vscode /workspaces/Project-AI
```

## Learn More

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Specification](https://containers.dev/)
