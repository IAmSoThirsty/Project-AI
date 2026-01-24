"""
T.A.R.L. (Thirsty's Active Resistance Language) - Monolithic Root Package

This is the sovereign entry point for the T.A.R.L. language implementation.
All subsystems are integrated through this monolithic root module following
Project-AI's production-grade, config-driven architecture standards.

Architecture:
    - Zero circular dependencies
    - Strict subsystem boundaries
    - Canonical interface methods
    - Configuration-driven initialization
    - Full observability and diagnostics

Subsystems:
    - compiler: Frontend compilation pipeline (lexer, parser, AST, semantic)
    - runtime: VM execution engine (bytecode VM, interpreter, JIT)
    - stdlib: Core standard library (built-ins, collections, I/O, networking)
    - modules: Module and package system (import resolution, package manager)
    - diagnostics: Error reporting and code quality (errors, warnings, linter)
    - ffi: Foreign Function Interface (C/Python bindings, bridge)
    - config: Configuration management (loader, validator, environment)
    - tooling: Development tools (LSP, build system, REPL, debugger)

License: MIT
Copyright: (c) 2026 Project-AI Team
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Version information
__version__ = "1.0.0"
__author__ = "Project-AI Team"
__license__ = "MIT"

# Establish logger
logger = logging.getLogger(__name__)

# Root directory for T.A.R.L. subsystems
TARL_ROOT = Path(__file__).parent.absolute()


class TARLSystem:
    """
    Monolithic T.A.R.L. System Controller
    
    This class serves as the central integration point for all T.A.R.L. subsystems.
    It enforces strict initialization order, validates subsystem contracts, and
    provides canonical access patterns for cross-subsystem communication.
    
    Attributes:
        config: Configuration registry instance
        compiler: Compiler frontend subsystem
        runtime: VM runtime subsystem
        stdlib: Standard library subsystem
        modules: Module system subsystem
        diagnostics: Diagnostics subsystem
        ffi: Foreign function interface subsystem
        tooling: Development tooling subsystem
        
    Example:
        >>> from tarl import TARLSystem
        >>> system = TARLSystem(config_path="config/tarl.toml")
        >>> system.initialize()
        >>> result = system.execute_source("pour 'Hello, T.A.R.L.!'")
    """
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        """
        Initialize T.A.R.L. system controller
        
        Args:
            config_path: Path to configuration file (defaults to config/tarl.toml)
            **kwargs: Additional configuration overrides
        """
        self.config_path = config_path or str(TARL_ROOT / "config" / "tarl.toml")
        self.config_overrides = kwargs
        
        # Subsystem references (initialized in strict order)
        self.config = None
        self.diagnostics = None
        self.stdlib = None
        self.ffi = None
        self.compiler = None
        self.runtime = None
        self.modules = None
        self.tooling = None
        
        # System state
        self._initialized = False
        self._subsystems_loaded = {}
        
        logger.info(
            "T.A.R.L. System initialized",
            extra={
                "version": __version__,
                "root": str(TARL_ROOT),
                "config_path": self.config_path
            }
        )
    
    def initialize(self) -> None:
        """
        Initialize all T.A.R.L. subsystems in strict dependency order
        
        Initialization order enforces zero circular dependencies:
        1. Configuration (no dependencies)
        2. Diagnostics (config only)
        3. Standard Library (config, diagnostics)
        4. FFI Bridge (config, diagnostics, stdlib)
        5. Compiler Frontend (all above)
        6. Runtime VM (all above)
        7. Module System (all above)
        8. Development Tooling (all subsystems)
        
        Raises:
            RuntimeError: If initialization fails or subsystem contracts violated
        """
        if self._initialized:
            logger.warning("T.A.R.L. system already initialized")
            return
        
        try:
            logger.info("Beginning T.A.R.L. subsystem initialization sequence")
            
            # Phase 1: Configuration
            self._initialize_config()
            
            # Phase 2: Diagnostics
            self._initialize_diagnostics()
            
            # Phase 3: Standard Library
            self._initialize_stdlib()
            
            # Phase 4: FFI Bridge
            self._initialize_ffi()
            
            # Phase 5: Compiler Frontend
            self._initialize_compiler()
            
            # Phase 6: Runtime VM
            self._initialize_runtime()
            
            # Phase 7: Module System
            self._initialize_modules()
            
            # Phase 8: Development Tooling
            self._initialize_tooling()
            
            self._initialized = True
            logger.info(
                "T.A.R.L. system fully initialized",
                extra={"subsystems": list(self._subsystems_loaded.keys())}
            )
            
        except Exception as e:
            logger.error(f"T.A.R.L. initialization failed: {e}", exc_info=True)
            raise RuntimeError(f"Failed to initialize T.A.R.L. system: {e}") from e
    
    def _initialize_config(self) -> None:
        """Initialize configuration subsystem"""
        from tarl.config import ConfigRegistry
        
        self.config = ConfigRegistry(
            config_path=self.config_path,
            overrides=self.config_overrides
        )
        self.config.load()
        self._subsystems_loaded["config"] = True
        logger.info("Configuration subsystem initialized")
    
    def _initialize_diagnostics(self) -> None:
        """Initialize diagnostics subsystem"""
        from tarl.diagnostics import DiagnosticsEngine
        
        self.diagnostics = DiagnosticsEngine(config=self.config)
        self.diagnostics.initialize()
        self._subsystems_loaded["diagnostics"] = True
        logger.info("Diagnostics subsystem initialized")
    
    def _initialize_stdlib(self) -> None:
        """Initialize standard library subsystem"""
        from tarl.stdlib import StandardLibrary
        
        self.stdlib = StandardLibrary(
            config=self.config,
            diagnostics=self.diagnostics
        )
        self.stdlib.load_builtins()
        self._subsystems_loaded["stdlib"] = True
        logger.info("Standard library subsystem initialized")
    
    def _initialize_ffi(self) -> None:
        """Initialize FFI bridge subsystem"""
        from tarl.ffi import FFIBridge
        
        self.ffi = FFIBridge(
            config=self.config,
            diagnostics=self.diagnostics,
            stdlib=self.stdlib
        )
        self.ffi.initialize()
        self._subsystems_loaded["ffi"] = True
        logger.info("FFI bridge subsystem initialized")
    
    def _initialize_compiler(self) -> None:
        """Initialize compiler frontend subsystem"""
        from tarl.compiler import CompilerFrontend
        
        self.compiler = CompilerFrontend(
            config=self.config,
            diagnostics=self.diagnostics,
            stdlib=self.stdlib
        )
        self.compiler.initialize()
        self._subsystems_loaded["compiler"] = True
        logger.info("Compiler frontend subsystem initialized")
    
    def _initialize_runtime(self) -> None:
        """Initialize runtime VM subsystem"""
        from tarl.runtime import RuntimeVM
        
        self.runtime = RuntimeVM(
            config=self.config,
            diagnostics=self.diagnostics,
            stdlib=self.stdlib,
            ffi=self.ffi
        )
        self.runtime.initialize()
        self._subsystems_loaded["runtime"] = True
        logger.info("Runtime VM subsystem initialized")
    
    def _initialize_modules(self) -> None:
        """Initialize module system subsystem"""
        from tarl.modules import ModuleSystem
        
        self.modules = ModuleSystem(
            config=self.config,
            diagnostics=self.diagnostics,
            compiler=self.compiler,
            runtime=self.runtime
        )
        self.modules.initialize()
        self._subsystems_loaded["modules"] = True
        logger.info("Module system subsystem initialized")
    
    def _initialize_tooling(self) -> None:
        """Initialize development tooling subsystem"""
        from tarl.tooling import DevelopmentTooling
        
        self.tooling = DevelopmentTooling(
            config=self.config,
            diagnostics=self.diagnostics,
            compiler=self.compiler,
            runtime=self.runtime,
            modules=self.modules
        )
        self.tooling.initialize()
        self._subsystems_loaded["tooling"] = True
        logger.info("Development tooling subsystem initialized")
    
    def execute_source(self, source: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute T.A.R.L. source code
        
        Args:
            source: Source code string
            context: Optional execution context
            
        Returns:
            Execution result
            
        Raises:
            RuntimeError: If system not initialized
        """
        if not self._initialized:
            raise RuntimeError("T.A.R.L. system not initialized. Call initialize() first.")
        
        # Compile source to bytecode
        bytecode = self.compiler.compile(source)
        
        # Execute in runtime VM
        result = self.runtime.execute(bytecode, context=context)
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Returns:
            Dictionary with status of all subsystems
        """
        return {
            "initialized": self._initialized,
            "version": __version__,
            "root": str(TARL_ROOT),
            "subsystems": self._subsystems_loaded,
            "config_path": self.config_path,
            "diagnostics_status": self.diagnostics.get_status() if self.diagnostics else None,
            "compiler_status": self.compiler.get_status() if self.compiler else None,
            "runtime_status": self.runtime.get_status() if self.runtime else None,
        }
    
    def shutdown(self) -> None:
        """Graceful shutdown of all subsystems"""
        if not self._initialized:
            return
        
        logger.info("Shutting down T.A.R.L. system")
        
        # Shutdown in reverse initialization order
        if self.tooling:
            self.tooling.shutdown()
        if self.modules:
            self.modules.shutdown()
        if self.runtime:
            self.runtime.shutdown()
        if self.compiler:
            self.compiler.shutdown()
        if self.ffi:
            self.ffi.shutdown()
        if self.stdlib:
            self.stdlib.shutdown()
        if self.diagnostics:
            self.diagnostics.shutdown()
        if self.config:
            self.config.shutdown()
        
        self._initialized = False
        self._subsystems_loaded.clear()
        
        logger.info("T.A.R.L. system shutdown complete")


# Module-level convenience instance
_system_instance: Optional[TARLSystem] = None


def get_system(config_path: Optional[str] = None, **kwargs) -> TARLSystem:
    """
    Get or create global T.A.R.L. system instance
    
    Args:
        config_path: Optional configuration path
        **kwargs: Configuration overrides
        
    Returns:
        Global TARLSystem instance
    """
    global _system_instance
    
    if _system_instance is None:
        _system_instance = TARLSystem(config_path=config_path, **kwargs)
    
    return _system_instance


# Public API exports
__all__ = [
    "TARLSystem",
    "get_system",
    "__version__",
    "TARL_ROOT",
]
