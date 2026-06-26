"""Unit tests for tarl H3 modules: system, modules, stdlib, ffi, default_policies."""

from __future__ import annotations

import pytest
from tarl.core import make_tarl
from tarl.policy import allow_policy

from tarl import (
    DEFAULT_POLICIES,
    DEFAULT_STDLIB,
    DENY_READ_ON_PROTECTED_PATH,
    DENY_UNAUTHORIZED_MUTATION,
    ESCALATE_ON_UNKNOWN_AGENT,
    REQUIRE_CAPABILITY,
    BuiltInFunction,
    FFIBridge,
    ForeignFunction,
    Module,
    StandardLibrary,
    TarlFFIError,
    TarlModuleError,
    TarlStdlibError,
    TarlSystemError,
    TarlVerdict,
    default_ffi,
    default_module_system,
    default_policy_set,
    deny_read_on_protected_path,
    deny_unauthorized_mutation,
    escalate_on_unknown_agent,
    get_system,
    make_ffi,
    make_module,
    make_stdlib,
    require_capability,
)

# ---------------------------------------------------------------------------
# default_policies
# ---------------------------------------------------------------------------


def test_default_policy_set_returns_fresh_copies() -> None:
    set1 = default_policy_set()
    set2 = default_policy_set()
    assert set1 is not set2
    assert len(set1) == 4
    assert len(set2) == 4


def test_default_policies_contains_expected_names() -> None:
    names = [p.name for p in DEFAULT_POLICIES]
    for n in (
        "deny_unauthorized_mutation",
        "escalate_on_unknown_agent",
        "deny_read_on_protected_path",
        "require_capability",
    ):
        assert n in names


def test_deny_unauthorized_mutation_denies_when_mutation_no_flag() -> None:
    decision = deny_unauthorized_mutation({"mutation": True})
    assert decision.verdict is TarlVerdict.DENY


def test_deny_unauthorized_mutation_allows_when_flag_set() -> None:
    decision = deny_unauthorized_mutation({"mutation": True, "mutation_allowed": True})
    assert decision.verdict is TarlVerdict.ALLOW


def test_deny_unauthorized_mutation_allows_when_no_mutation() -> None:
    decision = deny_unauthorized_mutation({"mutation": False})
    assert decision.verdict is TarlVerdict.ALLOW


def test_escalate_on_unknown_agent_escalates_when_no_agent() -> None:
    decision = escalate_on_unknown_agent({})
    assert decision.verdict is TarlVerdict.ESCALATE


def test_escalate_on_unknown_agent_allows_when_agent_present() -> None:
    decision = escalate_on_unknown_agent({"agent": "cap-1"})
    assert decision.verdict is TarlVerdict.ALLOW


def test_deny_read_on_protected_path_denies_etc() -> None:
    decision = deny_read_on_protected_path({"path": "/etc/passwd"})
    assert decision.verdict is TarlVerdict.DENY


def test_deny_read_on_protected_path_denies_sys() -> None:
    decision = deny_read_on_protected_path({"path": "/sys/kernel"})
    assert decision.verdict is TarlVerdict.DENY


def test_deny_read_on_protected_path_allows_safe() -> None:
    decision = deny_read_on_protected_path({"path": "/var/log"})
    assert decision.verdict is TarlVerdict.ALLOW


def test_require_capability_escalates_when_missing() -> None:
    decision = require_capability({})
    assert decision.verdict is TarlVerdict.ESCALATE


def test_require_capability_allows_when_present() -> None:
    decision = require_capability({"capability": "cap-1"})
    assert decision.verdict is TarlVerdict.ALLOW


def test_module_level_policy_wrappers_exist() -> None:
    """Module-level constants exist and are bound to the rules."""
    assert DENY_UNAUTHORIZED_MUTATION.name == "deny_unauthorized_mutation"
    assert ESCALATE_ON_UNKNOWN_AGENT.name == "escalate_on_unknown_agent"
    assert DENY_READ_ON_PROTECTED_PATH.name == "deny_read_on_protected_path"
    assert REQUIRE_CAPABILITY.name == "require_capability"


# ---------------------------------------------------------------------------
# stdlib
# ---------------------------------------------------------------------------


def test_make_stdlib_validates_list() -> None:
    with pytest.raises(TarlStdlibError, match="builtins must be list"):
        make_stdlib("not a list")  # type: ignore[arg-type]


def test_make_stdlib_validates_entries() -> None:
    with pytest.raises(TarlStdlibError, match="builtins\\[0\\]"):
        make_stdlib(["not a BuiltInFunction"])  # type: ignore[list-item]


def test_builtin_function_validates_name() -> None:
    with pytest.raises(TarlStdlibError, match="built-in name"):
        BuiltInFunction("", 1, lambda x: x)


def test_builtin_function_validates_arity() -> None:
    with pytest.raises(TarlStdlibError, match="arity"):
        BuiltInFunction("x", -2, lambda: None)


def test_builtin_function_validates_arity_type() -> None:
    with pytest.raises(TarlStdlibError, match="arity"):
        BuiltInFunction("x", "1", lambda: None)  # type: ignore[arg-type]


def test_builtin_function_validates_callable() -> None:
    with pytest.raises(TarlStdlibError, match="callable"):
        BuiltInFunction("x", 1, "not callable")  # type: ignore[arg-type]


def test_standard_library_rejects_duplicates() -> None:
    with pytest.raises(TarlStdlibError, match="duplicate"):
        StandardLibrary(
            builtins=(
                BuiltInFunction("foo", 0, lambda: None),
                BuiltInFunction("foo", 0, lambda: None),
            )
        )


def test_standard_library_get_returns_builtin() -> None:
    lib = DEFAULT_STDLIB
    builtin = lib.get("len")
    assert builtin.name == "len"


def test_standard_library_get_rejects_unknown() -> None:
    with pytest.raises(TarlStdlibError, match="unknown built-in"):
        DEFAULT_STDLIB.get("not_a_real_builtin")


def test_standard_library_get_rejects_non_string() -> None:
    with pytest.raises(TarlStdlibError, match="name must be str"):
        DEFAULT_STDLIB.get(42)  # type: ignore[arg-type]


def test_standard_library_has_returns_correctly() -> None:
    assert DEFAULT_STDLIB.has("len") is True
    assert DEFAULT_STDLIB.has("nonexistent") is False
    assert DEFAULT_STDLIB.has(42) is False  # type: ignore[arg-type]


def test_standard_library_names_includes_builtins() -> None:
    names = DEFAULT_STDLIB.names()
    for n in ("len", "str", "int", "max", "min"):
        assert n in names


def test_standard_library_call_invokes_builtin() -> None:
    result = DEFAULT_STDLIB.call("len", [1, 2, 3])
    assert result == 3


def test_standard_library_call_enforces_arity() -> None:
    with pytest.raises(TarlStdlibError, match="expects 1 args"):
        DEFAULT_STDLIB.call("len")  # arity 1, gave 0


def test_default_stdlib_len_works() -> None:
    assert DEFAULT_STDLIB.call("len", "hello") == 5


def test_default_stdlib_int_works() -> None:
    assert DEFAULT_STDLIB.call("int", "42") == 42


def test_default_stdlib_int_conversion_error() -> None:
    with pytest.raises(TarlStdlibError, match="cannot convert"):
        DEFAULT_STDLIB.call("int", "not a number")


def test_default_stdlib_max_works() -> None:
    assert DEFAULT_STDLIB.call("max", 1, 5, 3) == 5


def test_default_stdlib_max_from_list() -> None:
    assert DEFAULT_STDLIB.call("max", [1, 5, 3]) == 5


def test_default_stdlib_min_works() -> None:
    assert DEFAULT_STDLIB.call("min", 1, 5, 3) == 1


def test_default_stdlib_min_from_list() -> None:
    assert DEFAULT_STDLIB.call("min", [1, 5, 3]) == 1


def test_default_stdlib_min_max_no_args_raises() -> None:
    with pytest.raises(TarlStdlibError, match="requires at least one"):
        DEFAULT_STDLIB.call("max")
    with pytest.raises(TarlStdlibError, match="requires at least one"):
        DEFAULT_STDLIB.call("min")


def test_default_stdlib_len_no_len_method_raises() -> None:
    with pytest.raises(TarlStdlibError, match="has no len"):
        DEFAULT_STDLIB.call("len", 42)


# ---------------------------------------------------------------------------
# modules
# ---------------------------------------------------------------------------


def test_module_validates_name() -> None:
    with pytest.raises(TarlModuleError, match="module name"):
        Module(name="", loader=lambda: None)


def test_module_validates_loader() -> None:
    with pytest.raises(TarlModuleError, match="loader must be callable"):
        Module(name="x", loader="not callable")  # type: ignore[arg-type]


def test_make_module_converts_list_to_tuple() -> None:
    m = make_module(name="x", loader=lambda: None, exports=["a", "b"])
    assert m.exports == ("a", "b")


def test_make_module_rejects_non_list_exports() -> None:
    with pytest.raises(TarlModuleError, match="exports must be"):
        make_module(name="x", loader=lambda: None, exports="a")  # type: ignore[arg-type]


def test_module_system_register_and_has() -> None:
    ms = default_module_system()
    ms.register(make_module(name="foo", loader=lambda: None))
    assert ms.has("foo") is True
    assert ms.has("bar") is False


def test_module_system_register_rejects_duplicate() -> None:
    ms = default_module_system()
    ms.register(make_module(name="foo", loader=lambda: None))
    with pytest.raises(TarlModuleError, match="already registered"):
        ms.register(make_module(name="foo", loader=lambda: None))


def test_module_system_register_validates_type() -> None:
    ms = default_module_system()
    with pytest.raises(TarlModuleError, match="module must be Module"):
        ms.register("not a module")  # type: ignore[arg-type]


def test_module_system_load_returns_registered() -> None:
    ms = default_module_system()
    m = make_module(name="foo", loader=lambda: "result")
    ms.register(m)
    assert ms.load("foo") is m


def test_module_system_load_rejects_unknown() -> None:
    ms = default_module_system()
    with pytest.raises(TarlModuleError, match="not registered"):
        ms.load("unknown")


def test_module_system_load_rejects_empty_name() -> None:
    ms = default_module_system()
    with pytest.raises(TarlModuleError, match="module name"):
        ms.load("")


def test_module_system_detects_circular_dependency() -> None:
    ms = default_module_system()
    m = make_module(name="foo", loader=lambda: None)
    ms.register(m)
    ms.loading.add("foo")  # simulate in-progress load
    with pytest.raises(TarlModuleError, match="circular dependency"):
        ms.load("foo")


def test_module_system_names_returns_sorted() -> None:
    ms = default_module_system()
    ms.register(make_module(name="z", loader=lambda: None))
    ms.register(make_module(name="a", loader=lambda: None))
    ms.register(make_module(name="m", loader=lambda: None))
    assert ms.names() == ("a", "m", "z")


def test_module_system_unregister() -> None:
    ms = default_module_system()
    ms.register(make_module(name="foo", loader=lambda: None))
    ms.unregister("foo")
    assert ms.has("foo") is False
    ms.unregister("nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# ffi
# ---------------------------------------------------------------------------


def test_make_ffi_validates_list() -> None:
    with pytest.raises(TarlFFIError, match="bindings must be list"):
        make_ffi("not a list")  # type: ignore[arg-type]


def test_make_ffi_validates_entries() -> None:
    with pytest.raises(TarlFFIError, match="bindings\\[0\\]"):
        make_ffi(["not a ForeignFunction"])  # type: ignore[list-item]


def test_foreign_function_validates_name() -> None:
    with pytest.raises(TarlFFIError, match="ffi name"):
        ForeignFunction("", (str,), str, lambda x: x)


def test_foreign_function_validates_arg_types_tuple() -> None:
    with pytest.raises(TarlFFIError, match="arg_types must be tuple"):
        ForeignFunction("x", [str], str, lambda x: x)  # type: ignore[arg-type]


def test_foreign_function_validates_ret_type() -> None:
    with pytest.raises(TarlFFIError, match="ret_type must be type"):
        ForeignFunction("x", (str,), "str", lambda x: x)  # type: ignore[arg-type]


def test_foreign_function_validates_callable() -> None:
    with pytest.raises(TarlFFIError, match="func must be callable"):
        ForeignFunction("x", (str,), str, "not callable")  # type: ignore[arg-type]


def test_foreign_function_call_returns_value() -> None:
    f = ForeignFunction("double", (int,), int, lambda x: x * 2)
    assert f.call(5) == 10


def test_foreign_function_call_validates_arity() -> None:
    f = ForeignFunction("double", (int,), int, lambda x: x * 2)
    with pytest.raises(TarlFFIError, match="expects 1 args"):
        f.call()


def test_foreign_function_call_validates_arg_types() -> None:
    f = ForeignFunction("double", (int,), int, lambda x: x * 2)
    with pytest.raises(TarlFFIError, match="arg\\[0\\]"):
        f.call("not an int")


def test_foreign_function_call_allows_object_wildcard() -> None:
    f = ForeignFunction("id", (object,), object, lambda x: x)
    assert f.call(42) == 42
    assert f.call("hello") == "hello"


def test_foreign_function_call_validates_return_type() -> None:
    f = ForeignFunction("bad", (int,), int, lambda x: "wrong")
    with pytest.raises(TarlFFIError, match="returned"):
        f.call(1)


def test_foreign_function_call_bool_subclass() -> None:
    """bool is a subclass of int, but bool is also allowed when expected."""
    f = ForeignFunction("takes_int", (int,), int, lambda x: x)
    assert f.call(True) == 1


def test_ffi_bridge_rejects_duplicates() -> None:
    f1 = ForeignFunction("foo", (str,), str, lambda x: x)
    f2 = ForeignFunction("foo", (str,), str, lambda x: x)
    with pytest.raises(TarlFFIError, match="duplicate"):
        FFIBridge(bindings=(f1, f2))


def test_ffi_bridge_get_and_call() -> None:
    f = ForeignFunction("double", (int,), int, lambda x: x * 2)
    bridge = make_ffi([f])
    assert bridge.get("double") is f
    assert bridge.call("double", 5) == 10


def test_ffi_bridge_get_unknown_raises() -> None:
    with pytest.raises(TarlFFIError, match="unknown ffi"):
        default_ffi().get("nonexistent")


def test_ffi_bridge_get_non_string_raises() -> None:
    with pytest.raises(TarlFFIError, match="name must be str"):
        default_ffi().get(42)  # type: ignore[arg-type]


def test_ffi_bridge_has_returns_correctly() -> None:
    f = ForeignFunction("x", (str,), str, lambda x: x)
    bridge = make_ffi([f])
    assert bridge.has("x") is True
    assert bridge.has("y") is False
    assert bridge.has(42) is False  # type: ignore[arg-type]


def test_ffi_bridge_names_returns_correctly() -> None:
    bridge = make_ffi(
        [
            ForeignFunction("a", (str,), str, lambda x: x),
            ForeignFunction("b", (str,), str, lambda x: x),
        ]
    )
    assert bridge.names() == ("a", "b")


def test_default_ffi_is_empty() -> None:
    assert default_ffi().names() == ()


# ---------------------------------------------------------------------------
# system
# ---------------------------------------------------------------------------


def test_get_system_returns_fresh_instance() -> None:
    s1 = get_system()
    s2 = get_system()
    assert s1 is not s2


def test_system_initialize_is_idempotent() -> None:
    s = get_system()
    s.initialize()
    n_before = len(s.diagnostics.diagnostics)
    s.initialize()  # idempotent
    assert len(s.diagnostics.diagnostics) == n_before


def test_system_shutdown_is_idempotent() -> None:
    s = get_system()
    s.shutdown()  # not initialized; should be no-op
    s.initialize()
    s.shutdown()
    s.shutdown()  # idempotent
    assert s._initialized is False


def test_system_register_policy_validates_type() -> None:
    s = get_system()
    with pytest.raises(TarlSystemError, match="policy must be TarlPolicy"):
        s.register_policy("not a policy")  # type: ignore[arg-type]


def test_system_register_policy_adds_to_runtime() -> None:
    s = get_system()
    policy = allow_policy("test")
    s.register_policy(policy)
    assert any(p.name == "test" for p in s.runtime.policies)


def test_system_compile_and_execute_requires_init() -> None:
    s = get_system()
    record = make_tarl(intent="x", scope="x", authority="system")
    with pytest.raises(TarlSystemError, match="not initialized"):
        s.compile_and_execute(record, allow_policy("test"), {})


def test_system_compile_and_execute_validates_record_type() -> None:
    s = get_system()
    s.initialize()
    with pytest.raises(TarlSystemError, match="record must be TARL"):
        s.compile_and_execute("not a TARL", allow_policy("test"), {})  # type: ignore[arg-type]


def test_system_compile_and_execute_validates_policy_type() -> None:
    s = get_system()
    s.initialize()
    record = make_tarl(intent="x", scope="x", authority="system")
    with pytest.raises(TarlSystemError, match="policy must be TarlPolicy"):
        s.compile_and_execute(record, "not a policy", {})  # type: ignore[arg-type]


def test_system_compile_and_execute_succeeds() -> None:
    s = get_system()
    s.initialize()
    record = make_tarl(intent="x", scope="x", authority="system")
    policy = allow_policy("test")
    s.register_policy(policy)  # must register before execute
    decision: object = s.compile_and_execute(record, policy, {"any": "ctx"})
    assert decision.verdict is TarlVerdict.ALLOW  # type: ignore[attr-defined]


def test_system_compile_and_execute_validates_record_authority() -> None:
    s = get_system()
    s.initialize()
    record = make_tarl(intent="x", scope="x", authority="evil")
    with pytest.raises(TarlSystemError, match="validation"):
        s.compile_and_execute(record, allow_policy("test"), {})


def test_system_records_init_diagnostic() -> None:
    s = get_system()
    s.initialize()
    messages = [d.message for d in s.diagnostics.diagnostics]
    assert any("initialized" in m for m in messages)


def test_system_records_shutdown_diagnostic() -> None:
    s = get_system()
    s.initialize()
    s.shutdown()
    messages = [d.message for d in s.diagnostics.diagnostics]
    assert any("shutdown" in m for m in messages)


def test_system_end_to_end_with_default_policies() -> None:
    """Full integration: default policies against malicious inputs."""
    s = get_system()
    s.initialize()
    for p in DEFAULT_POLICIES:
        s.register_policy(p)
    # Test with mutation context — should DENY via deny_unauthorized_mutation
    record = make_tarl(intent="mutate", scope="/data", authority="system")
    decision: object = s.compile_and_execute(
        record,
        s.runtime.policies[0],  # first default policy
        {"mutation": True},  # triggers DENY
    )
    assert decision.verdict is TarlVerdict.DENY  # type: ignore[attr-defined]
