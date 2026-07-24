"""Read-only repository-intelligence routes for the existing FastAPI host."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from knowledge.repository import IndexUnavailable, RepositoryIndex, RepositoryStatus
from pydantic import BaseModel, ConfigDict, Field


class RepositoryStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    state: str
    root: str
    root_fingerprint: str | None
    indexed_files: int = Field(ge=0)
    indexed_chunks: int = Field(ge=0)
    excluded_files: int = Field(ge=0)
    exclusions: dict[str, int]
    index_path: str
    stale: bool
    reason: str | None = None


class RepositorySearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    language: str
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    excerpt: str = Field(min_length=1)
    score: float


class RepositorySearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    results: list[RepositorySearchResult]


def repository_paths() -> tuple[Path, Path]:
    """Return configured paths without creating or refreshing any artifact."""
    root = Path(os.environ.get("PROJECT_AI_REPOSITORY_ROOT", Path.cwd())).expanduser()
    index = Path(
        os.environ.get("PROJECT_AI_REPOSITORY_INDEX", root / "data" / "repository-intelligence")
    ).expanduser()
    return root, index


def status_response(status: RepositoryStatus) -> RepositoryStatusResponse:
    return RepositoryStatusResponse(
        schema_version=status.schema_version,
        state=status.state,
        root=status.root,
        root_fingerprint=status.root_fingerprint,
        indexed_files=status.indexed_files,
        indexed_chunks=status.indexed_chunks,
        excluded_files=status.excluded_files,
        exclusions=dict(status.exclusions),
        index_path=status.index_path,
        stale=status.stale,
        reason=status.reason,
    )


def create_repository_router(
    *, root: Path | None = None, index_path: Path | None = None
) -> APIRouter:
    """Create only read routes; requests never build, refresh, or save an index."""
    configured_root, configured_index = repository_paths()
    repo_root = root or configured_root
    artifact_path = index_path or configured_index
    router = APIRouter(prefix="/repository-intelligence", tags=["repository-intelligence"])

    @router.get("/status", response_model=RepositoryStatusResponse)
    def status() -> RepositoryStatusResponse:
        return status_response(RepositoryIndex.status_for(artifact_path, root=repo_root))

    @router.get("/search", response_model=RepositorySearchResponse)
    def search(
        query: Annotated[str, Query(min_length=1, max_length=500)],
        limit: Annotated[int, Query(ge=1, le=50)] = 10,
    ) -> RepositorySearchResponse:
        if not query.strip():
            raise HTTPException(status_code=422, detail="query must not be empty")
        try:
            index = RepositoryIndex.load(artifact_path, root=repo_root)
        except IndexUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        hits = index.search(query, limit)
        return RepositorySearchResponse(
            query=query,
            results=[
                RepositorySearchResult(
                    path=hit.path,
                    language=hit.language,
                    start_line=hit.start_line,
                    end_line=hit.end_line,
                    sha256=hit.sha256,
                    excerpt=hit.excerpt,
                    score=score,
                )
                for hit, score in hits
            ],
        )

    return router


__all__ = [
    "RepositorySearchResponse",
    "RepositorySearchResult",
    "RepositoryStatusResponse",
    "create_repository_router",
    "repository_paths",
]
