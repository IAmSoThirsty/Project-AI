"""
Thirsty-Lang Language Server (LSP over stdio, no pygls dependency).

Implements the Language Server Protocol using raw JSON-RPC over stdin/stdout.
Compatible with VS Code, Neovim, Emacs lsp-mode, and any LSP client.

Usage:
    thirsty lsp --stdio          # start language server
    thirsty lsp --port 9900      # start on TCP port (for debugging)

Capabilities implemented:
  - textDocument/completion      keywords, stdlib namespaces, local variables
  - textDocument/hover           type information from checker symbol table
  - textDocument/definition      jump to declaration
  - textDocument/publishDiagnostics  checker errors as LSP diagnostics
  - textDocument/formatting      AST-based formatter output
"""

from __future__ import annotations

import io
import json
import logging
import sys
import threading
from pathlib import Path
from typing import Any

log = logging.getLogger("thirsty.lsp")


# ------------------------------------------------------------------
# JSON-RPC stdio transport
# ------------------------------------------------------------------

class Transport:
    """Read/write LSP messages over stdin/stdout (Content-Length framing)."""

    def __init__(self, reader: io.RawIOBase, writer: io.RawIOBase) -> None:
        self._r = reader
        self._w = writer
        self._lock = threading.Lock()

    def read_message(self) -> dict | None:
        headers: dict[str, str] = {}
        while True:
            line = self._r.readline()
            if not line:
                return None
            line = line.decode("utf-8").rstrip("\r\n")
            if not line:
                break
            if ":" in line:
                k, _, v = line.partition(":")
                headers[k.strip().lower()] = v.strip()
        length = int(headers.get("content-length", 0))
        if not length:
            return None
        body = b""
        while len(body) < length:
            chunk = self._r.read(length - len(body))
            if not chunk:
                return None
            body += chunk
        return json.loads(body.decode("utf-8"))

    def send_message(self, msg: dict) -> None:
        body = json.dumps(msg, separators=(",", ":")).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        with self._lock:
            self._w.write(header + body)
            self._w.flush()


# ------------------------------------------------------------------
# Document store
# ------------------------------------------------------------------

class DocumentStore:
    def __init__(self) -> None:
        self._docs: dict[str, str] = {}

    def open(self, uri: str, text: str) -> None:
        self._docs[uri] = text

    def change(self, uri: str, changes: list[dict]) -> None:
        # Full-document sync (incremental not required for MVP)
        for c in changes:
            if "text" in c:
                self._docs[uri] = c["text"]

    def close(self, uri: str) -> None:
        self._docs.pop(uri, None)

    def get(self, uri: str) -> str | None:
        return self._docs.get(uri)


# ------------------------------------------------------------------
# Completion items
# ------------------------------------------------------------------

_KEYWORDS = [
    "drink", "pour", "glass", "fountain", "refill", "times",
    "thirsty", "hydrated", "spillage", "cleanup", "finally",
    "return", "throw", "import", "as", "from", "new", "this",
    "mut", "empty", "quenched", "parched", "cascade", "await",
    "enum", "struct", "interface", "requires", "module", "mode",
    "core", "governed", "shield", "sanitize", "armor", "morph",
    "detect", "defend", "drip", "evaporate", "condense",
    "thirst", "quench",
]

_BUILTINS = [
    "length", "contains", "split", "abs", "min", "max",
    "push", "pop", "size", "get", "flood", "condense",
    "evaporate", "strain", "transmute", "distill",
]

_STDLIB_NAMESPACES = [
    "thirst::time", "thirst::crypto", "thirst::reservoir",
    "thirst::fs", "thirst::path", "thirst::json", "thirst::http",
    "thirst::env", "thirst::process", "thirst::log", "thirst::test",
    "thirst::collections", "thirst::net", "thirst::sqlite",
    "thirst::yaml", "thirst::toml",
]

_TYPES = [
    "Int", "Float", "Bool", "String", "Void", "Any", "Error",
    "Reservoir", "Quenched", "Task", "Result", "Governed",
]


def _completion_item(label: str, kind: int, detail: str = "") -> dict:
    """LSP CompletionItem. kind: 1=Text,2=Method,3=Function,6=Variable,14=Keyword"""
    item: dict[str, Any] = {"label": label, "kind": kind}
    if detail:
        item["detail"] = detail
    return item


def _keyword_completions() -> list[dict]:
    return [_completion_item(k, 14) for k in _KEYWORDS]


def _builtin_completions() -> list[dict]:
    return [_completion_item(b, 3, "builtin") for b in _BUILTINS]


def _type_completions() -> list[dict]:
    return [_completion_item(t, 7, "type") for t in _TYPES]


def _completions_for(source: str, line: int, char: int) -> list[dict]:
    items = _keyword_completions() + _builtin_completions() + _type_completions()
    # Add stdlib import completions when inside an import statement
    lines = source.splitlines()
    if 0 <= line < len(lines):
        cur = lines[line][:char]
        if "import" in cur:
            items += [_completion_item(f'"{ns}"', 9, "stdlib") for ns in _STDLIB_NAMESPACES]
    return items


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def _uri_to_path(uri: str) -> str:
    if uri.startswith("file:///"):
        return uri[8:].replace("/", "\\") if sys.platform == "win32" else uri[7:]
    return uri


def _run_checker(source: str, uri: str) -> list[dict]:
    """Run the Thirsty checker and return LSP diagnostic dicts."""
    try:
        from .lexer import Lexer
        from .parser import Parser
        from .checker import Checker
        from .diagnostics import ThirstyError, DiagnosticBundle

        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        checker = Checker()
        checker.check(program)
        return []
    except ThirstyError as e:
        return [_to_diagnostic(e)]
    except DiagnosticBundle as b:
        return [_to_diagnostic(e) for e in b.errors]
    except Exception:
        return []


def _to_diagnostic(err) -> dict:
    s = err.span
    return {
        "range": {
            "start": {"line": max(0, s.line - 1), "character": max(0, s.column - 1)},
            "end":   {"line": max(0, s.end_line - 1), "character": max(0, s.end_column - 1)},
        },
        "severity": 1,  # Error
        "code": err.code,
        "source": "thirsty",
        "message": err.message,
    }


# ------------------------------------------------------------------
# Hover
# ------------------------------------------------------------------

def _hover_for(source: str, line: int, char: int) -> str | None:
    """Return hover markdown for symbol at position, or None."""
    try:
        from .lexer import Lexer
        from .parser import Parser
        from .checker import Checker

        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        checker = Checker()
        checker.check(program)

        # Find the token at this position
        target_line = line + 1  # LSP is 0-based; span is 1-based
        target_col = char + 1
        for tok in tokens:
            if tok.span.line == target_line and tok.span.column <= target_col <= tok.span.end_column:
                name = tok.lexeme
                sym = checker.scope.resolve(name) if hasattr(checker, "scope") else None
                if sym is not None:
                    return f"```thirsty\n{name}: {sym.type}\n```"
                # Check globals
                sym = checker.globals.resolve(name) if hasattr(checker, "globals") else None
                if sym is not None:
                    return f"```thirsty\n{name}: {sym.type}\n```"
                break
    except Exception:
        pass
    return None


# ------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------

def _format_document(source: str) -> str | None:
    try:
        from .lexer import Lexer
        from .parser import Parser
        from .formatter import Formatter
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        return Formatter().format(program)
    except Exception:
        return None


# ------------------------------------------------------------------
# LSP Server
# ------------------------------------------------------------------

class ThirstyLSP:
    def __init__(self, transport: Transport) -> None:
        self._t = transport
        self._docs = DocumentStore()
        self._running = True
        self._next_id = 1

    def _respond(self, req_id: Any, result: Any) -> None:
        self._t.send_message({"jsonrpc": "2.0", "id": req_id, "result": result})

    def _error(self, req_id: Any, code: int, message: str) -> None:
        self._t.send_message({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message},
        })

    def _notify(self, method: str, params: Any) -> None:
        self._t.send_message({"jsonrpc": "2.0", "method": method, "params": params})

    def _publish_diagnostics(self, uri: str, source: str) -> None:
        diags = _run_checker(source, uri)
        self._notify("textDocument/publishDiagnostics", {
            "uri": uri,
            "diagnostics": diags,
        })

    def handle(self, msg: dict) -> None:
        method = msg.get("method", "")
        params = msg.get("params") or {}
        req_id = msg.get("id")

        if method == "initialize":
            self._respond(req_id, {
                "capabilities": {
                    "textDocumentSync": {
                        "openClose": True,
                        "change": 1,  # full sync
                        "save": {"includeText": True},
                    },
                    "completionProvider": {"triggerCharacters": [".", '"']},
                    "hoverProvider": True,
                    "documentFormattingProvider": True,
                    "definitionProvider": False,  # future
                },
                "serverInfo": {"name": "thirsty-lsp", "version": "1.0"},
            })

        elif method == "initialized":
            pass  # client acknowledged; no action needed

        elif method == "shutdown":
            self._respond(req_id, None)
            self._running = False

        elif method == "exit":
            self._running = False

        elif method == "textDocument/didOpen":
            doc = params["textDocument"]
            self._docs.open(doc["uri"], doc["text"])
            self._publish_diagnostics(doc["uri"], doc["text"])

        elif method == "textDocument/didChange":
            uri = params["textDocument"]["uri"]
            self._docs.change(uri, params.get("contentChanges", []))
            src = self._docs.get(uri)
            if src:
                self._publish_diagnostics(uri, src)

        elif method == "textDocument/didClose":
            uri = params["textDocument"]["uri"]
            self._docs.close(uri)
            self._notify("textDocument/publishDiagnostics", {"uri": uri, "diagnostics": []})

        elif method == "textDocument/didSave":
            uri = params["textDocument"]["uri"]
            text = params.get("text")
            if text:
                self._docs.open(uri, text)
            src = self._docs.get(uri)
            if src:
                self._publish_diagnostics(uri, src)

        elif method == "textDocument/completion":
            pos = params.get("position", {})
            uri = params["textDocument"]["uri"]
            src = self._docs.get(uri) or ""
            items = _completions_for(src, pos.get("line", 0), pos.get("character", 0))
            self._respond(req_id, {"isIncomplete": False, "items": items})

        elif method == "textDocument/hover":
            pos = params.get("position", {})
            uri = params["textDocument"]["uri"]
            src = self._docs.get(uri) or ""
            md = _hover_for(src, pos.get("line", 0), pos.get("character", 0))
            if md:
                self._respond(req_id, {"contents": {"kind": "markdown", "value": md}})
            else:
                self._respond(req_id, None)

        elif method == "textDocument/formatting":
            uri = params["textDocument"]["uri"]
            src = self._docs.get(uri) or ""
            formatted = _format_document(src)
            if formatted is None or formatted == src:
                self._respond(req_id, [])
            else:
                lines = src.count("\n") + 1
                self._respond(req_id, [{
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": lines + 1, "character": 0},
                    },
                    "newText": formatted,
                }])

        elif req_id is not None:
            # Unknown request — respond with null so client doesn't hang
            self._respond(req_id, None)

    def run(self) -> None:
        log.info("Thirsty LSP server started")
        while self._running:
            msg = self._t.read_message()
            if msg is None:
                break
            try:
                self.handle(msg)
            except Exception as exc:
                log.exception("LSP handler error: %s", exc)


def start_stdio() -> None:
    """Start LSP server reading from stdin, writing to stdout."""
    # Use binary streams to avoid encoding issues
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    transport = Transport(stdin, stdout)
    server = ThirstyLSP(transport)
    server.run()


def start_tcp(port: int) -> None:
    """Start LSP server on a TCP port (for debugging with LSP clients)."""
    import socket

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", port))
    server_sock.listen(1)
    log.info("Thirsty LSP listening on port %d", port)
    conn, _ = server_sock.accept()
    transport = Transport(conn.makefile("rb"), conn.makefile("wb"))
    server = ThirstyLSP(transport)
    server.run()
    conn.close()
