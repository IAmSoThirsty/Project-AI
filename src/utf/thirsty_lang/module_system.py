
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import ast
from .diagnostics import ThirstyError
from .lexer import Lexer
from .parser import Parser
from .typesys import ANY, INT, STRING, VOID, BOOL, Type, reservoir
from .package_manager import project_search_roots, resolve_package_source


@dataclass
class ModuleValue:
    name: str
    members: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.members[key]


@dataclass
class ModuleTypeInfo:
    name: str
    members: dict[str, Type]


def builtin_module_types() -> dict[str, ModuleTypeInfo]:
    return {
        "thirst::time": ModuleTypeInfo("thirst::time", {
            "now": Type("BuiltinFn", (INT,)),
            "epoch_ms": Type("BuiltinFn", (INT,)),
        }),
        "thirst::crypto": ModuleTypeInfo("thirst::crypto", {
            "sha256": Type("BuiltinFn", (STRING, STRING)),
            "bless": Type("BuiltinFn", (STRING, STRING)),
        }),
        "thirst::reservoir": ModuleTypeInfo("thirst::reservoir", {
            "size": Type("BuiltinFn", (ANY, INT)),
            "push": Type("BuiltinFn", (ANY, ANY, VOID)),
            "pop": Type("BuiltinFn", (ANY, ANY)),
            "get": Type("BuiltinFn", (ANY, INT, ANY)),
            "strain": Type("BuiltinFn", (ANY, ANY, ANY)),
            "transmute": Type("BuiltinFn", (ANY, ANY, ANY)),
            "distill": Type("BuiltinFn", (ANY, ANY, ANY, ANY)),
            "flood": Type("BuiltinFn", (ANY, ANY, ANY)),
        }),
    }


def builtin_modules() -> dict[str, ModuleValue]:
    return {
        "thirst::time": ModuleValue("thirst::time", {
            "now": lambda: int(time.time()),
            "epoch_ms": lambda: int(time.time() * 1000),
        }),
        "thirst::crypto": ModuleValue("thirst::crypto", {
            "sha256": lambda text: hashlib.sha256(str(text).encode("utf-8")).hexdigest(),
            "bless": lambda text: "blessed:" + hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16],
        }),
        "thirst::reservoir": ModuleValue("thirst::reservoir", {
            "size": lambda items: len(items),
            "push": lambda items, value: items.append(value),
            "pop": lambda items: items.pop(),
            "get": lambda items, idx: items[idx],
            "flood": lambda items, payload: items.extend(payload if isinstance(payload, list) else [payload]) or items,
        }),
    }


def _module_exports_from_program(program: ast.Program) -> dict[str, Type]:
    exports: dict[str, Type] = {}
    from .typesys import from_type_node, task
    for decl in program.declarations:
        if isinstance(decl, ast.FunctionDecl):
            params = [from_type_node(p.type_node) for p in decl.params]
            result = VOID if decl.return_type is None else from_type_node(decl.return_type)
            fn_type = task(result) if decl.is_async else Type("Function", tuple(params + [result]))
            exports[decl.name] = fn_type
        elif isinstance(decl, ast.ClassDecl):
            exports[decl.name] = Type(decl.name)
        elif isinstance(decl, ast.VarDecl):
            exports[decl.name] = from_type_node(decl.type_node)
    return exports


def resolve_import_type(module_spec: str, current_file: str) -> ModuleTypeInfo:
    builtins = builtin_module_types()
    if module_spec in builtins:
        return builtins[module_spec]

    path = Path(current_file).resolve()
    base_dir = path.parent if path.suffix else path
    source_file = resolve_module_file(module_spec, base_dir)
    text = source_file.read_text(encoding="utf-8")
    tokens = Lexer(text, str(source_file)).lex()
    program = Parser.from_tokens(tokens).parse_program()
    return ModuleTypeInfo(module_spec, _module_exports_from_program(program))


def resolve_module_file(module_spec: str, base_dir: Path) -> Path:
    raw = Path(module_spec)
    if module_spec.startswith("./") or module_spec.startswith("../") or raw.suffix in {".thirsty", ".thirstofgods"}:
        candidate = (base_dir / module_spec).resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"module not found: {module_spec}")

    if module_spec.startswith("thirst::"):
        raise FileNotFoundError(f"builtin module {module_spec} is not file-backed")

    # Package spec: pkg or pkg::subpath
    if "::" in module_spec:
        pkg_name, remainder = module_spec.split("::", 1)
    else:
        pkg_name, remainder = module_spec, None
    source_root, manifest = resolve_package_source(pkg_name)
    if remainder:
        rel = remainder.replace("::", "/")
        if not rel.endswith((".thirsty", ".thirstofgods")):
            rel += ".thirsty"
        candidate = source_root / rel
        if candidate.exists():
            return candidate
        candidate = source_root / "src" / rel
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"package module not found: {module_spec}")
    entry = manifest.get("entry", "src/main.thirsty")
    candidate = source_root / entry
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"package entry not found for {pkg_name}")


def file_based_registry_root(project_dir: Path) -> list[Path]:
    return project_search_roots(project_dir)
