import argparse
import json
import os
import sys

from .orchestrator import ThirstysWaterfall
from .runtime_controls import ACTIVE_CONTROLS_ENV, DESTRUCTIVE_RESPONSES_ENV

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Thirstys Waterfall - Integrated Privacy-First System"
    )

    parser.add_argument("--config", type=str, help="Path to configuration file")

    parser.add_argument("--start", action="store_true", help="Start the system")

    parser.add_argument("--stop", action="store_true", help="Stop the system")

    parser.add_argument("--status", action="store_true", help="Show system status")

    parser.add_argument("--audit", action="store_true", help="Run privacy audit")
    parser.add_argument(
        "--enable-active-controls",
        action="store_true",
        help="Allow host/network controls for this process",
    )
    parser.add_argument(
        "--enable-destructive-responses",
        action="store_true",
        help="Allow destructive emergency responses for this process",
    )

    args = parser.parse_args()
    if args.enable_active_controls:
        os.environ[ACTIVE_CONTROLS_ENV] = "1"
    if args.enable_destructive_responses:
        os.environ[DESTRUCTIVE_RESPONSES_ENV] = "1"

    # Initialize system
    try:
        waterfall = ThirstysWaterfall(config_path=args.config)

        if args.start:
            print("Starting Thirstys Waterfall...")
            waterfall.start()
            print("System started successfully!")
            print("Press Ctrl+C to stop...")

            try:
                # Keep running
                import time

                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                waterfall.stop()

        elif args.status:
            if waterfall.is_active():
                waterfall.start()
            status = waterfall.get_status()
            print(json.dumps(status, indent=2))

        elif args.audit:
            if not waterfall.is_active():
                waterfall.start()
            audit_results = waterfall.run_privacy_audit()
            print(json.dumps(audit_results, indent=2))

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
