"""Theme Manager"""
import logging

class ThemeManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._current_theme = 'default'  # default/light/dark
        self.themes = {
            'light': {'background': '#FFFFFF', 'foreground': '#000000'},
            'dark': {'background': '#1E1E1E', 'foreground': '#FFFFFF'}
        }

    def set_theme(self, theme):
        self._current_theme = theme
        self.logger.info(f"Theme set to: {theme}")

    def get_effective_theme(self):
        if self._current_theme == 'default':
            from .theme_detector import SystemThemeDetector
            detector = SystemThemeDetector()
            return detector.detect_system_theme()
        return self._current_theme

    def get_theme_colors(self):
        effective = self.get_effective_theme()
        if effective == 'default':
            effective = 'dark'
        return self.themes.get(effective, self.themes['dark'])
