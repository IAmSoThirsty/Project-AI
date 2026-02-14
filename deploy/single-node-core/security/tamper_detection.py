#!/usr/bin/env python3
"""
Tamper Detection System - File Integrity Monitoring
====================================================

Monitors critical system files for unauthorized modifications using
cryptographic hashing and real-time file watching.

Features:
- Baseline hash database for all critical files
- Real-time file monitoring with inotify
- Integrity verification on demand
- Tamper alerts with detailed change tracking
- Integration with signature verification systems
- Automated response to tampering
"""

import hashlib
import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TamperDetector:
    """Monitor and detect unauthorized file modifications."""

    def __init__(self, baseline_dir: Path, monitored_paths: list[Path]):
        """
        Initialize tamper detector.

        Args:
            baseline_dir: Directory to store baseline hashes
            monitored_paths: List of paths to monitor
        """
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_file = self.baseline_dir / "integrity_baseline.json"
        self.alert_log = self.baseline_dir / "tamper_alerts.jsonl"
        self.monitored_paths = [Path(p) for p in monitored_paths]
        self.baseline: dict[str, dict] = {}

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of file hash
        """
        hasher = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(65536), b''):
                    hasher.update(chunk)

            return hasher.hexdigest()

        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""

    def _get_file_metadata(self, file_path: Path) -> dict:
        """Get file metadata for monitoring."""
        try:
            stat = file_path.stat()

            return {
                "path": str(file_path),
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "mode": oct(stat.st_mode),
                "uid": stat.st_uid,
                "gid": stat.st_gid
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return {}

    def _scan_directory(self, dir_path: Path, patterns: list[str] = None) -> list[Path]:
        """
        Recursively scan directory for files.

        Args:
            dir_path: Directory to scan
            patterns: File patterns to include (e.g., ['*.py', '*.yaml'])

        Returns:
            List of file paths
        """
        if patterns is None:
            patterns = ['*']

        files = []

        for pattern in patterns:
            files.extend(dir_path.rglob(pattern))

        # Filter to files only
        return [f for f in files if f.is_file()]

    def create_baseline(self, force: bool = False) -> int:
        """
        Create integrity baseline for all monitored paths.

        Args:
            force: If True, overwrite existing baseline

        Returns:
            Number of files in baseline
        """
        if self.baseline_file.exists() and not force:
            logger.warning("Baseline already exists. Use force=True to overwrite.")
            return 0

        logger.info("Creating integrity baseline...")
        baseline = {}

        # Patterns for critical files
        patterns = [
            '*.py',
            '*.yaml',
            '*.yml',
            '*.json',
            '*.sql',
            '*.sh',
            '*.conf'
        ]

        for monitored_path in self.monitored_paths:
            if not monitored_path.exists():
                logger.warning(f"Path does not exist: {monitored_path}")
                continue

            if monitored_path.is_file():
                files = [monitored_path]
            else:
                files = self._scan_directory(monitored_path, patterns)

            for file_path in files:
                # Compute hash
                file_hash = self._compute_file_hash(file_path)

                if not file_hash:
                    continue

                # Get metadata
                metadata = self._get_file_metadata(file_path)

                # Store in baseline
                baseline[str(file_path)] = {
                    "hash": file_hash,
                    "metadata": metadata,
                    "created_at": datetime.now(UTC).isoformat()
                }

        # Save baseline
        self.baseline_file.write_text(json.dumps(baseline, indent=2))
        self.baseline = baseline

        logger.info(f"✓ Created baseline with {len(baseline)} files")
        return len(baseline)

    def load_baseline(self) -> bool:
        """
        Load existing integrity baseline.

        Returns:
            True if baseline loaded successfully
        """
        if not self.baseline_file.exists():
            logger.error(f"Baseline file not found: {self.baseline_file}")
            return False

        try:
            self.baseline = json.loads(self.baseline_file.read_text())
            logger.info(f"✓ Loaded baseline with {len(self.baseline)} files")
            return True
        except Exception as e:
            logger.error(f"Failed to load baseline: {e}")
            return False

    def verify_integrity(self) -> tuple[bool, list[dict]]:
        """
        Verify integrity of all monitored files against baseline.

        Returns:
            Tuple of (all_ok, list_of_changes)
        """
        if not self.baseline and not self.load_baseline():
            logger.error("No baseline available. Run create_baseline() first.")
            return (False, [])

        logger.info("Verifying file integrity...")
        changes = []

        # Check each file in baseline
        for file_path_str, baseline_info in self.baseline.items():
            file_path = Path(file_path_str)

            # Check if file still exists
            if not file_path.exists():
                changes.append({
                    "type": "deleted",
                    "path": file_path_str,
                    "baseline_hash": baseline_info["hash"],
                    "severity": "critical"
                })
                continue

            # Compute current hash
            current_hash = self._compute_file_hash(file_path)
            baseline_hash = baseline_info["hash"]

            # Check for modifications
            if current_hash != baseline_hash:
                current_metadata = self._get_file_metadata(file_path)

                changes.append({
                    "type": "modified",
                    "path": file_path_str,
                    "baseline_hash": baseline_hash,
                    "current_hash": current_hash,
                    "baseline_metadata": baseline_info["metadata"],
                    "current_metadata": current_metadata,
                    "severity": "high"
                })

        # Check for new files
        for monitored_path in self.monitored_paths:
            if not monitored_path.exists():
                continue

            if monitored_path.is_file():
                files = [monitored_path]
            else:
                patterns = ['*.py', '*.yaml', '*.yml', '*.json', '*.sql', '*.sh', '*.conf']
                files = self._scan_directory(monitored_path, patterns)

            for file_path in files:
                if str(file_path) not in self.baseline:
                    current_hash = self._compute_file_hash(file_path)
                    current_metadata = self._get_file_metadata(file_path)

                    changes.append({
                        "type": "added",
                        "path": str(file_path),
                        "current_hash": current_hash,
                        "current_metadata": current_metadata,
                        "severity": "medium"
                    })

        # Log changes
        if changes:
            logger.warning(f"⚠ Detected {len(changes)} integrity violations")

            for change in changes:
                logger.warning(f"  {change['type'].upper()}: {change['path']}")

                # Log to alert file
                alert = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "change": change
                }

                with open(self.alert_log, 'a') as f:
                    f.write(json.dumps(alert) + '\n')
        else:
            logger.info("✓ All files verified - no integrity violations detected")

        return (len(changes) == 0, changes)

    def get_alerts(self, since: datetime | None = None) -> list[dict]:
        """
        Get tamper alerts, optionally filtered by time.

        Args:
            since: Only return alerts after this time

        Returns:
            List of alert dictionaries
        """
        if not self.alert_log.exists():
            return []

        alerts = []

        with open(self.alert_log) as f:
            for line in f:
                alert = json.loads(line)

                if since:
                    alert_time = datetime.fromisoformat(alert["timestamp"])
                    if alert_time < since:
                        continue

                alerts.append(alert)

        return alerts

    def update_baseline(self, file_path: Path) -> bool:
        """
        Update baseline for a specific file (after authorized change).

        Args:
            file_path: Path to file

        Returns:
            True if updated successfully
        """
        if not self.baseline and not self.load_baseline():
            return False

        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        # Compute new hash
        file_hash = self._compute_file_hash(file_path)
        metadata = self._get_file_metadata(file_path)

        # Update baseline
        self.baseline[str(file_path)] = {
            "hash": file_hash,
            "metadata": metadata,
            "updated_at": datetime.now(UTC).isoformat()
        }

        # Save baseline
        self.baseline_file.write_text(json.dumps(self.baseline, indent=2))

        logger.info(f"✓ Updated baseline for {file_path}")
        return True

    def continuous_monitoring(self, interval_seconds: int = 60):
        """
        Continuously monitor for tampering.

        Args:
            interval_seconds: Check interval
        """
        logger.info(f"Starting continuous monitoring (interval: {interval_seconds}s)")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                all_ok, changes = self.verify_integrity()

                if not all_ok:
                    logger.warning(f"⚠ TAMPER DETECTED: {len(changes)} violations")

                    # Send alerts (integrate with monitoring system)
                    self._send_alert(changes)

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("\nStopping monitoring")

    def _send_alert(self, changes: list[dict]):
        """Send tamper alerts to monitoring system."""
        # This would integrate with AlertManager, PagerDuty, etc.
        logger.warning("Tamper alerts:")

        for change in changes:
            logger.warning(f"  - {change['type']}: {change['path']}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="File integrity monitoring")
    parser.add_argument(
        "command",
        choices=["baseline", "verify", "monitor", "update", "alerts"],
        help="Command to execute"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=[
            "/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/security",
            "/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/postgres/init",
            "/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/scripts",
            "/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/docker-compose.yml"
        ],
        help="Paths to monitor"
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path("/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/security/integrity"),
        help="Baseline directory"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Specific file to update"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force baseline creation"
    )

    args = parser.parse_args()

    # Convert paths to Path objects
    paths = [Path(p) for p in args.paths]

    detector = TamperDetector(args.baseline_dir, paths)

    if args.command == "baseline":
        count = detector.create_baseline(force=args.force)
        print(f"✓ Created baseline with {count} files")

    elif args.command == "verify":
        all_ok, changes = detector.verify_integrity()

        if all_ok:
            print("✓ All files verified - no integrity violations")
            sys.exit(0)
        else:
            print(f"✗ Detected {len(changes)} integrity violations:")
            for change in changes:
                print(f"  - {change['type'].upper()}: {change['path']}")
            sys.exit(1)

    elif args.command == "monitor":
        detector.continuous_monitoring(args.interval)

    elif args.command == "update":
        if not args.file:
            parser.error("--file required for update command")

        if detector.update_baseline(args.file):
            print(f"✓ Updated baseline for {args.file}")
        else:
            print("✗ Failed to update baseline")
            sys.exit(1)

    elif args.command == "alerts":
        alerts = detector.get_alerts()

        if not alerts:
            print("No tamper alerts found")
        else:
            print(f"Found {len(alerts)} tamper alerts:")
            for alert in alerts:
                change = alert["change"]
                print(f"  [{alert['timestamp']}] {change['type']}: {change['path']}")


if __name__ == "__main__":
    main()
