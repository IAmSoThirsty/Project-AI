<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / DESKTOP_APP_README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / DESKTOP_APP_README.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->
# Project-AI Desktop Application

Welcome to **Project-AI**, an advanced AI dashboard with command override and memory expansion capabilities.

## Quick Start

### Option 1: Automatic Setup (Recommended)

1. **Double-click** `setup-desktop.bat` in the Project-AI folder
1. The setup will:
   - Check for Python 3.11+
   - Create a virtual environment
   - Install all dependencies
   - Launch the application
1. Follow the on-screen prompts

### Option 2: Manual Launch

1. **Double-click** `launch-desktop.bat` to run the application

### Option 3: PowerShell Launch

1. Right-click `launch-desktop.ps1`
1. Select "Run with PowerShell"

## Creating Desktop Shortcuts

After the first successful launch, you can create desktop and Start Menu shortcuts:

```powershell
python install-shortcuts.py
```

This creates:

- **Desktop Shortcut**: Quick access icon on your desktop
- **Start Menu Entry**: Find Project-AI in Windows Start Menu

To remove shortcuts later:

```powershell
python install-shortcuts.py uninstall
```

## System Requirements

- **Windows 7** or later (Windows 10/11 recommended)
- **Python 3.11+** (download from [python.org](https://www.python.org/downloads/))
- **4GB RAM** (8GB recommended)
- **500MB** free disk space for installation

## Features

### 🔐 Command Override System

- Master password protection
- Control 10 safety protocols
- Individual or master override
- Complete audit logging
- Emergency lockdown capability

### 🧠 Memory Expansion System

- Persistent AI memory
- Conversation storage
- Autonomous learning
- Knowledge base building
- Semantic search

### 📊 Additional Features

- Learning paths management
- Data analysis tools
- Security resources
- Location tracking
- Emergency alerts

## Troubleshooting

### "Python not found"

**Solution**: Install Python from [python.org](https://www.python.org/downloads/) and add it to PATH

### "Module not found" errors

**Solution**: Run `setup-desktop.bat` again to install/update dependencies

### Application won't start

**Solution**:

1. Check that you have administrator privileges
1. Run `setup-desktop.bat` to repair the installation
1. Check the console output for specific errors

### Shortcuts not created

**Solution**:

1. Run Command Prompt as Administrator
1. Navigate to Project-AI folder
1. Run: `python install-shortcuts.py`

## File Structure

```txt
Project-AI/
├── launch-desktop.bat          # Quick launch script
├── launch-desktop.ps1          # PowerShell launcher
├── setup-desktop.bat           # Full setup script
├── install-shortcuts.py        # Create desktop shortcuts
├── app-config.json             # Application configuration
├── src/
│   └── app/
│       ├── main.py            # Application entry point
│       ├── gui/
│       │   └── dashboard.py    # Main dashboard UI
│       └── core/               # Core systems
└── requirements.txt            # Python dependencies
```

## Configuration

Edit `app-config.json` to customize:

- Application name and version
- Auto-start settings
- Default features
- Icon and display properties

## Getting Help

- **Documentation**: See `README.md` in the main folder
- **Issues**: Report on [GitHub](https://github.com/IAmSoThirsty/Project-AI/issues)
- **Security Issues**: See `SECURITY.md`

## License

Project-AI is licensed under the MIT License. See `LICENSE` for details.

## Privacy & Security

- All data is stored locally on your machine
- No telemetry or tracking
- Command override actions are logged for audit purposes
- See `SECURITY.md` for detailed security information

______________________________________________________________________

**Version**: 1.0.0 **Last Updated**: November 28, 2025 **Status**: Production Ready ✓
