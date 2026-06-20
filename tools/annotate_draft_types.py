"""Add explicit boundaries to unannotated functions in a Python draft module."""

from __future__ import annotations

import argparse
from pathlib import Path

import libcst as cst

ANY = cst.Attribute(value=cst.Name("typing"), attr=cst.Name("Any"))


def annotate_parameter(parameter: cst.Param) -> cst.Param:
    if parameter.name.value in {"self", "cls"} or parameter.annotation is not None:
        return parameter
    return parameter.with_changes(annotation=cst.Annotation(ANY))


class DraftBoundaryTransformer(cst.CSTTransformer):
    """Retain observed annotations and mark every remaining boundary explicitly."""

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        del original_node
        parameters = updated_node.params
        annotated = parameters.with_changes(
            params=tuple(annotate_parameter(item) for item in parameters.params),
            posonly_params=tuple(annotate_parameter(item) for item in parameters.posonly_params),
            kwonly_params=tuple(annotate_parameter(item) for item in parameters.kwonly_params),
            star_arg=(
                annotate_parameter(parameters.star_arg)
                if isinstance(parameters.star_arg, cst.Param)
                else parameters.star_arg
            ),
            star_kwarg=(
                annotate_parameter(parameters.star_kwarg)
                if parameters.star_kwarg is not None
                else None
            ),
        )
        returns = updated_node.returns
        if returns is None:
            returns = cst.Annotation(cst.Name("None") if updated_node.name.value == "__init__" else ANY)
        return updated_node.with_changes(params=annotated, returns=returns)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    source = args.path.read_text(encoding="utf-8")
    updated = cst.parse_module(source).visit(DraftBoundaryTransformer()).code
    args.path.write_text(updated, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
