#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Documentation Generator
=======================

Auto-generate documentation from execution state and build artifacts.
Provides living documentation that reflects actual system behavior.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..audit.audit_integration import BuildAuditIntegration
from ..capsules.capsule_engine import CapsuleEngine
from ..cognition.state_integration import BuildStateIntegration
from project_ai.engine.state.state_manager import StateManager

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class APIDocumentation:
    """Structured API endpoint documentation metadata."""

    endpoint: str
    method: str
    description: str
    parameters: list[dict[str, Any]]
    response_schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "description": self.description,
            "parameters": self.parameters,
            "response_schema": self.response_schema,
        }


class DocumentationGenerator:
    """
    Generates living documentation from build execution state.
    Produces markdown documentation that reflects actual system behavior.
    """

    def __init__(
        self,
        capsule_engine: CapsuleEngine | None = None,
        state_integration: BuildStateIntegration | None = None,
        audit_integration: BuildAuditIntegration | None = None,
        output_dir: Path | None = None,
    ):
        """
        Initialize documentation generator.

        Args:
            capsule_engine: Capsule engine instance
            state_integration: State integration instance
            audit_integration: Audit integration instance
            output_dir: Output directory for documentation
        """
        self.capsule_engine = capsule_engine or CapsuleEngine()
        self.state_integration = state_integration or BuildStateIntegration(
            state_manager=StateManager(config={})
        )
        self.audit_integration = audit_integration or BuildAuditIntegration()
        self.output_dir = output_dir or Path("docs/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_docs: list[APIDocumentation] = []
        logger.info("Documentation generator initialized: %s", self.output_dir)

    def add_endpoint_documentation(self, documentation: APIDocumentation) -> None:
        """Add endpoint documentation to in-memory registry."""
        self.api_docs.append(documentation)

    def validate_documentation(self, documentation: APIDocumentation) -> bool:
        """Validate minimum endpoint documentation contract."""
        if not documentation.endpoint.startswith("/"):
            return False
        if documentation.method.upper() not in {
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
            "HEAD",
        }:
            return False
        if not documentation.description.strip():
            return False
        return True

    def generate_openapi_spec(self) -> dict[str, Any]:
        """Generate OpenAPI 3.0 spec from registered endpoint docs."""
        paths: dict[str, Any] = {}

        for doc in self.api_docs:
            if not self.validate_documentation(doc):
                continue

            endpoint = doc.endpoint
            method = doc.method.lower()
            paths.setdefault(endpoint, {})[method] = {
                "summary": doc.description,
                "parameters": doc.parameters,
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": doc.response_schema,
                            }
                        },
                    }
                },
            }

        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Gradle Evolution Verifiability API",
                "version": "1.0.0",
            },
            "paths": paths,
        }

    def generate_markdown_docs(self) -> str:
        """Generate Markdown API docs from registered endpoint docs."""
        lines = ["# API Documentation", ""]

        for doc in self.api_docs:
            lines.append(f"## {doc.method.upper()} {doc.endpoint}")
            lines.append("")
            lines.append(doc.description)
            lines.append("")
            if doc.parameters:
                lines.append("### Parameters")
                lines.append("")
                for param in doc.parameters:
                    lines.append(
                        f"- `{param.get('name', 'param')}` ({param.get('type', 'string')}): "
                        f"{param.get('description', '')}"
                    )
                lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_postman_collection(self) -> dict[str, Any]:
        """Generate Postman collection JSON from registered endpoint docs."""
        items = []
        for doc in self.api_docs:
            items.append(
                {
                    "name": f"{doc.method.upper()} {doc.endpoint}",
                    "request": {
                        "method": doc.method.upper(),
                        "url": {
                            "raw": f"{{{{baseUrl}}}}{doc.endpoint}",
                            "host": ["{{baseUrl}}"],
                            "path": [p for p in doc.endpoint.split("/") if p],
                        },
                        "description": doc.description,
                    },
                }
            )

        return {
            "info": {
                "name": "Gradle Evolution API",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": items,
        }

    def export_documentation(self, output_path: Path, format: str = "markdown") -> None:
        """Export generated documentation to disk."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            output.write_text(self.generate_markdown_docs(), encoding="utf-8")
        elif format == "openapi":
            output.write_text(
                json.dumps(self.generate_openapi_spec(), indent=2),
                encoding="utf-8",
            )
        elif format == "postman":
            output.write_text(
                json.dumps(self.generate_postman_collection(), indent=2),
                encoding="utf-8",
            )
        else:
            raise ValueError(f"Unsupported documentation format: {format}")

    def generate_examples(self, endpoint: str) -> dict[str, Any]:
        """Generate request/response examples for a documented endpoint."""
        doc = next((d for d in self.api_docs if d.endpoint == endpoint), None)
        if doc is None:
            return {"error": "endpoint_not_found"}

        return {
            "request": {
                "method": doc.method.upper(),
                "url": endpoint,
                "parameters": doc.parameters,
            },
            "response": {
                "status": 200,
                "schema": doc.response_schema,
            },
        }

    def generate_build_history_doc(self, limit: int = 50) -> Path:
        """
        Generate build history documentation.

        Args:
            limit: Number of builds to include

        Returns:
            Path to generated document
        """
        try:
            history = self.state_integration.get_build_history(limit=limit)
            stats = self.state_integration.get_build_statistics()

            doc = self._build_markdown_header("Build History")

            # Statistics section
            doc += "\n## Summary Statistics\n\n"
            doc += f"- **Total Builds**: {stats.get('total_builds', 0)}\n"
            doc += f"- **Successful Builds**: {stats.get('successful_builds', 0)}\n"
            doc += f"- **Failed Builds**: {stats.get('failed_builds', 0)}\n"
            doc += f"- **Average Duration**: {stats.get('average_duration_seconds', 0):.2f}s\n"

            # Build history table
            doc += "\n## Recent Builds\n\n"
            doc += "| Build ID | Timestamp | Tasks | Duration | Status |\n"
            doc += "|----------|-----------|-------|----------|--------|\n"

            for episode in history:
                build_id = episode.get("build_id", "N/A")
                timestamp = episode.get("timestamp", "N/A")
                tasks = ", ".join(episode.get("tasks", [])[:3])
                if len(episode.get("tasks", [])) > 3:
                    tasks += "..."

                result = episode.get("result", {})
                duration = result.get("duration_seconds", 0)
                success = result.get("success", False)
                status = "✅ Success" if success else "❌ Failed"

                doc += f"| {build_id[:8]} | {timestamp[:19]} | {tasks} | {duration:.2f}s | {status} |\n"

            # Write to file
            output_path = self.output_dir / "build-history.md"
            output_path.write_text(doc)

            logger.info("Generated build history doc: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Error generating build history doc: %s", e, exc_info=True)
            raise

    def generate_capsule_registry_doc(self) -> Path:
        """
        Generate capsule registry documentation.

        Returns:
            Path to generated document
        """
        try:
            doc = self._build_markdown_header("Build Capsule Registry")

            doc += "\n## Overview\n\n"
            doc += f"Total capsules: **{len(self.capsule_engine.capsules)}**\n\n"

            doc += "## Capsules\n\n"

            for capsule in sorted(
                self.capsule_engine.capsules.values(),
                key=lambda c: c.timestamp,
                reverse=True,
            ):
                doc += f"### Capsule: `{capsule.capsule_id}`\n\n"
                doc += f"- **Timestamp**: {capsule.timestamp}\n"
                doc += f"- **Merkle Root**: `{capsule.merkle_root}`\n"
                doc += f"- **Tasks**: {len(capsule.tasks)}\n"
                doc += f"- **Inputs**: {len(capsule.inputs)}\n"
                doc += f"- **Outputs**: {len(capsule.outputs)}\n"

                # Tasks list
                doc += "\n**Tasks Executed**:\n"
                for task in capsule.tasks:
                    doc += f"- `{task}`\n"

                doc += "\n---\n\n"

            output_path = self.output_dir / "capsule-registry.md"
            output_path.write_text(doc)

            logger.info("Generated capsule registry doc: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Error generating capsule registry doc: %s", e, exc_info=True)
            raise

    def generate_audit_summary_doc(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> Path:
        """
        Generate audit summary documentation.

        Args:
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            Path to generated document
        """
        try:
            report = self.audit_integration.generate_audit_report(
                start_time=start_time, end_time=end_time
            )

            doc = self._build_markdown_header("Audit Summary")

            # Period info
            doc += "\n## Report Period\n\n"
            if start_time:
                doc += f"- **Start**: {start_time.isoformat()}\n"
            if end_time:
                doc += f"- **End**: {end_time.isoformat()}\n"
            doc += f"- **Total Events**: {report.get('total_events', 0)}\n"

            # Event counts
            doc += "\n## Event Distribution\n\n"
            event_counts = report.get("event_counts", {})
            for event_type, count in sorted(event_counts.items()):
                doc += f"- **{event_type}**: {count}\n"

            # Policy decisions
            doc += "\n## Policy Decisions\n\n"
            policy_decisions = report.get("policy_decisions", {})
            doc += f"- **Allowed**: {policy_decisions.get('allowed', 0)}\n"
            doc += f"- **Denied**: {policy_decisions.get('denied', 0)}\n"

            # Security events
            doc += "\n## Security Events\n\n"
            security_events = report.get("security_events", {})
            doc += f"- **Allowed**: {security_events.get('allowed', 0)}\n"
            doc += f"- **Denied**: {security_events.get('denied', 0)}\n"

            output_path = self.output_dir / "audit-summary.md"
            output_path.write_text(doc)

            logger.info("Generated audit summary doc: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Error generating audit summary doc: %s", e, exc_info=True)
            raise

    def generate_api_reference_doc(self) -> Path:
        """
        Generate API reference documentation.

        Returns:
            Path to generated document
        """
        try:
            doc = self._build_markdown_header("Verifiability API Reference")

            doc += "\n## Base URL\n\n"
            doc += "```\nhttp://localhost:8080/api/v1\n```\n\n"

            # Endpoints
            endpoints = [
                {
                    "method": "GET",
                    "path": "/health",
                    "description": "Health check endpoint",
                },
                {
                    "method": "GET",
                    "path": "/capsules",
                    "description": "List all build capsules",
                },
                {
                    "method": "GET",
                    "path": "/capsules/<capsule_id>",
                    "description": "Get specific capsule details",
                },
                {
                    "method": "POST",
                    "path": "/capsules/<capsule_id>/verify",
                    "description": "Verify capsule integrity",
                },
                {
                    "method": "POST",
                    "path": "/capsules/<capsule_id>/replay",
                    "description": "Replay build from capsule",
                },
                {
                    "method": "POST",
                    "path": "/capsules/diff",
                    "description": "Compare two capsules",
                },
                {
                    "method": "GET",
                    "path": "/audit/events",
                    "description": "Get recent audit events",
                },
                {
                    "method": "GET",
                    "path": "/audit/report",
                    "description": "Generate audit report",
                },
                {
                    "method": "GET",
                    "path": "/proof/<capsule_id>",
                    "description": "Get cryptographic proof package",
                },
                {
                    "method": "GET",
                    "path": "/statistics",
                    "description": "Get API statistics",
                },
            ]

            doc += "## Endpoints\n\n"

            for endpoint in endpoints:
                doc += f"### `{endpoint['method']} {endpoint['path']}`\n\n"
                doc += f"{endpoint['description']}\n\n"

                doc += "**Example Request**:\n"
                doc += f"```bash\ncurl -X {endpoint['method']} http://localhost:8080/api/v1{endpoint['path']}\n```\n\n"
                doc += "---\n\n"

            output_path = self.output_dir / "api-reference.md"
            output_path.write_text(doc)

            logger.info("Generated API reference doc: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Error generating API reference doc: %s", e, exc_info=True)
            raise

    def generate_complete_documentation(self) -> list[Path]:
        """
        Generate complete documentation suite.

        Returns:
            List of paths to generated documents
        """
        try:
            logger.info("Generating complete documentation suite")

            docs = []
            docs.append(self.generate_build_history_doc())
            docs.append(self.generate_capsule_registry_doc())
            docs.append(self.generate_audit_summary_doc())
            docs.append(self.generate_api_reference_doc())

            # Generate index
            index_path = self._generate_index(docs)
            docs.insert(0, index_path)

            logger.info("Generated %s documentation files", len(docs))
            return docs

        except Exception as e:
            logger.error(
                "Error generating complete documentation: %s", e, exc_info=True
            )
            raise

    def _generate_index(self, docs: list[Path]) -> Path:
        """Generate documentation index."""
        doc = self._build_markdown_header("Gradle Evolution Documentation")

        doc += "\n## Documentation Index\n\n"
        doc += f"Generated: {_utc_now_iso()}\n\n"

        doc += "### Available Documents\n\n"
        for doc_path in docs:
            doc += f"- [{doc_path.stem.replace('-', ' ').title()}]({doc_path.name})\n"

        index_path = self.output_dir / "README.md"
        index_path.write_text(doc)

        return index_path

    def _build_markdown_header(self, title: str) -> str:
        """Build markdown document header."""
        return f"""# {title}

*Generated: {_utc_now_iso()}*

---
"""

    def export_json_snapshot(self) -> Path:
        """
        Export complete system state as JSON.

        Returns:
            Path to JSON snapshot
        """
        try:
            snapshot = {
                "timestamp": _utc_now_iso(),
                "capsules": [
                    cap.to_dict() for cap in self.capsule_engine.capsules.values()
                ],
                "build_statistics": self.state_integration.get_build_statistics(),
                "build_history": self.state_integration.get_build_history(limit=100),
                "audit_report": self.audit_integration.generate_audit_report(),
            }

            output_path = (
                self.output_dir
                / f"snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
            )
            with open(output_path, "w") as f:
                json.dump(snapshot, f, indent=2)

            logger.info("Exported JSON snapshot: %s", output_path)
            return output_path

        except Exception as e:
            logger.error("Error exporting JSON snapshot: %s", e, exc_info=True)
            raise


__all__ = ["APIDocumentation", "DocumentationGenerator"]
