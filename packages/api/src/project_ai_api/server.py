"""Standalone entrypoint for running the api gateway as a frozen/bundled process.

Not the uvicorn CLI: PyInstaller cannot reliably resolve the CLI's dynamic
``"project_ai_api.app:app"`` module-string import once frozen, so this binds
its own listening socket and drives ``uvicorn.Server`` directly.

Binds the socket itself (host/port resolved once, atomically) and writes the
OS-assigned port to ``--port-file`` immediately after bind and before serving.
A caller that wants to talk to this process should launch it, then read
``--port-file`` (bounded wait) rather than pre-selecting a port and hoping
nothing else claims it in between: the only process that ever binds this
socket is the one that also reports the port, so there is no window for a
second process to race for the same port.
"""

from __future__ import annotations

import argparse
import multiprocessing
import socket
from pathlib import Path

import uvicorn

from project_ai_api.app import create_app


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Project-AI api gateway standalone.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="0 selects an OS-assigned free port")
    parser.add_argument(
        "--port-file",
        type=Path,
        default=None,
        help="Path to write the resolved port to, before serving starts",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((args.host, args.port))
    sock.listen(socket.SOMAXCONN)
    resolved_port = sock.getsockname()[1]

    if args.port_file is not None:
        args.port_file.parent.mkdir(parents=True, exist_ok=True)
        args.port_file.write_text(str(resolved_port), encoding="utf-8")

    config = uvicorn.Config(create_app(), host=args.host, port=resolved_port, log_config=None)
    server = uvicorn.Server(config)
    server.run(sockets=[sock])


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
