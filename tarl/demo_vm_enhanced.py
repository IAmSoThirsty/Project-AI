#!/usr/bin/env python3
#                                           [2026-03-05 11:30]
#                                          Productivity: Active
"""
T.A.R.L. Enhanced VM Demo

Demonstrates key features of the enhanced VM:
1. Basic arithmetic
2. Loops and control flow
3. Garbage collection
4. Security sandboxing
5. Performance characteristics
"""

from tarl.vm_enhanced import (
    Capability,
    EnhancedVM,
    Instruction,
    Opcode,
    create_enhanced_vm,
)


def demo_basic_arithmetic():
    """Demo: Basic arithmetic operations"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Arithmetic")
    print("=" * 60)
    print("Computing: (10 + 5) * 2 - 3")

    instructions = [
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 10
        Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 5
        Instruction(Opcode.ADD, dest=2, src1=0, src2=1),  # r2 = 10 + 5
        Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),  # r3 = 2
        Instruction(Opcode.MUL, dest=4, src1=2, src2=3),  # r4 = r2 * 2
        Instruction(Opcode.LOAD_CONST, dest=5, immediate=3),  # r5 = 3
        Instruction(Opcode.SUB, dest=6, src1=4, src2=5),  # r6 = r4 - 3
        Instruction(Opcode.RETURN, dest=6),
    ]
    constants = [10, 5, 2, 3]

    vm = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
    vm.load_program(instructions, constants)

    result = vm.execute()
    print(f"Result: {result}")
    print(f"Expected: {(10 + 5) * 2 - 3}")
    print("✓ Demo complete\n")


def demo_loop():
    """Demo: Loop execution"""
    print("=" * 60)
    print("DEMO 2: Loop Execution")
    print("=" * 60)
    print("Computing: Sum of 1..100")

    N = 100
    instructions = [
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = 0 (sum)
        Instruction(Opcode.LOAD_CONST, dest=1, immediate=0),  # r1 = 0 (counter)
        Instruction(Opcode.LOAD_CONST, dest=2, immediate=1),  # r2 = N
        # Loop
        Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),  # r3 = 1
        Instruction(Opcode.ADD, dest=1, src1=1, src2=3),  # r1++
        Instruction(Opcode.ADD, dest=0, src1=0, src2=1),  # r0 += r1
        Instruction(Opcode.LT, dest=4, src1=1, src2=2),  # r4 = r1 < N
        Instruction(Opcode.JUMP_IF_TRUE, src1=4, immediate=3),
        Instruction(Opcode.RETURN, dest=0),
    ]
    constants = [0, N, 1]

    vm = create_enhanced_vm(enable_jit=True, enable_gc=False, enable_sandbox=False)
    vm.load_program(instructions, constants)

    result = vm.execute()
    expected = sum(range(1, N + 1))

    print(f"Result: {result}")
    print(f"Expected: {expected}")
    print(f"Instructions executed: {vm.state.instruction_count}")
    print("✓ Demo complete\n")


def demo_garbage_collection():
    """Demo: Garbage collection"""
    print("=" * 60)
    print("DEMO 3: Garbage Collection")
    print("=" * 60)
    print("Allocating 1,000 objects...")

    N = 1000
    instructions = [
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),  # r0 = N
        Instruction(Opcode.LOAD_CONST, dest=1, immediate=1),  # r1 = 0
        # Loop
        Instruction(Opcode.ALLOC, dest=2, immediate={"id": 0}),
        Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),
        Instruction(Opcode.ADD, dest=1, src1=1, src2=3),
        Instruction(Opcode.LT, dest=4, src1=1, src2=0),
        Instruction(Opcode.JUMP_IF_TRUE, src1=4, immediate=2),
        Instruction(Opcode.RETURN, dest=1),
    ]
    constants = [N, 0, 1]

    vm = create_enhanced_vm(enable_jit=False, enable_gc=True, enable_sandbox=False)
    vm.load_program(instructions, constants)

    result = vm.execute()
    stats = vm.get_stats()

    print(f"Allocated: {result} objects")
    print(f"\nGC Statistics:")
    gc_stats = stats.get("gc", {})
    print(f"  Minor collections: {gc_stats.get('minor_collections', 0)}")
    print(f"  Major collections: {gc_stats.get('major_collections', 0)}")
    print(f"  Objects collected: {gc_stats.get('objects_collected', 0)}")
    print(f"  Objects promoted: {gc_stats.get('objects_promoted', 0)}")
    print(f"  Nursery size: {gc_stats.get('nursery_size', 0)}")
    print(f"  Total pause time: {gc_stats.get('total_pause_time_ms', 0):.2f}ms")
    print("✓ Demo complete\n")


def demo_security():
    """Demo: Security sandboxing"""
    print("=" * 60)
    print("DEMO 4: Security Sandboxing")
    print("=" * 60)
    print("Testing capability-based security...")

    # Test 1: Allowed capability
    print("\nTest 1: Checking allowed capability (EXECUTE)")
    instructions1 = [
        Instruction(Opcode.CHECK_CAPABILITY, immediate=Capability.EXECUTE),
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),
        Instruction(Opcode.RETURN, dest=0),
    ]
    constants1 = [42]

    vm1 = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=True)
    vm1.load_program(instructions1, constants1)

    try:
        result = vm1.execute()
        print(f"  ✓ Capability check passed, result: {result}")
    except PermissionError as e:
        print(f"  ✗ Capability check failed: {e}")

    # Test 2: Restricted context
    print("\nTest 2: Entering restricted sandbox (READ only)")
    instructions2 = [
        Instruction(Opcode.SANDBOX_ENTER, immediate={Capability.READ}),
        Instruction(Opcode.CHECK_CAPABILITY, immediate=Capability.READ),
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),
        Instruction(Opcode.SANDBOX_EXIT),
        Instruction(Opcode.RETURN, dest=0),
    ]
    constants2 = [100]

    vm2 = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=True)
    vm2.load_program(instructions2, constants2)

    try:
        result = vm2.execute()
        print(f"  ✓ READ capability allowed, result: {result}")
    except PermissionError as e:
        print(f"  ✗ Capability check failed: {e}")

    # Test 3: Denied capability
    print("\nTest 3: Checking denied capability (NETWORK in restricted context)")
    instructions3 = [
        Instruction(Opcode.SANDBOX_ENTER, immediate={Capability.READ}),
        Instruction(Opcode.CHECK_CAPABILITY, immediate=Capability.NETWORK),
        Instruction(Opcode.SANDBOX_EXIT),
        Instruction(Opcode.RETURN, dest=0),
    ]
    constants3 = []

    vm3 = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=True)
    vm3.load_program(instructions3, constants3)

    try:
        result = vm3.execute()
        print(f"  ✗ Should have been denied! Result: {result}")
    except PermissionError as e:
        print(f"  ✓ Correctly denied: {e}")

    print("✓ Demo complete\n")


def demo_performance():
    """Demo: Performance characteristics"""
    print("=" * 60)
    print("DEMO 5: Performance Characteristics")
    print("=" * 60)
    print("Comparing execution modes...")

    N = 10000
    instructions = [
        Instruction(Opcode.LOAD_CONST, dest=0, immediate=0),
        Instruction(Opcode.LOAD_CONST, dest=1, immediate=0),
        Instruction(Opcode.LOAD_CONST, dest=2, immediate=1),
        # Loop
        Instruction(Opcode.LOAD_CONST, dest=3, immediate=2),
        Instruction(Opcode.ADD, dest=1, src1=1, src2=3),
        Instruction(Opcode.ADD, dest=0, src1=0, src2=1),
        Instruction(Opcode.LT, dest=4, src1=1, src2=2),
        Instruction(Opcode.JUMP_IF_TRUE, src1=4, immediate=3),
        Instruction(Opcode.RETURN, dest=0),
    ]
    constants = [0, N, 1]

    # Test 1: Basic execution
    print(f"\nTest 1: Basic execution (sum 1..{N})")
    vm1 = create_enhanced_vm(enable_jit=False, enable_gc=False, enable_sandbox=False)
    vm1.load_program(instructions, constants)

    import time

    start = time.perf_counter()
    result1 = vm1.execute()
    elapsed1 = time.perf_counter() - start

    print(f"  Result: {result1}")
    print(f"  Time: {elapsed1 * 1000:.2f}ms")
    print(f"  Instructions: {vm1.state.instruction_count}")

    # Test 2: With JIT enabled
    print(f"\nTest 2: With JIT hints enabled")
    vm2 = create_enhanced_vm(enable_jit=True, enable_gc=False, enable_sandbox=False)
    vm2.load_program(instructions, constants)

    start = time.perf_counter()
    result2 = vm2.execute()
    elapsed2 = time.perf_counter() - start

    print(f"  Result: {result2}")
    print(f"  Time: {elapsed2 * 1000:.2f}ms")
    print(f"  Speedup: {elapsed1 / elapsed2:.2f}x")

    # Test 3: All features enabled
    print(f"\nTest 3: All features enabled (JIT + GC + Sandbox)")
    vm3 = create_enhanced_vm(enable_jit=True, enable_gc=True, enable_sandbox=True)
    vm3.load_program(instructions, constants)

    start = time.perf_counter()
    result3 = vm3.execute()
    elapsed3 = time.perf_counter() - start

    print(f"  Result: {result3}")
    print(f"  Time: {elapsed3 * 1000:.2f}ms")
    print(f"  Overhead vs basic: {(elapsed3 / elapsed1 - 1) * 100:.1f}%")

    stats = vm3.get_stats()
    print(f"\n  VM Statistics:")
    print(f"    Instructions executed: {stats.get('execution', {}).get('instructions_executed', vm3.state.instruction_count)}")
    print(f"    Elapsed time: {stats.get('execution', {}).get('elapsed_ms', 0):.2f}ms")

    print("✓ Demo complete\n")


def main():
    """Run all demos"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + " T.A.R.L. ENHANCED VM - FEATURE DEMONSTRATION ".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)

    demo_basic_arithmetic()
    demo_loop()
    demo_garbage_collection()
    demo_security()
    demo_performance()

    print("█" * 60)
    print("█" + " ALL DEMOS COMPLETED SUCCESSFULLY ".center(58) + "█")
    print("█" * 60 + "\n")


if __name__ == "__main__":
    main()
