"""
TARL Source-Level Debugger for Thirsty-Lang
============================================

DAP-style debug server.  Listens on TCP port 9899 (configurable via --port).
Protocol: one JSON object per line, newline-terminated, over a raw TCP socket.

Client → server commands:
  {"cmd": "run", "file": "path/to/file.thirsty"}
  {"cmd": "set_breakpoint", "file": "hello.thirsty", "line": 5}
  {"cmd": "remove_breakpoint", "file": "hello.thirsty", "line": 5}
  {"cmd": "continue"}
  {"cmd": "step"}
  {"cmd": "step_in"}
  {"cmd": "step_out"}
  {"cmd": "evaluate", "expr": "x + 1"}
  {"cmd": "variables"}
  {"cmd": "stack"}
  {"cmd": "quit"}

Server → client events/responses are documented in PROTOCOL_MESSAGES below.
"""
from __future__ import annotations

import json
import queue
import socket
import threading
from pathlib import Path
from typing import Any

from .interpreter import (
    Env,
    Interpreter,
    ReturnSignal,
    RuntimeFault,
    ThrownSignal,
    UserFunction,
)
from . import ast as _ast
from .token import Span


# ---------------------------------------------------------------------------
# Step-mode sentinels
# ---------------------------------------------------------------------------

_STEP_NONE = "none"      # running freely until a breakpoint
_STEP_OVER = "step"      # stop at next statement boundary
_STEP_IN   = "step_in"   # same as STEP_OVER in current implementation
_STEP_OUT  = "step_out"  # run until call depth decreases


# ---------------------------------------------------------------------------
# ThirstyDebugger — interpreter subclass with debug hooks
# ---------------------------------------------------------------------------

class ThirstyDebugger(Interpreter):
    """
    Subclass of Interpreter that intercepts statement execution to support
    breakpoints and single-stepping.

    Hooks are injected by overriding ``_exec``.  When execution must pause
    (breakpoint hit or step boundary reached), the hook puts a ``stopped``
    event on ``event_queue`` and waits on ``resume_event`` for the session
    to allow execution to continue.

    Thread model
    ------------
    The interpreter runs in its own thread (``_interp_thread``).  The
    ``DebugSession`` read-loop runs in the networking thread.  All
    inter-thread communication goes through:

      event_queue  — interpreter → network (events / responses)
      cmd_queue    — network → interpreter (resume, step commands)
      resume_event — interpreter waits here when paused
    """

    def __init__(self, event_queue: queue.Queue, cmd_queue: queue.Queue, **kwargs):
        super().__init__(**kwargs)
        self._event_queue: queue.Queue = event_queue
        self._cmd_queue: queue.Queue = cmd_queue
        self._resume_event = threading.Event()

        # Breakpoints: dict[file_stem -> set[line]]
        self._breakpoints: dict[str, set[int]] = {}

        # Step mode
        self._step_mode: str = _STEP_NONE
        self._step_depth: int = 0          # call depth at the time step was issued

        # Current execution position (for variables/stack commands while paused)
        self._current_env: Env | None = None
        self._call_stack: list[dict] = []  # [{name, file, line}]

        # Patch output to emit events
        self.output = _DebugOutputList(self._event_queue)  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Breakpoint management
    # ------------------------------------------------------------------

    def set_breakpoint(self, file: str, line: int) -> None:
        key = Path(file).stem
        self._breakpoints.setdefault(key, set()).add(line)

    def remove_breakpoint(self, file: str, line: int) -> None:
        key = Path(file).stem
        self._breakpoints.get(key, set()).discard(line)

    # ------------------------------------------------------------------
    # Step mode
    # ------------------------------------------------------------------

    def _set_step(self, mode: str) -> None:
        self._step_mode = mode
        self._step_depth = self.call_depth
        self._resume_event.set()

    # ------------------------------------------------------------------
    # Override _exec to inject debug hooks
    # ------------------------------------------------------------------

    def _exec(self, stmt: _ast.Stmt, env: Env) -> None:
        # Only hook on statement nodes that carry meaningful line information
        if self._should_pause(stmt):
            self._pause(stmt, env)
        super()._exec(stmt, env)

    def _should_pause(self, stmt: _ast.Stmt) -> bool:
        # Skip declaration-only nodes; they don't correspond to runtime lines
        if isinstance(stmt, (
            _ast.FunctionDecl, _ast.GovernedFunctionDecl,
            _ast.ClassDecl, _ast.ImportDecl,
            _ast.EnumDecl, _ast.StructDecl, _ast.InterfaceDecl,
        )):
            return False

        line = stmt.span.line
        file = stmt.span.file

        # Check breakpoints
        key = Path(file).stem
        if key in self._breakpoints and line in self._breakpoints[key]:
            return True

        # Check step mode
        if self._step_mode == _STEP_OVER:
            return True
        if self._step_mode == _STEP_IN:
            return True
        if self._step_mode == _STEP_OUT:
            # pause when we've returned to a shallower call depth
            if self.call_depth < self._step_depth:
                return True
        return False

    def _pause(self, stmt: _ast.Stmt, env: Env) -> None:
        """Emit a stopped event and wait for a resume/step command."""
        self._current_env = env
        line = stmt.span.line
        file = stmt.span.file

        # Determine reason
        key = Path(file).stem
        if (
            key in self._breakpoints
            and line in self._breakpoints[key]
            and self._step_mode == _STEP_NONE
        ):
            reason = "breakpoint"
        else:
            reason = "step"

        self._step_mode = _STEP_NONE  # clear step mode before pausing
        self._resume_event.clear()

        self._event_queue.put({
            "event": "stopped",
            "reason": reason,
            "file": file,
            "line": line,
        })

        # Wait until session tells us to resume
        self._resume_event.wait()

    # ------------------------------------------------------------------
    # Handle commands that arrive while paused (called from session thread)
    # ------------------------------------------------------------------

    def handle_paused_cmd(self, msg: dict) -> dict | None:
        """
        Process a command that arrived while execution is paused.
        Returns a response dict, or None if execution should resume
        (i.e., the interpreter thread will be unblocked).
        """
        cmd = msg.get("cmd")

        if cmd == "continue":
            self._step_mode = _STEP_NONE
            self._resume_event.set()
            return {"response": "ok"}

        if cmd == "step":
            self._set_step(_STEP_OVER)
            return {"response": "ok"}

        if cmd == "step_in":
            self._set_step(_STEP_IN)
            return {"response": "ok"}

        if cmd == "step_out":
            self._set_step(_STEP_OUT)
            return {"response": "ok"}

        if cmd == "variables":
            env = self._current_env
            if env is None:
                return {"response": "variables", "vars": {}}
            raw: dict[str, Any] = {}
            cur: Env | None = env
            while cur:
                for k, v in cur.values.items():
                    if k not in raw:
                        raw[k] = self._stringify(v)
                cur = cur.parent
            return {"response": "variables", "vars": raw}

        if cmd == "stack":
            return {"response": "stack", "frames": list(self._call_stack)}

        if cmd == "evaluate":
            expr_src = msg.get("expr", "")
            if self._current_env is None:
                return {"response": "evaluate", "result": "error: no active scope"}
            try:
                from .lexer import Lexer
                from .parser import Parser
                tokens = Lexer(expr_src, "<debug>").lex()
                expr_node = Parser.from_tokens(tokens)._expression()
                value = self._eval(expr_node, self._current_env)
                return {"response": "evaluate", "result": self._stringify(value)}
            except Exception as exc:
                return {"response": "evaluate", "result": f"error: {exc}"}

        # Unknown command while paused — return error but stay paused
        return {"event": "error", "message": f"unknown command while paused: {cmd}"}


# ---------------------------------------------------------------------------
# _DebugOutputList — list-like object that forwards appends to the event queue
# ---------------------------------------------------------------------------

class _DebugOutputList(list):
    """
    Mimics ``list`` so the interpreter's ``self.output.append(text)`` works,
    but also forwards every append to the debug event queue as an output event.
    """

    def __init__(self, q: queue.Queue) -> None:
        super().__init__()
        self._q = q

    def append(self, text: str) -> None:  # type: ignore[override]
        super().append(text)
        self._q.put({"event": "output", "text": text + "\n"})


# ---------------------------------------------------------------------------
# DebugSession — handles one client TCP connection
# ---------------------------------------------------------------------------

class DebugSession:
    """
    Manages one client connection.

    Life-cycle:
      1. Client connects.
      2. Session waits for commands over the socket.
      3. Client sends {"cmd": "run", "file": "..."}.
      4. Session loads and starts the Thirsty program in a background thread.
      5. Session relays events from the event queue to the client.
      6. Session dispatches commands to the paused debugger.
      7. Session ends on "quit", socket close, or program termination.
    """

    def __init__(self, conn: socket.socket, addr: tuple) -> None:
        self.conn = conn
        self.addr = addr
        self._event_queue: queue.Queue = queue.Queue()
        self._cmd_queue: queue.Queue = queue.Queue()
        self._debugger: ThirstyDebugger | None = None
        self._interp_thread: threading.Thread | None = None
        self._paused = threading.Event()
        self._running = True
        # Lock so only one thread writes to the socket at a time
        self._send_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Socket I/O helpers
    # ------------------------------------------------------------------

    def _send(self, obj: dict) -> None:
        data = (json.dumps(obj) + "\n").encode("utf-8")
        with self._send_lock:
            try:
                self.conn.sendall(data)
            except OSError:
                self._running = False

    def _readline(self) -> str | None:
        """Read one newline-terminated line from the socket."""
        buf = b""
        while True:
            try:
                chunk = self.conn.recv(1)
            except OSError:
                return None
            if not chunk:
                return None
            if chunk == b"\n":
                return buf.decode("utf-8", errors="replace").strip()
            buf += chunk

    # ------------------------------------------------------------------
    # Event forwarder (runs in a daemon thread)
    # ------------------------------------------------------------------

    def _event_forwarder(self) -> None:
        """Drain the event queue and forward to the client."""
        while self._running:
            try:
                event = self._event_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            self._send(event)
            if event.get("event") == "terminated":
                self._running = False
                break

    # ------------------------------------------------------------------
    # Interpreter thread
    # ------------------------------------------------------------------

    def _run_program(self, file: str) -> None:
        from .lexer import Lexer
        from .parser import Parser
        from .checker import Checker
        from .diagnostics import DiagnosticBundle, ThirstyError

        try:
            text = Path(file).read_text(encoding="utf-8")
        except OSError as exc:
            self._event_queue.put({"event": "error", "message": str(exc)})
            self._event_queue.put({"event": "terminated", "exit_code": 1})
            self._debugger._resume_event.set()  # unblock any pending pause
            return

        try:
            tokens = Lexer(text, file).lex()
            program = Parser.from_tokens(tokens).parse_program()
            Checker().check(program)
        except (DiagnosticBundle, Exception) as exc:
            self._event_queue.put({"event": "error", "message": str(exc)})
            self._event_queue.put({"event": "terminated", "exit_code": 1})
            if self._debugger:
                self._debugger._resume_event.set()
            return

        try:
            self._debugger.run(program)
            self._event_queue.put({"event": "terminated", "exit_code": 0})
        except RuntimeFault as rf:
            self._event_queue.put({"event": "error", "message": f"{rf.code}: {rf.message}"})
            self._event_queue.put({"event": "terminated", "exit_code": 1})
        except ThrownSignal as ts:
            self._event_queue.put({"event": "error", "message": f"unhandled throw: {ts.value!r}"})
            self._event_queue.put({"event": "terminated", "exit_code": 1})
        except Exception as exc:
            self._event_queue.put({"event": "error", "message": str(exc)})
            self._event_queue.put({"event": "terminated", "exit_code": 1})

    # ------------------------------------------------------------------
    # Main session loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        # Start event forwarder
        fwd = threading.Thread(target=self._event_forwarder, daemon=True)
        fwd.start()

        while self._running:
            line = self._readline()
            if line is None:
                break
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                self._send({"event": "error", "message": "invalid JSON"})
                continue

            cmd = msg.get("cmd")

            # ----------------------------------------------------------
            if cmd == "quit":
                self._running = False
                if self._debugger:
                    self._debugger._step_mode = _STEP_NONE
                    self._debugger._resume_event.set()
                break

            # ----------------------------------------------------------
            if cmd == "run":
                file = msg.get("file", "")
                if not file:
                    self._send({"event": "error", "message": "run: missing 'file'"})
                    continue
                if self._interp_thread and self._interp_thread.is_alive():
                    self._send({"event": "error", "message": "program already running"})
                    continue

                self._debugger = ThirstyDebugger(
                    self._event_queue,
                    self._cmd_queue,
                    current_file=file,
                )
                self._interp_thread = threading.Thread(
                    target=self._run_program,
                    args=(file,),
                    daemon=True,
                )
                self._interp_thread.start()
                self._send({"response": "ok"})
                continue

            # ----------------------------------------------------------
            if cmd in ("set_breakpoint", "remove_breakpoint"):
                if self._debugger is None:
                    self._send({"event": "error", "message": "no program loaded"})
                    continue
                bp_file = msg.get("file", "")
                bp_line = msg.get("line", 0)
                if cmd == "set_breakpoint":
                    self._debugger.set_breakpoint(bp_file, bp_line)
                else:
                    self._debugger.remove_breakpoint(bp_file, bp_line)
                self._send({"response": "ok"})
                continue

            # ----------------------------------------------------------
            # Commands that require the interpreter to be paused
            if cmd in ("continue", "step", "step_in", "step_out",
                       "variables", "stack", "evaluate"):
                if self._debugger is None:
                    self._send({"event": "error", "message": "no program loaded"})
                    continue
                response = self._debugger.handle_paused_cmd(msg)
                if response:
                    self._send(response)
                continue

            # ----------------------------------------------------------
            self._send({"event": "error", "message": f"unknown command: {cmd!r}"})

        try:
            self.conn.close()
        except OSError:
            pass
        fwd.join(timeout=2.0)


# ---------------------------------------------------------------------------
# DebugServer — accepts TCP connections
# ---------------------------------------------------------------------------

class DebugServer:
    """
    Listens on ``host:port`` and spawns a ``DebugSession`` per connection.
    Only one concurrent session is expected in typical use.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 9899) -> None:
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None

    def start(self, initial_file: str | None = None) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(5)
        print(f"Thirsty debugger listening on {self.host}:{self.port}")
        if initial_file:
            print(f"  Ready to debug: {initial_file}")
            print(f"  Connect and send: {{\"cmd\": \"run\", \"file\": \"{initial_file}\"}}")
        try:
            while True:
                try:
                    conn, addr = self._sock.accept()
                except OSError:
                    break
                print(f"  Debug client connected from {addr}")
                session = DebugSession(conn, addr)
                t = threading.Thread(target=session.run, daemon=True)
                t.start()
        finally:
            self._stop()

    def _stop(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None


# ---------------------------------------------------------------------------
# Public entry point (called from CLI)
# ---------------------------------------------------------------------------

def start_debug_server(file: str | None = None, port: int = 9899) -> None:
    """
    Start the Thirsty debug server.  If ``file`` is given it will be printed
    as a hint to the connecting client but is NOT auto-loaded — the client
    must send the ``run`` command to start execution.  This preserves the
    round-trip that lets the client set breakpoints before the program starts.
    """
    server = DebugServer(host="127.0.0.1", port=port)
    server.start(initial_file=file)
