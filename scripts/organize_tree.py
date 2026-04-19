from __future__ import annotations

from pathlib import Path
import shutil
import os
import subprocess


def ensure_empty_dir(path: Path) -> None:
    is_junction = False
    try:
        is_junction = path.is_junction()  # Python 3.12+
    except AttributeError:
        is_junction = False

    if path.exists() or path.is_symlink() or is_junction or os.path.islink(path):
        if (path.is_symlink() or is_junction or os.path.islink(path)) and path.exists():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def write_readme(path: Path, title: str, body: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "README.md").write_text(f"# {title}\n\n{body}\n", encoding="utf-8")


def git_remote_branches(repo: Path) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "for-each-ref",
            "refs/remotes/origin",
            "--format=%(refname:short)",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    branches = []
    for line in result.stdout.splitlines():
        if line.strip() == "origin/HEAD":
            continue
        branches.append(line.replace("origin/", "", 1))
    return sorted(set(branches))


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    root = repo / "Project-AI-Monorepo"
    root.mkdir(parents=True, exist_ok=True)

    mapping = {
        "Core-System/PSIA-Pipeline": "src/psia",
        "Core-System/Triumvirate-Engine": "src/cognition",
        "Core-System/OctoReflex": "octoreflex",
        "Core-System/Iron-Path-Executor": "governance",
        "Governance/AGI-Charter": "docs/governance",
        "Governance/Sovereign-Covenant": "docs/governance",
        "Governance/Constitutional-Architectures": "docs/architecture",
        "Governance/Codex-Deus-Maximus": "Codex",
        "Governance/TSCG": "project_ai/utils",
        "Governance/TSCG-B": "project_ai/utils",
        "Runtime/TARL-VM": "tarl",
        "Runtime/Thirsty-Lang": "thirsty_lang",
        "Runtime/Shadow-Plane": "canonical",
        "Runtime/Canonical-State": "canonical",
        "Runtime/Gate-Engine": "src/app/core/governance",
        "Microservices/Genesis": "src/psia/bootstrap",
        "Infrastructure/TK8S": "k8s",
        "Infrastructure/Observability": "monitoring",
        "Infrastructure/Security-Policies": "policies",
        "Infrastructure/Signing-SBOM": "docs/security_compliance",
        "Tooling/CI-CD": ".github/workflows",
        "Tooling/Zero-Bypass-Verifier": "scripts",
        "Tooling/Audit-Engine": "gradle-evolution/audit",
        "Tooling/Reproducible-Builds": "gradle-evolution/capsules",
        "Experimental/New-Architectures": "examples",
        "Experimental/Unverified-Models": "demos",
        "Experimental/High-Risk-Concepts": "adversarial_tests",
        "Legacy/Deprecated-Systems": "archive",
        "Legacy/Archived-Modules": "archive",
        "Legacy/Compatibility-Layers": "integrations",
    }

    linked = 0
    stubbed = 0

    for rel, source_rel in mapping.items():
        node = root / rel
        source = repo / source_rel

        if source.exists():
            ensure_empty_dir(node)
            # Write a manifest pointer to real source and selected index.
            files = []
            for p in source.rglob("*"):
                if p.is_file():
                    files.append(p)
                if len(files) >= 200:
                    break

            lines = [
                f"# {node.name}",
                "",
                f"Mapped Source: `{source_rel}`",
                "",
                "## Representative Files",
                "",
            ]
            if files:
                for p in files:
                    lines.append(f"- `{p.relative_to(repo).as_posix()}`")
            else:
                lines.append("- _(no files discovered)_")

            (node / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            linked += 1
        else:
            write_readme(
                node,
                node.name,
                f"Missing source path `{source_rel}`; create/attach implementation here.",
            )
            stubbed += 1

    missing_nodes = [
        "Microservices/GIEWA",
        "Microservices/PTVS",
        "Microservices/Civic-Attest",
        "Documentation/OctoReflex-Report",
        "Documentation/Sovereign-Covenant",
        "Documentation/AGI-Charter",
        "Documentation/TSCG",
        "Documentation/TSCG-B",
        "Documentation/Flat-Gap",
        "Documentation/State-Register",
        "Documentation/Asymmetric-Security",
        "Documentation/Sovereign-AGI-Ecosystem",
        "Documentation/Iron-Path",
        "Documentation/Yggdrasil-DNS",
        "Documentation/Constitutional-Code-Store",
    ]

    for rel in missing_nodes:
        node = root / rel
        ensure_empty_dir(node)
        write_readme(
            node,
            node.name,
            "Node scaffolded from requested architecture. Attach canonical source and artifacts here.",
        )

    # Branch lane manifests sourced from actual git refs
    remote_branches = git_remote_branches(repo)
    lane_matchers = {
        "main": lambda b: b == "main",
        "dev": lambda b: b == "dev",
        "experiment": lambda b: b.startswith("experiment/"),
        "heal-repair": lambda b: b == "heal/repair",
        "legacy": lambda b: b.startswith("legacy/"),
        "release": lambda b: b.startswith("release/"),
        "hotfix": lambda b: b.startswith("hotfix/"),
        "governance-lock": lambda b: b == "governance-lock",
        "security-hardening": lambda b: b == "security-hardening",
    }

    governance_files = [
        ".github/THIRST_BRANCH_ACCEPTANCE_CRITERIA.md",
        ".github/branch-transfer-matrix.yaml",
        ".github/BRANCH_PROTECTION.md",
        "docs/security_compliance/BRANCH_PROTECTION_CONFIG.md",
    ]

    for lane, matcher in lane_matchers.items():
        lane_dir = root / "Branches" / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        hits = [b for b in remote_branches if matcher(b)]

        lines = [
            f"# {lane} lane files",
            "",
            "## Active Remote Branches",
            "",
        ]
        if hits:
            lines.extend([f"- `{b}`" for b in hits])
        else:
            lines.append("- _(no active branches found in this lane)_")

        lines.extend(
            [
                "",
                "## Governance and Transfer Artifacts",
                "",
            ]
        )
        for rel in governance_files:
            if (repo / rel).exists():
                lines.append(f"- `{rel}`")

        lines.extend(
            [
                "",
                "## Notes",
                "",
                "- This lane manifest is generated from live git refs and canonical governance files.",
                "- For promotion rules, see `.github/THIRST_BRANCH_ACCEPTANCE_CRITERIA.md`.",
            ]
        )

        (lane_dir / "FILES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Write root-level manifest proving organization linkage
    manifest = root / "ORGANIZATION_MANIFEST.md"
    manifest.write_text(
        "\n".join(
            [
                "# Project-AI Monorepo Organization Manifest",
                "",
                "This structure implements the requested architecture tree as an explicit organization layer.",
                "",
                f"- Mapped nodes: **{linked}**",
                f"- Stubbed nodes (missing source): **{stubbed + len(missing_nodes)}**",
                "",
                "## Canonical Terms",
                "- Thirsty-Lang",
                "- Thirst of Gods",
                "- T.A.R.L.",
                "- Shadow Thirst",
                "- TSCG",
                "- TSCG+B",
                "",
                "## Notes",
                "- Existing runtime source remains in place to avoid breaking import/build contracts.",
                "- Each node README links representative files from current canonical source paths.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"ORGANIZED_OK mapped={linked} stubbed={stubbed + len(missing_nodes)}")


if __name__ == "__main__":
    main()
