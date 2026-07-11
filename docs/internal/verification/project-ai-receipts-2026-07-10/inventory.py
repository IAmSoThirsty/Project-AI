"""Structural inventories from the Git-tracked file list (read-only).

Reads raw/01a_git_ls_files.txt (produced by collect.ps1) and writes items
27-33 plus a depth-2 tree (40) and inventory.json. Parses pyproject TOML for
package names/versions and [project.scripts]; parses helm YAML for kinds.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
RECEIPT = Path(sys.argv[2]).resolve()
RAW = RECEIPT / "raw"

tracked = [ln.strip() for ln in (RAW / "01a_git_ls_files.txt").read_text(
    encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
tset = set(tracked)


def name_of(p: str) -> str:
    return p.rsplit("/", 1)[-1]


# ---- 27 build / entry files -----------------------------------------------
build_patterns = {
    "pyproject.toml": [], "setup.py": [], "setup.cfg": [], "package.json": [],
    "Cargo.toml": [], "go.mod": [], "pom.xml": [], "build.gradle": [],
    "build.gradle.kts": [], "settings.gradle.kts": [], "Chart.yaml": [],
    "Dockerfile": [], "compose.yaml": [], "compose.yml": [],
    "docker-compose.yaml": [], "docker-compose.yml": [],
}
tf_files, k8s_files = [], []
for p in tracked:
    n = name_of(p)
    if n in build_patterns:
        build_patterns[n].append(p)
    elif n.startswith("Dockerfile"):
        build_patterns["Dockerfile"].append(p)
    if p.endswith(".tf"):
        tf_files.append(p)

with (RAW / "27_build_entry_files.txt").open("w", encoding="utf-8") as f:
    for kind in sorted(build_patterns):
        lst = build_patterns[kind]
        f.write(f"{kind}: {len(lst)}\n")
        for p in sorted(lst):
            f.write(f"    {p}\n")
    f.write(f".tf (terraform): {len(tf_files)}\n")
    for p in sorted(tf_files):
        f.write(f"    {p}\n")

# ---- 28 + 31 packages, apps, scripts, versions ----------------------------
packages = []
scripts = {}
for p in build_patterns["pyproject.toml"]:
    try:
        data = tomllib.loads((ROOT / p).read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        continue
    proj = data.get("project", {})
    nm = proj.get("name")
    ver = proj.get("version")
    if nm:
        packages.append((nm, ver, p))
    for s, target in (proj.get("scripts") or {}).items():
        scripts[s] = f"{target}  ({p})"

apps_dirs = sorted({p.split("/")[1] for p in tracked
                    if p.startswith("apps/") and len(p.split("/")) > 2})
pkg_dirs = sorted({p.split("/")[1] for p in tracked
                   if p.startswith("packages/") and len(p.split("/")) > 2})
crate_dirs = sorted({p.split("/")[1] for p in tracked
                     if p.startswith("crates/") and len(p.split("/")) > 2})

with (RAW / "28_apps_packages_clis.txt").open("w", encoding="utf-8") as f:
    f.write(f"packages/ members ({len(pkg_dirs)}):\n")
    for d in pkg_dirs:
        f.write(f"    packages/{d}\n")
    f.write(f"\napps/ ({len(apps_dirs)}):\n")
    for d in apps_dirs:
        f.write(f"    apps/{d}\n")
    f.write(f"\ncrates/ ({len(crate_dirs)}):\n")
    for d in crate_dirs:
        f.write(f"    crates/{d}\n")
    f.write(f"\nconsole-script entry points ({len(scripts)}):\n")
    for s in sorted(scripts):
        f.write(f"    {s} = {scripts[s]}\n")

with (RAW / "31_published_packages.txt").open("w", encoding="utf-8") as f:
    f.write("Package metadata from pyproject.toml [project]. Version 0.0.0.dev0 = "
            "pre-alpha / not published. PyPI resolvability NOT verified (no network "
            "call made during this read-only audit).\n\n")
    f.write(f"{'name':34} {'version':14} source\n")
    for nm, ver, p in sorted(packages):
        f.write(f"{nm:34} {str(ver):14} {p}\n")
    # package.json names
    f.write("\nnode packages (package.json name/version):\n")
    for p in sorted(build_patterns["package.json"]):
        try:
            j = json.loads((ROOT / p).read_text(encoding="utf-8"))
            f.write(f"    {j.get('name','?')}  {j.get('version','?')}  {p}\n")
        except (OSError, json.JSONDecodeError):
            f.write(f"    (unparseable) {p}\n")

# ---- 29 workflows / actions -----------------------------------------------
workflows = [p for p in tracked if p.startswith(".github/workflows/")]
actions = [p for p in tracked if p.startswith(".github/actions/") or name_of(p) == "action.yml"
           or name_of(p) == "action.yaml"]
with (RAW / "29_workflows_actions.txt").open("w", encoding="utf-8") as f:
    f.write(f"GitHub Actions workflows ({len(workflows)}):\n")
    for p in sorted(workflows):
        f.write(f"    {p}\n")
    f.write(f"\nComposite/other actions ({len(actions)}):\n")
    for p in sorted(actions):
        f.write(f"    {p}\n")

# ---- 30 infra: helm kinds, charts, values, k8s ----------------------------
kind_re = re.compile(r"^\s*kind:\s*([A-Za-z0-9]+)", re.MULTILINE)
kinds: dict[str, int] = defaultdict(int)
helm_templates = [p for p in tracked if p.startswith("helm/") and p.endswith((".yaml", ".yml"))
                  and "/templates/" in p]
for p in helm_templates:
    try:
        for m in kind_re.findall((ROOT / p).read_text(encoding="utf-8", errors="ignore")):
            kinds[m] += 1
    except OSError:
        pass
charts = [p for p in tracked if name_of(p) == "Chart.yaml"]
values = [p for p in tracked if name_of(p).startswith("values") and p.endswith((".yaml", ".yml"))]
compose = [p for p in tracked if "compose" in name_of(p) and p.endswith((".yaml", ".yml"))]
dockerfiles = [p for p in tracked if name_of(p).startswith("Dockerfile")]
with (RAW / "30_infrastructure.txt").open("w", encoding="utf-8") as f:
    f.write(f"Helm charts (Chart.yaml): {len(charts)}\n")
    for p in charts:
        f.write(f"    {p}\n")
    f.write(f"\nHelm template files: {len(helm_templates)}\n")
    f.write(f"values files: {len(values)}\n")
    for p in sorted(values):
        f.write(f"    {p}\n")
    f.write(f"\nKubernetes resource kinds declared in helm templates "
            f"({sum(kinds.values())} declarations):\n")
    for k, c in sorted(kinds.items(), key=lambda kv: -kv[1]):
        f.write(f"    {k}: {c}\n")
    f.write(f"\nDocker Compose files: {len(compose)}\n")
    for p in compose:
        f.write(f"    {p}\n")
    f.write(f"Dockerfiles: {len(dockerfiles)}\n")
    for p in sorted(dockerfiles):
        f.write(f"    {p}\n")
    f.write(f"Terraform files: {len(tf_files)}\n")

# ---- 32 papers / specs -----------------------------------------------------
pdfs = [p for p in tracked if p.endswith(".pdf")]
try:
    from pypdf import PdfReader  # type: ignore[import-untyped, unused-ignore]
    have_pypdf = True
except ImportError:
    have_pypdf = False
with (RAW / "32_papers_specs.txt").open("w", encoding="utf-8") as f:
    f.write(f"PDF documents (papers/standards/specs): {len(pdfs)}\n")
    f.write(f"(pypdf available for page counts: {have_pypdf})\n\n")
    for p in sorted(pdfs):
        pages = ""
        if have_pypdf:
            try:
                pages = f"  pages={len(PdfReader(str(ROOT / p)).pages)}"
            except Exception:  # noqa: BLE001 - page count best-effort
                pages = "  pages=?"
        size = (ROOT / p).stat().st_size if (ROOT / p).exists() else 0
        f.write(f"    {p}  ({size} bytes){pages}\n")
    charter = [p for p in tracked if "charter" in p.lower() or "AGI_Charter" in p]
    f.write(f"\nCharter/spec references: {len(charter)}\n")
    for p in sorted(charter):
        f.write(f"    {p}\n")

# ---- 33 licenses / notices / submodules / third-party ---------------------
license_files = [p for p in tracked if re.search(
    r"(^|/)(LICENSE|LICENCE|NOTICE|COPYING|COPYRIGHT)", name_of(p), re.IGNORECASE)]
gitmodules = ".gitmodules" in tset
spdx_hits = 0
for p in tracked:
    if p.endswith((".py", ".rs", ".ts", ".js", ".go")):
        try:
            head = (ROOT / p).read_text(encoding="utf-8", errors="ignore")[:400]
            if "SPDX-License-Identifier" in head:
                spdx_hits += 1
        except OSError:
            pass
with (RAW / "33_licenses_thirdparty.txt").open("w", encoding="utf-8") as f:
    f.write(f"License/notice/copying files ({len(license_files)}):\n")
    for p in sorted(license_files):
        f.write(f"    {p}\n")
    f.write(f"\n.gitmodules present (submodules): {gitmodules}\n")
    f.write(f"SPDX-License-Identifier headers in source: {spdx_hits}\n")
    f.write("\nByte-preserved / reference / vendored trees (repo-declared, tracked):\n")
    for pref in ("packages/_staging/", "packages/security/reference/",
                 "packages/rlp/governance_framework/", "docs/reference/",
                 "docs/internal/frozen-history/"):
        n = sum(1 for p in tracked if p.startswith(pref))
        f.write(f"    {pref}: {n} tracked files\n")
    lockfiles = [p for p in tracked if name_of(p) in
                 {"uv.lock", "pnpm-lock.yaml", "package-lock.json", "Cargo.lock"}]
    f.write(f"\nDependency lockfiles ({len(lockfiles)}):\n")
    for p in sorted(lockfiles):
        f.write(f"    {p}  ({(ROOT / p).stat().st_size} bytes)\n")

# ---- 40 depth-2 tree -------------------------------------------------------
tree_counts: dict[str, int] = defaultdict(int)
for p in tracked:
    parts = p.split("/")
    if len(parts) == 1:
        tree_counts["(root files)"] += 1
    elif len(parts) == 2:
        tree_counts[parts[0] + "/"] += 1
    else:
        tree_counts[parts[0] + "/" + parts[1] + "/"] += 1
with (RAW / "40_tree_depth2.txt").open("w", encoding="utf-8") as f:
    f.write("Depth-2 tree (Git-tracked file counts per node):\n")
    for node in sorted(tree_counts):
        f.write(f"    {node:56} {tree_counts[node]:>6}\n")

inv = {
    "tracked_files": len(tracked),
    "packages_pyproject": [{"name": n, "version": v, "path": p} for n, v, p in sorted(packages)],
    "packages_dirs": pkg_dirs,
    "apps_dirs": apps_dirs,
    "crates_dirs": crate_dirs,
    "console_scripts": scripts,
    "workflows": workflows,
    "actions": actions,
    "helm_charts": charts,
    "helm_templates": len(helm_templates),
    "k8s_kinds": dict(sorted(kinds.items(), key=lambda kv: -kv[1])),
    "dockerfiles": dockerfiles,
    "terraform_files": tf_files,
    "compose_files": compose,
    "pdf_count": len(pdfs),
    "license_files": license_files,
    "has_submodules": gitmodules,
    "spdx_headers": spdx_hits,
}
(RECEIPT / "inventory.json").write_text(json.dumps(inv, indent=2), encoding="utf-8")
print(f"tracked={len(tracked)} py_pkgs={len(packages)} apps={len(apps_dirs)} "
      f"workflows={len(workflows)} k8s_kinds={len(kinds)} pdfs={len(pdfs)} "
      f"licenses={len(license_files)}")
