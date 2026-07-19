"""Project-AI tarl public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from tarl.compiler import (
    CompiledTarl,
    Compiler,
    DefaultCompiler,
    TarlCompileError,
    compile_record,
    default_compile_policy,
)
from tarl.config import (
    ALLOWED_KEYS as CONFIG_ALLOWED_KEYS,
)
from tarl.config import (
    DEFAULT_AUDIT_ENABLED,
    DEFAULT_AUDIT_MAX_RECORDS,
    DEFAULT_CACHE_SIZE,
    DEFAULT_POLICY_TIMEOUT_MS,
    TarlConfig,
    TarlConfigError,
    config_from_mapping,
    make_config,
)
from tarl.core import TARL, TARL_VERSION, make_tarl
from tarl.default_policies import (
    DEFAULT_POLICIES,
    DENY_READ_ON_PROTECTED_PATH,
    DENY_UNAUTHORIZED_MUTATION,
    ESCALATE_ON_UNKNOWN_AGENT,
    REQUIRE_CAPABILITY,
    default_policy_set,
    deny_read_on_protected_path,
    deny_unauthorized_mutation,
    escalate_on_unknown_agent,
    require_capability,
)
from tarl.diagnostics import (
    Diagnostic,
    DiagnosticBatch,
    Location,
    Severity,
    make_diagnostic,
)
from tarl.ffi import (
    FFIBridge,
    ForeignFunction,
    TarlFFIError,
    default_ffi,
    make_ffi,
)
from tarl.modules import (
    Module,
    ModuleSystem,
    TarlModuleError,
    default_module_system,
    make_module,
)
from tarl.parser import (
    ALLOWED_KEYS as PARSER_ALLOWED_KEYS,
)
from tarl.parser import (
    TarlParseError,
    format_tarl,
    parse,
    parse_mapping,
)
from tarl.policy import (
    PolicyProtocol,
    PolicyRule,
    TarlPolicy,
    allow_policy,
    deny_policy,
)
from tarl.runtime import (
    ExecutionRecord,
    TarlRuntime,
    TarlRuntimeError,
    execute_compiled,
)
from tarl.spec import (
    ALLOWED_VERDICTS,
    TarlDecision,
    TarlError,
    TarlVerdict,
    make_decision,
)
from tarl.stdlib import (
    DEFAULT_STDLIB,
    BuiltInFunction,
    StandardLibrary,
    TarlStdlibError,
    make_stdlib,
)
from tarl.system import TARLSystem, TarlSystemError, get_system
from tarl.validate import (
    DEFAULT_ALLOWED_AUTHORITIES,
    Validator,
    allowed_authorities,
    is_valid,
    validate,
    validate_with_authorities,
)

try:
    __version__ = _pkg_version("project-ai-tarl")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_VERDICTS",
    "CONFIG_ALLOWED_KEYS",
    "DEFAULT_ALLOWED_AUTHORITIES",
    "DEFAULT_AUDIT_ENABLED",
    "DEFAULT_AUDIT_MAX_RECORDS",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_POLICIES",
    "DEFAULT_POLICY_TIMEOUT_MS",
    "DEFAULT_STDLIB",
    "DENY_READ_ON_PROTECTED_PATH",
    "DENY_UNAUTHORIZED_MUTATION",
    "ESCALATE_ON_UNKNOWN_AGENT",
    "PARSER_ALLOWED_KEYS",
    "REQUIRE_CAPABILITY",
    "TARL",
    "TARL_VERSION",
    "BuiltInFunction",
    "CompiledTarl",
    "Compiler",
    "DefaultCompiler",
    "Diagnostic",
    "DiagnosticBatch",
    "ExecutionRecord",
    "FFIBridge",
    "ForeignFunction",
    "Location",
    "Module",
    "ModuleSystem",
    "PolicyProtocol",
    "PolicyRule",
    "Severity",
    "StandardLibrary",
    "TARLSystem",
    "TarlCompileError",
    "TarlConfig",
    "TarlConfigError",
    "TarlDecision",
    "TarlError",
    "TarlFFIError",
    "TarlModuleError",
    "TarlParseError",
    "TarlPolicy",
    "TarlRuntime",
    "TarlRuntimeError",
    "TarlStdlibError",
    "TarlSystemError",
    "TarlVerdict",
    "Validator",
    "allow_policy",
    "allowed_authorities",
    "compile_record",
    "config_from_mapping",
    "default_compile_policy",
    "default_ffi",
    "default_module_system",
    "default_policy_set",
    "deny_policy",
    "deny_read_on_protected_path",
    "deny_unauthorized_mutation",
    "escalate_on_unknown_agent",
    "execute_compiled",
    "format_tarl",
    "get_system",
    "is_valid",
    "make_config",
    "make_decision",
    "make_diagnostic",
    "make_ffi",
    "make_module",
    "make_stdlib",
    "make_tarl",
    "parse",
    "parse_mapping",
    "require_capability",
    "validate",
    "validate_with_authorities",
]
