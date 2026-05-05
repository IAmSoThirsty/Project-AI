
from __future__ import annotations

import hashlib
import json
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REGISTRY_HOME = Path.home() / ".thirsty_registry"
PACKAGES_HOME = Path.home() / ".thirsty_packages"
GALLERY_INDEX = REGISTRY_HOME / "great_wells.json"


def ensure_hydration_dirs() -> None:
    REGISTRY_HOME.mkdir(parents=True, exist_ok=True)
    PACKAGES_HOME.mkdir(parents=True, exist_ok=True)
    if not GALLERY_INDEX.exists():
        GALLERY_INDEX.write_text("[]", encoding="utf-8")


def manifest_path(project: Path) -> Path:
    return project / "thirsty.json"


def default_manifest(project: Path) -> dict[str, Any]:
    return {
        "name": project.name,
        "version": "0.1.0",
        "entry": "src/main.thirsty",
        "description": "A freshly poured Thirsty package.",
        "tags": ["great-well"],
    }


def load_manifest(project: Path) -> dict[str, Any]:
    path = manifest_path(project)
    if not path.exists():
        data = default_manifest(project)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(project: Path, data: dict[str, Any]) -> None:
    manifest_path(project).write_text(json.dumps(data, indent=2), encoding="utf-8")


def _safe_name(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum() or ch in "-_:.").strip() or "unnamed"


def _registry_dir(name: str, version: str) -> Path:
    return REGISTRY_HOME / "packages" / _safe_name(name) / version


def _installed_dir(project: Path, name: str, version: str) -> Path:
    return project / ".thirsty_packages" / _safe_name(name) / version


def package_id(manifest: dict[str, Any]) -> str:
    return f"{manifest.get('name','unnamed')}@{manifest.get('version','0.0.0')}"


def publish_package(project: Path) -> dict[str, Any]:
    ensure_hydration_dirs()
    manifest = load_manifest(project)
    src = project.resolve()
    name = manifest["name"]
    version = manifest["version"]
    dest = _registry_dir(name, version)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git", "*.pyc"))
    entry = {
        "name": name,
        "version": version,
        "description": manifest.get("description", ""),
        "tags": manifest.get("tags", []),
        "entry": manifest.get("entry", "src/main.thirsty"),
        "publishedAt": int(time.time()),
        "registryPath": str(dest),
        "hash": hashlib.sha256((name + version + str(dest)).encode("utf-8")).hexdigest(),
    }
    items = load_gallery()
    items = [x for x in items if not (x["name"] == name and x["version"] == version)]
    items.append(entry)
    GALLERY_INDEX.write_text(json.dumps(sorted(items, key=lambda x: (x["name"], x["version"])), indent=2), encoding="utf-8")
    return entry


def load_gallery() -> list[dict[str, Any]]:
    ensure_hydration_dirs()
    return json.loads(GALLERY_INDEX.read_text(encoding="utf-8"))


def search_gallery(term: str | None = None) -> list[dict[str, Any]]:
    items = load_gallery()
    if not term:
        return items
    low = term.lower()
    out = []
    for item in items:
        hay = " ".join([item["name"], item.get("description", ""), " ".join(item.get("tags", []))]).lower()
        if low in hay:
            out.append(item)
    return out


def show_gallery_item(name: str) -> dict[str, Any] | None:
    items = load_gallery()
    matches = [x for x in items if x["name"] == name or f"{x['name']}@{x['version']}" == name]
    if not matches:
        return None
    matches.sort(key=lambda x: x["version"])
    return matches[-1]


def _project_lock(project: Path) -> Path:
    return project / "thirsty.lock.json"


def _load_lock(project: Path) -> dict[str, Any]:
    p = _project_lock(project)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"dependencies": {}}


def _save_lock(project: Path, data: dict[str, Any]) -> None:
    _project_lock(project).write_text(json.dumps(data, indent=2), encoding="utf-8")


def resolve_package_source(spec: str) -> tuple[Path, dict[str, Any]]:
    ensure_hydration_dirs()
    as_path = Path(spec)
    if as_path.exists():
        project = as_path.resolve()
        return project, load_manifest(project)
    item = show_gallery_item(spec)
    if item:
        project = Path(item["registryPath"])
        return project, load_manifest(project)
    if "@" in spec:
        name, version = spec.split("@", 1)
        candidate = _registry_dir(name, version)
        if candidate.exists():
            return candidate, load_manifest(candidate)
    raise FileNotFoundError(f"could not find thirsty package {spec!r}")


def install_package(project: Path, spec: str) -> dict[str, Any]:
    ensure_hydration_dirs()
    source, manifest = resolve_package_source(spec)
    name = manifest["name"]
    version = manifest["version"]
    dest = _installed_dir(project, name, version)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git", "*.pyc"))
    lock = _load_lock(project)
    lock["dependencies"][name] = {"version": version, "path": str(dest)}
    _save_lock(project, lock)
    proj_manifest = load_manifest(project)
    deps = proj_manifest.setdefault("dependencies", {})
    deps[name] = version
    save_manifest(project, proj_manifest)
    return {"name": name, "version": version, "installPath": str(dest)}


def list_installed_packages(project: Path) -> list[dict[str, Any]]:
    lock = _load_lock(project)
    items = []
    for name, meta in sorted(lock.get("dependencies", {}).items()):
        items.append({"name": name, **meta})
    return items


def project_search_roots(project: Path) -> list[Path]:
    roots = [project.resolve()]
    installed = project / ".thirsty_packages"
    if installed.exists():
        for pkg in installed.iterdir():
            if pkg.is_dir():
                for ver in pkg.iterdir():
                    if ver.is_dir():
                        roots.append(ver)
    ensure_hydration_dirs()
    roots.append(PACKAGES_HOME)
    return roots
