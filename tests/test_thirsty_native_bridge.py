# ============================================================================ #
# Focused tests for the native Thirsty bridge parser/executor.
# ============================================================================ #

from app.core.thirsty_native_bridge import ThirstyNativeBridge


def test_parse_single_expression_returns_expression_tree():
    bridge = ThirstyNativeBridge()

    parsed = bridge.parse("(HALT (SecurityViolation (UnauthorizedMutation)))")

    assert parsed == ["HALT", ["SecurityViolation", ["UnauthorizedMutation"]]]


def test_parse_multiple_top_level_expressions_preserves_all_roots():
    bridge = ThirstyNativeBridge()

    parsed = bridge.parse("(STATUS (ACTIVE)) (HALT (TEST))")

    assert parsed == [["STATUS", ["ACTIVE"]], ["HALT", ["TEST"]]]


def test_execute_multiple_top_level_expressions_returns_each_result():
    bridge = ThirstyNativeBridge()

    result = bridge.execute("(STATUS (ACTIVE)) (HALT (TEST))")

    assert result == [None, "HALTED"]
