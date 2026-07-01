"""Thirsty-Lang proof-obligation extraction for the security audit chain.

Per PHASE_T_DISCOVERY.md Phase T3: the canonical Project-AI audit chain
proof obligations are described in `audit_proof.thirst` (Thirsty-Lang
1st tier — base language). This module parses the .thirst source via
the language's Lexer + Parser and walks the AST to extract the
contract annotations (`requires`, `ensures`) declared on the governed
functions. The result is a `ProofObligationReport` that the audit
chain can verify before allowing operations.

Subordination contract:
  - The .thirst file is the declarative description of what the audit
    chain needs. The Python `AppendOnlyAuditRelay` is the authoritative
    runtime; this module is the verification surface.
  - Fail-closed: any extraction error (parse failure, missing dep,
    missing source) raises `ProofObligationError`. The audit chain
    treats this as a denied operation; an unfulfilled obligation is
    never silently bypassed.
  - The obligations are static and deterministic: same .thirst source
    => same report.
  - Strict typing: mypy --strict clean.

Honest scope (corrected from the original T3 plan):
- The published `thirsty-lang==0.8.1` wheel does NOT include the
  `utf.thirsty_lang.proof_obligations` module that the source repo
  contains. T3 therefore uses the Lexer + Parser directly and walks
  the AST to extract contract annotations. The full
  `extract_proof_obligations` integration is deferred to a later
  version bump of the language dep.
- The capability enumeration (read/write/compute on stdlib modules)
  is NOT extracted by this module — that's a feature of the higher
  `extract_proof_obligations` API. T3 reports contracts only.
- T3 is a static surface: it reports what the .thirst source says
  the chain needs. Enforcement is a separate sub-phase (T3.5).

Architectural invariants (AGENTS.md v3):
- Downward-only deps: this module imports `kernel` (canonical types)
  and `utf.thirsty_lang.*` (PyPI dep `thirsty-lang==0.8.1`).
- No upward imports: it does not import `security.bridge`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from utf.thirsty_lang.lexer import Lexer as _LexerType
    from utf.thirsty_lang.parser import Parser as _ParserType
else:
    _LexerType = object
    _ParserType = object

# utf.thirsty_lang.* is the PyPI dep `thirsty-lang==0.8.1` (Phase T1).
# The dotted namespace `utf.thirsty_lang` is the language's first tier.
_Lexer: _LexerType | None
_Parser: _ParserType | None
try:
    from utf.thirsty_lang.lexer import Lexer as _Lexer  # type: ignore[assignment]
    from utf.thirsty_lang.parser import Parser as _Parser  # type: ignore[assignment]

    _THIRSTY_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _THIRSTY_IMPORT_ERROR = str(_import_error)
    _Lexer = None
    _Parser = None


# Canonical .thirst source location (bundled with the security package).
_BUNDLED_SOURCE_FILENAME: Final[str] = "audit_proof.thirst"


class ProofObligationError(RuntimeError):
    """Raised when proof obligations cannot be extracted.

    Fail-closed surface. The audit relay treats this as a denied
    operation; an unfulfilled obligation is never silently bypassed.
    """


@dataclass(frozen=True)
class ContractAnnotation:
    """A `requires` or `ensures` clause declared on a governed function.

    These are the contract-level proof obligations: the function body
    is only safe to execute when its `requires` clause is true and
    after the call its `ensures` clause is true.
    """

    function: str
    phase: str  # "requires" or "ensures"
    annotation: str


@dataclass(frozen=True)
class ProofObligationReport:
    """The full proof-obligation report for the audit chain.

    `contracts` is the set of (function, phase, annotation) contract
        declarations on the governed functions in the .thirst source.
    `source_hash` is the SHA-256 of the .thirst source, for tamper
        detection and audit traceability.
    `source_path` is the absolute path to the loaded .thirst file.
    `module_name` is the module declared in the .thirst header.
    `module_mode` is the mode (core or governed) declared in the header.
    """

    contracts: tuple[ContractAnnotation, ...]
    source_hash: str
    source_path: str
    module_name: str
    module_mode: str

    def has_contract(self, function: str, phase: str) -> bool:
        """Return True if the report has a contract for (function, phase)."""
        return any(c.function == function and c.phase == phase for c in self.contracts)


def _load_bundled_source() -> tuple[str, str, str]:
    """Load the bundled .thirst source.

    Returns (source_text, source_hash, source_path). Raises
    ProofObligationError if the source cannot be read.
    """
    source_path = Path(__file__).parent / _BUNDLED_SOURCE_FILENAME
    try:
        text = source_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise ProofObligationError(f"audit_proof.thirst not found at {source_path}: {exc}") from exc
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, digest, str(source_path)


def _stringify_expr(node: object) -> str:
    """Render an AST expression node back to source-like text.

    The Thirsty-Lang AST nodes expose their constituent tokens as
    attributes. We walk the tree and reconstruct a canonical string
    representation suitable for inclusion in the report.
    """
    if node is None:
        return ""
    name = type(node).__name__
    if name == "Identifier":
        return str(getattr(node, "name", ""))
    if name == "StringLiteral":
        return f'"{getattr(node, "value", "")}"'
    if name == "IntLiteral":
        return str(getattr(node, "value", ""))
    if name == "FloatLiteral":
        return str(getattr(node, "value", ""))
    if name == "BoolLiteral":
        return str(getattr(node, "value", ""))
    if name == "NoneLiteral":
        return "none"
    if name == "BinaryOp":
        op = getattr(node, "operator", "?")
        return (
            f"{_stringify_expr(getattr(node, 'left', None))} "
            f"{op} {_stringify_expr(getattr(node, 'right', None))}"
        )
    if name == "UnaryOp":
        op = getattr(node, "operator", "?")
        return f"{op}{_stringify_expr(getattr(node, 'operand', None))}"
    if name == "CallExpr":
        callee = _stringify_expr(getattr(node, "callee", None))
        args = getattr(node, "arguments", []) or []
        rendered = ", ".join(_stringify_expr(a) for a in args)
        return f"{callee}({rendered})"
    if name == "MemberAccess":
        obj = _stringify_expr(getattr(node, "object", None))
        prop = getattr(node, "property", "")
        return f"{obj}.{prop}"
    return f"<{name}>"


def _extract_contracts(ast: Any) -> list[ContractAnnotation]:
    """Walk the AST and extract contract annotations from governed functions.

    The AST exposes declarations as `stmts` on the top-level `Program`
    node. Governed function declarations (`GovernedFunctionDecl`) carry
    three optional single-expression contract clauses: `requires_expr`,
    `ensures_expr`, `invariant_expr`. We iterate, filter for governed
    function decls, and pull out whichever contract expressions exist.
    """
    contracts: list[ContractAnnotation] = []
    stmts = getattr(ast, "stmts", None) or []
    for decl in stmts:
        decl_name = type(decl).__name__
        if decl_name not in {"FunctionDecl", "GovernedFunctionDecl"}:
            continue
        func_name = str(getattr(decl, "name", "<unnamed>"))
        # `requires_expr` is a single optional expression; some
        # older versions used a list. We tolerate both.
        requires_expr = getattr(decl, "requires_expr", None)
        if requires_expr is None:
            requires_list = (
                getattr(decl, "requires", None) or getattr(decl, "requires_clauses", None) or []
            )
            for req in requires_list:
                contracts.append(
                    ContractAnnotation(
                        function=func_name,
                        phase="requires",
                        annotation=_stringify_expr(req),
                    )
                )
        else:
            contracts.append(
                ContractAnnotation(
                    function=func_name,
                    phase="requires",
                    annotation=_stringify_expr(requires_expr),
                )
            )
        # `ensures_expr` is a single optional expression.
        ensures_expr = getattr(decl, "ensures_expr", None) or getattr(decl, "ensures", None)
        if ensures_expr is not None:
            contracts.append(
                ContractAnnotation(
                    function=func_name,
                    phase="ensures",
                    annotation=_stringify_expr(ensures_expr),
                )
            )
        # `invariant_expr` is a single optional expression (governed only).
        invariant_expr = getattr(decl, "invariant_expr", None)
        if invariant_expr is not None:
            contracts.append(
                ContractAnnotation(
                    function=func_name,
                    phase="invariant",
                    annotation=_stringify_expr(invariant_expr),
                )
            )
    return contracts


def _extract_module_header(ast: Any) -> tuple[str, str]:
    """Return (module_name, module_mode) from the AST header.

    The module header looks like `module project_ai_audit: governed`.
    We pull the name and the mode (`core` or `governed`).
    """
    header = getattr(ast, "header", None)
    if header is None:
        return ("<unknown>", "<unknown>")
    name = str(getattr(header, "name", "<unknown>"))
    mode = str(getattr(header, "mode", "<unknown>"))
    return (name, mode)


def extract_obligations() -> ProofObligationReport:
    """Extract the proof obligations from the bundled .thirst source.

    Returns a `ProofObligationReport` describing the contract
    annotations on the governed functions in the .thirst source.

    Raises ProofObligationError on any extraction failure (parse error,
    missing dep, missing source). Fail-closed by construction.
    """
    if _THIRSTY_IMPORT_ERROR is not None:
        raise ProofObligationError(f"thirsty-lang import failed: {_THIRSTY_IMPORT_ERROR}")

    source_text, source_hash, source_path = _load_bundled_source()

    try:
        if _Lexer is None or _Parser is None:
            raise ProofObligationError("thirsty-lang symbols unavailable")
        tokens = _Lexer(source_text).lex()  # type: ignore[operator]
        ast = _Parser(tokens).parse()  # type: ignore[operator]
        module_name, module_mode = _extract_module_header(ast)
        contracts = _extract_contracts(ast)
    except ProofObligationError:
        raise
    except Exception as exc:
        raise ProofObligationError(
            f"proof obligation extraction failed for {source_path}: {type(exc).__name__}: {exc}"
        ) from exc

    return ProofObligationReport(
        contracts=tuple(contracts),
        source_hash=source_hash,
        source_path=source_path,
        module_name=module_name,
        module_mode=module_mode,
    )


__all__ = [
    "ContractAnnotation",
    "ProofObligationError",
    "ProofObligationReport",
    "extract_obligations",
]
