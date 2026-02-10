"""
Artifact Manager for E2E Tests

Handles saving, organizing, and managing test artifacts including:
- Test logs
- Screenshots
- API request/response dumps
- Database snapshots
- Error traces
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ArtifactManager:
    """Manages test artifacts and outputs."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize artifact manager.

        Args:
            base_dir: Base directory for artifacts. Defaults to e2e/artifacts
        """
        self.base_dir = base_dir or Path(__file__).parent.parent / "artifacts"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.logs_dir = self.base_dir / "logs"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.dumps_dir = self.base_dir / "dumps"
        self.reports_dir = self.base_dir / "reports"

        for directory in [
            self.logs_dir,
            self.screenshots_dir,
            self.dumps_dir,
            self.reports_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Current test run identifier
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_run_dir = self.base_dir / self.run_id
        self.current_run_dir.mkdir(parents=True, exist_ok=True)

    def save_log(self, name: str, content: str) -> Path:
        """Save test log.

        Args:
            name: Log name
            content: Log content

        Returns:
            Path to saved log file
        """
        log_file = self.current_run_dir / "logs" / f"{name}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.write_text(content)
        logger.info("Saved log: %s", log_file)
        return log_file

    def save_screenshot(self, name: str, image_data: bytes) -> Path:
        """Save screenshot.

        Args:
            name: Screenshot name
            image_data: Image binary data

        Returns:
            Path to saved screenshot
        """
        screenshot_file = self.current_run_dir / "screenshots" / f"{name}.png"
        screenshot_file.parent.mkdir(parents=True, exist_ok=True)
        screenshot_file.write_bytes(image_data)
        logger.info("Saved screenshot: %s", screenshot_file)
        return screenshot_file

    def save_api_dump(self, name: str, request: dict, response: dict) -> Path:
        """Save API request/response dump.

        Args:
            name: Dump name
            request: Request data
            response: Response data

        Returns:
            Path to saved dump file
        """
        dump_file = self.current_run_dir / "dumps" / f"{name}.json"
        dump_file.parent.mkdir(parents=True, exist_ok=True)

        dump_data = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "response": response,
        }

        dump_file.write_text(json.dumps(dump_data, indent=2))
        logger.info("Saved API dump: %s", dump_file)
        return dump_file

    def save_error_trace(self, name: str, error_data: dict) -> Path:
        """Save error trace.

        Args:
            name: Error trace name
            error_data: Error information

        Returns:
            Path to saved error trace
        """
        error_file = self.current_run_dir / "errors" / f"{name}.json"
        error_file.parent.mkdir(parents=True, exist_ok=True)

        error_data["timestamp"] = datetime.now().isoformat()
        error_file.write_text(json.dumps(error_data, indent=2))
        logger.info("Saved error trace: %s", error_file)
        return error_file

    def save_json(self, name: str, data: Any) -> Path:
        """Save arbitrary JSON data.

        Args:
            name: File name
            data: Data to save

        Returns:
            Path to saved file
        """
        json_file = self.current_run_dir / f"{name}.json"
        json_file.write_text(json.dumps(data, indent=2, default=str))
        logger.info("Saved JSON: %s", json_file)
        return json_file

    def get_run_dir(self) -> Path:
        """Get current test run directory.

        Returns:
            Path to current run directory
        """
        return self.current_run_dir

    def cleanup_old_artifacts(self, keep_last: int = 10) -> None:
        """Clean up old artifact directories.

        Args:
            keep_last: Number of recent runs to keep
        """
        runs = sorted(
            [d for d in self.base_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        for old_run in runs[keep_last:]:
            try:
                shutil.rmtree(old_run)
                logger.info("Cleaned up old run: %s", old_run)
            except Exception as e:
                logger.warning("Failed to clean up %s: %s", old_run, e)

    def archive_run(self) -> Path:
        """Archive current test run.

        Returns:
            Path to archive file
        """
        archive_path = self.base_dir / f"{self.run_id}.tar.gz"
        shutil.make_archive(
            str(archive_path.with_suffix("")),
            "gztar",
            self.current_run_dir,
        )
        logger.info("Archived run to: %s", archive_path)
        return archive_path

    def get_artifact_summary(self) -> dict:
        """Get summary of artifacts for current run.

        Returns:
            Dictionary with artifact counts and sizes
        """
        summary = {
            "run_id": self.run_id,
            "run_dir": str(self.current_run_dir),
            "logs": (
                len(list((self.current_run_dir / "logs").glob("*.log")))
                if (self.current_run_dir / "logs").exists()
                else 0
            ),
            "screenshots": (
                len(list((self.current_run_dir / "screenshots").glob("*.png")))
                if (self.current_run_dir / "screenshots").exists()
                else 0
            ),
            "dumps": (
                len(list((self.current_run_dir / "dumps").glob("*.json")))
                if (self.current_run_dir / "dumps").exists()
                else 0
            ),
            "errors": (
                len(list((self.current_run_dir / "errors").glob("*.json")))
                if (self.current_run_dir / "errors").exists()
                else 0
            ),
        }
        return summary
