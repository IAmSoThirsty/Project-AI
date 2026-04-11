#                                           [2026-03-05 11:20]
#                                          Productivity: Active
"""
T.A.R.L. Enhanced VM Test Suite

Comprehensive tests for the enhanced VM covering:
- Bytecode execution
- Register operations
- Garbage collection
- Security/sandboxing
- Performance characteristics
"""

import pytest

from tarl.vm_enhanced import (
    Capability,
    EnhancedVM,
    GenerationalGC,
    Instruction,
    Opcode,
    SandboxManager,
    SecurityContext,
    create_enhanced_vm,
)


class TestEnhancedVM:
    """Test enhanced VM core functionality"""

    def test_vm_creation(self):
        """Test VM creation with different configurations"""
        vm = create_enhanced_vm()
        assert vm is not None
        assert vm.enable_jit is True
        assert vm.enable_gc is True
        assert vm.enable_sandbox is True

        vm2 = create_enhanced_vm(
            enable_jit=False, enable_gc=False, enable_sandbox=False
        )
        assert vm2.enable_jit is False
        assert vm2.enable_gc is False
        assert vm2.enable_sandbox is False

    def test_simple_arithmetic(self):
        """Test simple arithmetic operations"""
        # Compute 5 + 3
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 5
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 3
            Instruction(Opcode.ADD, dest=2, src1=0, src2=1),  # r2 = r0 + r1
            Instruction(Opcode.RETURN, dest=2),
        ]
        constants = [5, 3]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 8

    def test_multiplication_and_division(self):
        """Test multiplication and division"""
        # Compute (10 * 5) / 2
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 10
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 5
            Instruction(Opcode.MUL, dest=2, src1=0, src2=1),  # r2 = 10 * 5
            Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),  # r3 = 2
            Instruction(Opcode.DIV, dest=4, src1=2, src2=3),  # r4 = r2 / 2
            Instruction(Opcode.RETURN, dest=4),
        ]
        constants = [10, 5, 2]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 25.0

    def test_division_by_zero(self):
        """Test division by zero raises error"""
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 10
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 0
            Instruction(Opcode.DIV, dest=2, src1=0, src2=1),  # r2 = 10 / 0
            Instruction(Opcode.RETURN, dest=2),
        ]
        constants = [10, 0]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)

        with pytest.raises(ZeroDivisionError):
            vm.execute()

    def test_variable_operations(self):
        """Test variable load/store"""
        # Store 42 to variable, load it back
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 42
            Instruction(Opcode.STORE_VAR, src1=0, immediate="x"),  # x = r0
            Instruction(Opcode.LOAD_VAR, dest=1, immediate="x"),  # r1 = x
            Instruction(Opcode.RETURN, dest=1),
        ]
        constants = [42]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 42

    def test_undefined_variable(self):
        """Test loading undefined variable raises error"""
        instructions = [
            Instruction(Opcode.LOAD_VAR, dest=0, immediate="undefined"),
            Instruction(Opcode.RETURN, dest=0),
        ]
        constants = []

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)

        with pytest.raises(NameError):
            vm.execute()

    def test_conditional_jump(self):
        """Test conditional jump instructions"""
        # if (5 > 3) return 100 else return 200
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 5
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 3
            Instruction(Opcode.GT, dest=2, src1=0, src2=1),  # r2 = r0 > r1
            Instruction(Opcode.JUMP_IF_TRUE, src1=2, immediate=6),  # jump if true
            # False branch
            Instruction(Opcode.LOAD_CONST, dest=3, immediate=3),  # r3 = 200
            Instruction(Opcode.RETURN, dest=3),
            # True branch
            Instruction(Opcode.LOAD_CONST, dest=4, immediate=2),  # r4 = 100
            Instruction(Opcode.RETURN, dest=4),
        ]
        constants = [5, 3, 100, 200]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 100

    def test_loop_execution(self):
        """Test loop with jump"""
        # Sum 1..10
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 0 (sum)
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=0),  # r1 = 0 (counter)
            Instruction(Opcode.LOAD_CONST, dest=2, immediate=1),  # r2 = 10 (limit)
            # Loop start (pc=3)
            Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),  # r3 = 1
            Instruction(Opcode.ADD, dest=1, src1=1, src2=3),  # r1++
            Instruction(Opcode.ADD, dest=0, src1=0, src2=1),  # r0 += r1
            Instruction(Opcode.LT, dest=4, src1=1, src2=2),  # r4 = r1 < 10
            Instruction(Opcode.JUMP_IF_TRUE, src1=4, immediate=3),  # loop back
            Instruction(Opcode.RETURN, dest=0),
        ]
        constants = [0, 10, 1]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        expected = sum(range(1, 11))  # 1+2+...+10 = 55
        assert result == expected


class TestGarbageCollection:
    """Test generational garbage collector"""

    def test_gc_creation(self):
        """Test GC creation"""
        gc = GenerationalGC()
        assert gc is not None
        assert len(gc.nursery) == 0
        assert len(gc.tenured) == 0

    def test_object_allocation(self):
        """Test object allocation"""
        gc = GenerationalGC()

        obj_id = gc.allocate({"data": "test"}, size=100)
        assert obj_id > 0
        assert obj_id in gc.nursery

    def test_permanent_allocation(self):
        """Test permanent object allocation"""
        gc = GenerationalGC()

        obj_id = gc.allocate({"data": "permanent"}, permanent=True)
        assert obj_id in gc.permanent
        assert obj_id not in gc.nursery

    def test_minor_collection(self):
        """Test minor collection (nursery only)"""
        gc = GenerationalGC()

        # Allocate objects
        obj1 = gc.allocate({"data": "keep"})
        obj2 = gc.allocate({"data": "discard"})

        # Add obj1 to roots (reachable)
        gc.add_root(obj1)

        # Collect
        gc.collect_minor()

        # obj1 should survive, obj2 should be collected
        assert obj1 in gc.nursery or obj1 in gc.tenured
        assert obj2 not in gc.nursery and obj2 not in gc.tenured

    def test_object_promotion(self):
        """Test object promotion to tenured generation"""
        gc = GenerationalGC()

        obj_id = gc.allocate({"data": "long-lived"})
        gc.add_root(obj_id)

        # Survive multiple collections to get promoted
        for _ in range(GenerationalGC.PROMOTION_AGE):
            gc.collect_minor()

        # Should be promoted to tenured
        assert obj_id in gc.tenured
        assert obj_id not in gc.nursery

    def test_major_collection(self):
        """Test major collection (all generations)"""
        gc = GenerationalGC()

        # Allocate in both generations
        nursery_obj = gc.allocate({"data": "young"})
        gc.add_root(nursery_obj)

        # Promote to tenured
        for _ in range(GenerationalGC.PROMOTION_AGE):
            gc.collect_minor()

        tenured_obj = nursery_obj  # Now in tenured

        # Allocate more objects
        temp_obj = gc.allocate({"data": "temp"})

        # Major collection
        gc.collect_major()

        # Tenured object should survive, temp should be collected
        assert tenured_obj in gc.tenured
        assert temp_obj not in gc.nursery

    def test_write_barrier(self):
        """Test write barrier for cross-generational references"""
        gc = GenerationalGC()

        old_obj = gc.allocate({"data": "old"})
        gc.add_root(old_obj)

        # Promote to tenured
        for _ in range(GenerationalGC.PROMOTION_AGE):
            gc.collect_minor()

        young_obj = gc.allocate({"data": "young"})

        # Create cross-generational reference
        gc.write_barrier(old_obj, young_obj)

        assert (old_obj, young_obj) in gc.remembered_set


class TestSandboxing:
    """Test capability-based security"""

    def test_sandbox_creation(self):
        """Test sandbox manager creation"""
        sandbox = SandboxManager()
        assert sandbox is not None
        assert len(sandbox.context_stack) == 1

    def test_capability_check(self):
        """Test capability checking"""
        sandbox = SandboxManager()

        # Default context has READ capability
        sandbox.check_capability(Capability.READ)  # Should not raise

        # Create restricted context without NETWORK
        ctx = sandbox.create_restricted_context({Capability.READ})
        sandbox.push_context(ctx)

        # READ should work
        sandbox.check_capability(Capability.READ)

        # NETWORK should fail
        with pytest.raises(PermissionError):
            sandbox.check_capability(Capability.NETWORK)

    def test_context_stack(self):
        """Test context stack push/pop"""
        sandbox = SandboxManager()

        initial_depth = len(sandbox.context_stack)

        ctx1 = sandbox.create_restricted_context({Capability.READ})
        sandbox.push_context(ctx1)
        assert len(sandbox.context_stack) == initial_depth + 1

        ctx2 = sandbox.create_restricted_context({Capability.WRITE})
        sandbox.push_context(ctx2)
        assert len(sandbox.context_stack) == initial_depth + 2

        sandbox.pop_context()
        assert len(sandbox.context_stack) == initial_depth + 1

        sandbox.pop_context()
        assert len(sandbox.context_stack) == initial_depth

    def test_vm_sandbox_integration(self):
        """Test VM integration with sandboxing"""
        # Execute with capability check
        instructions = [
            Instruction(Opcode.CHECK_CAPABILITY, immediate=Capability.EXECUTE),
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),
            Instruction(Opcode.RETURN, dest=0),
        ]
        constants = [42]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=True)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 42

    def test_vm_sandbox_violation(self):
        """Test VM sandbox capability violation"""
        # Try to use capability without permission
        instructions = [
            Instruction(
                Opcode.SANDBOX_ENTER, immediate={Capability.READ}
            ),  # Enter restricted
            Instruction(
                Opcode.CHECK_CAPABILITY, immediate=Capability.NETWORK
            ),  # Check denied cap
            Instruction(Opcode.RETURN, dest=0),
        ]
        constants = []

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=True)
        vm.load_program(instructions, constants)

        with pytest.raises(PermissionError):
            vm.execute()


class TestVMIntegration:
    """Integration tests for full VM features"""

    def test_vm_with_gc(self):
        """Test VM execution with GC enabled"""
        # Allocate objects during execution
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # counter
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # limit
            # Loop
            Instruction(Opcode.ALLOC, dest=2, immediate={"data": "test"}),
            Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),
            Instruction(Opcode.ADD, dest=0, src1=0, src2=3),
            Instruction(Opcode.LT, dest=4, src1=0, src2=1),
            Instruction(Opcode.JUMP_IF_TRUE, src1=4, immediate=2),
            Instruction(Opcode.RETURN, dest=0),
        ]
        constants = [0, 100, 1]

        vm = create_enhanced_vm(enable_jit=False, enable_gc=True, enable_sandbox=False)
        vm.load_program(instructions, constants)
        result = vm.execute()

        assert result == 100

        stats = vm.get_stats()
        assert "gc" in stats
        assert stats["gc"]["total_objects"] > 0

    def test_vm_statistics(self):
        """Test VM statistics collection"""
        instructions = [
            Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),
            Instruction(Opcode.LOAD_CONST, dest=1, immediate=0),
            Instruction(Opcode.ADD, dest=2, src1=0, src2=1),
            Instruction(Opcode.RETURN, dest=2),
        ]
        constants = [10, 20]

        vm = create_enhanced_vm()
        vm.load_program(instructions, constants)
        vm.execute()

        stats = vm.get_stats()

        assert "vm" in stats
        assert "execution" in stats
        assert stats["execution"]["instructions_executed"] == 4

    def test_instruction_limit(self):
        """Test instruction count limit"""
        # Infinite loop
        instructions = [
            Instruction(Opcode.JUMP, immediate=0),  # Jump to self
        ]
        constants = []

        vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
        vm.load_program(instructions, constants)

        with pytest.raises(RuntimeError, match="Instruction limit exceeded"):
            vm.execute(max_instructions=100)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
