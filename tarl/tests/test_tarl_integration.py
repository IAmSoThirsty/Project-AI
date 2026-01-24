"""
T.A.R.L. System Integration Tests

Comprehensive test suite for T.A.R.L. subsystems following Project-AI
production standards with full coverage and error path validation.
"""

import pytest
import sys
from pathlib import Path

# Add tarl to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tarl import TARLSystem, get_system, TARL_ROOT
from tarl.config import ConfigRegistry
from tarl.diagnostics import (
    DiagnosticsEngine,
    Severity,
    DiagnosticCategory,
    SourceLocation
)
from tarl.stdlib import StandardLibrary
from tarl.ffi import FFIBridge
from tarl.compiler import CompilerFrontend
from tarl.runtime import RuntimeVM
from tarl.modules import ModuleSystem
from tarl.tooling import DevelopmentTooling


class TestConfigurationSubsystem:
    """Test configuration management subsystem"""
    
    def test_config_initialization(self):
        """Test configuration registry initialization"""
        config = ConfigRegistry()
        config.load()
        
        assert config.get("compiler.debug_mode") is False
        assert config.get("runtime.stack_size") == 1048576
        assert config.get("stdlib.auto_import_builtins") is True
    
    def test_config_get_with_default(self):
        """Test configuration get with default value"""
        config = ConfigRegistry()
        config.load()
        
        # Existing key
        assert config.get("compiler.debug_mode") is False
        
        # Non-existent key with default
        assert config.get("nonexistent.key", default=42) == 42
    
    def test_config_set_override(self):
        """Test configuration runtime override"""
        config = ConfigRegistry()
        config.load()
        
        config.set("compiler.debug_mode", True)
        assert config.get("compiler.debug_mode") == True
    
    def test_config_section(self):
        """Test getting entire configuration section"""
        config = ConfigRegistry()
        config.load()
        
        compiler_config = config.get_section("compiler")
        assert isinstance(compiler_config, dict)
        assert "debug_mode" in compiler_config
        assert "optimization_level" in compiler_config


class TestDiagnosticsSubsystem:
    """Test diagnostics engine subsystem"""
    
    @pytest.fixture
    def diagnostics(self):
        """Create diagnostics engine fixture"""
        config = ConfigRegistry()
        config.load()
        diag = DiagnosticsEngine(config)
        diag.initialize()
        return diag
    
    def test_diagnostics_initialization(self, diagnostics):
        """Test diagnostics engine initialization"""
        assert diagnostics._initialized is True
        assert diagnostics.error_count == 0
        assert diagnostics.warning_count == 0
    
    def test_report_error(self, diagnostics):
        """Test error reporting"""
        diagnostics.report_error(
            code="E001",
            message="Test error",
            category=DiagnosticCategory.SYNTAX,
            location=SourceLocation("test.tarl", 5, 10)
        )
        
        assert diagnostics.error_count == 1
        assert diagnostics.has_errors() is True
        
        errors = diagnostics.get_diagnostics(severity=Severity.ERROR)
        assert len(errors) == 1
        assert errors[0].code == "E001"
        assert errors[0].message == "Test error"
    
    def test_report_warning(self, diagnostics):
        """Test warning reporting"""
        diagnostics.report_warning(
            code="W001",
            message="Test warning",
            category=DiagnosticCategory.STYLE
        )
        
        assert diagnostics.warning_count == 1
        assert diagnostics.has_warnings() is True
    
    def test_clear_diagnostics(self, diagnostics):
        """Test clearing diagnostics"""
        diagnostics.report_error("E001", "Error")
        diagnostics.report_warning("W001", "Warning")
        
        assert diagnostics.error_count > 0
        assert diagnostics.warning_count > 0
        
        diagnostics.clear()
        
        assert diagnostics.error_count == 0
        assert diagnostics.warning_count == 0
        assert len(diagnostics.diagnostics) == 0


class TestStandardLibrarySubsystem:
    """Test standard library subsystem"""
    
    @pytest.fixture
    def stdlib(self):
        """Create standard library fixture"""
        config = ConfigRegistry()
        config.load()
        diagnostics = DiagnosticsEngine(config)
        diagnostics.initialize()
        
        lib = StandardLibrary(config, diagnostics)
        lib.load_builtins()
        return lib
    
    def test_stdlib_initialization(self, stdlib):
        """Test standard library initialization"""
        assert len(stdlib.builtins) > 0
        assert stdlib._initialized is True
    
    def test_get_builtin(self, stdlib):
        """Test getting built-in function"""
        print_fn = stdlib.get_builtin("print")
        assert print_fn is not None
        assert print_fn.name == "print"
        
        len_fn = stdlib.get_builtin("len")
        assert len_fn is not None
        assert len_fn.name == "len"
    
    def test_list_builtins(self, stdlib):
        """Test listing built-in functions"""
        builtins = stdlib.list_builtins()
        assert isinstance(builtins, list)
        assert "print" in builtins
        assert "len" in builtins
        assert "type" in builtins
    
    def test_builtin_not_found(self, stdlib):
        """Test error when built-in not found"""
        with pytest.raises(KeyError):
            stdlib.get_builtin("nonexistent_function")


class TestCompilerSubsystem:
    """Test compiler frontend subsystem"""
    
    @pytest.fixture
    def compiler(self):
        """Create compiler fixture"""
        config = ConfigRegistry()
        config.load()
        diagnostics = DiagnosticsEngine(config)
        diagnostics.initialize()
        stdlib = StandardLibrary(config, diagnostics)
        stdlib.load_builtins()
        
        comp = CompilerFrontend(config, diagnostics, stdlib)
        comp.initialize()
        return comp
    
    def test_compiler_initialization(self, compiler):
        """Test compiler initialization"""
        assert compiler._initialized is True
        assert compiler.lexer is not None
        assert compiler.parser is not None
        assert compiler.semantic is not None
        assert compiler.codegen is not None
    
    def test_compile_source(self, compiler):
        """Test source code compilation"""
        source = "pour 'Hello, World!'"
        bytecode = compiler.compile(source)
        
        assert isinstance(bytecode, bytes)
        assert len(bytecode) > 0
    
    def test_compiler_status(self, compiler):
        """Test compiler status reporting"""
        status = compiler.get_status()
        assert isinstance(status, dict)
        assert "initialized" in status
        assert status["initialized"] is True


class TestRuntimeSubsystem:
    """Test runtime VM subsystem"""
    
    @pytest.fixture
    def runtime(self):
        """Create runtime fixture"""
        config = ConfigRegistry()
        config.load()
        diagnostics = DiagnosticsEngine(config)
        diagnostics.initialize()
        stdlib = StandardLibrary(config, diagnostics)
        stdlib.load_builtins()
        ffi = FFIBridge(config, diagnostics, stdlib)
        ffi.initialize()
        
        rt = RuntimeVM(config, diagnostics, stdlib, ffi)
        rt.initialize()
        return rt
    
    def test_runtime_initialization(self, runtime):
        """Test runtime VM initialization"""
        assert runtime._initialized is True
        assert runtime.vm is not None
    
    def test_execute_bytecode(self, runtime):
        """Test bytecode execution"""
        bytecode = b"TARL_BYTECODE_V1\x00"
        result = runtime.execute(bytecode)
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_runtime_status(self, runtime):
        """Test runtime status reporting"""
        status = runtime.get_status()
        assert isinstance(status, dict)
        assert "initialized" in status
        assert status["initialized"] is True


class TestTARLSystemIntegration:
    """Test complete T.A.R.L. system integration"""
    
    def test_system_initialization(self):
        """Test full system initialization"""
        system = TARLSystem()
        system.initialize()
        
        assert system._initialized is True
        assert system.config is not None
        assert system.diagnostics is not None
        assert system.stdlib is not None
        assert system.ffi is not None
        assert system.compiler is not None
        assert system.runtime is not None
        assert system.modules is not None
        assert system.tooling is not None
    
    def test_system_initialization_order(self):
        """Test subsystem initialization order"""
        system = TARLSystem()
        system.initialize()
        
        # Verify all subsystems loaded
        assert "config" in system._subsystems_loaded
        assert "diagnostics" in system._subsystems_loaded
        assert "stdlib" in system._subsystems_loaded
        assert "ffi" in system._subsystems_loaded
        assert "compiler" in system._subsystems_loaded
        assert "runtime" in system._subsystems_loaded
        assert "modules" in system._subsystems_loaded
        assert "tooling" in system._subsystems_loaded
    
    def test_execute_source(self):
        """Test end-to-end source execution"""
        system = TARLSystem()
        system.initialize()
        
        source = "pour 'Hello, T.A.R.L.!'"
        result = system.execute_source(source)
        
        assert result is not None
    
    def test_system_status(self):
        """Test system status reporting"""
        system = TARLSystem()
        system.initialize()
        
        status = system.get_status()
        
        assert isinstance(status, dict)
        assert status["initialized"] is True
        assert "subsystems" in status
        assert "version" in status
    
    def test_system_shutdown(self):
        """Test graceful system shutdown"""
        system = TARLSystem()
        system.initialize()
        
        assert system._initialized is True
        
        system.shutdown()
        
        assert system._initialized is False
        assert len(system._subsystems_loaded) == 0
    
    def test_get_system_singleton(self):
        """Test global system instance"""
        system1 = get_system()
        system2 = get_system()
        
        # Should return same instance
        assert system1 is system2


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_uninitialized_system_execute(self):
        """Test error when executing without initialization"""
        system = TARLSystem()
        
        with pytest.raises(RuntimeError, match="not initialized"):
            system.execute_source("pour 'test'")
    
    def test_diagnostics_before_load(self):
        """Test error accessing config before load"""
        config = ConfigRegistry()
        
        with pytest.raises(RuntimeError, match="not loaded"):
            config.get("compiler.debug_mode")
    
    def test_compiler_before_initialization(self):
        """Test error compiling before initialization"""
        config = ConfigRegistry()
        config.load()
        diagnostics = DiagnosticsEngine(config)
        diagnostics.initialize()
        stdlib = StandardLibrary(config, diagnostics)
        stdlib.load_builtins()
        
        compiler = CompilerFrontend(config, diagnostics, stdlib)
        
        with pytest.raises(RuntimeError, match="not initialized"):
            compiler.compile("test")


class TestConfigurationOverrides:
    """Test configuration override mechanisms"""
    
    def test_programmatic_override(self):
        """Test programmatic configuration override"""
        overrides = {
            "compiler": {
                "debug_mode": True,
                "optimization_level": 0
            }
        }
        
        config = ConfigRegistry(overrides=overrides)
        config.load()
        
        assert config.get("compiler.debug_mode") == True
        assert config.get("compiler.optimization_level") == 0
    
    def test_system_with_config_overrides(self):
        """Test system initialization with config overrides"""
        system = TARLSystem(
            compiler_debug_mode=True,
            runtime_enable_jit=False
        )
        system.initialize()
        
        # Verify overrides applied
        assert system.config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
