"""
Benchmark Runner Script

Run comprehensive data plane benchmarks and generate reports.

Usage:
    python run_all.py [--quick] [--output results.json]
"""

import asyncio
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark import DataPlaneBenchmark
from temporal.dataplane import DataPlaneClient, DataPlaneConfig


async def main():
    """Run all benchmarks."""
    parser = argparse.ArgumentParser(description="Data Plane Benchmarks")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmarks with reduced iterations")
    parser.add_argument("--output", default="benchmark_results.json", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting data plane benchmarks...")

    # Load configuration
    config = DataPlaneConfig.from_env()
    config.validate()

    # Create client
    client = DataPlaneClient(config)

    try:
        # Connect to data plane
        logger.info("Connecting to data plane...")
        await client.connect()
        logger.info("Connected successfully")

        # Create benchmark suite
        benchmark = DataPlaneBenchmark(client)

        # Run benchmarks
        if args.quick:
            logger.info("Running QUICK benchmarks...")
            await benchmark.bench_small_messages(num_messages=1000)
            await benchmark.bench_large_messages(num_messages=10)
            await benchmark.bench_cache_operations(num_operations=10000)
        else:
            logger.info("Running FULL benchmarks (this may take several minutes)...")
            await benchmark.run_all()

        # Print results
        benchmark.print_results()

        # Save results
        benchmark.save_results(args.output)

    except Exception as e:
        logger.error(f"Benchmark failed: {e}", exc_info=True)
        return 1

    finally:
        # Disconnect
        logger.info("Disconnecting from data plane...")
        await client.disconnect()

    logger.info("Benchmarks complete!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
