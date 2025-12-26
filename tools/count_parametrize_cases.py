from __future__ import annotations

import ast
import sys
from pathlib import Path


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tests/test_four_laws_scenarios.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))

    count: int | None = None

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:
            nonlocal count
            if isinstance(node.func, ast.Attribute) and node.func.attr == "parametrize":
                if len(node.args) >= 2 and isinstance(node.args[1], ast.List):
                    count = len(node.args[1].elts)
            self.generic_visit(node)

    Visitor().visit(tree)
    print(count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
