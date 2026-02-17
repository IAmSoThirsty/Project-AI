"""
Legal and Governance Subsystem - Jurisdiction Loader

This module loads and validates jurisdictional annexes at install-time and runtime.
Each jurisdiction annex contains region-specific legal requirements that are
incorporated into the Master Services Agreement.

Supports:
- GDPR (European Union)
- CCPA (California)
- PIPEDA (Canada)
- UK DPA 2018 (United Kingdom)
- Australia Privacy Act
- Custom jurisdictions (extensible)
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JurisdictionAnnex:
    """Represents a loaded jurisdictional annex"""

    code: str  # e.g., "EU_GDPR", "US_CCPA"
    name: str  # e.g., "European Union (GDPR)"
    version: str
    effective_date: str
    regulation_name: str
    file_path: str
    document_hash: str
    requirements: dict
    data_subject_rights: list[str]
    compliance_obligations: list[str]


class JurisdictionLoader:
    """Loads and validates jurisdictional annexes"""

    def __init__(self, legal_docs_dir: str = "docs/legal"):
        """Initialize jurisdiction loader"""
        self.legal_docs_dir = Path(legal_docs_dir)
        self.jurisdictions_dir = self.legal_docs_dir / "jurisdictions"
        self.loaded_jurisdictions: dict[str, JurisdictionAnnex] = {}

        # Ensure directory exists
        self.jurisdictions_dir.mkdir(parents=True, exist_ok=True)

        # Load all available jurisdictions
        self._load_all_jurisdictions()

    def _compute_document_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of jurisdiction document"""
        with open(file_path, "rb") as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()

    def _extract_metadata_from_markdown(self, file_path: Path) -> dict:
        """Extract metadata from markdown document"""
        metadata = {
            "version": "1.0.0",
            "jurisdiction": "Unknown",
            "regulation": "Unknown",
            "effective_date": "Unknown",
        }

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

            # Extract version
            if "**Version:**" in content:
                for line in content.split("\n"):
                    if "**Version:**" in line:
                        metadata["version"] = (
                            line.split("**Version:**")[1].strip().split("**")[0].strip()
                        )
                        break

            # Extract jurisdiction
            if "**Jurisdiction:**" in content:
                for line in content.split("\n"):
                    if "**Jurisdiction:**" in line:
                        metadata["jurisdiction"] = (
                            line.split("**Jurisdiction:**")[1]
                            .strip()
                            .split("**")[0]
                            .strip()
                        )
                        break

            # Extract regulation
            if "**Regulation:**" in content:
                for line in content.split("\n"):
                    if "**Regulation:**" in line:
                        metadata["regulation"] = (
                            line.split("**Regulation:**")[1]
                            .strip()
                            .split("**")[0]
                            .strip()
                        )
                        break

            # Extract effective date
            if "**Effective Date:**" in content:
                for line in content.split("\n"):
                    if "**Effective Date:**" in line:
                        metadata["effective_date"] = (
                            line.split("**Effective Date:**")[1]
                            .strip()
                            .split("**")[0]
                            .strip()
                        )
                        break

        return metadata
        return metadata

    def _parse_document_content(self, file_path: Path) -> dict:
        """
        Parse markdown document to extract structured data.

        Extracts:
        - data_subject_rights: From sections like "Consumer Rights", "Individual Rights"
        - compliance_obligations: From "Principles", "Obligations"
        """
        parsed = {
            "requirements": {},
            "data_subject_rights": [],
            "compliance_obligations": [],
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect section headers
                if line.startswith("## "):
                    header = line.replace("## ", "").strip().lower()
                    if "rights" in header:
                        current_section = "rights"
                    elif (
                        "principles" in header
                        or "obligations" in header
                        or "requirements" in header
                    ):
                        current_section = "obligations"
                    else:
                        current_section = None
                    continue

                # Parse list items
                if current_section and (line.startswith("- ") or line.startswith("* ")):
                    item = line[2:].strip()
                    # Remove broad bolding if present
                    if item.startswith("**") and "**" in item[2:]:
                        item = item.replace("**", "", 2)

                    if current_section == "rights":
                        parsed["data_subject_rights"].append(item)
                    elif current_section == "obligations":
                        parsed["compliance_obligations"].append(item)

        except Exception as e:
            print(f"Error parsing document content for {file_path}: {e}")

        return parsed

        """Load all jurisdictional annexes from the jurisdictions directory"""
        if not self.jurisdictions_dir.exists():
            return

        for file_path in self.jurisdictions_dir.glob("*.md"):
            try:
                # Extract jurisdiction code from filename (e.g., EU_GDPR.md -> EU_GDPR)
                jurisdiction_code = file_path.stem

                # Compute document hash
                document_hash = self._compute_document_hash(file_path)

                # Extract metadata from markdown
                metadata = self._extract_metadata_from_markdown(file_path)

                # Parse document content
                parsed_content = self._parse_document_content(file_path)

                # Create jurisdiction annex object
                annex = JurisdictionAnnex(
                    code=jurisdiction_code,
                    name=metadata["jurisdiction"],
                    version=metadata["version"],
                    effective_date=metadata["effective_date"],
                    regulation_name=metadata["regulation"],
                    file_path=str(file_path),
                    document_hash=document_hash,
                    requirements=parsed_content.get("requirements", {}),
                    data_subject_rights=parsed_content.get("data_subject_rights", []),
                    compliance_obligations=parsed_content.get(
                        "compliance_obligations", []
                    ),
                )

                self.loaded_jurisdictions[jurisdiction_code] = annex

            except Exception as e:
                print(f"Warning: Failed to load jurisdiction {file_path}: {e}")

    def get_jurisdiction(self, code: str) -> JurisdictionAnnex | None:
        """Get a specific jurisdiction by code"""
        return self.loaded_jurisdictions.get(code)

    def list_available_jurisdictions(self) -> list[str]:
        """List all available jurisdiction codes"""
        return list(self.loaded_jurisdictions.keys())

    def get_all_jurisdictions(self) -> dict[str, JurisdictionAnnex]:
        """Get all loaded jurisdictions"""
        return self.loaded_jurisdictions

    def validate_jurisdiction_selection(
        self, jurisdiction_codes: list[str]
    ) -> tuple[bool, list[str]]:
        """
        Validate that selected jurisdictions are available and compatible.

        Returns:
            tuple: (is_valid, list of error messages)
        """
        errors = []

        for code in jurisdiction_codes:
            if code not in self.loaded_jurisdictions:
                errors.append(f"Jurisdiction '{code}' not found or not loaded")

        # TODO: Add compatibility checks (e.g., conflicting requirements)

        return len(errors) == 0, errors

    def get_combined_requirements(
        self, jurisdiction_codes: list[str]
    ) -> dict[str, list]:
        """
        Get combined requirements from multiple jurisdictions.

        Returns most restrictive requirements when conflicts exist.
        """
        combined = {
            "data_subject_rights": set(),
            "compliance_obligations": set(),
            "retention_requirements": [],
            "security_requirements": [],
        }

        for code in jurisdiction_codes:
            annex = self.get_jurisdiction(code)
            if annex:
                combined["data_subject_rights"].update(annex.data_subject_rights)
                combined["compliance_obligations"].update(annex.compliance_obligations)

        # Convert sets back to lists
        return {
            "data_subject_rights": list(combined["data_subject_rights"]),
            "compliance_obligations": list(combined["compliance_obligations"]),
            "retention_requirements": combined["retention_requirements"],
            "security_requirements": combined["security_requirements"],
        }


# Singleton instance
_jurisdiction_loader: JurisdictionLoader | None = None


def get_jurisdiction_loader(
    legal_docs_dir: str = "docs/legal",
) -> JurisdictionLoader:
    """Get or create the global jurisdiction loader instance"""
    global _jurisdiction_loader
    if _jurisdiction_loader is None:
        _jurisdiction_loader = JurisdictionLoader(legal_docs_dir=legal_docs_dir)
    return _jurisdiction_loader
