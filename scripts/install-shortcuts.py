"""
Create Windows Desktop Shortcuts for Project-AI
This script creates shortcuts on the Windows desktop and Start Menu
"""

import json
import os
import sys
from pathlib import Path

try:
    import win32com.client
except ImportError:
    print("Installing required package: pywin32...")
    os.system("pip install pywin32 -q")
    import win32com.client


def get_app_root():
    """Get the Project-AI root directory"""
    return Path(__file__).parent.absolute()


def get_desktop_path():
    """Get Windows Desktop path"""
    from pathlib import Path

    return Path.home() / "Desktop"


def get_start_menu_path():
    """Get Windows Start Menu path"""
    from pathlib import Path

    appdata = (
        Path.home()
        / "AppData"
        / "Roaming"
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
    )
    return appdata


def create_shortcut(target, link_path, icon_path=None, description=""):
    """Create a Windows shortcut file (.lnk)"""
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(link_path))
        shortcut.Targetpath = str(target)
        shortcut.WorkingDirectory = str(target.parent)
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = str(icon_path)
        if description:
            shortcut.Description = description
        shortcut.save()
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


def install_desktop_shortcuts():
    """Install Project-AI shortcuts on desktop and Start Menu"""
    app_root = get_app_root()
    desktop_path = get_desktop_path()
    start_menu_path = get_start_menu_path()

    # Load app configuration
    config_file = app_root / "app-config.json"
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        return False

    try:
        with open(config_file) as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return False

    # Launcher script path
    launcher_bat = app_root / "launch-desktop.bat"
    if not launcher_bat.exists():
        print(f"Error: {launcher_bat} not found")
        return False

    # App icon path (if exists)
    icon_path = app_root / config["desktop"].get("icon", "assets/app-icon.ico")
    icon_path = str(icon_path) if icon_path.exists() else None

    # Create desktop shortcut
    desktop_link = desktop_path / "Project-AI.lnk"
    desktop_config = config.get("shortcuts", {}).get("desktop", {})

    print("Creating desktop shortcut...")
    if create_shortcut(
        launcher_bat,
        desktop_link,
        icon_path,
        desktop_config.get("description", "Project-AI Dashboard"),
    ):
        print(f"✓ Desktop shortcut created: {desktop_link}")
    else:
        print("✗ Failed to create desktop shortcut")
        return False

    # Create Start Menu folder
    start_menu_app_folder = start_menu_path / config["system"]["start_menu_folder"]
    start_menu_app_folder.mkdir(parents=True, exist_ok=True)

    # Create Start Menu shortcut
    start_menu_link = start_menu_app_folder / "Project-AI.lnk"
    print("Creating Start Menu shortcut...")
    if create_shortcut(
        launcher_bat,
        start_menu_link,
        icon_path,
        desktop_config.get("description", "Project-AI Dashboard"),
    ):
        print(f"✓ Start Menu shortcut created: {start_menu_link}")
    else:
        print("✗ Failed to create Start Menu shortcut")
        return False

    print("\n✓ All shortcuts installed successfully!")
    print(f"  Desktop: {desktop_link}")
    print(f"  Start Menu: {start_menu_link}")
    return True


def uninstall_desktop_shortcuts():
    """Remove Project-AI shortcuts"""
    desktop_path = get_desktop_path()
    start_menu_path = get_start_menu_path()
    app_root = get_app_root()

    # Load config
    config_file = app_root / "app-config.json"
    if not config_file.exists():
        print("Configuration not found")
        return False

    try:
        with open(config_file) as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading configuration: {e}")
        return False

    shortcuts_removed = []

    # Remove desktop shortcut
    desktop_link = desktop_path / "Project-AI.lnk"
    if desktop_link.exists():
        try:
            desktop_link.unlink()
            shortcuts_removed.append(f"Desktop: {desktop_link}")
        except Exception as e:
            print(f"Error removing desktop shortcut: {e}")

    # Remove Start Menu shortcut
    start_menu_app_folder = start_menu_path / config["system"]["start_menu_folder"]
    start_menu_link = start_menu_app_folder / "Project-AI.lnk"
    if start_menu_link.exists():
        try:
            start_menu_link.unlink()
            shortcuts_removed.append(f"Start Menu: {start_menu_link}")
        except Exception as e:
            print(f"Error removing Start Menu shortcut: {e}")

    if shortcuts_removed:
        print("✓ Shortcuts removed:")
        for shortcut in shortcuts_removed:
            print(f"  {shortcut}")
        return True
    else:
        print("No shortcuts found to remove")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "uninstall":
        print("Uninstalling Project-AI shortcuts...")
        uninstall_desktop_shortcuts()
    else:
        print("Installing Project-AI shortcuts...")
        if install_desktop_shortcuts():
            sys.exit(0)
        else:
            sys.exit(1)
