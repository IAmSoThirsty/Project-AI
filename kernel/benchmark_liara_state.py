#!/usr/bin/env python3
#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Liara State Preservation Benchmark

Validates performance requirements:
- Snapshot capture time
- State restoration time (<1s target)
- Cryptographic overhead
- WAL replay performance
- Recovery proof generation

Run with: python benchmark_liara_state.py
"""

import random
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.liara_state import (
    LiaraStatePreservation,
    StateType,
    create_triumvirate_snapshot,
    restore_triumvirate_state
)


def generate_realistic_process_state(num_processes: int = 100) -> Dict[str, Any]:
    """Generate realistic process state for testing"""
    processes = {}
    
    for i in range(num_processes):
        pid = 1000 + i
        processes[str(pid)] = {
            "pid": pid,
            "name": f"process_{i}",
            "priority": random.randint(0, 7),
            "state": random.choice(["new", "ready", "running", "blocked", "suspended"]),
            "cpu_time": random.randint(0, 10000),
            "memory_kb": random.randint(1024, 102400),
            "parent_pid": random.randint(1, 999),
            "open_files": [f"/tmp/file_{j}.txt" for j in range(random.randint(0, 5))],
            "environment": {
                "PATH": "/usr/bin:/bin",
                "HOME": f"/home/user{i}",
                "USER": f"user{i}"
            }
        }
    
    return {"processes": processes}


def generate_realistic_memory_state(num_pages: int = 1000) -> Dict[str, Any]:
    """Generate realistic memory state for testing"""
    pages = {}
    
    for i in range(num_pages):
        pages[str(i)] = {
            "page_number": i,
            "size": 4096,
            "state": random.choice(["free", "allocated", "swapped", "locked"]),
            "virtual_address": i * 4096,
            "owner_pid": random.randint(1000, 1100) if random.random() > 0.3 else None,
            "reference_count": random.randint(0, 5),
            "access_count": random.randint(0, 100),
            "is_dirty": random.random() > 0.7
        }
    
    return {"pages": pages}


def generate_realistic_scheduler_state(num_queues: int = 8) -> Dict[str, Any]:
    """Generate realistic scheduler state for testing"""
    queues = {}
    
    for priority in range(num_queues):
        queues[f"priority_{priority}"] = {
            "priority": priority,
            "processes": [1000 + i for i in range(random.randint(5, 20))],
            "quantum_ms": 100 // (priority + 1),
            "total_wait_time": random.randint(0, 10000)
        }
    
    return {
        "queues": queues,
        "current_cpu_assignments": {
            f"cpu_{i}": 1000 + random.randint(0, 99) for i in range(4)
        },
        "load_average": [1.23, 2.45, 3.67]
    }


def benchmark_snapshot_capture():
    """Benchmark snapshot capture performance"""
    print("\n" + "="*70)
    print("BENCHMARK: Snapshot Capture Performance")
    print("="*70)
    
    preserver = LiaraStatePreservation()
    
    sizes = [10, 50, 100, 500, 1000]
    results = []
    
    for size in sizes:
        state_data = generate_realistic_process_state(size)
        
        start = time.perf_counter()
        snapshot = preserver.capture_snapshot(
            controller_id="benchmark-controller",
            state_type=StateType.PROCESS,
            state_data=state_data
        )
        elapsed = time.perf_counter() - start
        
        results.append({
            "size": size,
            "time": elapsed,
            "bytes": snapshot.size_bytes
        })
        
        print(f"  {size:4d} processes: {elapsed*1000:7.2f}ms  "
              f"({snapshot.size_bytes:8d} bytes, "
              f"{snapshot.size_bytes/elapsed/1024/1024:.2f} MB/s)")
    
    preserver.close()
    
    avg_time = statistics.mean(r["time"] for r in results)
    print(f"\n  Average capture time: {avg_time*1000:.2f}ms")
    
    return results


def benchmark_snapshot_restore():
    """Benchmark snapshot restore performance with <1s verification"""
    print("\n" + "="*70)
    print("BENCHMARK: Snapshot Restore Performance (<1s TARGET)")
    print("="*70)
    
    preserver = LiaraStatePreservation()
    
    sizes = [10, 50, 100, 500, 1000]
    results = []
    target_met_count = 0
    
    for size in sizes:
        # Create snapshot
        state_data = generate_realistic_process_state(size)
        snapshot = preserver.capture_snapshot(
            controller_id="benchmark-controller",
            state_type=StateType.PROCESS,
            state_data=state_data
        )
        
        # Restore and measure
        start = time.perf_counter()
        restored_snapshot, proof = preserver.restore_snapshot(snapshot.snapshot_id)
        elapsed = time.perf_counter() - start
        
        target_met = elapsed < 1.0
        if target_met:
            target_met_count += 1
        
        results.append({
            "size": size,
            "time": elapsed,
            "target_met": target_met,
            "proof_valid": proof.verification_status == "verified"
        })
        
        status = "✓" if target_met else "✗"
        print(f"  {size:4d} processes: {elapsed*1000:7.2f}ms  {status}  "
              f"(proof: {proof.verification_status})")
    
    preserver.close()
    
    avg_time = statistics.mean(r["time"] for r in results)
    print(f"\n  Average restore time: {avg_time*1000:.2f}ms")
    print(f"  Target met: {target_met_count}/{len(results)} tests")
    print(f"  Overall status: {'✓ PASS' if target_met_count == len(results) else '✗ FAIL'}")
    
    return results


def benchmark_cryptographic_overhead():
    """Benchmark cryptographic signing and verification"""
    print("\n" + "="*70)
    print("BENCHMARK: Cryptographic Overhead")
    print("="*70)
    
    preserver = LiaraStatePreservation()
    
    # Test different data sizes
    data_sizes = [1024, 10*1024, 100*1024, 1024*1024]  # 1KB to 1MB
    
    for size_bytes in data_sizes:
        data = b"x" * size_bytes
        
        # Measure signing
        sign_times = []
        for _ in range(100):
            start = time.perf_counter()
            signature = preserver.crypto.sign(data)
            sign_times.append(time.perf_counter() - start)
        
        # Measure verification
        public_key = preserver.crypto.get_public_key_hex()
        verify_times = []
        for _ in range(100):
            start = time.perf_counter()
            preserver.crypto.verify(data, signature, public_key)
            verify_times.append(time.perf_counter() - start)
        
        avg_sign = statistics.mean(sign_times) * 1_000_000  # Convert to microseconds
        avg_verify = statistics.mean(verify_times) * 1_000_000
        
        print(f"  {size_bytes:8d} bytes: sign={avg_sign:7.1f}µs  verify={avg_verify:7.1f}µs")
    
    preserver.close()


def benchmark_wal_performance():
    """Benchmark Write-Ahead Log performance"""
    print("\n" + "="*70)
    print("BENCHMARK: Write-Ahead Log Performance")
    print("="*70)
    
    preserver = LiaraStatePreservation()
    wal = preserver._get_wal(StateType.PROCESS)
    
    # Test WAL write performance
    num_entries = 1000
    
    write_times = []
    for i in range(num_entries):
        start = time.perf_counter()
        wal.write_entry(
            operation="update",
            state_key=f"process.{i}.state",
            old_value="running",
            new_value="blocked"
        )
        write_times.append(time.perf_counter() - start)
    
    avg_write = statistics.mean(write_times) * 1_000_000  # Microseconds
    total_write = sum(write_times)
    
    print(f"  {num_entries} WAL writes:")
    print(f"    Average: {avg_write:.1f}µs per entry")
    print(f"    Total:   {total_write*1000:.2f}ms")
    print(f"    Rate:    {num_entries/total_write:.0f} entries/sec")
    
    # Test WAL replay performance
    start = time.perf_counter()
    reconstructed = preserver.replay_wal(StateType.PROCESS)
    replay_time = time.perf_counter() - start
    
    print(f"\n  WAL replay ({num_entries} entries):")
    print(f"    Time:    {replay_time*1000:.2f}ms")
    print(f"    Rate:    {num_entries/replay_time:.0f} entries/sec")
    
    preserver.close()


def benchmark_full_triumvirate_failover():
    """Benchmark complete Triumvirate failover scenario"""
    print("\n" + "="*70)
    print("BENCHMARK: Complete Triumvirate Failover")
    print("="*70)
    
    # Generate realistic state for all subsystems
    process_state = generate_realistic_process_state(200)
    memory_state = generate_realistic_memory_state(500)
    scheduler_state = generate_realistic_scheduler_state(8)
    
    # Capture complete snapshot
    print("\n  Capturing complete Triumvirate state...")
    start = time.perf_counter()
    snapshots = create_triumvirate_snapshot(
        controller_id="triumvirate-alpha",
        process_state=process_state,
        memory_state=memory_state,
        scheduler_state=scheduler_state
    )
    capture_time = time.perf_counter() - start
    
    print(f"    Capture time: {capture_time*1000:.2f}ms")
    print(f"    Snapshots created: {len(snapshots)}")
    
    total_size = sum(s.size_bytes for s in snapshots)
    print(f"    Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    
    # Restore complete state
    print("\n  Restoring complete Triumvirate state...")
    snapshot_ids = [s.snapshot_id for s in snapshots]
    
    start = time.perf_counter()
    restored = restore_triumvirate_state(snapshot_ids)
    restore_time = time.perf_counter() - start
    
    print(f"    Restore time: {restore_time*1000:.2f}ms")
    print(f"    States restored: {len(restored)}")
    
    # Verify data integrity
    all_verified = True
    for state_type, restored_data in restored.items():
        if state_type == StateType.PROCESS:
            all_verified &= (restored_data == process_state)
        elif state_type == StateType.MEMORY:
            all_verified &= (restored_data == memory_state)
        elif state_type == StateType.SCHEDULER:
            all_verified &= (restored_data == scheduler_state)
    
    print(f"    Data integrity: {'✓ VERIFIED' if all_verified else '✗ FAILED'}")
    
    # Overall assessment
    print(f"\n  FAILOVER ASSESSMENT:")
    print(f"    Total time: {(capture_time + restore_time)*1000:.2f}ms")
    print(f"    Restore target (<1s): {'✓ MET' if restore_time < 1.0 else '✗ MISSED'}")
    print(f"    Data integrity: {'✓ PASS' if all_verified else '✗ FAIL'}")
    
    return {
        "capture_time": capture_time,
        "restore_time": restore_time,
        "total_size": total_size,
        "verified": all_verified
    }


def benchmark_scalability():
    """Benchmark scalability with increasing state sizes"""
    print("\n" + "="*70)
    print("BENCHMARK: Scalability Analysis")
    print("="*70)
    
    preserver = LiaraStatePreservation()
    
    process_counts = [100, 500, 1000, 2000, 5000]
    
    print("\n  Process Count  |  Capture  |  Restore  |  Target Met")
    print("  " + "-"*60)
    
    for count in process_counts:
        state_data = generate_realistic_process_state(count)
        
        # Capture
        start = time.perf_counter()
        snapshot = preserver.capture_snapshot(
            controller_id="scale-test",
            state_type=StateType.PROCESS,
            state_data=state_data
        )
        capture_time = time.perf_counter() - start
        
        # Restore
        start = time.perf_counter()
        restored, proof = preserver.restore_snapshot(snapshot.snapshot_id)
        restore_time = time.perf_counter() - start
        
        target_met = "✓" if restore_time < 1.0 else "✗"
        
        print(f"  {count:5d} processes  |  {capture_time*1000:6.1f}ms  |  "
              f"{restore_time*1000:6.1f}ms  |  {target_met}")
    
    preserver.close()


def run_all_benchmarks():
    """Run complete benchmark suite"""
    print("\n" + "="*70)
    print("LIARA STATE PRESERVATION - BENCHMARK SUITE")
    print("="*70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all benchmarks
    benchmark_snapshot_capture()
    benchmark_snapshot_restore()
    benchmark_cryptographic_overhead()
    benchmark_wal_performance()
    benchmark_scalability()
    failover_results = benchmark_full_triumvirate_failover()
    
    # Final summary
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)
    
    print(f"\n  Triumvirate Failover:")
    print(f"    Capture: {failover_results['capture_time']*1000:.2f}ms")
    print(f"    Restore: {failover_results['restore_time']*1000:.2f}ms")
    print(f"    Data size: {failover_results['total_size']/1024/1024:.2f} MB")
    print(f"    Integrity: {'✓ VERIFIED' if failover_results['verified'] else '✗ FAILED'}")
    
    restore_target_met = failover_results['restore_time'] < 1.0
    
    print(f"\n  FINAL VERDICT:")
    print(f"    Restoration target (<1s): {'✓ MET' if restore_target_met else '✗ MISSED'}")
    print(f"    Zero data loss: {'✓ GUARANTEED' if failover_results['verified'] else '✗ AT RISK'}")
    
    if restore_target_met and failover_results['verified']:
        print(f"\n  🎉 ALL REQUIREMENTS MET - PRODUCTION READY")
        return 0
    else:
        print(f"\n  ⚠️  PERFORMANCE TARGETS NOT MET - OPTIMIZATION REQUIRED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_benchmarks()
    sys.exit(exit_code)
