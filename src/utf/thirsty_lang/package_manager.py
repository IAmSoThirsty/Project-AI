from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REGISTRY_HOME = Path.home() / ".thirsty_registry"
PACKAGES_HOME = Path.home() / ".thirsty_packages"
GALLERY_INDEX = REGISTRY_HOME / "great_wells.json"

# Remote registry URL — set THIRSTY_REGISTRY_URL to use the central registry.
# When set, publish/search/install operations are routed through the HTTP API.
# Leave unset to use the local filesystem registry (~/.thirsty_registry).
REGISTRY_URL = os.environ.get("THIRSTY_REGISTRY_URL", "").rstrip("/")


# ---------------------------------------------------------------------------
# Remote registry helpers
# ---------------------------------------------------------------------------

def _remote_get(path: str) -> dict | list:
    """GET from the remote registry. Returns parsed JSON."""
    url = f"{REGISTRY_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"registry HTTP {e.code}: {body}") from e
    except Exception as e:
        raise RuntimeError(f"registry unreachable ({url}): {e}") from e


def _remote_post(path: str, data: dict) -> dict:
    """POST JSON to the remote registry. Returns parsed JSON."""
    url = f"{REGISTRY_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_str = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"registry HTTP {e.code}: {body_str}") from e
    except Exception as e:
        raise RuntimeError(f"registry unreachable ({url}): {e}") from e


def remote_registry_available() -> bool:
    """Return True if THIRSTY_REGISTRY_URL is set and the server responds."""
    if not REGISTRY_URL:
        return False
    try:
        _remote_get("/health")
        return True
    except Exception:
        return False


def ensure_hydration_dirs() -> None:
    REGISTRY_HOME.mkdir(parents=True, exist_ok=True)
    PACKAGES_HOME.mkdir(parents=True, exist_ok=True)
    if not GALLERY_INDEX.exists():
        GALLERY_INDEX.write_text("[]", encoding="utf-8")


def manifest_path(project: Path) -> Path:
    toml_path = project / "thirsty.toml"
    if toml_path.exists():
        return toml_path
    return project / "thirsty.json"


def _load_toml_manifest(path: Path) -> dict[str, Any]:
    try:
        import tomllib
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except ImportError:
        try:
            import tomli  # type: ignore
            raw = tomli.loads(path.read_text(encoding="utf-8"))
        except ImportError:
            raw = {}
    pkg = raw.get("package", {})
    return {
        "name": pkg.get("name", path.parent.name),
        "version": pkg.get("version", "0.1.0"),
        "entry": pkg.get("entry", "src/main.thirsty"),
        "description": pkg.get("description", ""),
        "mode": pkg.get("mode", "core"),
        "tags": raw.get("tags", []),
        "dependencies": raw.get("dependencies", {}),
        "governance": raw.get("governance", {}),
    }


def default_manifest(project: Path) -> dict[str, Any]:
    return {
        "name": project.name,
        "version": "0.1.0",
        "entry": "src/main.thirsty",
        "description": "A freshly poured Thirsty package.",
        "tags": ["great-well"],
    }


def load_manifest(project: Path) -> dict[str, Any]:
    toml_path = project / "thirsty.toml"
    if toml_path.exists():
        return _load_toml_manifest(toml_path)
    json_path = project / "thirsty.json"
    if not json_path.exists():
        data = default_manifest(project)
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    return json.loads(json_path.read_text(encoding="utf-8"))


def save_manifest(project: Path, data: dict[str, Any]) -> None:
    path = manifest_path(project)
    if path.suffix == ".toml":
        toml_lines = [
            "[package]",
            f'name = "{data.get("name", "")}"',
            f'version = "{data.get("version", "0.1.0")}"',
            f'entry = "{data.get("entry", "src/main.thirsty")}"',
            f'mode = "{data.get("mode", "core")}"',
            "",
            "[dependencies]",
        ]
        for dep, ver in data.get("dependencies", {}).items():
            toml_lines.append(f'"{dep}" = "{ver}"')
        path.write_text("\n".join(toml_lines) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _safe_name(name: str) -> str:
    return (
        "".join(ch for ch in name if ch.isalnum() or ch in "-_:.").strip() or "unnamed"
    )


def _registry_dir(name: str, version: str) -> Path:
    return REGISTRY_HOME / "packages" / _safe_name(name) / version


def _installed_dir(project: Path, name: str, version: str) -> Path:
    return project / ".thirsty_packages" / _safe_name(name) / version


def package_id(manifest: dict[str, Any]) -> str:
    return f"{manifest.get('name', 'unnamed')}@{manifest.get('version', '0.0.0')}"


def publish_package(project: Path) -> dict[str, Any]:
    ensure_hydration_dirs()
    manifest = load_manifest(project)
    name = manifest["name"]
    version = manifest["version"]

    # Remote publish: if registry URL configured, send to the HTTP registry
    if REGISTRY_URL:
        payload: dict[str, Any] = {
            "name": name,
            "version": version,
            "description": manifest.get("description", ""),
            "entry": manifest.get("entry", "main.thirsty"),
            "mode": manifest.get("mode", "core"),
            "tags": manifest.get("tags", []),
        }
        result = _remote_post("/packages", payload)
        return result.get("entry", result)

    src = project.resolve()
    dest = _registry_dir(name, version)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git", "*.pyc"),
    )
    entry = {
        "name": name,
        "version": version,
        "description": manifest.get("description", ""),
        "tags": manifest.get("tags", []),
        "entry": manifest.get("entry", "src/main.thirsty"),
        "publishedAt": int(time.time()),
        "registryPath": str(dest),
        "hash": hashlib.sha256(
            (name + version + str(dest)).encode("utf-8")
        ).hexdigest(),
    }
    items = load_gallery()
    items = [x for x in items if not (x["name"] == name and x["version"] == version)]
    items.append(entry)
    GALLERY_INDEX.write_text(
        json.dumps(sorted(items, key=lambda x: (x["name"], x["version"])), indent=2),
        encoding="utf-8",
    )
    return entry


def load_gallery() -> list[dict[str, Any]]:
    ensure_hydration_dirs()
    return json.loads(GALLERY_INDEX.read_text(encoding="utf-8"))


def search_gallery(term: str | None = None) -> list[dict[str, Any]]:
    # Remote search: if registry URL configured, query the HTTP registry
    if REGISTRY_URL:
        try:
            path = "/packages"
            if term:
                path += "?" + urllib.parse.urlencode({"q": term})
            data = _remote_get(path)
            if isinstance(data, dict):
                return data.get("packages", [])
            return data
        except Exception:
            pass  # Fall back to local gallery on connectivity failure

    items = load_gallery()
    if not term:
        return items
    low = term.lower()
    out = []
    for item in items:
        hay = " ".join(
            [item["name"], item.get("description", ""), " ".join(item.get("tags", []))]
        ).lower()
        if low in hay:
            out.append(item)
    return out


def show_gallery_item(name: str) -> dict[str, Any] | None:
    items = load_gallery()
    matches = [
        x for x in items if x["name"] == name or f"{x['name']}@{x['version']}" == name
    ]
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
    shutil.copytree(
        source,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git", "*.pyc"),
    )
    pkg_hash = "sha256:" + hashlib.sha256(
        (name + version).encode("utf-8")
    ).hexdigest()
    lock = _load_lock(project)
    lock["dependencies"][name] = {"version": version, "path": str(dest), "hash": pkg_hash}
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


def generate_lock(project: Path) -> None:
    """Regenerate thirsty.lock.json from the current manifest dependencies."""
    ensure_hydration_dirs()
    manifest = load_manifest(project)
    lock = _load_lock(project)
    deps = manifest.get("dependencies", {})
    for name, version_spec in deps.items():
        version = version_spec.lstrip("^~>=<")
        if name not in lock.get("dependencies", {}):
            installed = _installed_dir(project, name, version)
            pkg_hash = "sha256:" + hashlib.sha256(
                (name + version).encode("utf-8")
            ).hexdigest()
            lock.setdefault("dependencies", {})[name] = {
                "version": version,
                "path": str(installed),
                "hash": pkg_hash,
            }
    governance = manifest.get("governance", {})
    policy_hashes: dict[str, str] = {}
    for policy_rel in governance.get("requires_policy", []):
        policy_path = project / policy_rel
        if policy_path.exists():
            policy_hashes[policy_rel] = "sha256:" + hashlib.sha256(
                policy_path.read_bytes()
            ).hexdigest()
    if policy_hashes:
        lock["policy_hashes"] = policy_hashes
    _save_lock(project, lock)


def audit_dependencies(project: Path) -> list[str]:
    """Check installed dependencies for known governance violations.
    Returns a list of finding strings (empty = clean)."""
    findings: list[str] = []
    lock = _load_lock(project)
    for name, meta in lock.get("dependencies", {}).items():
        install_path = Path(meta.get("path", ""))
        if not install_path.exists():
            findings.append(f"{name}: installed path missing ({install_path})")
            continue
        stored_hash = meta.get("hash", "")
        computed = "sha256:" + hashlib.sha256(
            (name + meta.get("version", "")).encode("utf-8")
        ).hexdigest()
        if stored_hash and stored_hash != computed:
            findings.append(f"{name}: hash mismatch (possible tampering)")
    return findings
