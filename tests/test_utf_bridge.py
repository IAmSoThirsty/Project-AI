from __future__ import annotations

from app.core.utf_bridge import UTFBridge


def make_bridge(tmp_path) -> UTFBridge:
    return UTFBridge(substrate_root=str(tmp_path))


def test_fingerprint_utf_asset_detects_sovereign_thirsty_asset(tmp_path):
    asset = tmp_path / "sovereign_logic.thirsty"
    asset.write_text(
        "# STATUS: ACTIVE | DATE: 2026-03-22 | TIME: 12:00\n"
        "# COMPLIANCE: Sovereign Substrate / sovereign_logic.thirsty\n"
        "# Productivity: Active\n"
        "shield core_guard {\n"
        "drink voltage = 3.7\n"
        "pour voltage\n"
        "}\n",
        encoding="utf-8",
    )

    profile = make_bridge(tmp_path).fingerprint_utf_asset("sovereign_logic.thirsty")

    assert profile["fingerprint_operation"] == "utf_asset_fingerprint"
    assert profile["language"] == "Thirsty-Lang"
    assert profile["direct_execution_supported"] is True
    assert profile["bridge_operation"] == "execute_thirsty_file"
    assert profile["is_sovereign_asset"] is True
    assert profile["construct_categories"]["security"] == ["shield"]
    assert profile["construct_categories"]["core"] == ["drink", "pour"]


def test_fingerprint_utf_asset_marks_tarl_as_profile_only(tmp_path):
    asset = tmp_path / "kernel_guard.tarl"
    asset.write_text(
        "# STATUS: ACTIVE | DATE: 2026-03-22 | TIME: 12:00\n"
        "# COMPLIANCE: Sovereign Substrate / kernel_guard.tarl\n"
        "# Productivity: Active\n"
        "shield gate\n"
        "defend perimeter\n",
        encoding="utf-8",
    )

    profile = make_bridge(tmp_path).fingerprint_utf_asset("kernel_guard.tarl")

    assert profile["language"] == "T.A.R.L."
    assert profile["recommended_runtime"] == "tarl_runtime"
    assert profile["direct_execution_supported"] is False
    assert profile["bridge_operation"] == "profile_only"
    assert profile["is_utf_asset"] is True
    assert profile["construct_categories"]["security"] == ["shield", "defend"]


def test_fingerprint_utf_asset_uses_keywords_when_extension_is_unknown(tmp_path):
    asset = tmp_path / "mystery.substrate"
    asset.write_text(
        "fountain Council {\n"
        "glass decide() {\n"
        "return true\n"
        "}\n"
        "}\n",
        encoding="utf-8",
    )

    profile = make_bridge(tmp_path).fingerprint_utf_asset("mystery.substrate")

    assert profile["language"] == "Unknown"
    assert profile["is_utf_asset"] is True
    assert profile["direct_execution_supported"] is False
    assert profile["construct_categories"]["higher"] == ["glass", "fountain"]


def test_negotiate_utf_hydration_extracts_required_roots_and_fields(tmp_path):
    asset = tmp_path / "battery_master.thirsty"
    asset.write_text(
        "drink cycles = data[\"cycles\"]\n"
        "drink temperature = data[\"temperature\"]\n"
        "drink voltage = data[\"voltage\"]\n",
        encoding="utf-8",
    )

    negotiation = make_bridge(tmp_path).negotiate_utf_hydration(
        "battery_master.thirsty",
        {"data": {"cycles": 500, "temperature": 42.0}},
    )

    assert negotiation["operation"] == "utf_hydration_negotiation"
    assert negotiation["required_context_roots"] == ["data"]
    assert negotiation["required_fields_by_root"]["data"] == [
        "cycles",
        "temperature",
        "voltage",
    ]
    assert negotiation["missing_fields_by_root"]["data"] == ["voltage"]
    assert negotiation["context_satisfied"] is False


def test_negotiate_utf_hydration_tracks_defaults_and_override_candidates(tmp_path):
    asset = tmp_path / "kernel_master.thirsty"
    asset.write_text(
        "drink temporal_weight = 1.0\n"
        "drink session_continuity = \"CONTINUOUS\"\n"
        "pour temporal_weight\n",
        encoding="utf-8",
    )

    negotiation = make_bridge(tmp_path).negotiate_utf_hydration(
        "kernel_master.thirsty",
        {"temporal_weight": 0.25, "session_continuity": "RECOVERY", "noise": True},
    )

    assert negotiation["declared_defaults"]["temporal_weight"] == "1.0"
    assert negotiation["declared_defaults"]["session_continuity"] == "\"CONTINUOUS\""
    assert negotiation["override_candidates"] == [
        "session_continuity",
        "temporal_weight",
    ]
    assert negotiation["unused_context_keys"] == ["noise"]
    assert negotiation["context_satisfied"] is True


def test_execute_thirsty_file_with_contract_executes_when_context_is_satisfied(tmp_path):
    asset = tmp_path / "contract_ok.thirsty"
    asset.write_text(
        "drink voltage = data[\"voltage\"]\n"
        "drink result = voltage\n",
        encoding="utf-8",
    )

    result = make_bridge(tmp_path).execute_thirsty_file_with_contract(
        "contract_ok.thirsty",
        {"data": {"voltage": 3.7}},
    )

    assert result["voltage"] == 3.7
    assert result["result"] == 3.7


def test_execute_thirsty_file_with_contract_raises_for_missing_fields(tmp_path):
    asset = tmp_path / "contract_missing.thirsty"
    asset.write_text(
        "drink voltage = data[\"voltage\"]\n",
        encoding="utf-8",
    )

    bridge = make_bridge(tmp_path)

    try:
        bridge.execute_thirsty_file_with_contract(
            "contract_missing.thirsty",
            {"data": {}},
        )
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected a contract validation error")

    assert "UTF hydration contract not satisfied" in message
    assert "data[voltage]" in message


def test_profile_native_runtime_workspace_reads_cargo_manifest(tmp_path):
    runtime_root = tmp_path / "engines" / "waterfall_native"
    source_root = runtime_root / "src"
    source_root.mkdir(parents=True)

    (runtime_root / "Cargo.toml").write_text(
        "[package]\n"
        'name = "waterfall-native-engine"\n'
        'version = "0.1.0"\n'
        'edition = "2021"\n'
        "\n"
        "[lib]\n"
        'path = "src/lib.rs"\n'
        "\n"
        "[package.metadata.waterfall]\n"
        'engine_id = "thirstys-waterfall-native"\n'
        'integration = "utf-sidecar"\n'
        'focus = ["html-tokenizer", "block-layout"]\n',
        encoding="utf-8",
    )
    (runtime_root / "README.md").write_text("# WaterFall Native Engine\n", encoding="utf-8")
    (source_root / "lib.rs").write_text("pub fn engine_identity() {}\n", encoding="utf-8")

    profile = make_bridge(tmp_path).profile_native_runtime_workspace(
        "engines/waterfall_native"
    )

    assert profile["operation"] == "utf_native_runtime_profile"
    assert profile["runtime_family"] == "rust_native_engine"
    assert profile["cargo_manifest_present"] is True
    assert profile["package_name"] == "waterfall-native-engine"
    assert profile["package_version"] == "0.1.0"
    assert profile["library_entry"] == "src/lib.rs"
    assert profile["waterfall_engine_id"] == "thirstys-waterfall-native"
    assert profile["integration_track"] == "utf-sidecar"
    assert profile["render_focus"] == ["html-tokenizer", "block-layout"]
    assert profile["source_files"] == ["src/lib.rs"]
    assert profile["recommended_runtime"] == "cargo"
