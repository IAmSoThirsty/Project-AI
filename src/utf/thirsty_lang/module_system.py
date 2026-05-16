from __future__ import annotations

import hashlib
import hmac as _hmac
import json as _json
import logging
import os
import socket
import sqlite3
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request as _urllib_request

from . import ast
from .lexer import Lexer
from .package_manager import project_search_roots, resolve_package_source
from .parser import Parser
from .typesys import ANY, INT, STRING, VOID, Type


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
    fn = lambda *ts: Type("BuiltinFn", ts)  # noqa: E731
    return {
        "thirst::time": ModuleTypeInfo(
            "thirst::time",
            {
                "now": fn(INT),
                "epoch_ms": fn(INT),
                "format": fn(INT, STRING, STRING),
                "sleep": fn(INT, VOID),
                "parse": fn(STRING, INT),
            },
        ),
        "thirst::crypto": ModuleTypeInfo(
            "thirst::crypto",
            {
                "sha256": fn(STRING, STRING),
                "sign": fn(STRING, STRING),
                "hmac": fn(STRING, STRING, STRING),
                "random_bytes": fn(INT, STRING),
                "uuid4": fn(STRING),
            },
        ),
        "thirst::reservoir": ModuleTypeInfo(
            "thirst::reservoir",
            {
                "size": fn(ANY, INT),
                "push": fn(ANY, ANY, VOID),
                "pop": fn(ANY, ANY),
                "get": fn(ANY, INT, ANY),
                "flood": fn(ANY, ANY, ANY),
            },
        ),
        "thirst::fs": ModuleTypeInfo(
            "thirst::fs",
            {
                "read_file": fn(STRING, STRING),
                "write_file": fn(STRING, STRING, VOID),
                "exists": fn(STRING, ANY),
                "list_dir": fn(STRING, ANY),
                "mkdir": fn(STRING, VOID),
                "remove": fn(STRING, VOID),
            },
        ),
        "thirst::path": ModuleTypeInfo(
            "thirst::path",
            {
                "join": fn(STRING, STRING, STRING),
                "dirname": fn(STRING, STRING),
                "basename": fn(STRING, STRING),
                "extension": fn(STRING, STRING),
                "absolute": fn(STRING, STRING),
                "relative": fn(STRING, STRING, STRING),
            },
        ),
        "thirst::json": ModuleTypeInfo(
            "thirst::json",
            {
                "parse": fn(STRING, ANY),
                "stringify": fn(ANY, STRING),
                "get": fn(ANY, STRING, ANY),
                "set": fn(ANY, STRING, ANY, ANY),
            },
        ),
        "thirst::http": ModuleTypeInfo(
            "thirst::http",
            {
                "get": fn(STRING, ANY),
                "post": fn(STRING, ANY, ANY),
                "put": fn(STRING, ANY, ANY),
                "delete": fn(STRING, ANY),
            },
        ),
        "thirst::env": ModuleTypeInfo(
            "thirst::env",
            {
                "get": fn(STRING, ANY),
                "set": fn(STRING, STRING, VOID),
                "all": fn(ANY),
            },
        ),
        "thirst::process": ModuleTypeInfo(
            "thirst::process",
            {
                "run": fn(ANY, ANY),
                "exit": fn(INT, VOID),
                "args": fn(ANY),
                "pid": fn(INT),
            },
        ),
        "thirst::log": ModuleTypeInfo(
            "thirst::log",
            {
                "info": fn(STRING, VOID),
                "warn": fn(STRING, VOID),
                "error": fn(STRING, VOID),
                "debug": fn(STRING, VOID),
            },
        ),
        "thirst::test": ModuleTypeInfo(
            "thirst::test",
            {
                "assert_eq": fn(ANY, ANY, VOID),
                "assert_ne": fn(ANY, ANY, VOID),
                "assert_true": fn(ANY, VOID),
                "assert_raises": fn(ANY, ANY, VOID),
                "describe": fn(STRING, VOID),
                "it": fn(STRING, ANY, VOID),
            },
        ),
        "thirst::collections": ModuleTypeInfo(
            "thirst::collections",
            {
                "map": fn(ANY, ANY, ANY),
                "filter": fn(ANY, ANY, ANY),
                "reduce": fn(ANY, ANY, ANY, ANY),
                "sort": fn(ANY, ANY),
                "unique": fn(ANY, ANY),
                "flatten": fn(ANY, ANY),
                "zip": fn(ANY, ANY, ANY),
            },
        ),
        "thirst::net": ModuleTypeInfo(
            "thirst::net",
            {
                "tcp_connect": fn(STRING, INT, ANY),
                "tcp_listen": fn(INT, ANY),
                "udp_send": fn(STRING, INT, STRING, VOID),
            },
        ),
        "thirst::sqlite": ModuleTypeInfo(
            "thirst::sqlite",
            {
                "connect": fn(STRING, ANY),
                "query": fn(ANY, STRING, ANY),
                "execute": fn(ANY, STRING, VOID),
                "close": fn(ANY, VOID),
            },
        ),
        "thirst::yaml": ModuleTypeInfo(
            "thirst::yaml",
            {
                "parse": fn(STRING, ANY),
                "dump": fn(ANY, STRING),
            },
        ),
        "thirst::toml": ModuleTypeInfo(
            "thirst::toml",
            {
                "parse": fn(STRING, ANY),
                "dump": fn(ANY, STRING),
            },
        ),
    }


# ── thirst::test helpers ────────────────────────────────────────────────────

class _TestError(Exception):
    pass


def _assert_eq(a: Any, b: Any) -> None:
    if a != b:
        raise _TestError(f"assert_eq failed: {a!r} != {b!r}")


def _assert_ne(a: Any, b: Any) -> None:
    if a == b:
        raise _TestError(f"assert_ne failed: {a!r} == {b!r}")


def _assert_true(v: Any) -> None:
    if not v:
        raise _TestError(f"assert_true failed: {v!r} is falsy")


def _assert_raises(fn: Any, exc_type: Any) -> None:
    try:
        fn()
    except Exception:
        return
    raise _TestError("assert_raises: no exception was raised")


_LOG = logging.getLogger("thirst")
logging.basicConfig(format="[thirst:%(levelname)s] %(message)s")


# ── thirst::yaml helpers ────────────────────────────────────────────────────

def _yaml_parse(text: str) -> Any:
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        raise ImportError(
            "thirst::yaml requires PyYAML — install it with: pip install PyYAML"
        )


def _yaml_dump(data: Any) -> str:
    try:
        import yaml
        return yaml.safe_dump(data, default_flow_style=False)
    except ImportError:
        raise ImportError(
            "thirst::yaml requires PyYAML — install it with: pip install PyYAML"
        )


# ── thirst::toml helpers ────────────────────────────────────────────────────

def _toml_parse(text: str) -> Any:
    try:
        import tomllib
        return tomllib.loads(text)
    except ImportError:
        try:
            import tomli
            return tomli.loads(text)
        except ImportError:
            raise ImportError(
                "thirst::toml requires Python 3.11+ (tomllib) or tomli — "
                "install with: pip install tomli"
            )


def _toml_dump(data: Any) -> str:
    lines: list[str] = []

    def _encode_value(v: Any) -> str:
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, int):
            return str(v)
        if isinstance(v, float):
            return str(v)
        if isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'"{escaped}"'
        if isinstance(v, list):
            items = ", ".join(_encode_value(x) for x in v)
            return f"[{items}]"
        return f'"{v!r}"'

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                lines.append(f"[{k}]")
                for sk, sv in v.items():
                    lines.append(f"{sk} = {_encode_value(sv)}")
            else:
                lines.append(f"{k} = {_encode_value(v)}")
    return "\n".join(lines) + "\n"


# ── thirst::http helpers ─────────────────────────────────────────────────────

def _http_get(url: str) -> Any:
    with _urllib_request.urlopen(str(url)) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        try:
            return _json.loads(body)
        except _json.JSONDecodeError:
            return body


def _http_post(url: str, body: Any) -> Any:
    data = (_json.dumps(body) if not isinstance(body, (str, bytes)) else body)
    if isinstance(data, str):
        data = data.encode("utf-8")
    req = _urllib_request.Request(
        str(url), data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _urllib_request.urlopen(req) as resp:
        result = resp.read().decode("utf-8", errors="replace")
        try:
            return _json.loads(result)
        except _json.JSONDecodeError:
            return result


def _http_put(url: str, body: Any) -> Any:
    data = (_json.dumps(body) if not isinstance(body, (str, bytes)) else body)
    if isinstance(data, str):
        data = data.encode("utf-8")
    req = _urllib_request.Request(
        str(url), data=data,
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with _urllib_request.urlopen(req) as resp:
        result = resp.read().decode("utf-8", errors="replace")
        try:
            return _json.loads(result)
        except _json.JSONDecodeError:
            return result


def _http_delete(url: str) -> Any:
    req = _urllib_request.Request(str(url), method="DELETE")
    with _urllib_request.urlopen(req) as resp:
        result = resp.read().decode("utf-8", errors="replace")
        try:
            return _json.loads(result)
        except _json.JSONDecodeError:
            return result


# ── thirst::net helpers ──────────────────────────────────────────────────────

def _tcp_connect(host: str, port: int) -> Any:
    sock = socket.create_connection((str(host), int(port)), timeout=10)
    return {"socket": sock, "host": host, "port": port}


def _tcp_listen(port: int) -> Any:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("", int(port)))
    srv.listen(5)
    return {"server": srv, "port": port}


def _udp_send(host: str, port: int, message: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(str(message).encode("utf-8"), (str(host), int(port)))
    sock.close()


# ── thirst::sqlite helpers ───────────────────────────────────────────────────

def _sqlite_connect(path: str) -> Any:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _sqlite_query(conn: Any, sql: str) -> Any:
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    return [dict(row) for row in rows]


def _sqlite_execute(conn: Any, sql: str) -> None:
    conn.execute(sql)
    conn.commit()


def _sqlite_close(conn: Any) -> None:
    conn.close()


# ── main registry ────────────────────────────────────────────────────────────

def builtin_modules() -> dict[str, ModuleValue]:
    return {
        "thirst::time": ModuleValue(
            "thirst::time",
            {
                "now": lambda: int(time.time()),
                "epoch_ms": lambda: int(time.time() * 1000),
                "format": lambda ts, fmt: time.strftime(
                    str(fmt), time.localtime(int(ts))
                ),
                "sleep": lambda ms: time.sleep(int(ms) / 1000),
                "parse": lambda s: int(
                    time.mktime(time.strptime(str(s), "%Y-%m-%dT%H:%M:%S"))
                ),
            },
        ),
        "thirst::crypto": ModuleValue(
            "thirst::crypto",
            {
                "sha256": lambda text: hashlib.sha256(
                    str(text).encode("utf-8")
                ).hexdigest(),
                "sign": lambda text: (
                    "signed:"
                    + hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:16]
                ),
                "hmac": lambda key, text: _hmac.new(
                    str(key).encode("utf-8"),
                    str(text).encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest(),
                "random_bytes": lambda n: os.urandom(int(n)).hex(),
                "uuid4": lambda: str(uuid.uuid4()),
            },
        ),
        "thirst::reservoir": ModuleValue(
            "thirst::reservoir",
            {
                "size": lambda items: len(items),
                "push": lambda items, value: items.append(value),
                "pop": lambda items: items.pop(),
                "get": lambda items, idx: items[idx],
                "flood": lambda items, payload: (
                    items.extend(payload if isinstance(payload, list) else [payload])
                    or items
                ),
            },
        ),
        "thirst::fs": ModuleValue(
            "thirst::fs",
            {
                "read_file": lambda p: Path(str(p)).read_text(encoding="utf-8"),
                "write_file": lambda p, t: Path(str(p)).write_text(
                    str(t), encoding="utf-8"
                ),
                "exists": lambda p: Path(str(p)).exists(),
                "list_dir": lambda p: [str(x) for x in Path(str(p)).iterdir()],
                "mkdir": lambda p: Path(str(p)).mkdir(parents=True, exist_ok=True),
                "remove": lambda p: (
                    Path(str(p)).unlink()
                    if Path(str(p)).is_file()
                    else __import__("shutil").rmtree(str(p))
                ),
            },
        ),
        "thirst::path": ModuleValue(
            "thirst::path",
            {
                "join": lambda a, b: str(Path(str(a)) / str(b)),
                "dirname": lambda p: str(Path(str(p)).parent),
                "basename": lambda p: Path(str(p)).name,
                "extension": lambda p: Path(str(p)).suffix,
                "absolute": lambda p: str(Path(str(p)).resolve()),
                "relative": lambda p, base: str(
                    Path(str(p)).relative_to(str(base))
                ),
            },
        ),
        "thirst::json": ModuleValue(
            "thirst::json",
            {
                "parse": lambda s: _json.loads(str(s)),
                "stringify": lambda v: _json.dumps(v, ensure_ascii=False),
                "get": lambda obj, key: (
                    obj.get(str(key)) if isinstance(obj, dict) else None
                ),
                "set": lambda obj, key, val: (
                    obj.update({str(key): val}) or obj
                    if isinstance(obj, dict)
                    else obj
                ),
            },
        ),
        "thirst::http": ModuleValue(
            "thirst::http",
            {
                "get": _http_get,
                "post": _http_post,
                "put": _http_put,
                "delete": _http_delete,
            },
        ),
        "thirst::env": ModuleValue(
            "thirst::env",
            {
                "get": lambda key: os.environ.get(str(key)),
                "set": lambda key, val: os.environ.update({str(key): str(val)}),
                "all": lambda: dict(os.environ),
            },
        ),
        "thirst::process": ModuleValue(
            "thirst::process",
            {
                "run": lambda cmd: subprocess.run(
                    cmd if isinstance(cmd, list) else str(cmd),
                    shell=not isinstance(cmd, list),
                    capture_output=True,
                    text=True,
                    check=False,
                ),
                "exit": lambda code: sys.exit(int(code)),
                "args": lambda: sys.argv[1:],
                "pid": lambda: os.getpid(),
            },
        ),
        "thirst::log": ModuleValue(
            "thirst::log",
            {
                "info": lambda msg: _LOG.info(str(msg)),
                "warn": lambda msg: _LOG.warning(str(msg)),
                "error": lambda msg: _LOG.error(str(msg)),
                "debug": lambda msg: _LOG.debug(str(msg)),
            },
        ),
        "thirst::test": ModuleValue(
            "thirst::test",
            {
                "assert_eq": _assert_eq,
                "assert_ne": _assert_ne,
                "assert_true": _assert_true,
                "assert_raises": _assert_raises,
                "describe": lambda name: print(f"  describe: {name}"),
                "it": lambda name, fn: (
                    print(f"    ✓ {name}") if (fn(), True)[1] else None
                ),
            },
        ),
        "thirst::collections": ModuleValue(
            "thirst::collections",
            {
                "map": lambda xs, fn: [fn(x) for x in xs],
                "filter": lambda xs, fn: [x for x in xs if fn(x)],
                "reduce": lambda xs, seed, fn: (
                    __import__("functools").reduce(fn, xs, seed)
                ),
                "sort": lambda xs: sorted(xs),
                "unique": lambda xs: list(dict.fromkeys(xs)),
                "flatten": lambda xs: [
                    item for sub in xs for item in (sub if isinstance(sub, list) else [sub])
                ],
                "zip": lambda xs, ys: list(zip(xs, ys)),
            },
        ),
        "thirst::net": ModuleValue(
            "thirst::net",
            {
                "tcp_connect": _tcp_connect,
                "tcp_listen": _tcp_listen,
                "udp_send": _udp_send,
            },
        ),
        "thirst::sqlite": ModuleValue(
            "thirst::sqlite",
            {
                "connect": _sqlite_connect,
                "query": _sqlite_query,
                "execute": _sqlite_execute,
                "close": _sqlite_close,
            },
        ),
        "thirst::yaml": ModuleValue(
            "thirst::yaml",
            {
                "parse": _yaml_parse,
                "dump": _yaml_dump,
            },
        ),
        "thirst::toml": ModuleValue(
            "thirst::toml",
            {
                "parse": _toml_parse,
                "dump": _toml_dump,
            },
        ),
    }


def _module_exports_from_program(program: ast.Program) -> dict[str, Type]:
    exports: dict[str, Type] = {}
    from .typesys import from_type_node, task

    for decl in program.declarations:
        if isinstance(decl, ast.FunctionDecl):
            params = [from_type_node(p.type_node) for p in decl.params]
            result = (
                VOID if decl.return_type is None else from_type_node(decl.return_type)
            )
            fn_type = (
                task(result)
                if decl.is_async
                else Type("Function", tuple(params + [result]))
            )
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
    if (
        module_spec.startswith("./")
        or module_spec.startswith("../")
        or raw.suffix in {".thirsty", ".thirstofgods"}
    ):
        candidate = (base_dir / module_spec).resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"module not found: {module_spec}")

    if module_spec.startswith("thirst::"):
        raise FileNotFoundError(f"builtin module {module_spec} is not file-backed")

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
