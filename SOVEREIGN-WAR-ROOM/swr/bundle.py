"""
Bundle Manager for SOVEREIGN WAR ROOM

Manages scenario bundles, AI system packages, and deployment artifacts.
Handles packaging, versioning, and distribution of test scenarios.
"""

import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


class BundleManager:
    """Manages scenario bundles and AI system packages."""

    def __init__(self, bundle_dir: Path | None = None):
        """
        Initialize bundle manager.
        
        Args:
            bundle_dir: Directory for storing bundles (default: ./bundles)
        """
        self.bundle_dir = bundle_dir or Path("./bundles")
        self.bundle_dir.mkdir(parents=True, exist_ok=True)

    def create_scenario_bundle(
        self,
        name: str,
        scenarios: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Create a scenario bundle package.
        
        Args:
            name: Bundle name
            scenarios: List of scenario definitions
            metadata: Optional bundle metadata
            
        Returns:
            Path to created bundle file
        """
        bundle_id = hashlib.sha256(f"{name}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        bundle_filename = f"{name}_{bundle_id}.swrb"
        bundle_path = self.bundle_dir / bundle_filename

        # Create bundle metadata
        bundle_data = {
            "bundle_id": bundle_id,
            "name": name,
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(),
            "scenario_count": len(scenarios),
            "metadata": metadata or {},
            "scenarios": scenarios
        }

        # Calculate bundle hash
        bundle_json = json.dumps(bundle_data, sort_keys=True)
        bundle_hash = hashlib.sha3_256(bundle_json.encode()).hexdigest()
        bundle_data["hash"] = bundle_hash

        # Create zip bundle
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write manifest
            manifest_path = tmp_path / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(bundle_data, f, indent=2)

            # Write individual scenario files
            scenarios_dir = tmp_path / "scenarios"
            scenarios_dir.mkdir()

            for idx, scenario in enumerate(scenarios):
                scenario_file = scenarios_dir / f"scenario_{idx:03d}.json"
                with open(scenario_file, "w") as f:
                    json.dump(scenario, f, indent=2)

            # Create zip archive
            with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in tmp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(tmp_path)
                        zipf.write(file_path, arcname)

        return str(bundle_path)

    def load_scenario_bundle(self, bundle_path: str) -> dict[str, Any]:
        """
        Load scenario bundle from file.
        
        Args:
            bundle_path: Path to bundle file
            
        Returns:
            Bundle data dictionary
        """
        bundle_path = Path(bundle_path)

        if not bundle_path.exists():
            raise FileNotFoundError(f"Bundle not found: {bundle_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Extract bundle
            with zipfile.ZipFile(bundle_path, "r") as zipf:
                zipf.extractall(tmp_path)

            # Load manifest
            manifest_path = tmp_path / "manifest.json"
            with open(manifest_path) as f:
                bundle_data = json.load(f)

            # Verify bundle hash
            stored_hash = bundle_data.pop("hash", None)
            bundle_json = json.dumps(bundle_data, sort_keys=True)
            computed_hash = hashlib.sha3_256(bundle_json.encode()).hexdigest()

            if stored_hash != computed_hash:
                raise ValueError("Bundle integrity check failed: hash mismatch")

            bundle_data["hash"] = stored_hash

            return bundle_data

    def list_bundles(self) -> list[dict[str, Any]]:
        """
        List all available bundles.
        
        Returns:
            List of bundle metadata dictionaries
        """
        bundles = []

        for bundle_file in self.bundle_dir.glob("*.swrb"):
            try:
                bundle_data = self.load_scenario_bundle(str(bundle_file))
                bundles.append({
                    "file": str(bundle_file),
                    "bundle_id": bundle_data["bundle_id"],
                    "name": bundle_data["name"],
                    "version": bundle_data["version"],
                    "created_at": bundle_data["created_at"],
                    "scenario_count": bundle_data["scenario_count"]
                })
            except Exception:
                # Skip invalid bundles
                continue

        return bundles

    def create_ai_system_package(
        self,
        system_id: str,
        system_data: dict[str, Any],
        files: list[Path] | None = None
    ) -> str:
        """
        Create AI system package for testing.
        
        Args:
            system_id: Unique system identifier
            system_data: System configuration and metadata
            files: Optional list of files to include
            
        Returns:
            Path to created package
        """
        package_filename = f"ai_system_{system_id}.swrp"
        package_path = self.bundle_dir / package_filename

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Write system manifest
            manifest = {
                "system_id": system_id,
                "created_at": datetime.utcnow().isoformat(),
                "system_data": system_data
            }

            manifest_path = tmp_path / "system_manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)

            # Copy additional files
            if files:
                files_dir = tmp_path / "files"
                files_dir.mkdir()

                for file_path in files:
                    if file_path.exists():
                        dest = files_dir / file_path.name
                        shutil.copy2(file_path, dest)

            # Create package
            with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in tmp_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(tmp_path)
                        zipf.write(file_path, arcname)

        return str(package_path)

    def export_results(
        self,
        results: list[dict[str, Any]],
        export_name: str,
        format: str = "json"
    ) -> str:
        """
        Export test results to file.
        
        Args:
            results: List of test results
            export_name: Name for export file
            format: Export format (json, csv)
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            export_filename = f"{export_name}_{timestamp}.json"
            export_path = self.bundle_dir / export_filename

            with open(export_path, "w") as f:
                json.dump(results, f, indent=2)

        elif format == "csv":
            export_filename = f"{export_name}_{timestamp}.csv"
            export_path = self.bundle_dir / export_filename

            # Simple CSV export
            if results:
                headers = results[0].keys()
                with open(export_path, "w") as f:
                    f.write(",".join(headers) + "\n")
                    for result in results:
                        values = [str(result.get(h, "")) for h in headers]
                        f.write(",".join(values) + "\n")

        else:
            raise ValueError(f"Unsupported export format: {format}")

        return str(export_path)

    def verify_bundle_integrity(self, bundle_path: str) -> bool:
        """
        Verify bundle file integrity.
        
        Args:
            bundle_path: Path to bundle file
            
        Returns:
            True if bundle is valid and untampered
        """
        try:
            bundle_data = self.load_scenario_bundle(bundle_path)
            return True
        except Exception:
            return False
