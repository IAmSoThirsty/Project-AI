#                                           [2026-03-07 12:00]
#                                          Productivity: Active
"""Tests for the web frontend project structure and configuration."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestWebFrontendStructure:
    """Verify the Next.js web frontend has required files and configuration."""

    def test_package_json_exists(self):
        pkg = ROOT / "web" / "package.json"
        assert pkg.exists(), "web/package.json must exist"

    def test_package_json_has_required_fields(self):
        pkg = ROOT / "web" / "package.json"
        data = json.loads(pkg.read_text(encoding="utf-8"))
        assert "name" in data
        assert "version" in data
        assert "scripts" in data
        assert "dependencies" in data

    def test_package_json_has_build_script(self):
        pkg = ROOT / "web" / "package.json"
        data = json.loads(pkg.read_text(encoding="utf-8"))
        scripts = data.get("scripts", {})
        assert "build" in scripts, "package.json must have a 'build' script"
        assert "dev" in scripts, "package.json must have a 'dev' script"

    def test_next_config_exists(self):
        assert (ROOT / "web" / "next.config.js").exists(), "next.config.js must exist"

    def test_tsconfig_exists(self):
        assert (ROOT / "web" / "tsconfig.json").exists(), "tsconfig.json must exist"

    def test_app_directory_exists(self):
        assert (ROOT / "web" / "app").is_dir(), "web/app/ directory must exist"

    def test_homepage_exists(self):
        page = ROOT / "web" / "app" / "page.tsx"
        assert page.exists(), "web/app/page.tsx (homepage) must exist"

    def test_env_example_exists(self):
        env_example = ROOT / "web" / ".env.example"
        assert env_example.exists(), "web/.env.example must exist for developer setup"

    def test_eslint_config_exists(self):
        assert (ROOT / "web" / ".eslintrc.json").exists(), (
            "web/.eslintrc.json must exist"
        )

    def test_no_env_file_committed(self):
        env_file = ROOT / "web" / ".env"
        assert not env_file.exists(), ".env file must not be committed to git"
