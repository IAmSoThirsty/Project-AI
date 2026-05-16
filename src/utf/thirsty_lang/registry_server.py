"""
Thirsty-Lang Central Package Registry Server.

A FastAPI service that hosts the Thirsty package registry.  Packages can be
published, searched, installed, and yanked via HTTP endpoints.

Port: 9000 (default; configurable via THIRSTY_REGISTRY_PORT env var)
Storage: local filesystem (packages/ + index.json) — configurable via
         THIRSTY_REGISTRY_DATA_DIR env var

Start with:
    python -m thirsty_lang.registry_server
    # or
    uvicorn thirsty_lang.registry_server:app --host 0.0.0.0 --port 9000

Client configuration:
    Set THIRSTY_REGISTRY_URL=http://localhost:9000 (or your server URL)
    The package_manager.py will use this URL when set.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

_DEFAULT_PORT = int(os.environ.get("THIRSTY_REGISTRY_PORT", "9000"))
_DATA_DIR = Path(os.environ.get(
    "THIRSTY_REGISTRY_DATA_DIR",
    str(Path.home() / ".thirsty_registry_server"),
))

_PACKAGES_DIR = _DATA_DIR / "packages"
_INDEX_FILE = _DATA_DIR / "index.json"
_YANK_FILE = _DATA_DIR / "yanked.json"


def _ensure_dirs() -> None:
    _PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not _INDEX_FILE.exists():
        _INDEX_FILE.write_text("[]", encoding="utf-8")
    if not _YANK_FILE.exists():
        _YANK_FILE.write_text("[]", encoding="utf-8")


def _read_index() -> list[dict]:
    try:
        return json.loads(_INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_index(entries: list[dict]) -> None:
    _INDEX_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _read_yanked() -> set[str]:
    try:
        return set(json.loads(_YANK_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _pkg_key(name: str, version: str) -> str:
    return f"{name}@{version}"


try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, JSONResponse
    from pydantic import BaseModel

    _ensure_dirs()

    app = FastAPI(
        title="Thirsty-Lang Package Registry",
        description="Central package registry for Thirsty-Lang packages",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    class PublishRequest(BaseModel):
        name: str
        version: str
        description: str = ""
        entry: str = "main.thirsty"
        mode: str = "core"
        tags: list[str] = []
        source_hash: str = ""
        # Base64-encoded zip of the package source (optional for metadata-only publish)
        source_b64: str = ""

    class SearchResult(BaseModel):
        name: str
        version: str
        description: str
        tags: list[str]
        published_at: int
        source_hash: str
        yanked: bool

    # ------------------------------------------------------------------
    # Endpoints
    # ------------------------------------------------------------------

    @app.get("/")
    async def root():
        index = _read_index()
        yanked = _read_yanked()
        return {
            "service": "Thirsty-Lang Package Registry",
            "version": "1.0.0",
            "total_packages": len(index),
            "total_yanked": len(yanked),
            "endpoints": {
                "search": "GET /packages?q=<term>",
                "get": "GET /packages/<name>/<version>",
                "publish": "POST /packages",
                "yank": "DELETE /packages/<name>/<version>",
                "health": "GET /health",
            },
        }

    @app.get("/health")
    async def health():
        index = _read_index()
        return {
            "status": "healthy",
            "total_packages": len(index),
            "data_dir": str(_DATA_DIR),
        }

    @app.get("/packages")
    async def search_packages(q: str = "", limit: int = 50, offset: int = 0):
        """Search packages by name, description, or tags."""
        index = _read_index()
        yanked = _read_yanked()
        term = q.lower()

        results = []
        for entry in index:
            key = _pkg_key(entry["name"], entry["version"])
            if term:
                haystack = (
                    f"{entry['name']} {entry.get('description', '')} "
                    f"{' '.join(entry.get('tags', []))}"
                ).lower()
                if term not in haystack:
                    continue
            results.append({
                **entry,
                "yanked": key in yanked,
            })

        results.sort(key=lambda e: e["published_at"], reverse=True)
        return {
            "total": len(results),
            "packages": results[offset: offset + limit],
        }

    @app.get("/packages/{name}")
    async def get_package_versions(name: str):
        """List all versions of a package."""
        index = _read_index()
        yanked = _read_yanked()
        versions = [
            {**e, "yanked": _pkg_key(e["name"], e["version"]) in yanked}
            for e in index
            if e["name"] == name
        ]
        if not versions:
            raise HTTPException(404, f"Package '{name}' not found")
        versions.sort(key=lambda e: e["published_at"], reverse=True)
        return {"name": name, "versions": versions}

    @app.get("/packages/{name}/{version}")
    async def get_package(name: str, version: str):
        """Get metadata for a specific package version."""
        index = _read_index()
        yanked = _read_yanked()
        for entry in index:
            if entry["name"] == name and entry["version"] == version:
                return {**entry, "yanked": _pkg_key(name, version) in yanked}
        raise HTTPException(404, f"Package '{name}@{version}' not found")

    @app.post("/packages")
    async def publish_package(pkg: PublishRequest):
        """Publish a new package version."""
        key = _pkg_key(pkg.name, pkg.version)
        index = _read_index()
        yanked = _read_yanked()

        # Reject re-publish of yanked version
        if key in yanked:
            raise HTTPException(409, f"Version '{key}' has been yanked and cannot be re-published")

        # Reject duplicate
        for entry in index:
            if entry["name"] == pkg.name and entry["version"] == pkg.version:
                raise HTTPException(409, f"Package '{key}' already exists")

        entry: dict[str, Any] = {
            "name": pkg.name,
            "version": pkg.version,
            "description": pkg.description,
            "entry": pkg.entry,
            "mode": pkg.mode,
            "tags": pkg.tags,
            "source_hash": pkg.source_hash,
            "published_at": int(time.time()),
        }

        # Store source archive if provided
        if pkg.source_b64:
            import base64
            pkg_dir = _PACKAGES_DIR / pkg.name / pkg.version
            pkg_dir.mkdir(parents=True, exist_ok=True)
            archive_bytes = base64.b64decode(pkg.source_b64)
            actual_hash = "sha256:" + hashlib.sha256(archive_bytes).hexdigest()
            (pkg_dir / "source.tar.gz").write_bytes(archive_bytes)
            if pkg.source_hash and pkg.source_hash != actual_hash:
                raise HTTPException(400, f"source_hash mismatch: expected {pkg.source_hash}, got {actual_hash}")
            entry["source_hash"] = actual_hash
            entry["archive_path"] = str(pkg_dir / "source.tar.gz")

        index.append(entry)
        _write_index(index)
        return {"published": True, "key": key, "entry": entry}

    @app.delete("/packages/{name}/{version}")
    async def yank_package(name: str, version: str):
        """
        Yank a package version.

        Yanked packages remain visible but cannot be installed by new projects
        (existing lock files that already pin this version continue to work).
        """
        key = _pkg_key(name, version)
        index = _read_index()
        exists = any(e["name"] == name and e["version"] == version for e in index)
        if not exists:
            raise HTTPException(404, f"Package '{key}' not found")

        yanked = _read_yanked()
        yanked.add(key)
        _YANK_FILE.write_text(json.dumps(sorted(yanked), indent=2), encoding="utf-8")
        return {"yanked": True, "key": key}

    @app.get("/packages/{name}/{version}/source")
    async def download_source(name: str, version: str):
        """Download the source archive for a package version."""
        pkg_dir = _PACKAGES_DIR / name / version
        archive = pkg_dir / "source.tar.gz"
        if not archive.exists():
            raise HTTPException(404, f"Source archive for '{name}@{version}' not found")
        return FileResponse(
            str(archive),
            media_type="application/gzip",
            filename=f"{name}-{version}.tar.gz",
        )

    # ------------------------------------------------------------------
    # Module entry point
    # ------------------------------------------------------------------

    def main():
        import uvicorn
        port = _DEFAULT_PORT
        print(f"\nThirsty-Lang Package Registry")
        print(f"Listening on http://0.0.0.0:{port}")
        print(f"Data dir:   {_DATA_DIR}")
        print(f"Docs:       http://localhost:{port}/docs\n")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    if __name__ == "__main__":
        main()

except ImportError:
    # FastAPI not installed
    app = None  # type: ignore

    def main():
        raise ImportError(
            "FastAPI is required to run the Thirsty package registry. "
            "Install with: pip install fastapi uvicorn"
        )
