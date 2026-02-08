"""
FastAPI Router for Inspection & Audit System

Provides REST API endpoints for the inspection subsystem.

Author: Project-AI Team
Date: 2026-02-08
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.inspection.audit_pipeline import AuditConfig, AuditPipeline, AuditResults

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/inspection", tags=["inspection"])

# In-memory storage for audit results (replace with database in production)
audit_storage: dict[str, AuditResults] = {}


class AuditRequest(BaseModel):
    """Request model for starting an audit."""

    repo_path: str = Field(..., description="Path to repository root")
    output_dir: str | None = Field(
        None, description="Output directory for reports (optional)"
    )
    enable_lint: bool = Field(True, description="Enable lint checking")
    enable_quality: bool = Field(True, description="Enable quality analysis")
    enable_integrity: bool = Field(True, description="Enable integrity checking")
    generate_reports: bool = Field(
        True, description="Generate machine-readable reports"
    )
    generate_catalog: bool = Field(True, description="Generate markdown catalog")


class AuditResponse(BaseModel):
    """Response model for audit operations."""

    audit_id: str
    status: str  # pending, running, completed, failed
    message: str
    started_at: str | None = None
    completed_at: str | None = None
    execution_time_seconds: float | None = None


class AuditResultsResponse(BaseModel):
    """Response model for audit results."""

    audit_id: str
    success: bool
    timestamp: str
    execution_time_seconds: float
    overall_health_score: float | None = None
    grade: str | None = None
    statistics: dict[str, Any] | None = None
    reports: dict[str, str] | None = None
    catalog_path: str | None = None
    error: str | None = None


class ReportListResponse(BaseModel):
    """Response model for listing reports."""

    reports: list[dict[str, str]]
    count: int


@router.post("/audit", response_model=AuditResponse)
async def start_audit(request: AuditRequest, background_tasks: BackgroundTasks):
    """
    Start a new repository audit.

    The audit runs asynchronously in the background. Use the returned
    audit_id to check the status and retrieve results.
    """
    # Validate repository path
    repo_path = Path(request.repo_path)
    if not repo_path.exists() or not repo_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Repository path does not exist or is not a directory: {request.repo_path}",
        )

    # Generate audit ID
    audit_id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"

    # Create config
    config = AuditConfig(
        repo_root=repo_path,
        output_dir=request.output_dir or "audit_reports",
        enable_lint=request.enable_lint,
        enable_quality=request.enable_quality,
        enable_integrity=request.enable_integrity,
        generate_reports=request.generate_reports,
        generate_catalog=request.generate_catalog,
    )

    # Store initial status
    audit_storage[audit_id] = AuditResults(
        success=False,
        timestamp=datetime.now().isoformat(),
        execution_time_seconds=0.0,
    )

    # Schedule audit in background
    background_tasks.add_task(_run_audit_background, audit_id, config)

    logger.info("Started audit %s for repository: %s", audit_id, repo_path)

    return AuditResponse(
        audit_id=audit_id,
        status="pending",
        message="Audit started successfully",
        started_at=datetime.now().isoformat(),
    )


@router.get("/audit/{audit_id}", response_model=AuditResultsResponse)
async def get_audit_results(audit_id: str):
    """
    Get results of a completed audit.

    Returns the full audit results including health score, statistics,
    and paths to generated reports.
    """
    if audit_id not in audit_storage:
        raise HTTPException(status_code=404, detail=f"Audit not found: {audit_id}")

    results = audit_storage[audit_id]

    # Extract summary info
    overall_assessment = results.overall_assessment or {}
    inspection_stats = (
        results.inspection.get("statistics", {}) if results.inspection else {}
    )
    integrity_stats = (
        results.integrity.get("statistics", {}) if results.integrity else {}
    )
    lint_summary = results.lint.get("summary", {}) if results.lint else {}

    statistics = {
        "files_analyzed": inspection_stats.get("total_files", 0),
        "lines_of_code": inspection_stats.get("total_lines", 0),
        "components": (
            len(results.inspection.get("components", {})) if results.inspection else 0
        ),
        "dependencies": integrity_stats.get("total_dependencies", 0),
        "integrity_issues": integrity_stats.get("total_issues", 0),
        "circular_dependencies": (
            len(results.integrity.get("circular_dependencies", []))
            if results.integrity
            else 0
        ),
        "lint_issues": lint_summary.get("total_issues", 0),
        "lint_errors": lint_summary.get("issues_by_severity", {}).get("error", 0),
    }

    return AuditResultsResponse(
        audit_id=audit_id,
        success=results.success,
        timestamp=results.timestamp,
        execution_time_seconds=results.execution_time_seconds,
        overall_health_score=overall_assessment.get("health_score"),
        grade=overall_assessment.get("grade"),
        statistics=statistics,
        reports=results.reports,
        catalog_path=results.catalog_path,
        error=results.error,
    )


@router.get("/reports", response_model=ReportListResponse)
async def list_reports(
    output_dir: str = Query("audit_reports", description="Reports output directory")
):
    """
    List all available audit reports.

    Returns a list of report files in the specified output directory.
    """
    output_path = Path(output_dir)

    if not output_path.exists():
        return ReportListResponse(reports=[], count=0)

    reports = []

    for file_path in output_path.glob("*"):
        if file_path.is_file() and file_path.suffix in [".json", ".yaml", ".md"]:
            reports.append(
                {
                    "filename": file_path.name,
                    "path": str(file_path),
                    "type": file_path.suffix[1:],
                    "size_bytes": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                }
            )

    # Sort by modified time (newest first)
    reports.sort(key=lambda x: x["modified"], reverse=True)

    return ReportListResponse(reports=reports, count=len(reports))


@router.get("/reports/{filename}")
async def download_report(
    filename: str,
    output_dir: str = Query("audit_reports", description="Reports output directory"),
):
    """
    Download a specific audit report file.

    Returns the requested report file for download.
    """
    output_path = Path(output_dir) / filename

    if not output_path.exists() or not output_path.is_file():
        raise HTTPException(status_code=404, detail=f"Report not found: {filename}")

    # Determine media type
    media_type = "application/json"
    if output_path.suffix == ".yaml":
        media_type = "application/x-yaml"
    elif output_path.suffix == ".md":
        media_type = "text/markdown"

    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=filename,
    )


@router.delete("/audit/{audit_id}")
async def delete_audit(audit_id: str):
    """
    Delete an audit and its results from storage.

    Note: This only removes the audit from memory. Generated report files
    are not deleted.
    """
    if audit_id not in audit_storage:
        raise HTTPException(status_code=404, detail=f"Audit not found: {audit_id}")

    del audit_storage[audit_id]

    logger.info("Deleted audit: %s", audit_id)

    return {"message": f"Audit {audit_id} deleted successfully"}


async def _run_audit_background(audit_id: str, config: AuditConfig):
    """Run audit in background task."""
    try:
        logger.info("Starting background audit: %s", audit_id)

        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        # Store results
        audit_storage[audit_id] = results

        logger.info(
            "Completed background audit: %s, success: %s",
            audit_id,
            results.success,
        )

    except Exception as e:
        logger.exception("Background audit failed: %s", audit_id)

        # Store error
        audit_storage[audit_id] = AuditResults(
            success=False,
            timestamp=datetime.now().isoformat(),
            execution_time_seconds=0.0,
            error=str(e),
        )


__all__ = ["router"]
