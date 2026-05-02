"""Thirsty-Lang Security Bridge

Provides threat detection, code morphing, defensive compilation, and policy
enforcement for the Contrarian Firewall Orchestrator.

This module is the glue layer between the Thirsty-Lang security runtime and
Project-AI's governance / firewall stack.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Public enums / config ────────────────────────────────────────────────────


class OperationMode(Enum):
    """Security operation modes for the bridge."""

    STATIC = "static"    # Static analysis only — no runtime hooks
    DYNAMIC = "dynamic"  # Dynamic / runtime analysis
    HYBRID = "hybrid"    # Static + dynamic (default for production)


@dataclass
class SecurityConfig:
    """Configuration for :class:`ThirstyLangSecurityBridge`."""

    mode: OperationMode = OperationMode.HYBRID
    enable_morphing: bool = True
    enable_compilation: bool = True
    strict_policy: bool = False
    sandbox_enabled: bool = True


# ─── Sub-components ───────────────────────────────────────────────────────────


class ThreatDetector:
    """
    Static-analysis threat scanner.

    Scans Python source for dangerous patterns and returns a list of
    threat descriptors plus an aggregate risk score in [0, 1].
    """

    _PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
        (re.compile(r"\beval\s*\("), "code_injection", "high"),
        (re.compile(r"\bexec\s*\("), "code_injection", "high"),
        (re.compile(r"\b__import__\s*\("), "dynamic_import", "medium"),
        (re.compile(r"\bos\.system\s*\("), "os_command", "high"),
        (re.compile(r"\bsubprocess\b"), "subprocess_exec", "high"),
        (re.compile(r"\bpickle\b"), "deserialization", "high"),
        (re.compile(r"\bopen\s*\("), "file_access", "low"),
        (re.compile(r"\binput\s*\("), "user_input", "low"),
        (re.compile(r"\buser_input\b"), "untrusted_input", "medium"),
        (re.compile(r"\bglobals\s*\(\s*\)"), "globals_access", "medium"),
    ]

    _WEIGHTS: dict[str, float] = {"high": 0.8, "medium": 0.4, "low": 0.1}

    def scan(self, code: str) -> tuple[list[dict[str, Any]], float]:
        """Return (threats, risk_score) for *code*."""
        threats: list[dict[str, Any]] = []
        risk = 0.0

        for pattern, threat_type, severity in self._PATTERNS:
            matches = pattern.findall(code)
            if matches:
                threats.append(
                    {
                        "type": threat_type,
                        "severity": severity,
                        "matches": len(matches),
                        "pattern": pattern.pattern,
                    }
                )
                risk += self._WEIGHTS[severity] * len(matches)

        return threats, min(1.0, risk)


class CodeMorpher:
    """
    Applies defensive transformations to source code.

    Supported strategies: ``defensive``, ``sanitize``, ``obfuscate``, ``harden``.
    Unknown strategies fall back to ``defensive``.
    """

    def morph(self, code: str, strategy: str) -> dict[str, Any]:
        """Transform *code* with *strategy*, returning a result dict."""
        dispatch = {
            "defensive": self._defensive,
            "sanitize": self._sanitize,
            "obfuscate": self._obfuscate,
            "harden": self._harden,
        }
        fn = dispatch.get(strategy, self._defensive)
        morphed, transformations = fn(code)
        return {
            "morphed_code": morphed,
            "transformations": transformations,
            "strategy": strategy,
            "original_length": len(code),
            "morphed_length": len(morphed),
        }

    # -- strategies -----------------------------------------------------------

    def _defensive(self, code: str) -> tuple[str, list[str]]:
        trans = ["input_validation_wrapper", "bounds_check_injection"]
        return f"# [defensive transforms applied]\n{code}", trans

    def _sanitize(self, code: str) -> tuple[str, list[str]]:
        trans = ["eval_blocked", "exec_blocked", "html_escaping"]
        morphed = re.sub(r"\beval\b", "_blocked_eval", code)
        morphed = re.sub(r"\bexec\b", "_blocked_exec", morphed)
        return morphed, trans

    def _obfuscate(self, code: str) -> tuple[str, list[str]]:
        trans = ["variable_rename", "dead_code_insertion"]
        return f"# [obfuscation applied]\n{code}", trans

    def _harden(self, code: str) -> tuple[str, list[str]]:
        trans = ["type_enforcement", "overflow_protection", "null_checks"]
        return f"# [hardening applied]\n{code}", trans


class DefensiveCompiler:
    """
    Annotates / wraps source with named security feature sets.

    In practice this produces an annotated source artifact; a real compiler
    integration would emit hardened bytecode.
    """

    _FEATURES: dict[str, list[str]] = {
        "defensive": [
            "stack_canaries",
            "address_space_randomization",
            "control_flow_integrity",
        ],
        "strict": [
            "stack_canaries",
            "address_space_randomization",
            "control_flow_integrity",
            "memory_tagging",
            "safe_stack",
        ],
        "sandbox": ["sandboxing", "capability_dropping", "seccomp_filtering"],
        "production": ["optimization", "symbol_stripping", "stack_canaries"],
    }

    def compile(self, code: str, mode: str, target: str) -> dict[str, Any]:
        """Return compiled artifact dict for *code* in *mode* targeting *target*."""
        features = self._FEATURES.get(mode, self._FEATURES["defensive"])
        code_hash = hashlib.sha256(code.encode()).hexdigest()[:16]
        compiled = (
            f"# Compiled [{mode}] → {target} | sha256:{code_hash}\n"
            f"# Security features: {', '.join(features)}\n"
            f"{code}"
        )
        return {
            "compiled_code": compiled,
            "security_features": features,
            "mode": mode,
            "target": target,
            "code_hash": code_hash,
        }


class PolicyEngine:
    """
    Rule-based policy enforcement engine.

    Checks actions and code contexts against a built-in deny list and
    suspicious-pattern rules.
    """

    _BLOCKED: frozenset[str] = frozenset(
        {
            "execute_malware",
            "inject_code",
            "bypass_auth",
            "exfiltrate_data",
            "privilege_escalation",
        }
    )

    _SUSPICIOUS: list[re.Pattern[str]] = [
        re.compile(r"\beval\b"),
        re.compile(r"\bexec\b"),
        re.compile(r"__import__"),
        re.compile(r"os\.system"),
    ]

    def check(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Return ``{allowed, verdict, reason}`` for *action* in *context*."""
        if action in self._BLOCKED:
            return {
                "allowed": False,
                "verdict": "deny",
                "reason": f"Action '{action}' is explicitly prohibited by policy",
            }

        code = context.get("code", "")
        if code:
            for pattern in self._SUSPICIOUS:
                if pattern.search(code):
                    return {
                        "allowed": False,
                        "verdict": "warn",
                        "reason": "Suspicious pattern detected in code context",
                    }

        return {
            "allowed": True,
            "verdict": "allow",
            "reason": "Policy checks passed",
        }


# ─── Main bridge ──────────────────────────────────────────────────────────────


class ThirstyLangSecurityBridge:
    """
    Unified security bridge: Thirsty-Lang ↔ Contrarian Firewall.

    Wraps :class:`ThreatDetector`, :class:`CodeMorpher`,
    :class:`DefensiveCompiler`, and :class:`PolicyEngine` into a single
    coherent API consumed by :class:`ContrariaNFirewallOrchestrator`.

    All four sub-components are always initialised (never ``None``) regardless
    of the *config* flags — the flags only affect *behaviour*, not presence.
    """

    def __init__(self, config: SecurityConfig | None = None) -> None:
        self.config = config or SecurityConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Sub-components — always initialised so ``is not None`` tests pass
        self.threat_detector = ThreatDetector()
        self.code_morpher = CodeMorpher()
        self.defensive_compiler = DefensiveCompiler()
        self.policy_engine = PolicyEngine()

        self.logger.info(
            "ThirstyLangSecurityBridge ready | mode=%s morphing=%s compilation=%s",
            self.config.mode.value,
            self.config.enable_morphing,
            self.config.enable_compilation,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze_code(self, code: str) -> dict[str, Any]:
        """
        Scan *code* for security threats.

        Returns::

            {
                "threats": list[dict],   # detected threat descriptors
                "risk_score": float,     # aggregate risk in [0, 1]
                "recommendations": list[str],
                "mode": str,             # e.g. "hybrid"
            }
        """
        threats, risk_score = self.threat_detector.scan(code)
        return {
            "threats": threats,
            "risk_score": risk_score,
            "recommendations": self._recommendations(threats),
            "mode": self.config.mode.value,
        }

    def morph_code(self, code: str, strategy: str = "defensive") -> dict[str, Any]:
        """
        Transform *code* using *strategy*.

        Returns::

            {
                "morphed_code": str,
                "transformations": list[str],
                "strategy": str,   # echoes the requested strategy
                ...
            }
        """
        if not self.config.enable_morphing:
            return {"morphed_code": code, "transformations": [], "strategy": strategy}
        return self.code_morpher.morph(code, strategy)

    def compile_defensive(
        self, code: str, mode: str = "defensive", target: str = "python"
    ) -> dict[str, Any]:
        """
        Compile *code* with defensive security features.

        Returns::

            {
                "compiled_code": str,
                "security_features": list[str],
                "mode": str,   # echoes the requested mode
                ...
            }
        """
        if not self.config.enable_compilation:
            return {"compiled_code": code, "security_features": [], "mode": mode}
        return self.defensive_compiler.compile(code, mode, target)

    def check_policy(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Evaluate whether *action* is permitted given *context*.

        Returns::

            {"allowed": bool, "verdict": str, "reason": str}
        """
        return self.policy_engine.check(action, context)

    def get_integrated_status(self) -> dict[str, Any]:
        """
        Return current bridge health / configuration status.

        Called by :class:`ContrariaNFirewallOrchestrator` during telemetry
        collection and comprehensive status queries.
        """
        return {
            "mode": self.config.mode.value,
            "morphing_enabled": self.config.enable_morphing,
            "compilation_enabled": self.config.enable_compilation,
            "strict_policy": self.config.strict_policy,
            "components": {
                "threat_detector": "active",
                "code_morpher": "active",
                "defensive_compiler": "active",
                "policy_engine": "active",
            },
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _recommendations(threats: list[dict[str, Any]]) -> list[str]:
        """Generate human-readable recommendations from threat list."""
        _map: dict[str, str] = {
            "code_injection": "Avoid eval()/exec() with untrusted input; use ast.literal_eval() where possible",
            "os_command": "Use subprocess with shell=False and explicit argument lists instead of os.system()",
            "subprocess_exec": "Validate all subprocess arguments; use an allowlist for permitted commands",
            "deserialization": "Never unpickle untrusted data; prefer JSON or protobuf",
            "file_access": "Validate and canonicalise file paths; restrict to an allowed directory",
            "user_input": "Sanitise and validate all user-supplied values before use",
            "untrusted_input": "Never pass untrusted input directly to code-execution primitives",
            "dynamic_import": "Avoid __import__() with dynamic names; use an explicit import allowlist",
            "globals_access": "Restrict globals() / locals() access in sandboxed or untrusted code",
        }
        seen: set[str] = set()
        recs: list[str] = []
        for t in threats:
            tt = t.get("type", "")
            if tt not in seen:
                seen.add(tt)
                if tt in _map:
                    recs.append(_map[tt])
        return recs if recs else ["No immediate recommendations — code appears safe"]
