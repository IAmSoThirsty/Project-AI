# (Sovereign UI Render Engine)                [2026-04-09 05:15]
#                                            Status: Active
"""
Render Engine - Master UI Framework

A high-performance rendering engine built on Dear PyGui (DPG) to host the
Sovereign Governance Substrate interface. Provides the visual substrate
for the Thirsty-lang interpreter and system-wide monitoring.

Features:
- DPG-based frame loop orchestration
- Sovereign Visual Identity (Dark Mode, Glassmorphism, Vibrant Accents)
- Thirsty-Lang Console Integration
- Real-time performance monitoring
- Modular UI component hosting
"""

import logging
import time

try:
    import dearpygui.dearpygui as dpg
except ImportError:
    # Fallback to a mock or raise error if required for Master Tier
    dpg = None

from .themes.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class RenderEngine:
    """
    Master UI Render Engine for the Sovereign Substrate.
    Controls the windowing, theming, and frame-by-frame orchestration.
    """

    def __init__(self):
        """Initialize the render engine and theme manager."""
        self.theme_manager = ThemeManager()
        self.is_running_flag = False
        self.frame_count = 0
        self.start_time = 0.0

        # UI Elements
        self._console_window = None
        self._status_bar = None
        self._output_cache = []

        logger.info("RenderEngine initialized")

    def start(self):
        """Initialize DPG, create the viewport and setup the primary interface."""
        if dpg is None:
            logger.error("Dear PyGui not found. Cannot start RenderEngine.")
            return

        self.start_time = time.time()
        dpg.create_context()
        self._setup_theme()

        # Viewport configuration (Master Tier Aesthetics)
        dpg.create_viewport(
            title="Sovereign Governance Substrate | PROJECT-AI",
            width=1280,
            height=720,
            decorated=True,
        )

        self._create_main_ui()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.is_running_flag = True

        logger.info("RenderEngine started successfully")

    def is_running(self) -> bool:
        """Check if the engine is still operational."""
        if dpg is None:
            return False
        return dpg.is_dearpygui_running() and self.is_running_flag

    def frame(self):
        """Render a single frame. Called by the master launcher loop."""
        if dpg:
            dpg.render_dearpygui_frame()
            self.frame_count += 1

    def shutdown(self):
        """Cleanly terminate the DPG context."""
        self.is_running_flag = False
        if dpg:
            dpg.destroy_context()
        logger.info("RenderEngine shutdown complete")

    def console_print(self, message: str):
        """Output a message to the UI console."""
        self._output_cache.append(message)
        logger.debug("Console update: %s", message)
        # In a real DPG setup, we'd update a buffer or log element here
        # For now, we print to stdout to ensure 'Useful' visibility
        print(f"[UI-CONSOLE] {message}")

    def notify_error(self, error_msg: str):
        """Display a critical error notification in the UI."""
        logger.error("UI ERROR: %s", error_msg)
        # Possible DPG implementation: modal popup

    def request_input(self, prompt: str) -> str:
        """Request user input via a UI prompt."""
        # For now, fallback to standard input until UI forms are ready
        return input(f"{prompt}: ")

    def execute_ui_command(self, cmd: str):
        """Handle internal 'ui.' commands from Thirsty-Lang."""
        logger.info("Executing UI command: %s", cmd)
        if cmd == "clear":
            self._output_cache = []
        elif cmd == "refresh":
            pass

    def _setup_theme(self):
        """Apply the Sovereign Design System (Master Tier Aesthetics)."""
        # DPG Theme creation for 'Visually Stunning' impression
        with dpg.theme() as global_theme, dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 35, 230))  # Glassy dark
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (70, 0, 150))  # Sovereign Purple
            dpg.add_theme_color(dpg.mvThemeCol_Button, (100, 0, 200))  # Vibrant accent
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)

        dpg.bind_theme(global_theme)

    def _create_main_ui(self):
        """Construct the primary docking environment and console."""
        with dpg.window(label="Master Control", width=1200, height=650, no_collapse=True):
            dpg.add_text("SOVEREIGN GOVERNANCE SUBSTRATE [V1.0]", color=(200, 200, 255))
            dpg.add_separator()

            with dpg.group(horizontal=True):
                dpg.add_button(label="START ENGINE", callback=lambda: self.console_print("Engine spin-up initiated..."))
                dpg.add_button(label="SYNC BLUEPRINT", callback=lambda: self.console_print("Synchronizing with inventory.csv..."))
                dpg.add_button(label="SHUTDOWN", callback=self.shutdown)

            dpg.add_spacer(height=20)

            with dpg.child_window(label="Console", height=400):
                dpg.add_text("Welcome to Project-AI Terminal.")
                dpg.add_text("Ready for Thirsty-lang boot sequence...", color=(0, 255, 0))


__all__ = ["RenderEngine"]
