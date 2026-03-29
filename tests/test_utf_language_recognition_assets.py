from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "integrations" / "thirsty-lang-engine" / "utf_language_registry.json"


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_root_gitattributes_declares_every_utf_extension() -> None:
    registry = load_registry()
    contents = (ROOT / ".gitattributes").read_text(encoding="utf-8")

    for language in registry["languages"]:
        alias = language["gitattributes_alias"]
        for extension in language["extensions"]:
            expected = f"*{extension} linguist-language={alias} linguist-detectable"
            assert expected in contents


def test_engine_linguist_manifest_contains_every_utf_language() -> None:
    registry = load_registry()
    contents = (ROOT / "integrations" / "thirsty-lang-engine" / "languages.yml").read_text(
        encoding="utf-8"
    )

    for language in registry["languages"]:
        assert f"{language['name']}:" in contents
        for alias in language["aliases"]:
            assert f"- {alias}" in contents
        for extension in language["extensions"]:
            assert f'- "{extension}"' in contents


def test_vscode_extension_registers_every_utf_language_id() -> None:
    registry = load_registry()
    package = json.loads(
        (
            ROOT
            / "integrations"
            / "thirsty-lang-engine"
            / "vscode-extension"
            / "package.json"
        ).read_text(encoding="utf-8")
    )

    language_map = {entry["id"]: set(entry["extensions"]) for entry in package["contributes"]["languages"]}
    grammar_languages = {entry["language"] for entry in package["contributes"]["grammars"]}
    snippet_languages = {entry["language"] for entry in package["contributes"]["snippets"]}

    for language in registry["languages"]:
        language_id = language["vscode_id"]
        assert language_id in language_map
        assert set(language["extensions"]).issubset(language_map[language_id])
        assert language_id in grammar_languages
        assert language_id in snippet_languages


def test_local_linguist_mirror_contains_every_utf_language() -> None:
    registry = load_registry()
    contents = (
        ROOT / "integrations" / "linguist-test" / "lib" / "linguist" / "languages.yml"
    ).read_text(encoding="utf-8")

    for language in registry["languages"]:
        assert f"{language['name']}:" in contents
        for extension in language["extensions"]:
            assert f'- "{extension}"' in contents


def test_local_linguist_samples_exist_for_every_utf_language() -> None:
    registry = load_registry()
    samples_root = ROOT / "integrations" / "linguist-test" / "samples"

    for language in registry["languages"]:
        sample_dir = samples_root / language["sample_dir"]
        assert sample_dir.is_dir()
        assert any(sample_dir.iterdir())


def test_tree_sitter_scaffold_exists_for_utf() -> None:
    tree_sitter_root = ROOT / "integrations" / "thirsty-lang-engine" / "tree-sitter-utf"

    for relative_path in (
        "grammar.js",
        "tree-sitter.json",
        "README.md",
        "queries/highlights.scm",
        "queries/tags.scm",
        "queries/locals.scm",
    ):
        assert (tree_sitter_root / relative_path).is_file()


def test_submission_bundle_exists_for_github_linguist() -> None:
    bundle_root = (
        ROOT
        / "integrations"
        / "thirsty-lang-engine"
        / "submissions"
        / "github-linguist"
    )

    for relative_path in (
        "README.md",
        "PR_STRATEGY.md",
        "PULL_REQUEST_DRAFT.md",
        "SEARCH_QUERIES.md",
        "SAMPLE_INDEX.md",
        "build_submission_bundle.py",
    ):
        assert (bundle_root / relative_path).is_file()
