# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / validate_pack.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / validate_pack.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
TTP Pack Validator - Production-grade validation tool for texture pack metadata

This tool validates texture pack metadata against the official JSON schema,
performs additional semantic validation, and checks asset integrity.

Usage:
    python validate_pack.py <pack_directory>
    python validate_pack.py --strict <pack_directory>
    python validate_pack.py --check-assets <pack_directory>

Exit codes:
    0: Validation passed
    1: Validation failed
    2: Invalid arguments or file not found
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
from jsonschema import Draft7Validator, validators
from PIL import Image


class PackValidator:
    """
    Comprehensive texture pack validator with multi-level validation.

    Validation levels:
    1. Schema validation (JSON Schema conformance)
    2. Semantic validation (business rules, constraints)
    3. Asset validation (file existence, integrity, format)
    4. Security validation (path traversal, malicious content)
    """

    SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "pack-schema-v1.json"

    # Maximum file sizes by quality tier (bytes)
    MAX_SIZES = {
        "pixel": 10 * 1024 * 1024,        # 10 MB
        "standard": 50 * 1024 * 1024,     # 50 MB per file
        "high": 200 * 1024 * 1024,        # 200 MB per file
        "cinematic": 500 * 1024 * 1024,   # 500 MB per file
        "ultra": 1 * 1024 * 1024 * 1024,  # 1 GB per file
    }

    # Resolution constraints by quality tier
    RESOLUTION_CONSTRAINTS = {
        "pixel": (8, 128),           # Min-max dimension
        "standard": (256, 2048),
        "high": (1024, 4096),
        "cinematic": (2048, 8192),
        "ultra": (4096, 16384),
    }

    # Forbidden file path patterns (security)
    FORBIDDEN_PATTERNS = [
        "..",           # Path traversal
        "~",            # Home directory
        "/",            # Absolute paths
        "\\",           # Windows absolute paths
        "$",            # Environment variables
        "`",            # Command substitution
    ]

    def __init__(self, strict_mode: bool = False, check_assets: bool = False):
        """
        Initialize validator.

        Args:
            strict_mode: Enable strict validation (warnings become errors)
            check_assets: Validate actual asset files (slower but thorough)
        """
        self.strict_mode = strict_mode
        self.check_assets = check_assets
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        try:
            with open(self.SCHEMA_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Schema file not found: {self.SCHEMA_PATH}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid schema JSON: {e}", file=sys.stderr)
            sys.exit(2)

    def validate(self, pack_dir: Path) -> bool:
        """
        Main validation entry point.

        Args:
            pack_dir: Path to pack directory

        Returns:
            True if validation passed, False otherwise
        """
        if not pack_dir.exists():
            self._error(f"Pack directory not found: {pack_dir}")
            return False

        if not pack_dir.is_dir():
            self._error(f"Not a directory: {pack_dir}")
            return False

        # Find and load pack.json
        pack_json_path = pack_dir / "pack.json"
        if not pack_json_path.exists():
            self._error(f"pack.json not found in {pack_dir}")
            return False

        try:
            with open(pack_json_path, 'r', encoding='utf-8') as f:
                pack_data = json.load(f)
        except json.JSONDecodeError as e:
            self._error(f"Invalid JSON in pack.json: {e}")
            return False
        except UnicodeDecodeError:
            self._error("pack.json is not valid UTF-8")
            return False

        # Level 1: Schema validation
        self._validate_schema(pack_data)

        # Level 2: Semantic validation
        self._validate_semantics(pack_data, pack_dir)

        # Level 3: Asset validation (if enabled)
        if self.check_assets:
            self._validate_assets(pack_data, pack_dir)

        # Level 4: Security validation
        self._validate_security(pack_data, pack_dir)

        # Report results
        return self._report_results()

    def _validate_schema(self, pack_data: Dict[str, Any]) -> None:
        """Validate against JSON schema."""
        try:
            Draft7Validator(self.schema).validate(pack_data)
        except jsonschema.ValidationError as e:
            self._error(f"Schema validation failed: {e.message}")
            if e.path:
                path = ".".join(str(p) for p in e.path)
                self._error(f"  At: {path}")
            if e.schema_path:
                schema_path = ".".join(str(p) for p in e.schema_path)
                self._error(f"  Schema path: {schema_path}")
        except jsonschema.SchemaError as e:
            self._error(f"Invalid schema: {e.message}")

    def _validate_semantics(self, pack_data: Dict[str, Any], pack_dir: Path) -> None:
        """Validate business rules and constraints."""
        # Check quality tier vs resolution constraints
        quality_tier = pack_data.get("qualityTier")
        if quality_tier and "technical" in pack_data:
            min_res, max_res = self.RESOLUTION_CONSTRAINTS.get(quality_tier, (0, 99999))

            # Parse resolution strings
            max_resolution = pack_data["technical"].get("maximumResolution", "")
            if max_resolution:
                try:
                    width, height = map(int, max_resolution.split("x"))
                    max_dim = max(width, height)

                    if max_dim > max_res:
                        self._warning(
                            f"Maximum resolution {max_resolution} exceeds recommended "
                            f"maximum for '{quality_tier}' tier ({max_res}px)"
                        )
                    if max_dim < min_res:
                        self._error(
                            f"Maximum resolution {max_resolution} below minimum "
                            f"for '{quality_tier}' tier ({min_res}px)"
                        )
                except (ValueError, AttributeError):
                    self._warning(f"Invalid resolution format: {max_resolution}")

        # Check asset count consistency
        declared_count = pack_data.get("technical", {}).get("assetCount", 0)
        actual_count = len(pack_data.get("assets", []))
        if declared_count != actual_count:
            self._error(
                f"Asset count mismatch: declared {declared_count}, "
                f"but found {actual_count} assets"
            )

        # Check version format
        version = pack_data.get("version", "")
        if version:
            parts = version.split(".")
            if len(parts) < 3:
                self._error(f"Version '{version}' must have at least 3 parts (major.minor.patch)")

        # Check for required preview images
        preview = pack_data.get("preview", {})
        if not preview:
            self._warning("No preview images defined - pack may not render well in UI")

        # Validate dependencies exist
        dependencies = pack_data.get("dependencies", [])
        for dep in dependencies:
            if not dep.get("optional", False):
                self._warning(f"Required dependency: {dep.get('name')} {dep.get('version')}")

        # Check license compatibility
        license_type = pack_data.get("license")
        if license_type == "Proprietary":
            license_details = pack_data.get("licenseDetails", {})
            if not license_details.get("text") and not license_details.get("url"):
                self._error("Proprietary license must include license text or URL")

    def _validate_assets(self, pack_data: Dict[str, Any], pack_dir: Path) -> None:
        """Validate actual asset files."""
        assets = pack_data.get("assets", [])
        quality_tier = pack_data.get("qualityTier", "standard")
        max_file_size = self.MAX_SIZES.get(quality_tier, 100 * 1024 * 1024)

        for idx, asset in enumerate(assets):
            asset_path_str = asset.get("path") or asset.get("filename")
            if not asset_path_str:
                self._error(f"Asset {idx}: missing path/filename")
                continue

            asset_path = pack_dir / asset_path_str

            # Check file exists
            if not asset_path.exists():
                self._error(f"Asset file not found: {asset_path_str}")
                continue

            # Check file size
            actual_size = asset_path.stat().st_size
            declared_size = asset.get("sizeBytes")

            if declared_size and abs(actual_size - declared_size) > 1024:
                self._error(
                    f"Asset {asset_path_str}: size mismatch "
                    f"(declared {declared_size}, actual {actual_size})"
                )

            if actual_size > max_file_size:
                self._error(
                    f"Asset {asset_path_str}: size {actual_size} exceeds "
                    f"limit for '{quality_tier}' tier ({max_file_size})"
                )

            # Verify checksum
            checksum_data = asset.get("checksum")
            if checksum_data:
                self._verify_checksum(asset_path, checksum_data, asset_path_str)

            # Validate image properties (if image file)
            if asset.get("format") in ["png", "jpg", "jpeg", "tiff", "tif", "bmp"]:
                self._validate_image_properties(asset_path, asset, asset_path_str)

    def _verify_checksum(
        self,
        file_path: Path,
        checksum_data: Dict[str, str],
        asset_name: str
    ) -> None:
        """Verify file checksum."""
        algorithm = checksum_data.get("algorithm", "sha256")
        expected_checksum = checksum_data.get("value", "").lower()

        if algorithm == "sha256":
            hasher = hashlib.sha256()
        elif algorithm == "sha512":
            hasher = hashlib.sha512()
        elif algorithm == "md5":
            hasher = hashlib.md5()
            self._warning(f"MD5 is deprecated, use SHA-256 instead: {asset_name}")
        else:
            self._error(f"Unknown checksum algorithm: {algorithm}")
            return

        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)

            actual_checksum = hasher.hexdigest().lower()
            if actual_checksum != expected_checksum:
                self._error(
                    f"Checksum mismatch for {asset_name}: "
                    f"expected {expected_checksum}, got {actual_checksum}"
                )
        except IOError as e:
            self._error(f"Failed to read file for checksum: {asset_name}: {e}")

    def _validate_image_properties(
        self,
        image_path: Path,
        asset: Dict[str, Any],
        asset_name: str
    ) -> None:
        """Validate image file properties match metadata."""
        try:
            with Image.open(image_path) as img:
                # Check resolution
                declared_res = asset.get("resolution", {})
                if declared_res:
                    declared_w = declared_res.get("width")
                    declared_h = declared_res.get("height")
                    actual_w, actual_h = img.size

                    if declared_w != actual_w or declared_h != actual_h:
                        self._error(
                            f"Resolution mismatch for {asset_name}: "
                            f"declared {declared_w}x{declared_h}, "
                            f"actual {actual_w}x{actual_h}"
                        )

                # Check channels
                declared_channels = asset.get("channels")
                actual_channels = len(img.getbands())
                if declared_channels and declared_channels != actual_channels:
                    self._warning(
                        f"Channel count mismatch for {asset_name}: "
                        f"declared {declared_channels}, actual {actual_channels}"
                    )

                # Verify power-of-2 dimensions for better GPU performance
                width, height = img.size
                if not self._is_power_of_2(width) or not self._is_power_of_2(height):
                    self._warning(
                        f"Non-power-of-2 texture dimensions for {asset_name}: "
                        f"{width}x{height}. May cause performance issues on some platforms."
                    )

        except Exception as e:
            self._error(f"Failed to validate image {asset_name}: {e}")

    def _validate_security(self, pack_data: Dict[str, Any], pack_dir: Path) -> None:
        """Security validation to prevent malicious packs."""
        # Check for path traversal in asset paths
        assets = pack_data.get("assets", [])
        for asset in assets:
            path = asset.get("path") or asset.get("filename", "")

            # Check for forbidden patterns
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in path:
                    self._error(
                        f"Security violation: forbidden pattern '{pattern}' "
                        f"in path: {path}"
                    )

            # Ensure path stays within pack directory
            try:
                full_path = (pack_dir / path).resolve()
                if not str(full_path).startswith(str(pack_dir.resolve())):
                    self._error(
                        f"Security violation: path escapes pack directory: {path}"
                    )
            except Exception as e:
                self._error(f"Invalid path: {path}: {e}")

        # Check total pack size (prevent zip bombs)
        total_size = pack_data.get("technical", {}).get("totalSizeBytes", 0)
        if total_size > 100 * 1024 * 1024 * 1024:  # 100 GB
            self._error(f"Pack size {total_size} exceeds maximum (100 GB)")

    def _is_power_of_2(self, n: int) -> bool:
        """Check if number is power of 2."""
        return n > 0 and (n & (n - 1)) == 0

    def _error(self, message: str) -> None:
        """Record an error."""
        self.errors.append(message)

    def _warning(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)

    def _report_results(self) -> bool:
        """Report validation results and return success status."""
        # Print warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):", file=sys.stderr)
            for warning in self.warnings:
                print(f"  - {warning}", file=sys.stderr)

        # Print errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):", file=sys.stderr)
            for error in self.errors:
                print(f"  - {error}", file=sys.stderr)
            return False

        # Check if strict mode treats warnings as errors
        if self.strict_mode and self.warnings:
            print("\n❌ VALIDATION FAILED (strict mode, warnings present)", file=sys.stderr)
            return False

        print("\n✅ VALIDATION PASSED", file=sys.stderr)
        if self.warnings:
            print(f"   ({len(self.warnings)} warnings)", file=sys.stderr)
        return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate TTP texture pack metadata and assets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s packs/my-texture-pack
  %(prog)s --strict --check-assets packs/cinematic-pack
  %(prog)s --help
        """
    )

    parser.add_argument(
        "pack_dir",
        type=Path,
        help="Path to texture pack directory"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: treat warnings as errors"
    )

    parser.add_argument(
        "--check-assets",
        action="store_true",
        help="Validate actual asset files (slower but thorough)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )

    args = parser.parse_args()

    # Create validator and run validation
    validator = PackValidator(
        strict_mode=args.strict,
        check_assets=args.check_assets
    )

    success = validator.validate(args.pack_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
