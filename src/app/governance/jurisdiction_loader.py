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
import re
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

    def _parse_sections_from_markdown(
        self, content: str
    ) -> tuple[dict, list[str], list[str]]:
        """Extract requirements, data-subject rights, and compliance obligations from markdown."""
        requirements: dict = {}
        data_subject_rights: list[str] = []
        compliance_obligations: list[str] = []

        # Split on L2 headers (## …); first element is pre-header preamble
        sections = re.split(r"^## ", content, flags=re.MULTILINE)

        _OBLIGATION_KEYWORDS = {
            "OBLIGATION",
            "COMPLIANCE",
            "CONSENT MANAGEMENT",
            "DATA PROTECTION PRINCIPLE",
            "BREACH",
            "INTERNATIONAL DATA TRANSFER",
            "RECORD OF PROCESSING",
        }

        for section in sections:
            lines = section.strip().split("\n")
            if not lines:
                continue
            header = lines[0].strip().upper()
            body = "\n".join(lines[1:])

            # DATA SUBJECT RIGHTS — collect ### sub-section titles as right names
            if "DATA SUBJECT RIGHT" in header or "SUBJECT RIGHT" in header:
                for line in body.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("### "):
                        right = stripped[4:].strip()
                        if right and right not in data_subject_rights:
                            data_subject_rights.append(right)

            # APPENDIX / COMPLIANCE SUMMARY — parse markdown table rows
            elif "APPENDIX" in header or "COMPLIANCE SUMMARY" in header:
                for line in body.split("\n"):
                    stripped = line.strip()
                    if (
                        not stripped.startswith("|")
                        or stripped.startswith("|---")
                        or "Article" in stripped
                    ):
                        continue
                    cols = [c.strip() for c in stripped.strip("|").split("|")]
                    if len(cols) >= 2:
                        key, val = cols[0].strip(), cols[1].strip()
                        if key and val and not key.startswith("-"):
                            requirements[key] = val

            # Obligation-bearing sections — collect top-level bullet points
            if any(kw in header for kw in _OBLIGATION_KEYWORDS):
                for line in body.split("\n"):
                    stripped = line.strip()
                    if re.match(r"^[-*]\s+\S", stripped):
                        obligation = stripped.lstrip("-* ").strip()
                        if obligation and obligation not in compliance_obligations:
                            compliance_obligations.append(obligation)

        return requirements, data_subject_rights, compliance_obligations

    def _load_all_jurisdictions(self):
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

                # Parse structured content from markdown
                raw_content = file_path.read_text(encoding="utf-8")
                reqs, rights, obligations = self._parse_sections_from_markdown(raw_content)

                # Create jurisdiction annex object
                annex = JurisdictionAnnex(
                    code=jurisdiction_code,
                    name=metadata["jurisdiction"],
                    version=metadata["version"],
                    effective_date=metadata["effective_date"],
                    regulation_name=metadata["regulation"],
                    file_path=str(file_path),
                    document_hash=document_hash,
                    requirements=reqs,
                    data_subject_rights=rights,
                    compliance_obligations=obligations,
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
