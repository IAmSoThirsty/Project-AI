"""
T.A.R.L. Main System Controller

Production-grade system controller that orchestrates all T.A.R.L. subsystems:
- Configuration
- Diagnostics
- Standard Library
- FFI Bridge
- Compiler
- Runtime VM
- Module System
- Development Tooling

This module provides the main entry point for the complete T.A.R.L. system.

Example:
    >>> from tarl import TARLSystem, get_system
    >>> system = TARLSystem()
    >>> system.initialize()
    >>> result = system.execute_source("pour 'Hello, T.A.R.L.!'")
    >>> system.shutdown()
"""

import logging
from typing import Any, Dict, Optional

from tarl.compiler import CompilerFrontend
from tarl.config import ConfigRegistry
from tarl.diagnostics import DiagnosticsEngine
from tarl.ffi import FFIBridge
from tarl.modules import ModuleSystem
from tarl.runtime import RuntimeVM
from tarl.stdlib import StandardLibrary
from tarl.tooling import DevelopmentTooling

logger = logging.getLogger(__name__)


class TARLSystem:
    """
    Main T.A.R.L. System Controller

    Manages lifecycle and coordination of all T.A.R.L. subsystems.
    Provides the primary interface for T.A.R.L. compilation and execution.

    Architecture:
        1. Config Registry (foundation)
        2. Diagnostics Engine (error reporting)
        3. Standard Library (built-ins)
        4. FFI Bridge (foreign functions)
        5. Compiler Frontend (source → bytecode)
        6. Runtime VM (bytecode execution)
        7. Module System (imports)
        8. Development Tooling (LSP, REPL, debugger)

    Example:
        >>> system = TARLSystem()
        >>> system.initialize()
        >>> result = system.execute_source("pour 'Hello!'")
        >>> status = system.get_status()
        >>> system.shutdown()
    """

    VERSION = "1.0.0"

    def __init__(
        self,
        config_path: Optional[str] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Initialize T.A.R.L. system

        Args:
            config_path: Path to configuration file
            config_overrides: Configuration overrides
            **kwargs: Additional configuration overrides (e.g., compiler_debug_mode=True)
        """
        # Build config overrides from kwargs
        overrides = config_overrides or {}

        # Convert flat kwargs to nested config structure
        for key, value in kwargs.items():
            if "_" in key:
                parts = key.split("_", 1)
                section = parts[0]
                option = parts[1]
                if section not in overrides:
                    overrides[section] = {}
                overrides[section][option] = value

        # Initialize subsystems (created but not initialized)
        self.config: Optional[ConfigRegistry] = None
        self.diagnostics: Optional[DiagnosticsEngine] = None
        self.stdlib: Optional[StandardLibrary] = None
        self.ffi: Optional[FFIBridge] = None
        self.compiler: Optional[CompilerFrontend] = None
        self.runtime: Optional[RuntimeVM] = None
        self.modules: Optional[ModuleSystem] = None
        self.tooling: Optional[DevelopmentTooling] = None

        # System state
        self._initialized = False
        self._subsystems_loaded: list[str] = []
        self._config_path = config_path
        self._config_overrides = overrides

        logger.info("TARLSystem created")

    def initialize(self) -> None:
        """
        Initialize all T.A.R.L. subsystems

        Initialization order is critical and follows dependency hierarchy:
        1. Config (no dependencies)
        2. Diagnostics (depends on config)
        3. Stdlib (depends on config, diagnostics)
        4. FFI (depends on config, diagnostics, stdlib)
        5. Compiler (depends on config, diagnostics, stdlib)
        6. Runtime (depends on config, diagnostics, stdlib, ffi)
        7. Modules (depends on config, diagnostics, compiler, runtime)
        8. Tooling (depends on config, diagnostics, compiler, runtime, modules)
        """
        if self._initialized:
            logger.warning("System already initialized")
            return

        logger.info("Initializing T.A.R.L. system...")

        try:
            # 1. Configuration Registry
            self.config = ConfigRegistry(
                config_path=self._config_path, overrides=self._config_overrides
            )
            self.config.load()
            self._subsystems_loaded.append("config")
            logger.info("✓ Configuration loaded")

            # 2. Diagnostics Engine
            self.diagnostics = DiagnosticsEngine(self.config)
            self.diagnostics.initialize()
            self._subsystems_loaded.append("diagnostics")
            logger.info("✓ Diagnostics initialized")

            # 3. Standard Library
            self.stdlib = StandardLibrary(self.config, self.diagnostics)
            self.stdlib.load_builtins()
            self._subsystems_loaded.append("stdlib")
            logger.info("✓ Standard library loaded")

            # 4. FFI Bridge
            self.ffi = FFIBridge(self.config, self.diagnostics, self.stdlib)
            self.ffi.initialize()
            self._subsystems_loaded.append("ffi")
            logger.info("✓ FFI bridge initialized")

            # 5. Compiler Frontend
            self.compiler = CompilerFrontend(
                self.config, self.diagnostics, self.stdlib
            )
            self.compiler.initialize()
            self._subsystems_loaded.append("compiler")
            logger.info("✓ Compiler initialized")

            # 6. Runtime VM
            self.runtime = RuntimeVM(
                self.config, self.diagnostics, self.stdlib, self.ffi
            )
            self.runtime.initialize()
            self._subsystems_loaded.append("runtime")
            logger.info("✓ Runtime VM initialized")

            # 7. Module System
            self.modules = ModuleSystem(
                self.config, self.diagnostics, self.compiler, self.runtime
            )
            self.modules.initialize()
            self._subsystems_loaded.append("modules")
            logger.info("✓ Module system initialized")

            # 8. Development Tooling
            self.tooling = DevelopmentTooling(
                self.config, self.diagnostics, self.compiler, self.runtime, self.modules
            )
            self.tooling.initialize()
            self._subsystems_loaded.append("tooling")
            logger.info("✓ Development tooling initialized")

            self._initialized = True
            logger.info(f"T.A.R.L. System v{self.VERSION} initialized successfully")

        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            # Cleanup partially initialized subsystems
            self._cleanup_subsystems()
            raise RuntimeError(f"T.A.R.L. system initialization failed: {e}") from e

    def execute_source(self, source: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Compile and execute T.A.R.L. source code

        Args:
            source: T.A.R.L. source code string
            context: Optional execution context (globals)

        Returns:
            Execution result

        Raises:
            RuntimeError: If system not initialized or execution fails
        """
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        try:
            # Compile source to bytecode
            logger.debug("Compiling source code...")
            bytecode = self.compiler.compile(source)

            # Execute bytecode
            logger.debug("Executing bytecode...")
            result = self.runtime.execute(bytecode, context=context)

            return result

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            # Log diagnostics if available
            if self.diagnostics and self.diagnostics.has_errors():
                logger.error("Diagnostics:\n" + self.diagnostics.format_all())
            raise

    def compile_source(self, source: str) -> bytes:
        """
        Compile T.A.R.L. source to bytecode without executing

        Args:
            source: T.A.R.L. source code

        Returns:
            Compiled bytecode

        Raises:
            RuntimeError: If system not initialized or compilation fails
        """
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self.compiler.compile(source)

    def execute_bytecode(self, bytecode: bytes, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute pre-compiled T.A.R.L. bytecode

        Args:
            bytecode: Compiled T.A.R.L. bytecode
            context: Optional execution context

        Returns:
            Execution result

        Raises:
            RuntimeError: If system not initialized
        """
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")

        return self.runtime.execute(bytecode, context=context)

    def get_status(self) -> Dict[str, Any]:
        """
        Get system status

        Returns:
            Dictionary with system status information
        """
        status = {
            "version": self.VERSION,
            "initialized": self._initialized,
            "subsystems": self._subsystems_loaded.copy(),
        }

        if self._initialized:
            status.update(
                {
                    "config": self.config.get_section("compiler") if self.config else {},
                    "diagnostics": (
                        self.diagnostics.get_status() if self.diagnostics else {}
                    ),
                    "stdlib_builtins": (
                        len(self.stdlib.builtins) if self.stdlib else 0
                    ),
                    "compiler": self.compiler.get_status() if self.compiler else {},
                    "runtime": self.runtime.get_status() if self.runtime else {},
                }
            )

        return status

    def shutdown(self) -> None:
        """
        Shutdown T.A.R.L. system

        Cleanly shuts down all subsystems in reverse initialization order.
        """
        if not self._initialized:
            logger.warning("System not initialized, nothing to shutdown")
            return

        logger.info("Shutting down T.A.R.L. system...")

        self._cleanup_subsystems()

        self._initialized = False
        logger.info("T.A.R.L. system shutdown complete")

    def _cleanup_subsystems(self) -> None:
        """Cleanup all subsystems in reverse order"""
        # Reverse order of initialization
        if "tooling" in self._subsystems_loaded and self.tooling:
            self.tooling.shutdown()
            logger.info("✓ Tooling shutdown")

        if "modules" in self._subsystems_loaded and self.modules:
            self.modules.shutdown()
            logger.info("✓ Modules shutdown")

        if "runtime" in self._subsystems_loaded and self.runtime:
            self.runtime.shutdown()
            logger.info("✓ Runtime shutdown")

        if "compiler" in self._subsystems_loaded and self.compiler:
            self.compiler.shutdown()
            logger.info("✓ Compiler shutdown")

        if "ffi" in self._subsystems_loaded and self.ffi:
            self.ffi.shutdown()
            logger.info("✓ FFI shutdown")

        if "stdlib" in self._subsystems_loaded and self.stdlib:
            self.stdlib.shutdown()
            logger.info("✓ Stdlib shutdown")

        if "diagnostics" in self._subsystems_loaded and self.diagnostics:
            self.diagnostics.shutdown()
            logger.info("✓ Diagnostics shutdown")

        if "config" in self._subsystems_loaded and self.config:
            self.config.shutdown()
            logger.info("✓ Config shutdown")

        self._subsystems_loaded.clear()


# Global system instance for singleton pattern
_global_system: Optional[TARLSystem] = None


def get_system() -> TARLSystem:
    """
    Get global T.A.R.L. system instance (singleton)

    Returns:
        Global TARLSystem instance

    Example:
        >>> system = get_system()
        >>> if not system._initialized:
        ...     system.initialize()
    """
    global _global_system

    if _global_system is None:
        _global_system = TARLSystem()

    return _global_system


# Public API
__all__ = ["TARLSystem", "get_system"]
