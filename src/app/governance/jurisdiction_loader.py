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

STATUS: PRODUCTION
"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Known incompatibilities ──────────────────────────────────
# Maps pairs of jurisdiction codes to lists of conflict descriptions.
# Used by validate_jurisdiction_selection to flag cross-border issues.
_KNOWN_CONFLICTS: dict[frozenset[str], list[str]] = {
    frozenset({"EU_GDPR", "US_CCPA"}): [
        "GDPR requires explicit consent while CCPA allows opt-out; "
        "apply GDPR (stricter) as the binding standard",
    ],
    frozenset({"EU_GDPR", "AU_PRIVACY"}): [
        "Australian Privacy Act allows broader exceptions for law-enforcement "
        "access; GDPR imposes additional safeguards for cross-border transfers",
    ],
}

# Retention keywords ranked by restrictiveness (strictest first)
_RETENTION_STRICTNESS = [
    "delete immediately",
    "delete upon request",
    "retain no longer than necessary",
    "retain for limited period",
    "retain as required by law",
]

# Security keywords that signal explicit requirements
_SECURITY_KEYWORDS = [
    "encryption",
    "pseudonymisation",
    "access control",
    "audit",
    "breach notification",
    "data protection impact",
    "security assessment",
    "penetration test",
]


@dataclass
class JurisdictionAnnex:
    """Represents a loaded jurisdictional annex."""

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
    retention_requirements: list[str] = field(default_factory=list)
    security_requirements: list[str] = field(default_factory=list)


class JurisdictionLoader:
    """Loads and validates jurisdictional annexes."""

    def __init__(self, legal_docs_dir: str = "docs/legal"):
        """Initialize jurisdiction loader."""
        self.legal_docs_dir = Path(legal_docs_dir)
        self.jurisdictions_dir = self.legal_docs_dir / "jurisdictions"
        self.loaded_jurisdictions: dict[str, JurisdictionAnnex] = {}

        # Ensure directory exists
        self.jurisdictions_dir.mkdir(parents=True, exist_ok=True)

        # Load all available jurisdictions
        self._load_all_jurisdictions()

    # ── Document parsing ──────────────────────────────────────

    def _compute_document_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of jurisdiction document."""
        with open(file_path, "rb") as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()

    def _extract_metadata_from_markdown(self, file_path: Path) -> dict:
        """Extract metadata from markdown document."""
        metadata = {
            "version": "1.0.0",
            "jurisdiction": "Unknown",
            "regulation": "Unknown",
            "effective_date": "Unknown",
        }

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

            for key, marker in [
                ("version", "**Version:**"),
                ("jurisdiction", "**Jurisdiction:**"),
                ("regulation", "**Regulation:**"),
                ("effective_date", "**Effective Date:**"),
            ]:
                if marker in content:
                    for line in content.split("\n"):
                        if marker in line:
                            metadata[key] = (
                                line.split(marker)[1].strip().split("**")[0].strip()
                            )
                            break

        return metadata

    def _parse_document_content(self, file_path: Path) -> dict:
        """Parse markdown document to extract structured data.

        Extracts:
        - data_subject_rights: From sections like "Consumer Rights", "Individual Rights"
        - compliance_obligations: From "Principles", "Obligations"
        - retention_requirements: From "Retention", "Data Storage"
        - security_requirements: From "Security", "Safeguards"
        """
        parsed: dict[str, list[str]] = {
            "data_subject_rights": [],
            "compliance_obligations": [],
            "retention_requirements": [],
            "security_requirements": [],
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            current_section: str | None = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect section headers
                if line.startswith("## "):
                    header = line.replace("## ", "").strip().lower()
                    if "rights" in header:
                        current_section = "rights"
                    elif any(
                        kw in header
                        for kw in ("principles", "obligations", "requirements")
                    ):
                        current_section = "obligations"
                    elif any(
                        kw in header for kw in ("retention", "storage", "deletion")
                    ):
                        current_section = "retention"
                    elif any(
                        kw in header for kw in ("security", "safeguard", "protection")
                    ):
                        current_section = "security"
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
                    elif current_section == "retention":
                        parsed["retention_requirements"].append(item)
                    elif current_section == "security":
                        parsed["security_requirements"].append(item)

            # Auto-extract security requirements from obligations text
            for obligation in parsed["compliance_obligations"]:
                ob_lower = obligation.lower()
                for kw in _SECURITY_KEYWORDS:
                    if (
                        kw in ob_lower
                        and obligation not in parsed["security_requirements"]
                    ):
                        parsed["security_requirements"].append(obligation)
                        break

        except Exception as e:
            logger.error("Error parsing document content for %s: %s", file_path, e)

        return parsed

    def _load_all_jurisdictions(self) -> None:
        """Load all jurisdictional annexes from the jurisdictions directory."""
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
                    retention_requirements=parsed_content.get(
                        "retention_requirements", []
                    ),
                    security_requirements=parsed_content.get(
                        "security_requirements", []
                    ),
                )

                self.loaded_jurisdictions[jurisdiction_code] = annex

            except Exception as e:
                logger.warning("Failed to load jurisdiction %s: %s", file_path, e)

    # ── Query ─────────────────────────────────────────────────

    def get_jurisdiction(self, code: str) -> JurisdictionAnnex | None:
        """Get a specific jurisdiction by code."""
        return self.loaded_jurisdictions.get(code)

    def list_available_jurisdictions(self) -> list[str]:
        """List all available jurisdiction codes."""
        return list(self.loaded_jurisdictions.keys())

    def get_all_jurisdictions(self) -> dict[str, JurisdictionAnnex]:
        """Get all loaded jurisdictions."""
        return self.loaded_jurisdictions

    # ── Compatibility validation ──────────────────────────────

    def validate_jurisdiction_selection(
        self, jurisdiction_codes: list[str]
    ) -> tuple[bool, list[str]]:
        """Validate that selected jurisdictions are available and compatible.

        Checks:
        1. All codes must be loaded
        2. Known cross-border conflicts are flagged as warnings
        3. Retention policy conflicts are detected

        Returns:
            tuple: (is_valid, list of error/warning messages)
        """
        errors: list[str] = []

        # 1. Check availability
        for code in jurisdiction_codes:
            if code not in self.loaded_jurisdictions:
                errors.append(f"Jurisdiction '{code}' not found or not loaded")

        if errors:
            # If any codes are missing, skip compatibility checks
            return False, errors

        # 2. Known cross-border conflicts
        warnings: list[str] = []
        for i, code_a in enumerate(jurisdiction_codes):
            for code_b in jurisdiction_codes[i + 1 :]:
                pair = frozenset({code_a, code_b})
                if pair in _KNOWN_CONFLICTS:
                    for conflict in _KNOWN_CONFLICTS[pair]:
                        warnings.append(
                            f"[COMPATIBILITY] {code_a} ↔ {code_b}: {conflict}"
                        )

        # 3. Retention policy conflicts
        retention_levels: dict[str, int] = {}
        for code in jurisdiction_codes:
            annex = self.loaded_jurisdictions[code]
            if annex.retention_requirements:
                # Find strictest retention level mentioned
                strictest = len(_RETENTION_STRICTNESS)
                for req in annex.retention_requirements:
                    req_lower = req.lower()
                    for idx, keyword in enumerate(_RETENTION_STRICTNESS):
                        if keyword in req_lower:
                            strictest = min(strictest, idx)
                            break
                retention_levels[code] = strictest

        if len(retention_levels) > 1:
            levels = list(retention_levels.values())
            if max(levels) - min(levels) > 2:
                strictest_code = min(retention_levels, key=retention_levels.get)  # type: ignore[arg-type]
                warnings.append(
                    f"[RETENTION] Significant retention policy gap detected; "
                    f"apply {strictest_code} (most restrictive) as binding"
                )

        all_messages = errors + warnings
        return len(errors) == 0, all_messages

    # ── Combined requirements ─────────────────────────────────

    def get_combined_requirements(
        self, jurisdiction_codes: list[str]
    ) -> dict[str, list[str]]:
        """Get combined requirements from multiple jurisdictions.

        Returns the union of all rights and obligations (most restrictive
        wins policy — the superset satisfies all jurisdictions).

        Returns:
            Dict with ``data_subject_rights``, ``compliance_obligations``,
            ``retention_requirements``, ``security_requirements``.
        """
        combined: dict[str, set[str]] = {
            "data_subject_rights": set(),
            "compliance_obligations": set(),
            "retention_requirements": set(),
            "security_requirements": set(),
        }

        for code in jurisdiction_codes:
            annex = self.get_jurisdiction(code)
            if annex:
                combined["data_subject_rights"].update(annex.data_subject_rights)
                combined["compliance_obligations"].update(annex.compliance_obligations)
                combined["retention_requirements"].update(annex.retention_requirements)
                combined["security_requirements"].update(annex.security_requirements)

        # Convert sets to sorted lists for deterministic output
        return {key: sorted(values) for key, values in combined.items()}


# Singleton instance
_jurisdiction_loader: JurisdictionLoader | None = None


def get_jurisdiction_loader(
    legal_docs_dir: str = "docs/legal",
) -> JurisdictionLoader:
    """Get or create the global jurisdiction loader instance."""
    global _jurisdiction_loader
    if _jurisdiction_loader is None:
        _jurisdiction_loader = JurisdictionLoader(legal_docs_dir=legal_docs_dir)
    return _jurisdiction_loader
