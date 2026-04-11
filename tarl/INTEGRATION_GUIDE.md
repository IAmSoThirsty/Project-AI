# T.A.R.L. Enhanced VM Integration Guide

## Overview

This guide explains how to integrate the Enhanced VM with the existing T.A.R.L. system.

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    T.A.R.L. System                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Compiler   │─────▶│  Enhanced VM │                    │
│  │   Frontend   │      │  (Register)  │                    │
│  └──────────────┘      └──────────────┘                    │
│         │                      │                            │
│         │                      │                            │
│         ▼                      ▼                            │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Bytecode   │      │     GC       │                    │
│  │   Generator  │      │ (Generational)│                    │
│  └──────────────┘      └──────────────┘                    │
│         │                      │                            │
│         │                      ▼                            │
│         │              ┌──────────────┐                    │
│         └─────────────▶│   Sandbox    │                    │
│                        │  (Capability) │                    │
│                        └──────────────┘                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Compiler Integration

The Enhanced VM can be integrated as an alternative execution backend:

```python
from tarl.system import TARLSystem
from tarl.vm_enhanced import create_enhanced_vm, Instruction, Opcode

class EnhancedRuntimeVM:
    """
    Adapter to integrate Enhanced VM with TARL system
    """
    
    def __init__(self, config, diagnostics, stdlib, ffi):
        self.config = config
        self.diagnostics = diagnostics
        self.stdlib = stdlib
        self.ffi = ffi
        
        # Create enhanced VM
        self.vm = create_enhanced_vm(
            enable_jit=config.get("runtime.enable_jit", True),
            enable_gc=config.get("runtime.enable_gc", True),
            enable_sandbox=config.get("runtime.enable_sandbox", True)
        )
        
        self._initialized = False
    
    def initialize(self):
        """Initialize runtime"""
        # Register native functions from stdlib
        for name, func in self.stdlib.builtins.items():
            self.vm.register_native(name, func)
        
        self._initialized = True
    
    def execute(self, bytecode: bytes, context: dict = None):
        """
        Execute bytecode
        
        Converts TARL bytecode to Enhanced VM format
        """
        if not self._initialized:
            raise RuntimeError("Runtime not initialized")
        
        # Convert bytecode format
        instructions, constants = self._convert_bytecode(bytecode)
        
        # Load program
        self.vm.load_program(instructions, constants)
        
        # Execute
        result = self.vm.execute()
        
        return {"status": "success", "result": result}
    
    def _convert_bytecode(self, bytecode: bytes):
        """
        Convert TARL bytecode to Enhanced VM format
        
        This is a simplified converter - production would need
        full bytecode translation
        """
        # Parse TARL bytecode header
        if not bytecode.startswith(b"TARL_BYTECODE_V1\x00"):
            raise ValueError("Invalid bytecode format")
        
        # Extract constants pool (simplified)
        constants = self._extract_constants(bytecode)
        
        # Convert instructions (simplified mapping)
        instructions = self._convert_instructions(bytecode)
        
        return instructions, constants
    
    def _extract_constants(self, bytecode: bytes):
        """Extract constants from bytecode"""
        # Simplified - real implementation would parse constant pool
        return []
    
    def _convert_instructions(self, bytecode: bytes):
        """Convert TARL instructions to Enhanced VM format"""
        instructions = []
        
        # Simplified mapping - real implementation would do full conversion
        # TARL opcode 0x01 (LOAD_CONST) -> Enhanced VM LOAD_CONST
        # TARL opcode 0x06 (ADD) -> Enhanced VM ADD (register-based)
        # etc.
        
        return instructions
    
    def get_status(self):
        """Get runtime status"""
        stats = self.vm.get_stats()
        return {
            "initialized": self._initialized,
            "vm_type": "enhanced_register_based",
            "stats": stats
        }
    
    def shutdown(self):
        """Shutdown runtime"""
        self.vm.shutdown()
        self._initialized = False
```

### 2. Using Enhanced VM in TARL System

```python
from tarl.system import TARLSystem
from tarl.vm_enhanced import create_enhanced_vm

# Option 1: Direct usage (standalone)
vm = create_enhanced_vm()
# ... load program and execute

# Option 2: Integrate with TARL system
system = TARLSystem()
system.initialize()

# Replace runtime with enhanced version
# system.runtime = EnhancedRuntimeVM(
#     system.config,
#     system.diagnostics,
#     system.stdlib,
#     system.ffi
# )

# Execute TARL code
result = system.execute_source("""
    pour "Hello from Enhanced VM!"
""")
```

### 3. Compiler Backend

To fully integrate, the compiler needs to emit register-based bytecode:

```python
class EnhancedCompilerBackend:
    """
    Compiler backend that generates Enhanced VM bytecode
    """
    
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.next_register = 0
    
    def allocate_register(self):
        """Allocate next available register"""
        reg = self.next_register
        self.next_register += 1
        return reg
    
    def emit_constant(self, value):
        """Add constant to pool"""
        self.constants.append(value)
        return len(self.constants) - 1
    
    def emit_load_const(self, value):
        """Emit LOAD_CONST instruction"""
        reg = self.allocate_register()
        const_idx = self.emit_constant(value)
        
        self.instructions.append(
            Instruction(Opcode.LOAD_CONST, dest=reg, immediate=const_idx)
        )
        return reg
    
    def emit_add(self, reg1, reg2):
        """Emit ADD instruction"""
        dest = self.allocate_register()
        self.instructions.append(
            Instruction(Opcode.ADD, dest=dest, src1=reg1, src2=reg2)
        )
        return dest
    
    def emit_return(self, reg):
        """Emit RETURN instruction"""
        self.instructions.append(
            Instruction(Opcode.RETURN, dest=reg)
        )
    
    def get_program(self):
        """Get compiled program"""
        return self.instructions, self.constants
```

### 4. Usage Example

Complete integration example:

```python
from tarl.vm_enhanced import create_enhanced_vm, Instruction, Opcode

# Compile TARL source to Enhanced VM bytecode
def compile_tarl_to_enhanced_vm(source: str):
    """
    Compile TARL source to Enhanced VM format
    
    Example for: pour 5 + 3
    """
    backend = EnhancedCompilerBackend()
    
    # Parse AST (simplified)
    # AST: BinaryOp(Add, Const(5), Const(3))
    
    # Emit instructions
    r0 = backend.emit_load_const(5)    # r0 = 5
    r1 = backend.emit_load_const(3)    # r1 = 3
    r2 = backend.emit_add(r0, r1)      # r2 = r0 + r1
    backend.emit_return(r2)            # return r2
    
    return backend.get_program()

# Create VM
vm = create_enhanced_vm(enable_jit=True, enable_gc=True)

# Compile and execute
instructions, constants = compile_tarl_to_enhanced_vm("pour 5 + 3")
vm.load_program(instructions, constants)
result = vm.execute()

print(f"Result: {result}")  # Result: 8
```

## Migration Strategy

### Phase 1: Parallel Deployment
- Run both stack-based and register-based VMs
- Compare results for correctness
- Benchmark performance differences

### Phase 2: Gradual Migration
- Migrate simple programs first
- Add register allocation to compiler
- Optimize bytecode generation

### Phase 3: Full Cutover
- Enhanced VM becomes default
- Legacy VM remains for compatibility
- Performance monitoring continues

## Performance Considerations

### When to Use Enhanced VM

**Best for:**
- Compute-intensive workloads
- Long-running processes
- Memory-intensive applications
- Security-critical code

**May not benefit:**
- Very short scripts
- I/O-bound operations
- Single-use executions

### Configuration

```python
# High-performance configuration
vm = create_enhanced_vm(
    enable_jit=True,      # JIT compilation
    enable_gc=True,       # Generational GC
    enable_sandbox=False  # Disable for max speed
)

# Security-focused configuration
vm = create_enhanced_vm(
    enable_jit=False,     # Deterministic execution
    enable_gc=True,       # Memory safety
    enable_sandbox=True   # Capability enforcement
)

# Balanced configuration (default)
vm = create_enhanced_vm(
    enable_jit=True,
    enable_gc=True,
    enable_sandbox=True
)
```

## Testing Integration

```python
import pytest
from tarl.vm_enhanced import create_enhanced_vm

def test_enhanced_vm_integration():
    """Test Enhanced VM with TARL compiler"""
    
    # Compile simple TARL program
    source = "pour 10 + 5"
    instructions, constants = compile_tarl_to_enhanced_vm(source)
    
    # Execute on Enhanced VM
    vm = create_enhanced_vm()
    vm.load_program(instructions, constants)
    result = vm.execute()
    
    assert result == 15

def test_gc_integration():
    """Test GC with TARL memory management"""
    
    vm = create_enhanced_vm(enable_gc=True)
    
    # Allocate objects
    # ... execute program ...
    
    stats = vm.get_stats()
    assert stats['gc']['total_objects'] > 0

def test_security_integration():
    """Test sandbox with TARL security model"""
    
    vm = create_enhanced_vm(enable_sandbox=True)
    
    # Execute with capability checks
    # ... execute program ...
    
    # Verify audit trail
    assert len(vm.sandbox.audit_log) > 0
```

## Monitoring and Debugging

```python
# Enable statistics collection
vm = create_enhanced_vm()

# Execute program
vm.execute()

# Get detailed stats
stats = vm.get_stats()

print(f"VM Stats: {stats['vm']}")
print(f"Execution: {stats['execution']}")
print(f"GC: {stats.get('gc', {})}")
print(f"Sandbox: {stats.get('sandbox', {})}")
```

## Best Practices

1. **Use register allocation**: Minimize memory operations
2. **Enable GC**: For long-running processes
3. **Profile first**: Measure before optimizing
4. **Test thoroughly**: Verify correctness
5. **Monitor performance**: Track metrics over time

## Troubleshooting

### Common Issues

**Issue**: Bytecode format mismatch
```
Solution: Ensure compiler generates Enhanced VM format
```

**Issue**: Out of registers
```
Solution: Increase num_registers or optimize allocation
```

**Issue**: GC pause times too high
```
Solution: Tune GC thresholds or use incremental collection
```

**Issue**: Capability denied
```
Solution: Grant required capabilities to sandbox context
```

## Conclusion

The Enhanced VM provides significant performance and security improvements while maintaining compatibility with the T.A.R.L. system through proper integration patterns.

For questions or issues, refer to:
- `VM_ENHANCED_README.md` - API documentation
- `ENHANCEMENT_SUMMARY.md` - Feature overview
- `demo_vm_enhanced.py` - Usage examples
- `test_vm_enhanced.py` - Test suite
