import pathlib
import re

PATTERNS: list[tuple[str, str]] = [
    ("openai", r"sk-(?:proj-)?[A-Za-z0-9_-]{10,}"),
    ("hf", r"hf_[A-Za-z0-9]{10,}"),
    ("aws_access", r"AKIA[0-9A-Z]{16}"),
    ("smtp_pass", r"SMTP_PASSWORD\s*=\s*\S+"),
    ("generic_secret", r"(SECRET|PASSWORD|TOKEN|API_KEY)\s*[=:]\s*\S+"),
]


def main() -> int:
    root = pathlib.Path(".")
    tracked_file_list = root / "docs" / "security" / "tracked-files.txt"
    out_path = root / "docs" / "security" / "secret-scan-findings.txt"

    files = [
        p.strip()
        for p in tracked_file_list.read_text(encoding="utf-8").splitlines()
        if p.strip()
    ]

    findings: list[tuple[str, str]] = []
    for f in files:
        path = root / f
        if not path.is_file():
            continue
        if path.suffix.lower() == ".pyc":
            continue

        try:
            data = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for name, pat in PATTERNS:
            if re.search(pat, data):
                findings.append((f, name))
                break

    out_path.write_text("\n".join([f"{f}\t{t}" for f, t in findings]), encoding="utf-8")

    print(f"FINDINGS {len(findings)}")
    for f, t in findings[:50]:
        print(f"{f} [{t}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
