"""Project-AI tarl public interface."""

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
from tarl.diagnostics import (
    Diagnostic,
    DiagnosticBatch,
    Location,
    Severity,
    make_diagnostic,
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
from tarl.validate import (
    DEFAULT_ALLOWED_AUTHORITIES,
    Validator,
    allowed_authorities,
    is_valid,
    validate,
    validate_with_authorities,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_VERDICTS",
    "CONFIG_ALLOWED_KEYS",
    "DEFAULT_ALLOWED_AUTHORITIES",
    "DEFAULT_AUDIT_ENABLED",
    "DEFAULT_AUDIT_MAX_RECORDS",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_POLICY_TIMEOUT_MS",
    "PARSER_ALLOWED_KEYS",
    "TARL",
    "TARL_VERSION",
    "CompiledTarl",
    "Compiler",
    "DefaultCompiler",
    "Diagnostic",
    "DiagnosticBatch",
    "ExecutionRecord",
    "Location",
    "PolicyProtocol",
    "PolicyRule",
    "Severity",
    "TarlCompileError",
    "TarlConfig",
    "TarlConfigError",
    "TarlDecision",
    "TarlError",
    "TarlParseError",
    "TarlPolicy",
    "TarlRuntime",
    "TarlRuntimeError",
    "TarlVerdict",
    "Validator",
    "allow_policy",
    "allowed_authorities",
    "compile_record",
    "config_from_mapping",
    "default_compile_policy",
    "deny_policy",
    "execute_compiled",
    "format_tarl",
    "is_valid",
    "make_config",
    "make_decision",
    "make_diagnostic",
    "make_tarl",
    "parse",
    "parse_mapping",
    "validate",
    "validate_with_authorities",
]
