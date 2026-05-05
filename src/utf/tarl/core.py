from __future__ import annotations

import ast as pyast
import json
import operator
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VERDICTS = {"ALLOW", "DENY", "ESCALATE"}


@dataclass
class Rule:
    expr: str
    verdict: str


@dataclass
class Policy:
    name: str
    rules: list[Rule]


POLICY_RE = re.compile(r"policy\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{(?P<body>.*)\}", re.S)
RULE_RE = re.compile(r"when\s+(.*?)\s*=>\s*(ALLOW|DENY|ESCALATE)\s*;", re.S)


def parse_policy(text: str) -> Policy:
    m = POLICY_RE.search(text)
    if not m:
        raise ValueError("invalid TARL policy file")
    name = m.group(1)
    body = m.group("body")
    rules = [Rule(expr.strip(), verdict) for expr, verdict in RULE_RE.findall(body)]
    if not rules:
        raise ValueError("policy contains no rules")
    return Policy(name, rules)


class SafeExpr:
    ALLOWED_NODES = (
        pyast.Expression, pyast.BoolOp, pyast.BinOp, pyast.UnaryOp, pyast.Compare,
        pyast.Name, pyast.Load, pyast.Constant, pyast.And, pyast.Or, pyast.Not,
        pyast.Eq, pyast.NotEq, pyast.Lt, pyast.LtE, pyast.Gt, pyast.GtE,
        pyast.Attribute, pyast.Subscript, pyast.Add, pyast.Sub, pyast.Mult,
        pyast.Div, pyast.Mod, pyast.USub, pyast.List, pyast.Tuple,
    )

    def __init__(self, expr: str):
        self.expr = expr
        self.tree = pyast.parse(expr, mode="eval")
        for node in pyast.walk(self.tree):
            if not isinstance(node, self.ALLOWED_NODES):
                raise ValueError(f"disallowed TARL expression node: {type(node).__name__}")

    def eval(self, context: dict[str, Any]) -> Any:
        return self._node(self.tree.body, context)

    def _node(self, node, context):
        if isinstance(node, pyast.Constant):
            return node.value
        if isinstance(node, pyast.Name):
            return context.get(node.id)
        if isinstance(node, pyast.Attribute):
            value = self._node(node.value, context)
            if isinstance(value, dict):
                return value.get(node.attr)
            return getattr(value, node.attr, None)
        if isinstance(node, pyast.Subscript):
            value = self._node(node.value, context)
            key = self._node(node.slice, context) if not isinstance(node.slice, pyast.Constant) else node.slice.value
            return value[key]
        if isinstance(node, pyast.List):
            return [self._node(x, context) for x in node.elts]
        if isinstance(node, pyast.Tuple):
            return tuple(self._node(x, context) for x in node.elts)
        if isinstance(node, pyast.BoolOp):
            if isinstance(node.op, pyast.And):
                return all(self._node(v, context) for v in node.values)
            return any(self._node(v, context) for v in node.values)
        if isinstance(node, pyast.UnaryOp):
            operand = self._node(node.operand, context)
            if isinstance(node.op, pyast.Not):
                return not operand
            if isinstance(node.op, pyast.USub):
                return -operand
        if isinstance(node, pyast.BinOp):
            ops = {
                pyast.Add: operator.add,
                pyast.Sub: operator.sub,
                pyast.Mult: operator.mul,
                pyast.Div: operator.truediv,
                pyast.Mod: operator.mod,
            }
            return ops[type(node.op)](self._node(node.left, context), self._node(node.right, context))
        if isinstance(node, pyast.Compare):
            left = self._node(node.left, context)
            for op, comp in zip(node.ops, node.comparators):
                right = self._node(comp, context)
                ok = {
                    pyast.Eq: left == right,
                    pyast.NotEq: left != right,
                    pyast.Lt: left < right,
                    pyast.LtE: left <= right,
                    pyast.Gt: left > right,
                    pyast.GtE: left >= right,
                }[type(op)]
                if not ok:
                    return False
                left = right
            return True
        raise ValueError(f"unsupported node: {type(node).__name__}")


def evaluate(policy: Policy, context: dict[str, Any]) -> str:
    for rule in policy.rules:
        if SafeExpr(rule.expr).eval(context):
            return rule.verdict
    return "DENY"


def load_context(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
