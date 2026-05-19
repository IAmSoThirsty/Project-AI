"""Shadow Thirst — mutation simulation and safety validation layer (UTF Tier 4).

Architecture
------------
  parse_shadow()  →  ShadowModule (MutationDecl*, ModuleInvariantDecl*, AtomicGroup*)
  analyze()       →  list[AnalysisResult]   (11 analyzers, in order)
  promote()       →  dict  {"verdict": "PROMOTE"|"REJECT", ...}

Eleven analyzers
----------------
  Critical (block promotion):
    1. PlaneIsolationAnalyzer       shadow cannot write canonical_ vars
    2. DeterminismAnalyzer          shadow must be deterministic
    3. PuritySpringAnalyzer         invariant must be pure
    4. CanonicalConvergenceAnalyzer shadow must model the same data as canonical commits
    5. PrivilegeEscalationAnalyzer  canonical cannot write privileged namespaces
    6. DeadShadowAnalyzer           shadow cannot be empty when canonical has writes

  Warning (logged, do not block):
    7.  ResourceEstimator             cpu / memory budget estimate
    8.  MemoryEvaporationAnalyzer     peak reservoir estimate
    9.  DivergenceRiskAnalyzer        shadow-only intermediate vars count
    10. SectionOrderAnalyzer          sections must appear shadow → invariant → canonical
    11. InvariantCompletenessAnalyzer invariant should gate canonical writes
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from thirsty_lang.lexer import Lexer
from thirsty_lang.parser import Parser
from thirsty_lang.token import Span, Token, TokenType

from thirsty_lang import ast


# ── Public data model ─────────────────────────────────────────────────────────

@dataclass
class ModuleInvariantDecl:
    """Named invariant declared at module scope — reusable across mutations."""
    name: str
    params: list[tuple[str, str]]   # (param_name, type_str)
    body: list[ast.Stmt]
    span: Span


@dataclass
class MutationDecl:
    name: str
    params: list[tuple[str, str]]
    shadow_body: list[ast.Stmt] = field(default_factory=list)
    invariant_body: list[ast.Stmt] = field(default_factory=list)
    canonical_body: list[ast.Stmt] = field(default_factory=list)
    on_reject_body: list[ast.Stmt] = field(default_factory=list)
    section_order: list[str] = field(default_factory=list)  # actual parse order
    span: Span | None = None


@dataclass
class AtomicGroup:
    """All-or-nothing group: every contained mutation must PROMOTE or all REJECT."""
    name: str
    mutations: list[MutationDecl]
    span: Span | None = None


@dataclass
class ShadowModule:
    mutations: list[MutationDecl]
    module_invariants: list[ModuleInvariantDecl] = field(default_factory=list)
    atomic_groups: list[AtomicGroup] = field(default_factory=list)


@dataclass
class AnalysisResult:
    analyzer: str
    level: str      # "critical" | "warning"
    passed: bool
    message: str
    mutation: str = ""  # which mutation produced this result

    @property
    def name(self) -> str:
        return self.analyzer


# ── Sentinel sets ─────────────────────────────────────────────────────────────

_NONDETERMINISTIC_NAMES: frozenset[str] = frozenset({
    "now", "epoch_ms", "rand", "random", "random_bytes", "uuid4",
})
_IO_NAMES: frozenset[str] = frozenset({"pour", "sip"})
_IMPURE_NAMES: frozenset[str] = _NONDETERMINISTIC_NAMES | _IO_NAMES

# Privileged variable prefixes — writing these from canonical without
# an escalation_token is a PrivilegeEscalationAnalyzer failure.
_PRIVILEGED_PREFIXES: tuple[str, ...] = (
    "sys_", "root_", "auth_", "kernel_", "admin_", "sovereign_", "ghost_",
)

# Privileged function names — calling these from canonical is an escalation.
_PRIVILEGED_CALLS: frozenset[str] = frozenset({
    "escalate", "sudo", "elevate", "override_policy",
    "bypass_tarl", "force_canonical", "raw_write",
})

_EXPECTED_SECTION_ORDER = ["shadow", "invariant", "canonical"]


# ── AST walking primitives ────────────────────────────────────────────────────
# ALL compound statement types in the Thirsty-Lang AST:
#   BlockStmt, IfStmt, LoopStmt, TryStmt, FunctionDecl,
#   ReturnStmt, ThrowStmt, DripStmt, ExprStmt, PrintStmt, VarDecl
#
# Every walker that traverses statements MUST handle all of them to prevent
# analyzer bypass via wrapping violations in control-flow constructs.

def _child_stmt_lists(stmt: ast.Stmt) -> list[list[ast.Stmt]]:
    """Return all nested statement lists reachable from *stmt* (one level down).

    Callers iterate over this and recurse.  Using a flat list-of-lists instead
    of direct recursion lets each walker apply its own logic before descending.
    """
    result: list[list[ast.Stmt]] = []
    if isinstance(stmt, ast.BlockStmt):
        result.append(stmt.statements)
    elif isinstance(stmt, ast.IfStmt):
        result.append(stmt.then_branch.statements)
        if stmt.else_branch is not None:
            result.append(stmt.else_branch.statements)
    elif isinstance(stmt, ast.LoopStmt):
        result.append(stmt.body.statements)
    elif isinstance(stmt, ast.TryStmt):
        result.append(stmt.try_block.statements)
        for catch in stmt.catches:
            result.append(catch.block.statements)
        if stmt.finally_block is not None:
            result.append(stmt.finally_block.statements)
    elif isinstance(stmt, ast.FunctionDecl):
        result.append(stmt.body.statements)
    elif isinstance(stmt, ast.GovernedFunctionDecl):
        result.append(stmt.body.statements)
    return result


def _child_exprs(stmt: ast.Stmt) -> list[ast.Expr]:
    """Return all top-level expressions directly owned by *stmt*."""
    exprs: list[ast.Expr] = []
    if isinstance(stmt, ast.ExprStmt):
        exprs.append(stmt.expr)
    elif isinstance(stmt, ast.PrintStmt):
        exprs.append(stmt.expr)
    elif isinstance(stmt, ast.VarDecl) and stmt.initializer is not None:
        exprs.append(stmt.initializer)
    elif isinstance(stmt, ast.ReturnStmt) and stmt.expr is not None:
        exprs.append(stmt.expr)
    elif isinstance(stmt, ast.ThrowStmt):
        exprs.append(stmt.expr)
    elif isinstance(stmt, ast.DripStmt) and stmt.amount is not None:
        exprs.append(stmt.amount)
    elif isinstance(stmt, ast.IfStmt):
        exprs.append(stmt.condition)
    elif isinstance(stmt, ast.LoopStmt):
        exprs.append(stmt.count)
    return exprs


# ── Expression walkers ────────────────────────────────────────────────────────

def _walk_expr_for(expr: ast.Expr, names: frozenset[str]) -> bool:
    """Return True if *expr* (recursively) references any name in *names*."""
    if isinstance(expr, ast.VariableExpr) and expr.name in names:
        return True
    if isinstance(expr, ast.InputExpr):
        return "sip" in names
    if isinstance(expr, ast.CallExpr):
        callee = expr.callee
        if isinstance(callee, ast.VariableExpr) and callee.name in names:
            return True
        if isinstance(callee, ast.MemberExpr) and callee.name in names:
            return True
    _EXPR_CHILD_ATTRS = (
        "left", "right", "expr", "target", "value", "obj",
        "index", "condition", "when_true", "when_false", "callee",
    )
    for attr in _EXPR_CHILD_ATTRS:
        child = getattr(expr, attr, None)
        if isinstance(child, ast.Expr) and _walk_expr_for(child, names):
            return True
    for arg in getattr(expr, "args", []):
        if isinstance(arg, ast.Expr) and _walk_expr_for(arg, names):
            return True
    return False


def _collect_read_names_expr(expr: ast.Expr) -> set[str]:
    """Return all variable names *read* within *expr*."""
    names: set[str] = set()
    if isinstance(expr, ast.VariableExpr):
        names.add(expr.name)
    _EXPR_CHILD_ATTRS = (
        "left", "right", "expr", "value", "obj", "index",
        "condition", "when_true", "when_false", "callee",
    )
    for attr in _EXPR_CHILD_ATTRS:
        child = getattr(expr, attr, None)
        if isinstance(child, ast.Expr):
            names |= _collect_read_names_expr(child)
    for arg in getattr(expr, "args", []):
        if isinstance(arg, ast.Expr):
            names |= _collect_read_names_expr(arg)
    return names


# ── Statement walkers — all use _child_stmt_lists for full coverage ───────────

def _writes_canonical(stmts: list[ast.Stmt]) -> bool:
    """True if any statement in *stmts* (recursively) writes a canonical_ var."""
    for stmt in stmts:
        if (
            isinstance(stmt, ast.ExprStmt)
            and isinstance(stmt.expr, ast.AssignExpr)
            and isinstance(stmt.expr.target, ast.VariableExpr)
            and stmt.expr.target.name.startswith("canonical_")
        ):
            return True
        if isinstance(stmt, ast.VarDecl) and stmt.name.startswith("canonical_"):
            return True
        for child_stmts in _child_stmt_lists(stmt):
            if _writes_canonical(child_stmts):
                return True
    return False


def _has_nondeterminism(stmts: list[ast.Stmt]) -> bool:
    """True if any statement (recursively) calls a non-deterministic function."""
    for stmt in stmts:
        for expr in _child_exprs(stmt):
            if _walk_expr_for(expr, _NONDETERMINISTIC_NAMES):
                return True
        for child_stmts in _child_stmt_lists(stmt):
            if _has_nondeterminism(child_stmts):
                return True
    return False


def _has_impure_calls(stmts: list[ast.Stmt]) -> tuple[bool, str]:
    """Return (True, offending_name) if invariant block has I/O or nondeterminism."""
    for stmt in stmts:
        if isinstance(stmt, ast.PrintStmt):
            return True, "pour"
        for expr in _child_exprs(stmt):
            for name in _IMPURE_NAMES:
                if _walk_expr_for(expr, frozenset({name})):
                    return True, name
        for child_stmts in _child_stmt_lists(stmt):
            found, name = _has_impure_calls(child_stmts)
            if found:
                return True, name
    return False, ""


def _writes_privileged(stmts: list[ast.Stmt]) -> tuple[bool, str]:
    """Return (True, target) if canonical block writes a privileged var or calls a
    privileged function without an explicit escalation_token."""
    for stmt in stmts:
        if (
            isinstance(stmt, ast.ExprStmt)
            and isinstance(stmt.expr, ast.AssignExpr)
            and isinstance(stmt.expr.target, ast.VariableExpr)
        ):
            vname = stmt.expr.target.name
            for prefix in _PRIVILEGED_PREFIXES:
                if vname.startswith(prefix):
                    return True, vname
        if isinstance(stmt, ast.VarDecl):
            for prefix in _PRIVILEGED_PREFIXES:
                if stmt.name.startswith(prefix):
                    return True, stmt.name
        if isinstance(stmt, ast.ExprStmt) and isinstance(stmt.expr, ast.CallExpr):
            callee = stmt.expr.callee
            if isinstance(callee, ast.VariableExpr) and callee.name in _PRIVILEGED_CALLS:
                return True, callee.name
        for child_stmts in _child_stmt_lists(stmt):
            found, target = _writes_privileged(child_stmts)
            if found:
                return True, target
    return False, ""


def _collect_written_names(stmts: list[ast.Stmt]) -> set[str]:
    """Collect all variable names written (declared or assigned) in *stmts*."""
    names: set[str] = set()
    for stmt in stmts:
        if isinstance(stmt, ast.VarDecl):
            names.add(stmt.name)
        if (
            isinstance(stmt, ast.ExprStmt)
            and isinstance(stmt.expr, ast.AssignExpr)
            and isinstance(stmt.expr.target, ast.VariableExpr)
        ):
            names.add(stmt.expr.target.name)
        for child_stmts in _child_stmt_lists(stmt):
            names |= _collect_written_names(child_stmts)
    return names


def _collect_read_names(stmts: list[ast.Stmt]) -> set[str]:
    """Collect all variable names *read* (referenced as values) in *stmts*."""
    names: set[str] = set()
    for stmt in stmts:
        for expr in _child_exprs(stmt):
            names |= _collect_read_names_expr(expr)
        for child_stmts in _child_stmt_lists(stmt):
            names |= _collect_read_names(child_stmts)
    return names


def _count_branches(stmts: list[ast.Stmt]) -> int:
    """Count conditional branch points (thirst/hydrated and refill loops)."""
    count = 0
    for stmt in stmts:
        if isinstance(stmt, ast.IfStmt):
            count += 1  # the branch itself
        if isinstance(stmt, ast.LoopStmt):
            count += 1  # loops also represent conditional control flow
        for child_stmts in _child_stmt_lists(stmt):
            count += _count_branches(child_stmts)
    return count


def _estimate_pressure(stmts: list[ast.Stmt]) -> tuple[int, int]:
    """Return (estimated_cpu_ms, estimated_mem_mb) for resource budgeting."""
    count = 0
    reservoirs = 0
    for stmt in stmts:
        count += 1
        if isinstance(stmt, ast.VarDecl) and getattr(stmt.type_node, "name", "") in {
            "Reservoir", "well",
        }:
            reservoirs += 1
        for child_stmts in _child_stmt_lists(stmt):
            c, r = _estimate_pressure(child_stmts)
            count += c
            reservoirs += r
    return count * 10, reservoirs * 64


# ── Per-mutation analysis helpers ─────────────────────────────────────────────

def _canonical_convergence(mutation: MutationDecl) -> tuple[bool, str]:
    """Shadow simulation must model the same inputs that canonical commits.

    Checks:
    1. If canonical reads mutation params, shadow must read at least one of them.
       A shadow that ignores all inputs is not simulating the mutation.
    2. If shadow explores ≥3 more branch points than canonical (and canonical is
       branch-free), the simulation may be over-speculative.
    """
    shadow_branches = _count_branches(mutation.shadow_body)
    canonical_branches = _count_branches(mutation.canonical_body)

    if shadow_branches > 0 and canonical_branches == 0 and shadow_branches >= 3:
        return False, (
            f"shadow explores {shadow_branches} branch(es) but canonical is "
            "unconditional — simulation may model unreachable paths"
        )

    param_names = {p[0] for p in mutation.params}
    if param_names:
        shadow_reads = _collect_read_names(mutation.shadow_body)
        canonical_reads = _collect_read_names(mutation.canonical_body)
        canonical_reads_params = bool(canonical_reads & param_names)
        shadow_reads_params = bool(shadow_reads & param_names)

        if canonical_reads_params and not shadow_reads_params:
            overlapping = canonical_reads & param_names
            return False, (
                f"canonical reads param(s) {overlapping!r} but shadow reads none — "
                "shadow is modelling a different execution than canonical commits"
            )

    return True, "shadow spring aligns with the canonical river"


def _section_order_ok(mutation: MutationDecl) -> tuple[bool, str]:
    """Sections must appear in shadow → invariant → canonical order.

    on_reject, if present, must come last.
    """
    order = mutation.section_order
    if not order:
        return True, "no sections to order"

    # Strip on_reject from the ordered check (it's always last by construction)
    core_order = [s for s in order if s != "on_reject"]
    expected = [s for s in _EXPECTED_SECTION_ORDER if s in core_order]

    if core_order != expected:
        return False, (
            f"sections appear in order {core_order!r}; "
            f"expected {expected!r}"
        )
    if "on_reject" in order and order[-1] != "on_reject":
        return False, "on_reject must be the last section if present"
    return True, f"section order {order!r} is valid"


def _invariant_completeness(mutation: MutationDecl) -> tuple[bool, str]:
    """Invariant block should contain at least one expression per two canonical writes.

    An empty invariant combined with multiple canonical writes suggests the
    mutation is committing state without gating it — high risk.
    """
    canonical_write_count = len(_collect_written_names(mutation.canonical_body))
    invariant_expr_count = sum(
        1 for s in mutation.invariant_body if isinstance(s, (ast.ExprStmt, ast.VarDecl))
    )

    if canonical_write_count >= 2 and invariant_expr_count == 0:
        return False, (
            f"canonical commits {canonical_write_count} variable(s) but invariant "
            "block is empty — add gate checks to protect the canonical writes"
        )
    if canonical_write_count > 0 and invariant_expr_count == 0:
        return False, (
            "canonical block writes state but invariant block has no checks — "
            "consider adding at least one guard expression"
        )
    return True, (
        f"invariant has {invariant_expr_count} check(s) "
        f"for {canonical_write_count} canonical write(s)"
    )


# ── Content hash (for replay integrity) ──────────────────────────────────────

def _stmt_fingerprint(stmts: list[ast.Stmt]) -> str:
    """Produce a stable content fingerprint of a statement list.

    Includes structural type names and literal values — two mutations with the
    same statement count but different content will produce different hashes.
    """
    parts: list[str] = []
    for stmt in stmts:
        parts.append(type(stmt).__name__)
        if isinstance(stmt, ast.VarDecl):
            parts.append(stmt.name)
            parts.append(getattr(stmt.type_node, "name", "?"))
            # Include initializer content so different values produce different hashes.
            # Previously only type+name were fingerprinted, meaning `drink x: Int = n`
            # and `drink x: Int = 42` collided — replay audit gap now closed.
            if stmt.initializer is not None:
                init = stmt.initializer
                if isinstance(init, ast.LiteralExpr):
                    parts.append(f"lit:{init.value!r}")
                elif isinstance(init, ast.VariableExpr):
                    parts.append(f"var:{init.name}")
                else:
                    reads = sorted(_collect_read_names_expr(init))
                    parts.append(f"expr:{','.join(reads)}")
        if isinstance(stmt, ast.ExprStmt):
            expr = stmt.expr
            if isinstance(expr, ast.AssignExpr) and isinstance(expr.target, ast.VariableExpr):
                parts.append(f"assign:{expr.target.name}")
            if isinstance(expr, ast.CallExpr) and isinstance(expr.callee, ast.VariableExpr):
                parts.append(f"call:{expr.callee.name}")
        if isinstance(stmt, ast.PrintStmt):
            parts.append("pour")
        for child_stmts in _child_stmt_lists(stmt):
            parts.append(_stmt_fingerprint(child_stmts))
    return "|".join(parts)


def replay_hash(module: ShadowModule) -> str:
    """SHA-256 of the mutation *content*, not just its structural counts.

    Stable across identical source text.  Different shadow bodies with the same
    statement count produce different hashes — fixing the prior audit gap.
    """
    payload = json.dumps(
        {
            "mutations": [
                {
                    "name": m.name,
                    "params": m.params,
                    "shadow": _stmt_fingerprint(m.shadow_body),
                    "invariant": _stmt_fingerprint(m.invariant_body),
                    "canonical": _stmt_fingerprint(m.canonical_body),
                    "on_reject": _stmt_fingerprint(m.on_reject_body),
                }
                for m in module.mutations
            ]
        },
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ── Plugin loader (cached per process lifetime) ───────────────────────────────

_PLUGIN_CACHE: list[Callable[[ShadowModule], list[AnalysisResult]]] | None = None


def _plugin_analyzers() -> list[Callable[[ShadowModule], list[AnalysisResult]]]:
    global _PLUGIN_CACHE
    if _PLUGIN_CACHE is not None:
        return _PLUGIN_CACHE
    plugins: list[Callable[[ShadowModule], list[AnalysisResult]]] = []
    plugins_dir = Path(__file__).resolve().parent / "plugins"
    if plugins_dir.exists():
        for py in sorted(plugins_dir.glob("*.py")):
            spec = importlib.util.spec_from_file_location(py.stem, py)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "analyze_plugin"):
                plugins.append(mod.analyze_plugin)
    _PLUGIN_CACHE = plugins
    return _PLUGIN_CACHE


# ── Main analysis pipeline ────────────────────────────────────────────────────

def analyze(module: ShadowModule) -> list[AnalysisResult]:
    out: list[AnalysisResult] = []

    for m in module.mutations:
        def r(analyzer: str, level: str, passed: bool, message: str) -> AnalysisResult:
            return AnalysisResult(analyzer, level, passed, message, mutation=m.name)

        # 1. PlaneIsolationAnalyzer ────────────────────────────────────────────
        isolation_ok = not _writes_canonical(m.shadow_body)
        out.append(r(
            "PlaneIsolationAnalyzer", "critical", isolation_ok,
            "shadow plane cannot write canonical state"
            if isolation_ok else
            "shadow plane writes a canonical_ variable — plane isolation violated",
        ))

        # 2. DeterminismAnalyzer ───────────────────────────────────────────────
        det_ok = not _has_nondeterminism(m.shadow_body)
        out.append(r(
            "DeterminismAnalyzer", "critical", det_ok,
            "shadow plane is deterministic"
            if det_ok else
            "shadow plane calls a non-deterministic function — simulation is not replayable",
        ))

        # 3. PuritySpringAnalyzer ──────────────────────────────────────────────
        impure, offender = _has_impure_calls(m.invariant_body)
        out.append(r(
            "PuritySpringAnalyzer", "critical", not impure,
            "invariant block is pure"
            if not impure else
            f"invariant block calls impure function '{offender}' — gates must be side-effect-free",
        ))

        # 4. CanonicalConvergenceAnalyzer ─────────────────────────────────────
        converges, conv_msg = _canonical_convergence(m)
        out.append(r("CanonicalConvergenceAnalyzer", "critical", converges, conv_msg))

        # 5. PrivilegeEscalationAnalyzer ──────────────────────────────────────
        escalates, esc_target = _writes_privileged(m.canonical_body)
        out.append(r(
            "PrivilegeEscalationAnalyzer", "critical", not escalates,
            "no privilege escalation detected in canonical block"
            if not escalates else
            f"canonical block writes privileged target '{esc_target}' without escalation_token",
        ))

        # 6. DeadShadowAnalyzer ───────────────────────────────────────────────
        shadow_is_empty = len(m.shadow_body) == 0
        canonical_has_writes = len(_collect_written_names(m.canonical_body)) > 0
        dead_shadow = shadow_is_empty and canonical_has_writes
        out.append(r(
            "DeadShadowAnalyzer", "critical", not dead_shadow,
            "shadow simulation is active"
            if not dead_shadow else
            "shadow block is empty but canonical commits state — "
            "canonical write is unprotected (no simulation performed)",
        ))

        # 7. ResourceEstimator ────────────────────────────────────────────────
        cpu_ms, mem_mb = _estimate_pressure(m.shadow_body)
        res_ok = cpu_ms <= 1000 and mem_mb <= 256
        out.append(r(
            "ResourceEstimator", "warning", res_ok,
            f"estimated cpu={cpu_ms}ms memory={mem_mb}MB"
            + ("" if res_ok else " — exceeds budget"),
        ))

        # 8. MemoryEvaporationAnalyzer ────────────────────────────────────────
        out.append(r(
            "MemoryEvaporationAnalyzer", "warning", mem_mb <= 256,
            f"peak reservoir estimate={mem_mb}MB"
            + ("" if mem_mb <= 256 else " — exceeds 256MB soft limit"),
        ))

        # 9. DivergenceRiskAnalyzer ───────────────────────────────────────────
        shadow_writes = _collect_written_names(m.shadow_body)
        canonical_writes = _collect_written_names(m.canonical_body)
        canonical_base = {n.removeprefix("canonical_") for n in canonical_writes}
        sim_only = shadow_writes - canonical_base - {p[0] for p in m.params}
        div_risk = len(sim_only) > 2
        out.append(r(
            "DivergenceRiskAnalyzer", "warning", not div_risk,
            "shadow simulation variables align with canonical commit scope"
            if not div_risk else
            f"shadow introduces {len(sim_only)} intermediate variable(s) "
            f"({', '.join(sorted(sim_only)[:3])}) with no canonical counterpart — "
            "verify simulation fidelity",
        ))

        # 10. SectionOrderAnalyzer ────────────────────────────────────────────
        order_ok, order_msg = _section_order_ok(m)
        out.append(r("SectionOrderAnalyzer", "warning", order_ok, order_msg))

        # 11. InvariantCompletenessAnalyzer ───────────────────────────────────
        complete_ok, complete_msg = _invariant_completeness(m)
        out.append(r("InvariantCompletenessAnalyzer", "warning", complete_ok, complete_msg))

    for plugin in _plugin_analyzers():
        out.extend(plugin(module))

    return out


def promote(
    module: ShadowModule,
    dry_run: bool = False,
    replay_id: str | None = None,
) -> dict[str, Any]:
    results = analyze(module)
    failures = [r for r in results if r.level == "critical" and not r.passed]
    decision = "PROMOTE" if not failures else "REJECT"
    rh = replay_hash(module)   # compute once
    return {
        "decision": decision,
        "verdict": decision,
        "dry_run": dry_run,
        "replay_id": replay_id or rh[:16],
        "replay_hash": rh,
        "analysis": [
            {k: v for k, v in r.__dict__.items()} for r in results
        ],
        "diff": (
            "shadow spring aligns with the canonical river"
            if decision == "PROMOTE" else
            "the shadow river diverges and is withheld from the spring"
        ),
        "failures": [f.analyzer for f in failures],
    }


def promote_atomic(
    group: AtomicGroup,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Promote all mutations in an atomic group.  All must PROMOTE or all REJECT."""
    results_per = {}
    any_reject = False
    for m in group.mutations:
        mod = ShadowModule(mutations=[m])
        res = promote(mod, dry_run=dry_run)
        results_per[m.name] = res
        if res["verdict"] == "REJECT":
            any_reject = True

    final = "REJECT" if any_reject else "PROMOTE"
    return {
        "group": group.name,
        "verdict": final,
        "dry_run": dry_run,
        "mutations": results_per,
        "diff": (
            f"atomic group '{group.name}' promoted successfully"
            if final == "PROMOTE" else
            f"atomic group '{group.name}' rejected — rolling back all mutations"
        ),
    }


def visualize(module: ShadowModule) -> str:
    lines = ["flowchart TD"]
    for m in module.mutations:
        sid = m.name.replace("-", "_")
        lines.append(f'  {sid}_shadow["{m.name}: shadow"] --> {sid}_inv["{m.name}: invariant"]')
        lines.append(f'  {sid}_inv --> {sid}_canon["{m.name}: canonical"]')
        if m.on_reject_body:
            lines.append(
                f'  {sid}_canon -. reject .-> {sid}_reject["{m.name}: on_reject"]'
            )
    if module.atomic_groups:
        lines.append("")
        lines.append("  subgraph Atomic Groups")
        for g in module.atomic_groups:
            gid = g.name.replace("-", "_")
            lines.append(f'    {gid}["atomic: {g.name}"]')
        lines.append("  end")
    return "\n".join(lines)


# ── Parser ────────────────────────────────────────────────────────────────────

def _collect_block(tokens: list[Token], start_index: int) -> tuple[list[Token], int]:
    """Collect tokens inside the braces at *start_index*, returning (inner_tokens, next_i)."""
    if tokens[start_index].kind != TokenType.LBRACE:
        raise ValueError(
            f"expected '{{' at token {start_index}, "
            f"got {tokens[start_index].lexeme!r}"
        )
    depth = 0
    collected: list[Token] = []
    i = start_index
    while i < len(tokens):
        tok = tokens[i]
        if tok.kind == TokenType.LBRACE:
            depth += 1
            if depth > 1:
                collected.append(tok)
        elif tok.kind == TokenType.RBRACE:
            depth -= 1
            if depth == 0:
                return collected, i + 1
            collected.append(tok)
        else:
            collected.append(tok)
        i += 1
    raise ValueError("unterminated block — missing closing '}'")


def _parse_statements(tokens: list[Token], file: str = "<shadow>") -> list[ast.Stmt]:
    """Delegate a token stream to the Thirsty-Lang parser to produce AST statements."""
    if not tokens:
        return []
    eof_span = tokens[-1].span
    wrapped = (
        [Token(TokenType.LBRACE, "{", None, eof_span)]
        + tokens
        + [
            Token(TokenType.RBRACE, "}", None, eof_span),
            Token(TokenType.EOF, "", None, eof_span),
        ]
    )
    parser = Parser.from_tokens(wrapped)
    block = parser._block()
    return block.statements


_SECTION_KEYWORDS = {
    TokenType.SHADOW:    "shadow",
    TokenType.INVARIANT: "invariant",
    TokenType.CANONICAL: "canonical",
}
_ON_REJECT_LEXEME = "on_reject"


def _parse_mutation(
    tokens: list[Token], i: int, file: str
) -> tuple[MutationDecl, int]:
    """Parse one `mutation validated_canonical Name(params) { ... }` declaration."""
    start_span = tokens[i].span
    i += 1  # consume MUTATION

    if tokens[i].kind != TokenType.VALIDATED_CANONICAL:
        raise ValueError(
            f"expected 'validated_canonical' after 'mutation', "
            f"got {tokens[i].lexeme!r} at {tokens[i].span}"
        )
    i += 1

    name_tok = tokens[i]
    if name_tok.kind != TokenType.IDENT:
        raise ValueError(f"expected mutation name (IDENT), got {name_tok.lexeme!r}")
    i += 1

    if tokens[i].kind != TokenType.LPAREN:
        raise ValueError(f"expected '(' after mutation name, got {tokens[i].lexeme!r}")
    i += 1

    params: list[tuple[str, str]] = []
    while tokens[i].kind != TokenType.RPAREN:
        pname = tokens[i]
        if pname.kind != TokenType.IDENT:
            raise ValueError(f"expected parameter name, got {pname.lexeme!r}")
        i += 1
        if tokens[i].kind != TokenType.COLON:
            raise ValueError(f"expected ':' after parameter '{pname.lexeme}'")
        i += 1
        ptype = tokens[i]
        i += 1
        params.append((pname.lexeme, ptype.lexeme))
        if tokens[i].kind == TokenType.COMMA:
            i += 1

    i += 1  # consume RPAREN

    if tokens[i].kind != TokenType.LBRACE:
        raise ValueError(f"expected '{{' after mutation signature, got {tokens[i].lexeme!r}")

    body_tokens, i = _collect_block(tokens, i)

    # Parse sections inside the mutation body
    shadow_body: list[ast.Stmt] = []
    invariant_body: list[ast.Stmt] = []
    canonical_body: list[ast.Stmt] = []
    on_reject_body: list[ast.Stmt] = []
    section_order: list[str] = []
    seen_sections: set[str] = set()

    j = 0
    while j < len(body_tokens):
        section_tok = body_tokens[j]

        # Determine section keyword
        if section_tok.kind in _SECTION_KEYWORDS:
            section_name = _SECTION_KEYWORDS[section_tok.kind]
        elif (
            section_tok.kind == TokenType.IDENT
            and section_tok.lexeme == _ON_REJECT_LEXEME
        ):
            section_name = _ON_REJECT_LEXEME
        else:
            raise ValueError(
                f"expected section keyword (shadow/invariant/canonical/on_reject), "
                f"got {section_tok.lexeme!r}"
            )

        if section_name in seen_sections:
            raise ValueError(f"duplicate section '{section_name}' in mutation '{name_tok.lexeme}'")
        seen_sections.add(section_name)
        section_order.append(section_name)
        j += 1

        if j >= len(body_tokens) or body_tokens[j].kind != TokenType.LBRACE:
            raise ValueError(
                f"expected '{{' after section keyword '{section_name}'"
            )
        block_tokens, j = _collect_block(body_tokens, j)
        stmts = _parse_statements(block_tokens, file)

        if section_name == "shadow":
            shadow_body = stmts
        elif section_name == "invariant":
            invariant_body = stmts
        elif section_name == "canonical":
            canonical_body = stmts
        elif section_name == _ON_REJECT_LEXEME:
            on_reject_body = stmts

    return MutationDecl(
        name=name_tok.lexeme,
        params=params,
        shadow_body=shadow_body,
        invariant_body=invariant_body,
        canonical_body=canonical_body,
        on_reject_body=on_reject_body,
        section_order=section_order,
        span=start_span,
    ), i


def _parse_module_invariant(
    tokens: list[Token], i: int, file: str
) -> tuple[ModuleInvariantDecl, int]:
    """Parse a module-level `invariant Name(params) { body }` declaration."""
    start_span = tokens[i].span
    i += 1  # consume INVARIANT

    name_tok = tokens[i]
    if name_tok.kind != TokenType.IDENT:
        raise ValueError(f"expected invariant name (IDENT), got {name_tok.lexeme!r}")
    i += 1

    params: list[tuple[str, str]] = []
    if tokens[i].kind == TokenType.LPAREN:
        i += 1
        while tokens[i].kind != TokenType.RPAREN:
            pname = tokens[i]
            if pname.kind != TokenType.IDENT:
                raise ValueError(f"expected param name in invariant, got {pname.lexeme!r}")
            i += 1
            if tokens[i].kind != TokenType.COLON:
                raise ValueError("expected ':' after invariant param name")
            i += 1
            ptype = tokens[i]
            i += 1
            params.append((pname.lexeme, ptype.lexeme))
            if tokens[i].kind == TokenType.COMMA:
                i += 1
        i += 1  # consume RPAREN

    if tokens[i].kind != TokenType.LBRACE:
        raise ValueError(f"expected '{{' after invariant name, got {tokens[i].lexeme!r}")
    block_tokens, i = _collect_block(tokens, i)
    body = _parse_statements(block_tokens, file)
    return ModuleInvariantDecl(name_tok.lexeme, params, body, start_span), i


def _parse_atomic_group(
    tokens: list[Token], i: int, file: str
) -> tuple[AtomicGroup, int]:
    """Parse an `atomic group_name { mutation ... mutation ... }` block."""
    start_span = tokens[i].span
    i += 1  # consume IDENT("atomic")

    name_tok = tokens[i]
    if name_tok.kind != TokenType.IDENT:
        raise ValueError(f"expected atomic group name, got {name_tok.lexeme!r}")
    i += 1

    if tokens[i].kind != TokenType.LBRACE:
        raise ValueError("expected '{' after atomic group name")
    group_tokens, i = _collect_block(tokens, i)

    # Parse mutations inside the atomic group
    mutations: list[MutationDecl] = []
    k = 0
    while k < len(group_tokens) and group_tokens[k].kind != TokenType.EOF:
        gtok = group_tokens[k]
        if gtok.kind == TokenType.MUTATION:
            mut, k = _parse_mutation(group_tokens, k, file)
            mutations.append(mut)
        else:
            k += 1

    return AtomicGroup(name=name_tok.lexeme, mutations=mutations, span=start_span), i


def parse_shadow(text: str, file: str = "<shadow>") -> ShadowModule:
    """Parse a .shadowthirst source file into a ShadowModule.

    Supported top-level constructs:
      mutation validated_canonical Name(params) { shadow{} invariant{} canonical{} [on_reject{}] }
      invariant Name(params) { body }
      atomic group_name { mutation ... }
    """
    tokens = Lexer(text, file).lex()
    mutations: list[MutationDecl] = []
    module_invariants: list[ModuleInvariantDecl] = []
    atomic_groups: list[AtomicGroup] = []

    i = 0
    while i < len(tokens) and tokens[i].kind != TokenType.EOF:
        tok = tokens[i]

        if tok.kind == TokenType.MUTATION:
            mut, i = _parse_mutation(tokens, i, file)
            mutations.append(mut)

        elif tok.kind == TokenType.INVARIANT:
            # Peek ahead: if next token after INVARIANT is an IDENT followed by
            # LPAREN or LBRACE, this is a module-level invariant declaration.
            # (Inside a mutation body it's handled by _parse_mutation.)
            if i + 1 < len(tokens) and tokens[i + 1].kind == TokenType.IDENT:
                inv, i = _parse_module_invariant(tokens, i, file)
                module_invariants.append(inv)
            else:
                i += 1

        elif (
            tok.kind == TokenType.IDENT
            and tok.lexeme == "atomic"
            and i + 1 < len(tokens)
            and tokens[i + 1].kind == TokenType.IDENT
        ):
            group, i = _parse_atomic_group(tokens, i, file)
            atomic_groups.append(group)

        else:
            i += 1

    return ShadowModule(
        mutations=mutations,
        module_invariants=module_invariants,
        atomic_groups=atomic_groups,
    )
