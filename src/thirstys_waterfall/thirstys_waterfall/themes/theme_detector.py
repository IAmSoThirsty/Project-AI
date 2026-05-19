"""System Theme Detector"""

import logging
import platform


class SystemThemeDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.os_name = platform.system()

    def detect_system_theme(self):
        try:
            if self.os_name == "Windows":
                return self._detect_windows()
            elif self.os_name == "Darwin":
                return self._detect_macos()
            else:
                return "dark"
        except Exception:
            return "dark"

    def _detect_windows(self):
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception:
            return "dark"

    def _detect_macos(self):
        import subprocess

        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            return "dark" if "Dark" in result.stdout else "light"
        except Exception:
            return "light"
